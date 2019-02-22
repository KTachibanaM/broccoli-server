import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.boards_store import BoardsStore
from api.objects.board_query import BoardQuery
from api_handlers import DefaultHandler
from common.logging import configure_werkzeug_logger

if os.path.exists('api.env'):
    print("Loading api.env")
    load_dotenv(dotenv_path=Path('api.env'))
else:
    print("api.env does not exist")

boards_store = BoardsStore(
    hostname=os.getenv("CONFIG_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONFIG_MONGODB_PORT")),
    db=os.getenv("CONFIG_MONGODB_DB")
)
server_hostname = os.getenv("SERVER_HOSTNAME")

app = Flask(__name__)
configure_werkzeug_logger()
CORS(app)

api_handler = DefaultHandler()


@app.route("/api", defaults={'path': ''}, methods=["GET"])
@app.route("/api/<path:path>")
def api(path):
    return jsonify(api_handler.handle_request(path, request.args.to_dict())), 200


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
    app.run(port=5001)
