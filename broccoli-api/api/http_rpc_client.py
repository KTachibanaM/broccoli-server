import requests
from typing import Dict, List, Optional
from broccoli_plugin_interface.rpc_client import RpcClient


class HttpRpcClient(RpcClient):
    def __init__(self, hostname: str, port: int):
        self.apiEndpoint = f"http://{hostname}:{port}/api"

    def blocking_query(self, q: Dict, limit: Optional[int] = None, projection: List[str] = None,
                       sort: Dict[str, int] = None, datetime_q: List[Dict] = None) -> List[Dict]:
        return self._call(
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

    def blocking_update_one(self, filter_q: Dict, update_doc: Dict):
        raise NotImplemented()

    def blocking_update_one_binary_string(self, filter_q: Dict, key: str, binary_string: List[bool]):
        raise NotImplemented()

    def blocking_append(self, idempotency_key: str, doc: Dict):
        raise NotImplemented()

    def _call(self, verb: str, metadata: Dict, payload: Dict):
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
