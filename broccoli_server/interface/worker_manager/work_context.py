import logging
from abc import ABCMeta
from broccoli_server.interface.rpc import RpcClient
from .metadata_store import MetadataStore


class WorkContext(metaclass=ABCMeta):
    @property
    def metadata_store(self) -> MetadataStore:
        pass

    @property
    def rpc_client(self) -> RpcClient:
        pass

    @property
    def logger(self) -> logging.Logger:
        pass
