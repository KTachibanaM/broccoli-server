import json
import importlib
from broccoli_plugin_interface.api.api_handler import ApiHandler
from broccoli_common.is_flask_debug import is_flask_debug
from broccoli_common.load_dotenv import load_dotenv
from broccoli_common.getenv_or_raise import getenv_or_raise
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.boards_store import BoardsStore
from api.objects.board_query import BoardQuery
from api.http_rpc_client import HttpRpcClient
from broccoli_common.logging import configure_werkzeug_logger


load_dotenv(__file__, "api.env")

boards_store = BoardsStore(
    hostname=getenv_or_raise("API_MONGODB_HOSTNAME"),
    port=int(getenv_or_raise("API_MONGODB_PORT")),
    db=getenv_or_raise("API_MONGODB_DB"),
    username=getenv_or_raise("API_MONGODB_USERNAME"),
    password=getenv_or_raise("API_MONGODB_PASSWORD")
)
http_rpc_client = HttpRpcClient(
    hostname=getenv_or_raise("CONTENT_SERVER_HOSTNAME"),
    port=int(getenv_or_raise("CONTENT_SERVER_PORT"))
)

app = Flask(__name__)
configure_werkzeug_logger()
CORS(app)

default_api_handler = None  # type: ApiHandler


@app.route("/api", defaults={'path': ''}, methods=["GET"])
@app.route("/api/<path:path>")
def api(path):
    return jsonify(default_api_handler.handle_request(
        path,
        request.args.to_dict(),
        http_rpc_client
    )), 200


BOARD_QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "q": {
            "type": "object",
        },
        "limit": {
            "type": "number",
        },
        "sort": {
            "type": "object"
        },
        "projections": {
            "type": "array",
            "contains": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "js_filename": {
                        "type": "string",
                    },
                    'args': {
                        "type": "array",
                    }
                },
                "required": ["name", "js_filename", "args"]
            }
        }
    },
    "required": ["q", "projections"]
}


@app.route("/board/<string:board_id>", methods=["POST"])
def upsert_board(board_id: str):
    parsed_body = request.json
    parsed_body["q"] = json.dumps(parsed_body["q"])
    boards_store.upsert(board_id, BoardQuery(parsed_body))
    return jsonify({
        "status": "ok"
    }), 200


@app.route("/board/<string:board_id>", methods=["GET"])
def get_board(board_id: str):
    board_query = boards_store.get(board_id).to_dict()
    board_query["q"] = json.loads(board_query["q"])
    return jsonify(board_query), 200


@app.route("/boards", methods=["GET"])
def get_boards():
    boards = []
    for (board_id, board_query) in boards_store.get_all():
        board_query = board_query.to_dict()
        board_query["q"] = json.loads(board_query["q"])
        boards.append({
            "board_id": board_id,
            "board_query": board_query
        })
    return jsonify(boards), 200


@app.route("/boards/swap/<string:board_id>/<string:another_board_id>", methods=["POST"])
def swap_boards(board_id: str, another_board_id: str):
    boards_store.swap(board_id, another_board_id)
    return jsonify({
        "status": "ok"
    }), 200


@app.route("/board/<string:board_id>", methods=["DELETE"])
def remove_board(board_id: str):
    boards_store.remove(board_id)
    return jsonify({
        "status": "ok"
    }), 200


if __name__ == '__main__':
    if not is_flask_debug(app):
        handler_clazz = getattr(
            importlib.import_module(getenv_or_raise("DEFAULT_API_HANDLER_MODULE")),
            getenv_or_raise("DEFAULT_API_HANDLER_CLASSNAME")
        )
        default_api_handler = handler_clazz()

    app.run(port=5001)
