import os
import sys
import datetime
from broccoli_common.logging import configure_werkzeug_logger
from broccoli_common.is_flask_debug import is_flask_debug
from broccoli_common.load_dotenv import load_dotenv
from broccoli_common.getenv_or_raise import getenv_or_raise
from broccoli_common.configure_flask_jwt_secret_key import configure_flask_jwt_secret_key
from broccoli_common.flask_auth_route import flask_auth_route
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from jsonschema import validate, ValidationError
from apscheduler.schedulers.blocking import BlockingScheduler
from worker_manager.reconcile import reconcile, RECONCILE_JOB_ID
from worker_manager.config_store import ConfigStore
from worker_manager.global_metadata_store import GlobalMetadataStore

load_dotenv(__file__, "worker_manager.env")
load_dotenv(__file__, "workers.env")


config_store = ConfigStore(
    hostname=getenv_or_raise("WORKER_MANAGER_MONGODB_HOSTNAME"),
    port=int(getenv_or_raise("WORKER_MANAGER_MONGODB_PORT")),
    db=getenv_or_raise("WORKER_MANAGER_MONGODB_DB"),
    username=getenv_or_raise("WORKER_MANAGER_MONGODB_USERNAME"),
    password=getenv_or_raise("WORKER_MANAGER_MONGODB_PASSWORD")
)
global_metadata_store = GlobalMetadataStore(
    hostname=getenv_or_raise("WORKER_MANAGER_MONGODB_HOSTNAME"),
    port=int(getenv_or_raise("WORKER_MANAGER_MONGODB_PORT")),
    db=getenv_or_raise("WORKER_MANAGER_MONGODB_DB"),
    username=getenv_or_raise("WORKER_MANAGER_MONGODB_USERNAME"),
    password=getenv_or_raise("WORKER_MANAGER_MONGODB_PASSWORD")
)

app = Flask(__name__)
configure_werkzeug_logger()
CORS(app)
configure_flask_jwt_secret_key(app)
jwt = JWTManager(app)
jwt_exceptions = ['/', '/auth']


def create_access_token_f(identity: str) -> str:
    return create_access_token(
        identity=identity,
        expires_delta=datetime.timedelta(days=365)  # todo: just for now
    )


@app.route('/', methods=['GET'])
def root():
    return "Hello from worker-manager!"


@app.route('/auth', methods=['POST'])
def auth():
    status_code, token_or_message = flask_auth_route(request, create_access_token_f)
    if status_code != 200:
        return jsonify({
            "status": "error",
            "message": token_or_message
        }), status_code
    return jsonify({
        "status": "ok",
        "access_token": token_or_message
    }), status_code


@app.before_request
def before_request():
    r_path = request.path
    if r_path in jwt_exceptions:
        return
    verify_jwt_in_request()


ADD_WORKER_BODY_SCHEMA = {
    "type": "object",
    "properties": {
        "module": {
            "type": "string",
        },
        "class_name": {
            "type": "string",
        },
        "args": {
            "type": "object"
        },
        "interval_seconds": {
            "type": "number"
        }
    },
    "required": ["module", "class_name", "args", "interval_seconds"]
}


@app.route("/api/worker", methods=["POST"])
def add_worker():
    body = request.json
    try:
        validate(instance=body, schema=ADD_WORKER_BODY_SCHEMA)
        status, message_or_worker_id = config_store.add(
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
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": e.message
        }), 400


@app.route("/api/worker", methods=["GET"])
def get_workers():
    workers = []
    for worker_id, worker in config_store.get_all().items():
        module, class_name, args, interval_seconds = worker
        workers.append({
            "worker_id": worker_id,
            "module": module,
            "class_name": class_name,
            "args": args,
            "interval_seconds": interval_seconds
        })
    return jsonify(workers), 200


@app.route("/api/worker/<string:worker_id>", methods=["DELETE"])
def remove_worker(worker_id: str):
    status, message = config_store.remove(worker_id)
    if not status:
        return jsonify({
            "status": "error",
            "message": message
        }), 400
    else:
        return jsonify({
            "status": "ok"
        }), 200


@app.route("/api/worker/<string:worker_id>/intervalSeconds/<int:interval_seconds>", methods=["PUT"])
def update_worker_interval_seconds(worker_id: str, interval_seconds: int):
    status, message = config_store.update_interval_seconds(worker_id, interval_seconds)
    if not status:
        return jsonify({
            "status": "error",
            "message": message
        }), 400
    else:
        return jsonify({
            "status": "ok"
        }), 200


@app.route("/api/worker/<string:worker_id>/metadata", methods=["GET"])
def get_worker_metadata(worker_id: str):
    return jsonify(global_metadata_store.get_all(worker_id)), 200


@app.route("/api/worker/<string:worker_id>/metadata", methods=["POST"])
def set_worker_metadata(worker_id: str):
    parsed_body = request.json
    global_metadata_store.set_all(worker_id, parsed_body)
    return jsonify({
        "status": "ok"
    }), 200


if __name__ == "__main__":
    def start_workers():
        scheduler = BlockingScheduler()

        def reconcile_wrap():
            reconcile(config_store, scheduler)

        # todo: better way to retry after exception other than work_robust?
        scheduler.add_job(
            reconcile_wrap,
            id=RECONCILE_JOB_ID,
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


    if not is_flask_debug(app):
        t = Thread(target=start_workers)
        t.start()

    app.run(host='0.0.0.0', port=5002)
