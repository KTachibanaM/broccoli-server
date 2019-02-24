import os
import logging
import time
from abc import ABCMeta, abstractmethod
from .amqp_rpc_client import AmqpRpcClient
from .metadata_store import MetadataStore

DefaultHandler = logging.StreamHandler()
DefaultHandler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))


class BaseWorker(metaclass=ABCMeta):
    def __init__(self, _id: str):
        self._id = f"broccoli.workers.{_id}"
        self.logger = None
        self.rpc_client = None
        self.metadata_store = None

    def pre_work_wrap(self):
        self.logger = logging.getLogger(self._id)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(DefaultHandler)

        self.rpc_client = AmqpRpcClient(
            host=os.getenv("RPC_AMQP_HOSTNAME"),
            port=int(os.getenv("RPC_AMQP_PORT")),
            rpc_request_queue_name=os.getenv("RPC_AMQP_REQUEST_QUEUE_NAME"),
            logger=self.logger,
            callback_queue_name=self._id
        )
        self.metadata_store = MetadataStore(
            hostname=os.getenv("WORKER_MANAGER_MONGODB_HOSTNAME"),
            port=int(os.getenv("WORKER_MANAGER_MONGODB_PORT")),
            db=os.getenv("WORKER_MANAGER_MONGODB_DB"),
            username=os.getenv("WORKER_MANAGER_MONGODB_USERNAME"),
            password=os.getenv("WORKER_MANAGER_MONGODB_PASSWORD"),
            collection_name=self._id
        )

        self.pre_work()

    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def pre_work(self):
        pass

    def work_wrap(self):
        if not self.logger or not self.rpc_client or not self.metadata_store:
            self.logger.error(f"Some of the clients are not initialized")
            return
        try:
            # todo: reaper to clean events
            self.logger.info("Worker started")
            started_time = time.time_ns()

            self.work()

            finished_time = time.time_ns()
            self.logger.info(f"Worker finished, runtime {(finished_time - started_time) / 1000 / 1000} milliseconds")
        except Exception as e:
            exception_as_string = getattr(e, 'message', repr(e))
            self.logger.error(f"Caught exception while doing work, message {exception_as_string}")
