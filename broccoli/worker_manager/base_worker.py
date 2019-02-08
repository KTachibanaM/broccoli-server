import logging
import time
from abc import ABCMeta, abstractmethod
from worker_manager.clients.amqp_rpc_client import AmqpRpcClient
from worker_manager.clients.metadata_store import MetadataStore
from worker_manager.events_store import add_event


class BaseWorker(metaclass=ABCMeta):
    def __init__(self, _id: str):
        self._id = f"broccoli.workers.{_id}"
        self.logger = None
        self.rpc_client = None
        self.metadata_store = None

    def pre_work_wrap(self):
        self.logger = logging.getLogger(self._id)
        # logger is already setup in workers.logger
        # since logger "broccoli.workers.xxx" is a descendant of logger 'broccoli.workers"

        # self.logger.setLevel(logging.INFO)
        # self.logger.addHandler(DefaultHandler)

        # todo: pass parameters in
        self.rpc_client = AmqpRpcClient(host='localhost', port=5672, logger=self.logger, callback_queue_name=self._id)
        self.metadata_store = MetadataStore(hostname='localhost', port=27017, collection_name=self._id)

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
            add_event(self._id, "STARTED", {})
            started_time = time.time_ns()

            self.work()

            finished_time = time.time_ns()
            add_event(self._id, "FINISHED", {"run_time_nanoseconds": finished_time - started_time})
        except Exception as e:
            exception_as_string = getattr(e, 'message', repr(e))
            self.logger.error(f"Caught exception while doing work, message {exception_as_string}")
            add_event(self._id, "ERRORED", {"exception": exception_as_string})
