import logging
from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory, WorkFactory

logger = logging.getLogger(__name__)


class ApsNativeExecutor(ApsExecutor):
    def __init__(self, work_factory: WorkFactory, work_context_factory: WorkContextFactory):
        super(ApsNativeExecutor, self).__init__()
        self.work_factory = work_factory
        self.work_context_factory = work_context_factory

    def get_worker_func(self, worker_id: str, worker_metadata: WorkerMetadata):
        work_func_and_id = self.work_factory.get_work_func(worker_metadata)
        if not work_func_and_id:
            logger.error("Cannot get work function", extra={
                "worker_metadata": worker_metadata
            })
            raise RuntimeError("Cannot get work function")
        work_func, _ = work_func_and_id
        return work_func

    def get_slug(self) -> str:
        return "aps_native"
