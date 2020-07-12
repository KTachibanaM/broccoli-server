from typing import List, Callable
from .executor import Executor
from abc import ABC, abstractmethod
from broccoli_server.worker import WorkerMetadata
from apscheduler.schedulers.background import BackgroundScheduler


class ApsExecutor(Executor, ABC):
    def __init__(self, aps_background_scheduler: BackgroundScheduler):
        self.aps_background_scheduler = aps_background_scheduler

    @abstractmethod
    def get_worker_func(self, worker_id: str, worker_metadata: WorkerMetadata) -> Callable:
        pass

    def _get_job_id(self, worker_id: str):
        # prefix executor slug because different aps executors share the same aps_background_scheduler
        return f"{self.get_slug()}+{worker_id}"

    def add_worker(self, worker_id: str, worker_metadata: WorkerMetadata):
        self.aps_background_scheduler.add_job(
            self.get_worker_func(worker_id, worker_metadata),
            id=self._get_job_id(worker_id),
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )

    def get_worker_ids(self) -> List[str]:
        worker_ids = []
        job_id_prefix = f"{self.get_slug()}+"
        for job in self.aps_background_scheduler.get_jobs():
            job_id = job.id
            if job_id.startswith(job_id_prefix):
                worker_ids.append(job_id[len(job_id_prefix):])
        return worker_ids

    def remove_worker(self, worker_id: str):
        self.aps_background_scheduler.remove_job(self._get_job_id(worker_id))

    def get_worker_interval_seconds(self, worker_id: str) -> int:
        return self.aps_background_scheduler.get_job(self._get_job_id(worker_id)).trigger.interval.seconds

    def set_worker_interval_seconds(self, worker_id: str, desired_interval_seconds: int):
        self.aps_background_scheduler.reschedule_job(self._get_job_id(worker_id), 'interval', desired_interval_seconds)
