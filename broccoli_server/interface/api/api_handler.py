from typing import Dict
from abc import ABCMeta, abstractmethod
from broccoli_server.interface.rpc import RpcClient


class ApiHandler(metaclass=ABCMeta):
    @abstractmethod
    def handle_request(self, path: str, query_params: Dict, rpc_client: RpcClient):
        pass
