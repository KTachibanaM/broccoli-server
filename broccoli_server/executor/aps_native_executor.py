from typing import Callable
from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory
from apscheduler.schedulers.background import BackgroundScheduler


class ApsNativeExecutor(ApsExecutor):
    def __init__(self,
                 scheduler: BackgroundScheduler,
                 wrap_work_func: Callable,
                 work_context_factory: WorkContextFactory
                 ):
        super(ApsNativeExecutor, self).__init__(scheduler)
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
