from typing import List, Callable
from .executor import Executor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory
from apscheduler.schedulers.background import BackgroundScheduler


class ApsNativeExecutor(Executor):
    def __init__(self,
                 scheduler: BackgroundScheduler,
                 wrap_work_func: Callable,
                 work_context_factory: WorkContextFactory
                 ):
        self.scheduler = scheduler
        self.wrap_work_func = wrap_work_func
        self.work_context_factory = work_context_factory

    def add_job(self, job_id: str, worker_metadata: WorkerMetadata):
        work_wrap = self.wrap_work_func(worker_metadata, self.work_context_factory)

        self.scheduler.add_job(
            work_wrap,
            id=job_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )

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
