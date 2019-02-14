from typing import Dict
from api.base_handler import BaseHandler


class DefaultHandler(BaseHandler):
    def handle_request(self, query_params: Dict):
        from_timestamp = int(query_params["from"]) if "from" in query_params else None
        return self.http_rpc_client.query(
            q={
                "mod": True
            },
            limit=15,
            projection=["s3_image_id", "source"],
            sort={
                "created_at": -1
            },
            earlier_than=from_timestamp
        )
