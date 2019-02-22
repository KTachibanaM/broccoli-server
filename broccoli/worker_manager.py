import os
import sys
from common.logging import configure_werkzeug_logger
from dotenv import load_dotenv
from pathlib import Path
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from jsonschema import validate, ValidationError
from apscheduler.schedulers.blocking import BlockingScheduler
from broccoli_plugin_base.base_worker import BaseWorker
from worker_manager.reconcile import reconcile, RECONCILE_JOB_ID
from worker_manager.config_store import ConfigStore
from worker_manager.events_store import EventsStore
from worker_manager.global_metadata_store import GlobalMetadataStore

if os.path.exists('worker_manager.env'):
    print("Loading worker_manager.env")
    load_dotenv(dotenv_path=Path('worker_manager.env'))
else:
    print("worker_manager.env does not exist")

events_store = EventsStore(
    hostname=os.getenv("EVENTS_MONGODB_HOSTNAME"),
    port=int(os.getenv("EVENTS_MONGODB_PORT")),
    db=os.getenv("EVENTS_MONGODB_DB")
)
BaseWorker.events_store = events_store
config_store = ConfigStore(
    hostname=os.getenv("CONFIG_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONFIG_MONGODB_PORT")),
    db=os.getenv("CONFIG_MONGODB_DB")
)
global_metadata_store = GlobalMetadataStore(
    hostname=os.getenv("METADATA_MONGODB_HOSTNAME"),
    port=int(os.getenv("METADATA_MONGODB_PORT")),
    db=os.getenv("METADATA_MONGODB_DB"),
)

app = Flask(__name__)
configure_werkzeug_logger()
CORS(app)

# todo: authenticate all those endpoints


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


@app.route("/api/worker/<string:worker_id>/events", methods=["GET"])
def get_worker_events(worker_id: str):
    from_ms_str = request.args.get("from_ms")
    to_ms_str = request.args.get("to_ms")
    limit_str = request.args.get("limit")
    results = []
    for event in events_store.get_events_by_timestamp_descending(
        worker_id,
        from_milliseconds=None if from_ms_str is None else int(from_ms_str),
        to_milliseconds=None if to_ms_str is None else int(to_ms_str),
        limit=None if limit_str is None else int(limit_str)
    ):
        timestamp, state, metadata = event
        results.append({
            "timestamp": timestamp,
            "state": state,
            "metadata": metadata
        })
    return jsonify(results), 200


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


    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = Thread(target=start_workers)
        t.start()
    else:
        # avoid starting workers twice
        # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
        print("Didn't start workers because I am in debug mode")

    app.run(port=5002)
