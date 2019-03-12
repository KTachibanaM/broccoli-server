import os
import sys
import logging
import datetime
import importlib
import json
import dotenv
from threading import Thread
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from apscheduler.schedulers.blocking import BlockingScheduler
from common.getenv_or_raise import getenv_or_raise
from common.validate_schema_or_not import validate_schema_or_not
from common.in_process_rpc_client import InProcessRpcClient
from content.content_store import ContentStore
from content.rpc_core import RpcCore
from scheduler.worker_config_store import WorkerConfigStore
from scheduler.reconciler import Reconciler
from scheduler.global_metadata_store import GlobalMetadataStore
from dashboard.boards_store import BoardsStore
from dashboard.objects.board_query import BoardQuery
from common.request_schemas import ADD_WORKER_BODY_SCHEMA

# Load environment variables
if Path(".env").exists():
    print("Loading .env")
    dotenv.load_dotenv(Path(".env"))
else:
    print("Not loading .env")
if Path(".workers.env").exists():
    print("Loading .workers.env")
    dotenv.load_dotenv(Path(".workers.env"))
else:
    print("Not loading .workers.env")

# Initialize content objects
content_store = ContentStore(
    connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
    db=getenv_or_raise("MONGODB_DB")
)
rpc_core = RpcCore(content_store)

# Initialize common objects
in_process_rpc_client = InProcessRpcClient(content_store)

# Initialize scheduler objects
worker_config_store = WorkerConfigStore(
    connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
    db=getenv_or_raise("MONGODB_DB")
)
global_metadata_store = GlobalMetadataStore(
    connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
    db=getenv_or_raise("MONGODB_DB")
)
reconciler = Reconciler(
    worker_config_store=worker_config_store,
    rpc_client=in_process_rpc_client
)

# Initialize dashboard objects
boards_store = BoardsStore(
    connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
    db=getenv_or_raise("MONGODB_DB")
)

# Initialize API objects
default_api_handler_clazz = getattr(
    importlib.import_module(getenv_or_raise("DEFAULT_API_HANDLER_MODULE")),
    getenv_or_raise("DEFAULT_API_HANDLER_CLASSNAME")
)
default_api_handler = default_api_handler_clazz()

# Flask misc.
app = Flask(__name__)
CORS(app)

# Less verbose logging from Flask
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

# Configure Flask JWT
app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")
jwt = JWTManager(app)
admin_username = getenv_or_raise("ADMIN_USERNAME")
admin_password = getenv_or_raise("ADMIN_PASSWORD")


# Less verbose logging from apscheduler
apscheduler_logger = logging.getLogger("apscheduler")
apscheduler_logger.setLevel(logging.ERROR)


# Configure so that every request except for a few are authenticated
@app.before_request
def before_request():
    r_path = request.path
    if r_path in ['/', '/auth', '/api']:
        return
    verify_jwt_in_request()


@app.route('/', methods=['GET'])
def root():
    return "A web content crawling and sorting platform"


@app.route('/auth', methods=['POST'])
def auth():
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


@app.route("/api", defaults={'path': ''}, methods=["GET"])
@app.route("/api/<path:path>")
def api(path):
    result = default_api_handler.handle_request(
        path,
        request.args.to_dict(),
        in_process_rpc_client
    )
    return jsonify(result), 200


@app.route("/apiInternal/rpc", methods=['POST'])
def _rpc():
    # todo: parse json failure
    parsed_body = request.json
    status, message_or_result = rpc_core.call(parsed_body)
    if not status:
        return jsonify({
            "status": "error",
            "payload": {
                "message": message_or_result
            }
        }), 500
    else:
        return jsonify({
            "status": "ok",
            "payload": message_or_result
        })


