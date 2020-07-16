from typing import List
from abc import ABCMeta, abstractmethod
from broccoli_server.worker import WorkerMetadata


class Executor(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def add_worker(self, worker_id: str, worker_metadata: WorkerMetadata):
        pass

    @abstractmethod
    def get_worker_ids(self) -> List[str]:
        pass

    @abstractmethod
    def remove_worker(self, worker_id: str):
        pass

    @abstractmethod
    def get_worker_interval_seconds(self, worker_id: str) -> int:
        pass

    @abstractmethod
    def set_worker_interval_seconds(self, worker_id: str, desired_interval_seconds: int):
        pass

    @abstractmethod
    def get_slug(self) -> str:
        pass
