import logging
import os
import sys
import datetime
import json
import sentry_sdk
from typing import Callable, Dict
from broccoli_server.database import Migration
from broccoli_server.utils import validate_schema_or_not, getenv_or_raise
from broccoli_server.utils.request_schemas import ADD_WORKER_BODY_SCHEMA
from broccoli_server.content import ContentStore
from broccoli_server.content import RpcCore
from broccoli_server.content import InProcessRpcClient
from broccoli_server.scheduler import WorkerConfigStore
from broccoli_server.scheduler import GlobalMetadataStore
from broccoli_server.scheduler import Reconciler
from broccoli_server.scheduler import Worker
from broccoli_server.mod_view import ModViewStore
from broccoli_server.mod_view import ModViewRenderer
from broccoli_server.mod_view.objects import ModViewQuery
from broccoli_server.scheduler import WorkerCache
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from apscheduler.schedulers.background import BackgroundScheduler


class Application(object):
    def __init__(self):
        if 'SENTRY_DSN' in os.environ:
            print("SENTRY_DSN environ found, settings up sentry")
            sentry_sdk.init(os.environ['SENTRY_DSN'])
            sentry_enabled = True
        else:
            print("Not setting up sentry")
            sentry_enabled = False

        Migration(
            admin_connection_string=getenv_or_raise("MONGODB_ADMIN_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        ).migrate()

        self.content_store = ContentStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.rpc_core = RpcCore(self.content_store)
        self.worker_cache = WorkerCache()
        self.in_process_rpc_client = InProcessRpcClient(self.content_store)
        self.worker_config_store = WorkerConfigStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_cache=self.worker_cache
        )
        self.global_metadata_store = GlobalMetadataStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.reconciler = Reconciler(
            worker_config_store=self.worker_config_store,
            rpc_client=self.in_process_rpc_client,
            worker_cache=self.worker_cache,
            sentry_enabled=sentry_enabled
        )
        self.boards_store = ModViewStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.boards_renderer = ModViewRenderer(self.in_process_rpc_client)
        self.default_api_handler = None

        # Figure out path for static web artifact
        my_path = os.path.abspath(__file__)
        my_par_path = os.path.dirname(my_path)
        self.web_root = os.path.join(my_par_path, 'web')
        if os.path.exists(self.web_root):
            print(f"Loading static web artifact from {self.web_root}")
        else:
            raise RuntimeError(f"Static web artifact is not found under {self.web_root}")

        # Flask
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)

        # Less verbose logging from Flask
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)

        # Configure Flask JWT
        self.flask_app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")
        JWTManager(self.flask_app)
        self.admin_username = getenv_or_raise("ADMIN_USERNAME")
        self.admin_password = getenv_or_raise("ADMIN_PASSWORD")

        # Less verbose logging from apscheduler
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.ERROR)

        self.flask_app.before_request(self._before_request)
        self.flask_app.add_url_rule('/auth', view_func=self._auth, methods=['POST'])
        self.flask_app.add_url_rule('/api', view_func=self._api, methods=['GET'])
        self.flask_app.add_url_rule('/api/<path:path>', view_func=self._api, methods=['GET'])
        self.flask_app.add_url_rule('/apiInternal/worker', view_func=self._add_worker, methods=['POST'])
        self.flask_app.add_url_rule('/apiInternal/worker', view_func=self._get_workers, methods=['GET'])
        self.flask_app.add_url_rule(
            '/apiInternal/worker/<string:worker_id>',
            view_func=self._remove_worker,
            methods=['DELETE']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/worker/<string:worker_id>/intervalSeconds/<int:interval_seconds>',
            view_func=self._update_worker_interval_seconds,
            methods=['PUT']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/worker/<string:worker_id>/metadata',
            view_func=self._get_worker_metadata,
            methods=['GET']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/worker/<string:worker_id>/metadata',
            view_func=self._set_worker_metadata,
            methods=['POST']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/board/<string:board_id>',
            view_func=self._upsert_board,
            methods=['POST']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/board/<string:board_id>',
            view_func=self._get_board,
            methods=['GET']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/boards',
            view_func=self._get_boards,
            methods=['GET']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/boards/swap/<string:board_id>/<string:another_board_id>',
            view_func=self._swap_boards,
            methods=['POST']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/board/<string:board_id>',
            view_func=self._remove_board,
            methods=['DELETE']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/renderBoard/<string:board_id>',
            view_func=self._render_board,
            methods=['GET']
        )
        self.flask_app.add_url_rule(
            '/apiInternal/callbackBoard/<string:callback_id>',
            view_func=self._callback_board,
            methods=['POST']
        )
        self.flask_app.add_url_rule('/web', view_func=self._web, methods=['GET'])
        self.flask_app.add_url_rule('/web/<path:filename>', view_func=self._web, methods=['GET'])
        self.flask_app.add_url_rule('/', view_func=self._index, methods=['GET'])

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

    @staticmethod
    def _before_request():
        r_path = request.path
        if r_path.startswith("/apiInternal"):
            verify_jwt_in_request()

    def _auth(self):
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
        if username != self.admin_username or password != self.admin_password:
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

    @staticmethod
    def _index():
        return redirect('/web')

    def _api(self, path=''):
        result = self.default_api_handler.handle_request(
            path,
            request.args.to_dict(),
            self.in_process_rpc_client
        )
        return jsonify(result), 200

    def _add_worker(self):
        body = request.json
        success, message = validate_schema_or_not(instance=body, schema=ADD_WORKER_BODY_SCHEMA)
        if not success:
            return jsonify({
                "status": "error",
                "message": message
            })
        status, message_or_worker_id = self.worker_config_store.add(
            Worker(
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

    def _get_workers(self):
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

    def _remove_worker(self, worker_id: str):
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

    def _update_worker_interval_seconds(self, worker_id: str, interval_seconds: int):
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

    def _get_worker_metadata(self, worker_id: str):
        return jsonify(self.global_metadata_store.get_all(worker_id)), 200

    def _set_worker_metadata(self, worker_id: str):
        parsed_body = request.json
        self.global_metadata_store.set_all(worker_id, parsed_body)
        return jsonify({
            "status": "ok"
        }), 200

    def _upsert_board(self, board_id: str):
        parsed_body = request.json
        parsed_body["q"] = json.dumps(parsed_body["q"])
        self.boards_store.upsert(board_id, ModViewQuery(parsed_body))
        return jsonify({
            "status": "ok"
        }), 200

    def _get_board(self, board_id: str):
        board_query = self.boards_store.get(board_id).to_dict()
        board_query["q"] = json.loads(board_query["q"])
        return jsonify(board_query), 200

    def _get_boards(self):
        boards = []
        for (board_id, board_query) in self.boards_store.get_all():
            board_query = board_query.to_dict()
            board_query["q"] = json.loads(board_query["q"])
            boards.append({
                "board_id": board_id,
                "board_query": board_query
            })
        return jsonify(boards), 200

    def _swap_boards(self, board_id: str, another_board_id: str):
        self.boards_store.swap(board_id, another_board_id)
        return jsonify({
            "status": "ok"
        }), 200

    def _remove_board(self, board_id: str):
        self.boards_store.remove(board_id)
        return jsonify({
            "status": "ok"
        }), 200

    def _render_board(self, board_id: str):
        q = self.boards_store.get(board_id)
        return jsonify({
            "board_query": q.to_dict(),
            "payload": self.boards_renderer.render_as_dict(q),
            "count_without_limit": self.content_store.count(json.loads(q.q))
        }), 200

    def _callback_board(self, callback_id: str):
        document = request.json  # type: Dict
        self.boards_renderer.callback(callback_id, document)
        return jsonify({
            "status": "ok"
        }), 200

    def _web(self, filename=''):
        if filename == '':
            return send_from_directory(self.web_root, "index.html")
        elif os.path.exists(os.path.join(self.web_root, *filename.split("/"))):
            return send_from_directory(self.web_root, filename)
        else:
            return send_from_directory(self.web_root, "index.html")

    def start(self):
        # detect flask debug mode
        # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
        if not self.flask_app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print("Not in debug mode, starting scheduler")
            scheduler = BackgroundScheduler()
            self.reconciler.set_scheduler(scheduler)
            scheduler.add_job(
                self.reconciler.reconcile,
                id=self.reconciler.RECONCILE_JOB_ID,
                trigger='interval',
                seconds=10
            )

            print(f"Press Ctrl+{'Break' if os.name == 'nt' else 'C'} to exit")
            try:
                scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                print('Workers exit')
                scheduler.shutdown(wait=False)
                sys.exit(0)
        else:
            print("In debug mode, not starting scheduler")

        self.flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
