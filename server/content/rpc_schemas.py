SCHEMAS = {
    "update_one_binary_string": {
        "payload": {
            "type": "object",
            "properties": {
                "filter_q": {
                    "type": "object",
                },
                "key": {
                    "type": "string",
                },
                "binary_string": {
                    "type": "string"
                }
            },
            "required": ["filter_q", "key", "binary_string"]
        }
    },
    "query_nearest_hamming_neighbors": {
        "payload": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "object",
                },
                "binary_string_key": {
                    "type": "string",
                },
                "from_binary_string": {
                    "type": "string"
                },
                "max_distance": {
                    "type": "number"
                }
            },
            "required": ["q", "binary_string_key", "from_binary_string", "max_distance"]
        }
    },
    "query": {
        "payload": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "object",
                },
                "limit": {
                    "type": "number",
                },
                "projection": {
                    "type": "array",
                    "contains": {
                        "type": "string"
                    }
                },
                "sort": {
                    "type": "object",
                    "contains": {
                        "type": "number"
                    }
                }
            },
            "required": ["q"]
        }
    },
    "random_one": {
        "payload": {
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
    },
    "append": {
        "payload": {
            "type": "object",
            "properties": {
                "idempotency_key": {
                    "type": "string",
                },
                "doc": {
                    "type": "object"
                }
            },
            "required": ["idempotency_key", "doc"]
        }
    },
    "count": {
        "payload": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "object",
                },
            },
            "required": ["q"]
        }
    }
}
