import logging
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from .executor import Executor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory, WorkWrapper

logger = logging.getLogger(__name__)


class ApsReducedExecutor(Executor):
    MAX_JOBS = 24

    def __init__(self, work_wrapper: WorkWrapper, work_context_factory: WorkContextFactory):
        self.scheduler = BackgroundScheduler()
        self.work_wrapper = work_wrapper
        self.work_context_factory = work_context_factory

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def add_worker(self, worker_id: str, worker_metadata: WorkerMetadata):
        pass

    def get_worker_ids(self) -> List[str]:
        pass

    def remove_worker(self, worker_id: str):
        pass

    def get_worker_interval_seconds(self, worker_id: str) -> int:
        pass

    def set_worker_interval_seconds(self, worker_id: str, desired_interval_seconds: int):
        pass

    def get_slug(self) -> str:
        return "aps_reduced"
