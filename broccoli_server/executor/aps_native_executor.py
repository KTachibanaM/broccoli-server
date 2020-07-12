import logging
from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory, WorkWrapper
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


class ApsNativeExecutor(ApsExecutor):
    def __init__(self, aps_background_scheduler: BackgroundScheduler, work_wrapper: WorkWrapper,
                 work_context_factory: WorkContextFactory):
        super(ApsNativeExecutor, self).__init__(aps_background_scheduler)
        self.work_wrapper = work_wrapper
        self.work_context_factory = work_context_factory

    def get_worker_func(self, worker_id: str, worker_metadata: WorkerMetadata):
        work_wrap_and_id = self.work_wrapper.wrap(worker_metadata)
        if not work_wrap_and_id:
            logger.error("Cannot wrap work", extra={
                "worker_metadata": worker_metadata
            })
            raise RuntimeError("Cannot wrap work")
        work_wrap, _ = work_wrap_and_id
        return work_wrap

    def get_slug(self):
        return "aps_native"
