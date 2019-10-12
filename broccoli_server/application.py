import logging
import os
import sys
from typing import Callable
from broccoli_server.database.migration import Migration
from broccoli_server.common.getenv_or_raise import getenv_or_raise
from broccoli_server.content import ContentStore
from broccoli_server.content import RpcCore
from broccoli_server.content.in_process_rpc_client import InProcessRpcClient
from broccoli_server.scheduler.worker_config_store import WorkerConfigStore
from broccoli_server.scheduler.global_metadata_store import GlobalMetadataStore
from broccoli_server.scheduler.reconciler import Reconciler
from broccoli_server.dashboard.boards_store import BoardsStore
from broccoli_server.dashboard.boards_renderer import BoardsRenderer
from broccoli_server.scheduler import WorkerCache
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from apscheduler.schedulers.background import BackgroundScheduler


class Application(object):
    def __init__(self):
        Migration(
            admin_connection_string=getenv_or_raise("MONGODB_ADMIN_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        ).migrate()

        content_store = ContentStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.rpc_core = RpcCore(content_store)
        self.worker_cache = WorkerCache()
        in_process_rpc_client = InProcessRpcClient(content_store)
        worker_config_store = WorkerConfigStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_cache=self.worker_cache
        )
        self.global_metadata_store = GlobalMetadataStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.reconciler = Reconciler(
            worker_config_store=worker_config_store,
            rpc_client=in_process_rpc_client,
            worker_cache=self.worker_cache
        )
        self.boards_store = BoardsStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB")
        )
        self.boards_renderer = BoardsRenderer(in_process_rpc_client)
        self.default_api_handler = None

        # Flask
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)

        # Less verbose logging from Flask
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)

        # Configure Flask JWT
        self.flask_app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")
        jwt = JWTManager(self.flask_app)
        admin_username = getenv_or_raise("ADMIN_USERNAME")
        admin_password = getenv_or_raise("ADMIN_PASSWORD")

        # Less verbose logging from apscheduler
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.ERROR)

        self.flask_app.before_request(self._before_request)
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

    @staticmethod
    def _index():
        return 'You\'ve hit broccoli-platform, now turn back.\n', 200

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
