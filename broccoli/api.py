import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.config_store import ConfigStore
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
server_hostname = os.getenv("SERVER_HOSTNAME")


@app.route("/api", methods=["GET"])
def api():
    config = config_store.get_config()
    if not config:
        return jsonify([]), 200
    q, fields = config

    rpc_response = requests.post(f"http://{server_hostname}:5000/api", json={
        "verb": "query",
        "metadata": {},
        "payload": q
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

    # todo: use projection here
    def shred_document(document):
        result = {}
        for field in fields:
            if field in document:
                result[field] = document[field]
        return result

    return jsonify({
        "status": "ok",
        "payload": list(map(shred_document, response["payload"]))
    }), 200


@app.route("/apiConfig", methods=["GET"])
def get_api_config():
    config = config_store.get_config()
    if not config:
        return jsonify({}), 200
    q, fields = config
    return jsonify({
        "q": q,
        "fields": fields
    }), 200


SET_API_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "q": {
            "type": "object",
        },
        "fields": {
            "type": "array",
            "contains": {
                "type": "string"
            }
        }
    },
    "required": ["q", "fields"]
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
    config_store.set_config(parsed_body["q"], parsed_body["fields"])
    return jsonify({
        "status": "ok"
    }), 200


if __name__ == '__main__':
    app.run(port=5001)
