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