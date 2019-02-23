import requests
from typing import Dict, List


class HttpRpcClient(object):
    def __init__(self, hostname: str, port: int):
        self.apiEndpoint = f"http://{hostname}:{port}/api"

    def query(self, q: Dict, limit: int, projection: List[str], sort: Dict[str, int], datetime_q: List[Dict]):
        return self.call(
            verb="query",
            metadata={},
            payload={
                "q": q,
                "limit": limit,
                "projection": projection,
                "sort": sort,
                "datetime_q": datetime_q
            }
        )

    def call(self, verb: str, metadata: Dict, payload: Dict):
        rpc_response = requests.post(self.apiEndpoint, json={
            "verb": verb,
            "metadata": metadata,
            "payload": payload
        })
        response = rpc_response.json()
        if "status" not in response:
            raise Exception(f"status not found in response {response}")
        if "payload" not in response:
            raise Exception(f"payload not found in response {response}")
        if response["status"] != "ok":
            raise Exception(f"status in response {response} is not ok")
        return response["payload"]
