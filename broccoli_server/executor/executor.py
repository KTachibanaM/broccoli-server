from typing import List
from abc import ABCMeta, abstractmethod
from broccoli_server.worker import WorkerMetadata


class Executor(metaclass=ABCMeta):
    @abstractmethod
    def add_job(self, job_id: str, worker_metadata: WorkerMetadata):
        pass

    @abstractmethod
    def get_job_ids(self) -> List[str]:
        pass

    @abstractmethod
    def remove_job(self, job_id: str):
        pass

    @abstractmethod
    def get_job_interval_seconds(self, job_id: str) -> int:
        pass

    @abstractmethod
    def set_job_interval_seconds(self, job_id: str, desired_interval_seconds: int):
        pass
