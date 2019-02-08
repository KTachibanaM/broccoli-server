import os
from pathlib import Path
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from server.logger import logger
from server.content_store import ContentStore
from server.amqp_rpc_server import AmqpRpcServer
from server.rpc_core import RpcCore

if os.path.exists('server.env'):
    print("Loading server.env")
    load_dotenv(dotenv_path=Path('server.env'))
else:
    print("server.env does not exist")

content_store = ContentStore(
    hostname=os.getenv("CONTENT_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONTENT_MONGODB_PORT")),
    db=os.getenv("CONTENT_MONGODB_DB")
)
rpc_core = RpcCore(content_store, logger)
app = Flask(__name__)
CORS(app)


# todo: authenticate this
@app.route("/api", methods=['POST'])
def api():
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


if __name__ == '__main__':
    def start_rpc_server():
        rpc_server = AmqpRpcServer(
            host=os.getenv("RPC_AMQP_HOSTNAME"),
            port=int(os.getenv("RPC_AMQP_PORT")),
            rpc_request_queue_name=os.getenv("RPC_AMQP_REQUEST_QUEUE_NAME"),
            rpc_core=rpc_core,
            logger=logger
        )
        # todo: ctrl+c to stop this
        rpc_server.start_block_consuming()

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = Thread(target=start_rpc_server)
        t.start()
    else:
        # avoid starting workers twice
        # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
        print("Didn't start rpc server because I am in debug mode")

    app.run(port=5000)
