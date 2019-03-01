from typing import Dict, Optional, List, Tuple, Union
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
    def blocking_update_one_binary_string(self, filter_q: Dict, key: str, binary_string: List[bool]):
        pass

    @abstractmethod
    def blocking_append(self, idempotency_key: str, doc: Dict):
        pass

    @abstractmethod
    def blocking_random_one(self, q: Dict, projection: List[str]) -> List[Dict]:
        pass
