from typing import Dict, List, Optional
from broccoli_server.content.content_store import ContentStore
from broccoli_server.interface.rpc import RpcClient


class InProcessRpcClient(RpcClient):
    def __init__(self, content_store: ContentStore):
        self.content_store = content_store

    def blocking_query(self, q: Dict, limit: Optional[int] = None, projection: List[str] = None,
                       sort: Dict[str, int] = None, datetime_q: List[Dict] = None) -> List[Dict]:
        return self.content_store.query(q, limit, projection, sort, datetime_q)

    def blocking_update_one(self, filter_q: Dict, update_doc: Dict):
        self.content_store.update_one(filter_q, update_doc)

    def blocking_update_many(self, filter_q: Dict, update_doc: Dict):
        self.content_store.update_many(filter_q, update_doc)

    def blocking_update_one_binary_string(self, filter_q: Dict, key: str, binary_string: List[bool]):
        bs = ''.join(list(map(lambda b: '1' if b else '0', binary_string)))
        self.content_store.update_one_binary_string(filter_q, key, bs)

    def blocking_append(self, idempotency_key: str, doc: Dict):
        self.content_store.append(doc, idempotency_key)

    def blocking_append_multiple(self, idempotency_key: str, docs: List[Dict]):
        self.content_store.append_multiple(docs, idempotency_key)

    def blocking_random_one(self, q: Dict, projection: List[str]) -> dict:
        return self.content_store.random_one(q, projection)

    def blocking_count(self, q: Dict) -> int:
        return self.content_store.count(q)

    def blocking_query_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                                 max_distance: int):
        return self.content_store.query_nearest_hamming_neighbors(q, binary_string_key, from_binary_string, max_distance)

    def blocking_query_n_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                                   pick_n: int) -> List[Dict]:
        return self.content_store.query_n_nearest_hamming_neighbors(q, binary_string_key, from_binary_string, pick_n)
