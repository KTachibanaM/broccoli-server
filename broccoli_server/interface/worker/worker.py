from abc import ABCMeta, abstractmethod
from broccoli_server.worker import WorkContext


class Worker(metaclass=ABCMeta):
    @abstractmethod
    # WARNING: actual worker_id's persisted in mongodb start with "broccoli.worker."
    # check all usages of this func
    def get_id(self) -> str:
        pass

    @abstractmethod
    def pre_work(self, context: WorkContext):
        pass

    @abstractmethod
    def work(self, context: WorkContext):
        pass
