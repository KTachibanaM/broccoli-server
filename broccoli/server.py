import os
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
from common.rpc import RPC_REQUEST_QUEUE
from server.logger import logger
from server.amqp_rpc_server import AmqpRpcServer
from server.rpc_core import RpcCore

rpc_core = RpcCore(logger)
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
        # todo: make it in a config file
        rpc_server = AmqpRpcServer(host='localhost', port=5672, rpc_request_queue_name=RPC_REQUEST_QUEUE, rpc_core=rpc_core,
                                   logger=logger)
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
