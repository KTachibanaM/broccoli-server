import os
import sys
from common.logging import configure_werkzeug_logger
from common.is_flask_debug import is_flask_debug
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
    hostname=os.getenv("CONTENT_SERVER_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONTENT_SERVER_MONGODB_PORT")),
    db=os.getenv("CONTENT_SERVER_MONGODB_DB"),
    username=os.getenv("CONTENT_SERVER_MONGODB_USERNAME"),
    password=os.getenv("CONTENT_SERVER_MONGODB_PASSWORD")
)
rpc_core = RpcCore(content_store, logger)

app = Flask(__name__)
configure_werkzeug_logger()
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
        try:
            rpc_server.start_block_consuming()
        except (KeyboardInterrupt, SystemExit):
            print('RPC server exits')
            rpc_server.channel.stop_consuming()
            sys.exit(0)

    if not is_flask_debug(app):
        t = Thread(target=start_rpc_server)
        t.start()

    app.run(port=5000)
