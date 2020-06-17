from typing import List
from .executor import Executor
from abc import ABC, abstractmethod
from broccoli_server.worker import WorkerMetadata
from apscheduler.schedulers.background import BackgroundScheduler


class ApsExecutor(Executor, ABC):
    def __init__(self, scheduler: BackgroundScheduler):
        self.scheduler = scheduler

    @abstractmethod
    def add_job(self, job_id: str, worker_metadata: WorkerMetadata):
        pass

    def get_job_ids(self) -> List[str]:
        job_ids = []
        for job in self.scheduler.get_jobs():
            job_ids.append(job.id)
        return job_ids

    def remove_job(self, job_id: str):
        self.scheduler.remove_job(job_id)

    def get_job_interval_seconds(self, job_id: str) -> int:
        return self.scheduler.get_job(job_id).trigger.interval.seconds

    def set_job_interval_seconds(self, job_id: str, desired_interval_seconds: int):
        self.scheduler.reschedule_job(
            job_id=job_id,
            trigger='interval',
            seconds=desired_interval_seconds
        )
