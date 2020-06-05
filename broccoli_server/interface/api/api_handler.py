from typing import Dict
from abc import ABCMeta, abstractmethod
from broccoli_server.content import ContentStore


class ApiHandler(metaclass=ABCMeta):
    @abstractmethod
    def handle_request(self, path: str, query_params: Dict, content_store: ContentStore):
        pass
