import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.config_store import ConfigStore
from api.boards_store import BoardsStore
from api.board_query import BoardQuery
from common.validate_schema_or_not import validate_schema_or_not

if os.path.exists('api.env'):
    print("Loading api.env")
    load_dotenv(dotenv_path=Path('api.env'))
else:
    print("api.env does not exist")

app = Flask(__name__)
CORS(app)
config_store = ConfigStore(
    hostname=os.getenv("CONFIG_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONFIG_MONGODB_PORT")),
    db=os.getenv("CONFIG_MONGODB_DB")
)
boards_store = BoardsStore(
    hostname=os.getenv("CONFIG_MONGODB_HOSTNAME"),
    port=int(os.getenv("CONFIG_MONGODB_PORT")),
    db=os.getenv("CONFIG_MONGODB_DB")
)
server_hostname = os.getenv("SERVER_HOSTNAME")


@app.route("/api", methods=["GET"])
def api():
    config = config_store.get_config()
    if not config:
        return jsonify([]), 200
    q, projection = config

    rpc_response = requests.post(f"http://{server_hostname}:5000/api", json={
        "verb": "query",
        "metadata": {},
        "payload": {
            "q": q,
            "projection": projection
        }
    })
    response = rpc_response.json()
    if "status" not in response:
        return jsonify({
            "status": "error",
            "payload": {
                "message": "No status"
            }
        }), 400
    if "payload" not in response:
        return jsonify({
            "status": "error",
            "payload": {
                "message": "No payload"
            }
        }), 400
    if response["status"] != "ok":
        return jsonify({
            "status": "error",
            "payload": response["payload"]
        }), 400

    return jsonify({
        "status": "ok",
        "payload": response["payload"]
    }), 200


@app.route("/apiConfig", methods=["GET"])
def get_api_config():
    config = config_store.get_config()
    if not config:
        return jsonify({}), 200
    q, projection = config
    return jsonify({
        "q": q,
        "projection": projection
    }), 200


SET_API_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "q": {
            "type": "object",
        },
        "projection": {
            "type": "array",
            "contains": {
                "type": "string"
            }
        }
    },
    "required": ["q", "projection"]
}


@app.route("/apiConfig", methods=["POST"])
def set_api_config():
    parsed_body = request.json
    status, message = validate_schema_or_not(parsed_body, SET_API_CONFIG_SCHEMA)
    if not status:
        return jsonify({
            "status": "error",
            "message": message
        })
    config_store.set_config(parsed_body["q"], parsed_body["projection"])
    return jsonify({
        "status": "ok"
    }), 200


BOARD_QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "q": {
            "type": "object",
        },
        "limit": {
            "type": "number",
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