@app.route("/apiInternal/worker", methods=["POST"])
def _add_worker():
    body = request.json
    success, message = validate_schema_or_not(instance=body, schema=ADD_WORKER_BODY_SCHEMA)
    if not success:
        return jsonify({
            "status": "error",
            "message": message
        })
    status, message_or_worker_id = worker_config_store.add(
        module=body["module"],
        class_name=body["class_name"],
        args=body["args"],
        interval_seconds=body["interval_seconds"]
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


@app.route("/apiInternal/worker", methods=["GET"])
def _get_workers():
    workers = []
    for worker_id, worker in worker_config_store.get_all().items():
        module, class_name, args, interval_seconds = worker
        workers.append({
            "worker_id": worker_id,
            "module": module,
            "class_name": class_name,
            "args": args,
            "interval_seconds": interval_seconds
        })
    return jsonify(workers), 200


@app.route("/apiInternal/worker/<string:worker_id>", methods=["DELETE"])
def _remove_worker(worker_id: str):
    status, message = worker_config_store.remove(worker_id)
    if not status:
        return jsonify({
            "status": "error",
            "message": message
        }), 400
    else:
        return jsonify({
            "status": "ok"
        }), 200


@app.route("/apiInternal/worker/<string:worker_id>/intervalSeconds/<int:interval_seconds>", methods=["PUT"])
def _update_worker_interval_seconds(worker_id: str, interval_seconds: int):
    status, message = worker_config_store.update_interval_seconds(worker_id, interval_seconds)
    if not status:
        return jsonify({
            "status": "error",
            "message": message
        }), 400
    else:
        return jsonify({
            "status": "ok"
        }), 200


@app.route("/apiInternal/worker/<string:worker_id>/metadata", methods=["GET"])
def _get_worker_metadata(worker_id: str):
    return jsonify(global_metadata_store.get_all(worker_id)), 200


@app.route("/apiInternal/worker/<string:worker_id>/metadata", methods=["POST"])
def _set_worker_metadata(worker_id: str):
    parsed_body = request.json
    global_metadata_store.set_all(worker_id, parsed_body)
    return jsonify({
        "status": "ok"
    }), 200


@app.route("/apiInternal/board/<string:board_id>", methods=["POST"])
def _upsert_board(board_id: str):
    parsed_body = request.json
    parsed_body["q"] = json.dumps(parsed_body["q"])
    boards_store.upsert(board_id, BoardQuery(parsed_body))
    return jsonify({
        "status": "ok"
    }), 200


@app.route("/apiInternal/board/<string:board_id>", methods=["GET"])
def _get_board(board_id: str):
    board_query = boards_store.get(board_id).to_dict()
    board_query["q"] = json.loads(board_query["q"])
    return jsonify(board_query), 200


@app.route("/apiInternal/boards", methods=["GET"])
def _get_boards():
    boards = []
    for (board_id, board_query) in boards_store.get_all():
        board_query = board_query.to_dict()
        board_query["q"] = json.loads(board_query["q"])
        boards.append({
            "board_id": board_id,
            "board_query": board_query
        })
    return jsonify(boards), 200


@app.route("/apiInternal/boards/swap/<string:board_id>/<string:another_board_id>", methods=["POST"])
def _swap_boards(board_id: str, another_board_id: str):
    boards_store.swap(board_id, another_board_id)
    return jsonify({
        "status": "ok"
    }), 200


@app.route("/apiInternal/board/<string:board_id>", methods=["DELETE"])
def _remove_board(board_id: str):
    boards_store.remove(board_id)
    return jsonify({
        "status": "ok"
    }), 200


def start_scheduler():
    scheduler = BlockingScheduler()
    reconciler.set_scheduler(scheduler)
    scheduler.add_job(
        reconciler.reconcile,
        id=reconciler.RECONCILE_JOB_ID,
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


if __name__ == '__main__':
    # detect flask debug mode
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Not in debug mode, starting scheduler")
        scheduler_t = Thread(target=start_scheduler)
        scheduler_t.start()
    else:
        print("In debug mode, not starting scheduler")

    app.run(host='0.0.0.0', port=5000)
