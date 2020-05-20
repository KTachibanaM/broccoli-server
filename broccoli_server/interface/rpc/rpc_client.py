from typing import Dict, Optional, List
from abc import ABCMeta, abstractmethod


class RpcClient(metaclass=ABCMeta):
    @abstractmethod
    def blocking_query(self, q: Dict, limit: Optional[int] = None, projection: List[str] = None,
                       sort: Dict[str, int] = None, datetime_q: List[Dict] = None) -> List[Dict]:
        pass

    @abstractmethod
    def blocking_update_one(self, filter_q: Dict, update_doc: Dict):
        pass

    @abstractmethod
    def blocking_update_many(self, filter_q: Dict, update_doc: Dict):
        pass

    @abstractmethod
    def blocking_update_one_binary_string(self, filter_q: Dict, key: str, binary_string: List[bool]):
        pass

    @abstractmethod
    def blocking_append(self, idempotency_key: str, doc: Dict):
        pass

    @abstractmethod
    def blocking_append_multiple(self, idempotency_key: str, docs: List[Dict]):
        pass

    @abstractmethod
    def blocking_random_one(self, q: Dict, projection: List[str]) -> List[Dict]:
        pass

    @abstractmethod
    def blocking_count(self, q: Dict) -> int:
        pass

    @abstractmethod
    def blocking_query_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                                 max_distance: int) -> List[Dict]:
        pass

    @abstractmethod
    def blocking_query_n_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                                   pick_n: int) -> List[Dict]:
        pass
