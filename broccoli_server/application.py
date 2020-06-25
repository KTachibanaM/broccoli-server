import logging
import os
import sys
import datetime
import json
import base64
import sentry_sdk
from typing import Callable, Dict, List, Tuple, Optional
from broccoli_server.database import Migration
from broccoli_server.utils import validate_schema_or_not, getenv_or_raise
from broccoli_server.utils.request_schemas import ADD_WORKER_BODY_SCHEMA
from broccoli_server.content import ContentStore
from broccoli_server.worker import WorkerConfigStore, GlobalMetadataStore, WorkerMetadata, WorkerCache, \
    MetadataStoreFactory, WorkContextFactory, WorkWrapper
from broccoli_server.reconciler import Reconciler
from broccoli_server.mod_view import ModViewStore, ModViewRenderer, ModViewQuery
from broccoli_server.executor import ApsNativeExecutor, ApsSubprocessExecutor
from broccoli_server.interface.api import ApiHandler
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from apscheduler.schedulers.background import BackgroundScheduler


class Application(object):
    def __init__(self, run_worker_invocation_py_path: Optional[str] = None):
        self.run_worker_invocation_py_path = run_worker_invocation_py_path  # type: Optional[str]

        # Environment
        if 'SENTRY_DSN' in os.environ:
            print("SENTRY_DSN environ found, settings up sentry")
            sentry_sdk.init(os.environ['SENTRY_DSN'])
            sentry_enabled = True
        else:
            print("Not setting up sentry")
            sentry_enabled = False

        if os.environ.get('PAUSE_WORKERS', 'false') == 'true':
            pause_workers = True
        else:
            pause_workers = False

        # Database migration
        Migration(
            admin_connection_string=getenv_or_raise("MONGODB_ADMIN_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        ).migrate()

        # Work wrapper
        self.content_store = ContentStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        metadata_store_factory = MetadataStoreFactory(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )
        self.worker_context_factory = WorkContextFactory(self.content_store, metadata_store_factory)
        self.worker_cache = WorkerCache()
        self.worker_config_store = WorkerConfigStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_cache=self.worker_cache
        )
        self.work_wrapper = WorkWrapper(
            work_context_factory=self.worker_context_factory,
            worker_cache=self.worker_cache,
            worker_config_store=self.worker_config_store,
            sentry_enabled=sentry_enabled,
            pause_workers=pause_workers
        )

        self.default_api_handler = None  # type: Optional[ApiHandler]
        self.mod_view_store = ModViewStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.boards_renderer = ModViewRenderer(self.content_store)

    def add_worker(self, module: str, class_name: str, constructor: Callable):
        self.worker_cache.add(
            module=module,
            class_name=class_name,
            constructor=constructor
        )

    def set_default_api_handler(self, constructor: Callable):
        self.default_api_handler = constructor()

    def add_column(self, module: str, class_name: str, constructor: Callable):
        self.boards_renderer.add_column(
            module=module,
            class_name=class_name,
            constructor=constructor
        )

    def declare_mod_views(self, mod_views: List[Tuple[str, ModViewQuery]]):
        self.mod_view_store.declare_mod_views(mod_views)

    def start(self):
        # Other objects
        global_metadata_store = GlobalMetadataStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )

        root_scheduler = BackgroundScheduler()

        if self.run_worker_invocation_py_path:
            print("Solely using aps subprocess executor")
            executor = ApsSubprocessExecutor(
                scheduler=root_scheduler,
                run_worker_invocation_py_path=self.run_worker_invocation_py_path
            )
        else:
            executor = ApsNativeExecutor(
                scheduler=root_scheduler,
                work_wrapper=self.work_wrapper,
                work_context_factory=self.worker_context_factory,
            )
        reconciler = Reconciler(
            worker_config_store=self.worker_config_store,
            root_scheduler=root_scheduler,
            executor=executor
        )

        # Figure out path for static web artifact
        my_path = os.path.abspath(__file__)
        my_par_path = os.path.dirname(my_path)
        web_root = os.path.join(my_par_path, 'web')
        if os.path.exists(web_root):
            print(f"Loading static web artifact from {web_root}")
        else:
            raise RuntimeError(f"Static web artifact is not found under {web_root}")

        # Configure Flask
        flask_app = Flask(__name__)
        CORS(flask_app)

        # Less verbose logging from Flask
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)

        # Configure Flask JWT
        flask_app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")
        JWTManager(flask_app)
        admin_username = getenv_or_raise("ADMIN_USERNAME")
        admin_password = getenv_or_raise("ADMIN_PASSWORD")

        # Configure Flask paths and handlers
        def _before_request():
            r_path = request.path
            if r_path.startswith("/apiInternal"):
                verify_jwt_in_request()

        flask_app.before_request(_before_request)

        @flask_app.route('/auth', methods=['POST'])
        def _auth():
            username = request.json.get('username', None)
            password = request.json.get('password', None)
            if not username:
                return jsonify({
                    "status": "error",
                    "message": "Missing username"
                }), 400
            if not password:
                return jsonify({
                    "status": "error",
                    "message": "Missing password"
                }), 400
            if username != admin_username or password != admin_password:
                return jsonify({
                    "status": "error",
                    "message": "Wrong username/password"
                }), 401
            access_token = create_access_token(
                identity=username,
                expires_delta=datetime.timedelta(days=365)  # todo: just for now
            )
            return jsonify({
                "status": "ok",
                "access_token": access_token
            }), 200

        @flask_app.route('/', methods=['GET'])
        def _index():
            return redirect('/web')

        @flask_app.route('/api', methods=['GET'])
        @flask_app.route('/api/<path:path>', methods=['GET'])
        def _api(path=''):
            if not self.default_api_handler:
                return {"error": "no api"}, 404
            default_api_handler = self.default_api_handler  # type: ApiHandler
            result = default_api_handler.handle_request(
                path,
                request.args.to_dict(),
                self.content_store
            )
            return jsonify(result), 200

        @flask_app.route('/apiInternal/worker', methods=['POST'])
        def _add_worker():
            body = request.json
            success, message = validate_schema_or_not(instance=body, schema=ADD_WORKER_BODY_SCHEMA)
            if not success:
                return jsonify({
                    "status": "error",
                    "message": message
                })
            status, message_or_worker_id = self.worker_config_store.add(
                WorkerMetadata(
                    module=body["module"],
                    class_name=body["class_name"],
                    args=body["args"],
                    interval_seconds=body["interval_seconds"],
                    # TODO: allow changing when add
                    error_resiliency=-1
                )
            )
            if not status:
                return jsonify({
                    "status": "error",
                    "message": message_or_worker_id
                }), 400
            else:
                return jsonify({
                    "status": "ok",
                    "worker_id": message_or_worker_id
                }), 200

        @flask_app.route('/apiInternal/worker', methods=['GET'])
        def _get_workers():
            workers = []
            for worker_id, worker in self.worker_config_store.get_all().items():
                module, class_name, args, interval_seconds, error_resiliency \
                    = worker.module, worker.class_name, worker.args, worker.interval_seconds, worker.error_resiliency
                workers.append({
                    "worker_id": worker_id,
                    "module": module,
                    "class_name": class_name,
                    "args": args,
                    "interval_seconds": interval_seconds,
                    "error_resiliency": error_resiliency
                })
            return jsonify(workers), 200

        @flask_app.route('/apiInternal/worker/<string:worker_id>', methods=['DELETE'])
        def _remove_worker(worker_id: str):
            status, message = self.worker_config_store.remove(worker_id)
            if not status:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
            else:
                return jsonify({
                    "status": "ok"
                }), 200

        @flask_app.route(
            '/apiInternal/worker/<string:worker_id>/intervalSeconds/<int:interval_seconds>',
            methods=['PUT']
        )
        def _update_worker_interval_seconds(worker_id: str, interval_seconds: int):
            status, message = self.worker_config_store.update_interval_seconds(worker_id, interval_seconds)
            if not status:
                return jsonify({
                    "status": "error",
                    "message": message
                }), 400
            else:
                return jsonify({
                    "status": "ok"
                }), 200

        @flask_app.route('/apiInternal/worker/<string:worker_id>/metadata', methods=['GET'])
        def _get_worker_metadata(worker_id: str):
            return jsonify(global_metadata_store.get_all(worker_id)), 200

        @flask_app.route('/apiInternal/worker/<string:worker_id>/metadata', methods=['POST'])
        def _set_worker_metadata(worker_id: str):
            parsed_body = request.json
            global_metadata_store.set_all(worker_id, parsed_body)
            return jsonify({
                "status": "ok"
            }), 200

        @flask_app.route('/apiInternal/board/<string:board_id>', methods=['POST'])
        def _upsert_board(board_id: str):
            parsed_body = request.json
            parsed_body["q"] = json.dumps(parsed_body["q"])
            self.mod_view_store.upsert(board_id, ModViewQuery(parsed_body))
            return jsonify({
                "status": "ok"
            }), 200

        @flask_app.route('/apiInternal/board/<string:board_id>', methods=['GET'])
        def _get_board(board_id: str):
            board_query = self.mod_view_store.get(board_id).to_dict()
            board_query["q"] = json.loads(board_query["q"])
            return jsonify(board_query), 200

        @flask_app.route('/apiInternal/boards', methods=['GET'])
        def _get_boards():
            boards = []
            for (board_id, board_query) in self.mod_view_store.get_all():
                board_query = board_query.to_dict()
                board_query["q"] = json.loads(board_query["q"])
                boards.append({
                    "board_id": board_id,
                    "board_query": board_query
                })
            return jsonify(boards), 200

        @flask_app.route(
            '/apiInternal/boards/swap/<string:board_id>/<string:another_board_id>',
            methods=['POST']
        )
        def _swap_boards(board_id: str, another_board_id: str):
            self.mod_view_store.swap(board_id, another_board_id)
            return jsonify({
                "status": "ok"
            }), 200

        @flask_app.route('/apiInternal/board/<string:board_id>', methods=['DELETE'])
        def _remove_board(board_id: str):
            self.mod_view_store.remove(board_id)
            return jsonify({
                "status": "ok"
            }), 200

        @flask_app.route('/apiInternal/renderBoard/<string:board_id>', methods=['GET'])
        def _render_board(board_id: str):
            q = self.mod_view_store.get(board_id)
            return jsonify({
                "board_query": q.to_dict(),
                "payload": self.boards_renderer.render_as_dict(q),
                "count_without_limit": self.content_store.count(json.loads(q.q))
            }), 200

        @flask_app.route('/apiInternal/callbackBoard/<string:callback_id>', methods=['POST'])
        def _callback_board(callback_id: str):
            document = request.json  # type: Dict
            self.boards_renderer.callback(callback_id, document)
            return jsonify({
                "status": "ok"
            }), 200

        @flask_app.route('/web', methods=['GET'])
        @flask_app.route('/web/<path:filename>', methods=['GET'])
        def _web(filename=''):
            if filename == '':
                return send_from_directory(web_root, "index.html")
            elif os.path.exists(os.path.join(web_root, *filename.split("/"))):
                return send_from_directory(web_root, filename)
            else:
                return send_from_directory(web_root, "index.html")

        # detect flask debug mode
        # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
        if not flask_app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print("Not in debug mode, starting reconciler")
            print(f"Press Ctrl+{'Break' if os.name == 'nt' else 'C'} to exit")
            try:
                reconciler.start()
            except (KeyboardInterrupt, SystemExit):
                print('Reconciler stopping...')
                reconciler.stop()
                sys.exit(0)
        else:
            print("In debug mode, not starting reconciler")

        flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))

    def run_worker(self):
        args = getenv_or_raise('WORKER_ARGS_BASE64')
        args = base64.b64decode(args)
        args = json.loads(args)

        worker_metadata = WorkerMetadata(
            module=getenv_or_raise('WORKER_MODULE'),
            class_name=getenv_or_raise('WORKER_CLASS_NAME'),
            args=args,
            interval_seconds=int(getenv_or_raise('WORKER_INTERVAL_SECONDS')),
            error_resiliency=int(getenv_or_raise('WORKER_ERROR_RESILIENCY')),
        )
        work_wrap_and_id = self.work_wrapper.wrap(worker_metadata)
        if not work_wrap_and_id:
            # todo: log
            return
        work_wrap, worker_id = work_wrap_and_id
        work_wrap()
        print(f"Executed worker {worker_id}")
