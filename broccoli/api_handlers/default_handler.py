from typing import Dict
from api.base_handler import BaseHandler


class DefaultHandler(BaseHandler):
    def handle_request(self, query_params: Dict):
        from_timestamp = int(query_params["from"]) if "from" in query_params else None
        datetime_q = None
        if from_timestamp:
            datetime_q = [
                {
                    "key": "created_at",
                    "op": "lte",
                    "value": from_timestamp
                }
            ]
        return self.http_rpc_client.query(
            q={
                "mod": True
            },
            limit=15,
            projection=["s3_image_id", "source"],
            sort={
                "created_at": -1
            },
            datetime_q=datetime_q
        )
