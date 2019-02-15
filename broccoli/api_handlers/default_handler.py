from typing import Dict
from api.base_handler import BaseHandler


class DefaultHandler(BaseHandler):
    def handle_request(self, path: str, query_params: Dict):
        if path == "":
            return self.handle_root(query_params)
        elif path == "random":
            return self.handle_random(query_params)
        else:
            raise Exception(f"Unknown path {path}")

    def handle_root(self, query_params: Dict):
        from_timestamp = int(query_params["from"]) if "from" in query_params else None
        to_timestamp = int(query_params["to"]) if "to" in query_params else None
        if from_timestamp:
            return self.http_rpc_client.query(
                q={
                    "mod": True
                },
                limit=15,
                projection=["s3_image_id", "source"],
                sort={
                    "created_at": -1
                },
                datetime_q=[
                    {
                        "key": "created_at",
                        "op": "lte",
                        "value": from_timestamp
                    }
                ]
            )
        elif to_timestamp:
            return list(reversed(self.http_rpc_client.query(
                q={
                    "mod": True
                },
                limit=15,
                projection=["s3_image_id", "source"],
                sort={
                    "created_at": 1
                },
                datetime_q=[
                    {
                        "key": "created_at",
                        "op": "gte",
                        "value": to_timestamp
                    }
                ]
            )))
        else:
            return self.http_rpc_client.query(
                q={
                    "mod": True
                },
                limit=15,
                projection=["s3_image_id", "source"],
                sort={
                    "created_at": -1
                },
                datetime_q=None
            )

    def handle_random(self, query_param: Dict):
        return []
