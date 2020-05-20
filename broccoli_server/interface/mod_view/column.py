from abc import ABCMeta, abstractmethod
from typing import Dict
from broccoli_server.interface.rpc import RpcClient
from .column_render import ModViewColumnRender


class ModViewColumn(metaclass=ABCMeta):
    @abstractmethod
    def render(self, document: Dict, rpc_client: RpcClient) -> ModViewColumnRender:
        pass

    @abstractmethod
    def has_callback(self) -> bool:
        pass

    @abstractmethod
    def callback_id(self) -> str:
        pass

    @abstractmethod
    def callback(self, document: Dict, rpc_client: RpcClient):
        pass


class NonCallbackModViewColumn(ModViewColumn):
    @abstractmethod
    def render(self, document: Dict, rpc_client: RpcClient) -> ModViewColumnRender:
        pass

    def has_callback(self) -> bool:
        return False

    def callback_id(self) -> str:
        return ""

    def callback(self, document: Dict, rpc_client: RpcClient):
        pass
