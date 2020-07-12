import logging
from typing import Set, Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from broccoli_server.worker import WorkerMetadata, WorkerConfigStore
from broccoli_server.executor import Executor

logger = logging.getLogger(__name__)


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self, worker_config_store: WorkerConfigStore, executors: List[Executor]):
        self.worker_config_store = worker_config_store
        self.root_scheduler = BackgroundScheduler()
        self.root_scheduler.add_job(
            self.reconcile,
            id=self.RECONCILE_JOB_ID,
            trigger='interval',
            seconds=10
        )
        self.executors = executors  # type: List[Executor]

    def start(self):
        # Less verbose logging from apscheduler
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.ERROR)

        self.root_scheduler.start()

    def stop(self):
        self.root_scheduler.shutdown(wait=False)

    def reconcile(self):
        for e in self.executors:
            self.reconcile_by_executor(e)

    def reconcile_by_executor(self, executor: Executor):
        actual_job_ids = set(executor.get_job_ids()) - {self.RECONCILE_JOB_ID}  # type: Set[str]
        desired_jobs = self.worker_config_store.get_all_by_executor_slug(executor.get_slug())
        desired_job_ids = set(desired_jobs.keys())  # type: Set[str]

        Reconciler.remove_jobs(executor, actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids)
        Reconciler.add_jobs(executor, actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids,
                            desired_jobs=desired_jobs)
        Reconciler.configure_jobs(executor, actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids,
                                  desired_jobs=desired_jobs)

    @staticmethod
    def remove_jobs(executor: Executor, actual_job_ids: Set[str], desired_job_ids: Set[str]):
        removed_job_ids = actual_job_ids - desired_job_ids
        if not removed_job_ids:
            logger.debug(f"No job to remove")
            return
        logger.info(f"Going to remove jobs with id {removed_job_ids} in executor {executor.get_slug()}")
        for removed_job_id in removed_job_ids:
            executor.remove_job(removed_job_id)

    @staticmethod
    def add_jobs(executor: Executor, actual_job_ids: Set[str], desired_job_ids: Set[str],
                 desired_jobs: Dict[str, WorkerMetadata]):
        added_job_ids = desired_job_ids - actual_job_ids
        if not added_job_ids:
            logger.debug(f"No job to add")
            return
        logger.info(f"Going to add jobs with id {added_job_ids} in executor {executor.get_slug()}")
        for added_job_id in added_job_ids:
            Reconciler.add_job(executor, added_job_id, desired_jobs)

    @staticmethod
    def add_job(executor: Executor, added_job_id: str, desired_jobs: Dict[str, WorkerMetadata]):
        worker_metadata = desired_jobs[added_job_id]
        executor.add_job(added_job_id, worker_metadata)

    @staticmethod
    def configure_jobs(executor: Executor, actual_job_ids: Set[str], desired_job_ids: Set[str],
                       desired_jobs: Dict[str, WorkerMetadata]):
        # todo: configure job if worker.work bytecode changes..?
        same_job_ids = actual_job_ids.intersection(desired_job_ids)
        for job_id in same_job_ids:
            desired_interval_seconds = desired_jobs[job_id].interval_seconds
            actual_interval_seconds = executor.get_job_interval_seconds(job_id)
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure job interval with id {job_id} to {desired_interval_seconds} seconds "
                            f"in executor {executor.get_slug()}")
                executor.set_job_interval_seconds(job_id, desired_interval_seconds)
