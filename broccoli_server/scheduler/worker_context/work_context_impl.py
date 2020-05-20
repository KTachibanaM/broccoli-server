import logging
from .metadata_store_impl import MetadataStoreImpl
from broccoli_server.utils import DefaultHandler, get_logging_level
from broccoli_server.utils.getenv_or_raise import getenv_or_raise
from broccoli_server.interface.worker_manager import WorkContext
from broccoli_server.interface.worker_manager import MetadataStore
from broccoli_server.interface.rpc import RpcClient


class WorkContextImpl(WorkContext):
    def __init__(self, worker_id: str, rpc_client: RpcClient):
        self._logger = logging.getLogger(worker_id)
        self._logger.setLevel(get_logging_level())
        self._logger.addHandler(DefaultHandler)

        self._rpc_client = rpc_client
        self._metadata_store = MetadataStoreImpl(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_id=worker_id
        )

    @property
    def rpc_client(self) -> RpcClient:
        return self._rpc_client

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def metadata_store(self) -> MetadataStore:
        return self._metadata_store
