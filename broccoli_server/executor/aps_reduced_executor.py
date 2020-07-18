import logging
import time
from typing import List, Callable, Tuple, Optional
from dataclasses import dataclass
from apscheduler.schedulers.background import BackgroundScheduler
from .executor import Executor
from broccoli_server.worker import WorkerMetadata, WorkContextFactory, WorkFactory
from broccoli_server.utils import gcd_multiple

logger = logging.getLogger(__name__)


@dataclass
class _Worker:
    worker_id: str
    worker_metadata: WorkerMetadata
    work_func: Callable
    last_executed_seconds: int


class ApsReducedExecutor(Executor):
    def __init__(self, work_factory: WorkFactory, work_context_factory: WorkContextFactory, max_jobs: int):
        self.scheduler = BackgroundScheduler()
        self.work_factory = work_factory
        self.work_context_factory = work_context_factory
        self.max_jobs = max_jobs
        self.job_index_to_workers = []  # type: List[List[_Worker]]

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def add_worker(self, worker_id: str, worker_metadata: WorkerMetadata):
        work_func_and_id = self.work_factory.get_work_func(worker_metadata)
        if not work_func_and_id:
            logger.error("Cannot get work function", extra={
                "worker_metadata": worker_metadata
            })
            raise RuntimeError("Cannot get work function")
        work_func, _ = work_func_and_id

        if len(self.job_index_to_workers) < self.max_jobs:
            job_id = len(self.job_index_to_workers)
            interval_seconds = worker_metadata.interval_seconds
            self.job_index_to_workers.append([_Worker(worker_id, worker_metadata, work_func, 0)])
            self.scheduler.add_job(
                self._get_job_func(job_id),
                id=str(job_id),
                trigger='interval',
                seconds=interval_seconds
            )
            logger.info(f"Added internal job id {job_id}")
        else:
            attaching_job_id = 0
            for i, workers in enumerate(self.job_index_to_workers):
                if len(workers) < len(self.job_index_to_workers[attaching_job_id]):
                    attaching_job_id = i

            new_interval_seconds = gcd_multiple(
                list(map(lambda w: w.worker_metadata.interval_seconds, self.job_index_to_workers[attaching_job_id]))
                + [worker_metadata.interval_seconds]
            )
            self.job_index_to_workers[attaching_job_id].append(_Worker(worker_id, worker_metadata, work_func, 0))
            self.scheduler.reschedule_job(
                job_id=str(attaching_job_id),
                trigger='interval',
                seconds=new_interval_seconds
            )
            logger.info(f"Reconfigured internal job id {attaching_job_id} "
                        f"with new interval seconds {new_interval_seconds}")

    def _get_job_func(self, job_id: int) -> Callable:
        def _f():
            now_seconds = int(time.time())
            for i, worker in enumerate(self.job_index_to_workers[job_id]):
                if now_seconds - worker.last_executed_seconds > worker.worker_metadata.interval_seconds - 1:
                    worker.work_func()
                    self.job_index_to_workers[job_id][i].last_executed_seconds = now_seconds

        return _f

    def get_worker_ids(self) -> List[str]:
        worker_ids = []
        for workers in self.job_index_to_workers:
            for worker in workers:
                worker_ids.append(worker.worker_id)
        return worker_ids

    def _get_worker_pointer(self, worker_id: str) -> Optional[Tuple[int, int]]:
        for i, workers in enumerate(self.job_index_to_workers):
            for j, worker in enumerate(workers):
                if worker.worker_id == worker_id:
                    return i, j
        return None

    def remove_worker(self, worker_id: str):
        pointer = self._get_worker_pointer(worker_id)
        if not pointer:
            logger.warning(f"Cannot find worker with id {worker_id}")
            return
        job_id, i = pointer
        del self.job_index_to_workers[job_id][i]

    def get_worker_interval_seconds(self, worker_id: str) -> int:
        pointer = self._get_worker_pointer(worker_id)
        if not pointer:
            logger.warning(f"Cannot find worker with id {worker_id}")
            return -1
        job_id, i = pointer
        return self.job_index_to_workers[job_id][i].worker_metadata.interval_seconds

    def set_worker_interval_seconds(self, worker_id: str, desired_interval_seconds: int):
        pointer = self._get_worker_pointer(worker_id)
        if not pointer:
            logger.warning(f"Cannot find worker with id {worker_id}")
            return
        job_id, i = pointer
        self.job_index_to_workers[job_id][i].worker_metadata.interval_seconds = desired_interval_seconds
        new_interval_seconds = gcd_multiple(
            list(map(lambda w: w.worker_metadata.interval_seconds, self.job_index_to_workers[job_id]))
            + [desired_interval_seconds]
        )
        self.scheduler.reschedule_job(job_id=worker_id, trigger='interval', seconds=new_interval_seconds)

    def get_slug(self) -> str:
        return "aps_reduced"
