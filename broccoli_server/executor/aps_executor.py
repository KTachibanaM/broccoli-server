from typing import List, Callable
from .executor import Executor
from abc import ABC, abstractmethod
from broccoli_server.worker import WorkerMetadata
from apscheduler.schedulers.background import BackgroundScheduler


class ApsExecutor(Executor, ABC):
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    @abstractmethod
    def get_worker_func(self, worker_id: str, worker_metadata: WorkerMetadata) -> Callable:
        pass

    def add_worker(self, worker_id: str, worker_metadata: WorkerMetadata):
        self.scheduler.add_job(
            self.get_worker_func(worker_id, worker_metadata),
            id=worker_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )

    def get_worker_ids(self) -> List[str]:
        worker_ids = []
        for job in self.scheduler.get_jobs():
            worker_ids.append(job.id)
        return worker_ids

    def remove_worker(self, worker_id: str):
        self.scheduler.remove_job(worker_id)

    def get_worker_interval_seconds(self, worker_id: str) -> int:
        return self.scheduler.get_job(worker_id).trigger.interval.seconds

    def set_worker_interval_seconds(self, worker_id: str, desired_interval_seconds: int):
        self.scheduler.reschedule_job(job_id=worker_id, trigger='interval', seconds=desired_interval_seconds)
