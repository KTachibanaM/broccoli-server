import sys
from common.logging import configure_werkzeug_logger
from common.is_flask_debug import is_flask_debug
from common.load_dotenv import load_dotenv
from common.getenv_or_raise import getenv_or_raise
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from server.logger import logger
from server.content_store import ContentStore
from server.amqp_rpc_server import AmqpRpcServer
from server.rpc_core import RpcCore

load_dotenv(__file__, "server.env")


content_store = ContentStore(
    hostname=getenv_or_raise("CONTENT_SERVER_MONGODB_HOSTNAME"),
    port=int(getenv_or_raise("CONTENT_SERVER_MONGODB_PORT")),
    db=getenv_or_raise("CONTENT_SERVER_MONGODB_DB"),
    username=getenv_or_raise("CONTENT_SERVER_MONGODB_USERNAME"),
    password=getenv_or_raise("CONTENT_SERVER_MONGODB_PASSWORD")
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
            host=getenv_or_raise("RPC_AMQP_HOSTNAME"),
            port=int(getenv_or_raise("RPC_AMQP_PORT")),
            vhost=getenv_or_raise("RPC_AMQP_VHOST"),
            username=getenv_or_raise("RPC_AMQP_USERNAME"),
            password=getenv_or_raise("RPC_AMQP_PASSWORD"),
            rpc_request_queue_name=getenv_or_raise("RPC_AMQP_REQUEST_QUEUE_NAME"),
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
