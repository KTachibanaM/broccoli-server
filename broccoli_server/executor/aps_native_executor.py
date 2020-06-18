from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory, WorkWrapper
from apscheduler.schedulers.background import BackgroundScheduler


class ApsNativeExecutor(ApsExecutor):
    def __init__(self,
                 scheduler: BackgroundScheduler,
                 work_wrapper: WorkWrapper,
                 work_context_factory: WorkContextFactory
                 ):
        super(ApsNativeExecutor, self).__init__(scheduler)
        self.work_wrapper = work_wrapper
        self.work_context_factory = work_context_factory

    def add_job(self, job_id: str, worker_metadata: WorkerMetadata):
        work_wrap_and_id = self.work_wrapper.wrap(worker_metadata)
        if not work_wrap_and_id:
            # TODO: log
            return

        work_wrap, _ = work_wrap_and_id
        self.scheduler.add_job(
            work_wrap,
            id=job_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )
