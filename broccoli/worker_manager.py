import os
import sys
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from jsonschema import validate, ValidationError
from apscheduler.schedulers.blocking import BlockingScheduler
from worker_globals import worker_globals
from worker_manager.reconcile import reconcile, RECONCILE_JOB_ID
from worker_manager.configs_store import add, get_all, remove, update_interval_seconds
from worker_manager.events_store import get_events_by_timestamp_descending

app = Flask(__name__)
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
        "global_args": {
            "type": "array",
            "contains": {
                "type": "string"
            }
        },
        "interval_seconds": {
            "type": "number"
        }
    },
    "required": ["module", "class_name", "args", "global_args", "interval_seconds"]
}


@app.route("/api/worker", methods=["POST"])
def add_worker():
    body = request.json
    try:
        validate(instance=body, schema=ADD_WORKER_BODY_SCHEMA)
        status, message_or_worker_id = add(
            module=body["module"],
            class_name=body["class_name"],
            args=body["args"],
            global_args=body["global_args"],
            worker_globals=worker_globals,
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
    for worker_id, worker in get_all().items():
        module, class_name, args, global_args, interval_seconds = worker
        workers.append({
            "worker_id": worker_id,
            "module": module,
            "class_name": class_name,
            "args": args,
            'global_args': global_args,
            "interval_seconds": interval_seconds
        })
    return jsonify(workers), 200


@app.route("/api/worker/<string:worker_id>", methods=["DELETE"])
def remove_worker(worker_id: str):
    status, message = remove(worker_id)
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
    status, message = update_interval_seconds(worker_id, interval_seconds)
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
    for event in get_events_by_timestamp_descending(
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


if __name__ == "__main__":
    def start_workers():
        scheduler = BlockingScheduler()

        def reconcile_wrap():
            reconcile(scheduler, worker_globals)

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
