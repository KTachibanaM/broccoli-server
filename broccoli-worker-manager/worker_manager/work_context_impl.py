import logging
import os
from .amqp_rpc_client import AmqpRpcClient
from .metadata_store_impl import MetadataStoreImpl
from broccoli_common.logging import DefaultHandler
from broccoli_plugin_interface.worker_manager.work_context import WorkContext
from broccoli_plugin_interface.worker_manager.metadata_store import MetadataStore
from broccoli_plugin_interface.rpc_client import RpcClient


class WorkContextImpl(WorkContext):
    def __init__(self, worker_id: str):
        self._logger = logging.getLogger(worker_id)
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(DefaultHandler)

        self._rpc_client = AmqpRpcClient(
            host=os.getenv("RPC_AMQP_HOSTNAME"),
            port=int(os.getenv("RPC_AMQP_PORT")),
            vhost=os.getenv("RPC_AMQP_VHOST"),
            username=os.getenv("RPC_AMQP_USERNAME"),
            password=os.getenv("RPC_AMQP_PASSWORD"),
            rpc_request_queue_name=os.getenv("RPC_AMQP_REQUEST_QUEUE_NAME"),
            callback_queue_name=worker_id,
            logger=self.logger,
        )
        self._metadata_store = MetadataStoreImpl(
            hostname=os.getenv("WORKER_MANAGER_MONGODB_HOSTNAME"),
            port=int(os.getenv("WORKER_MANAGER_MONGODB_PORT")),
            db=os.getenv("WORKER_MANAGER_MONGODB_DB"),
            username=os.getenv("WORKER_MANAGER_MONGODB_USERNAME"),
            password=os.getenv("WORKER_MANAGER_MONGODB_PASSWORD"),
            collection_name=worker_id
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
