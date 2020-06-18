import logging
from typing import Set, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from broccoli_server.worker import WorkerMetadata, WorkerConfigStore
from broccoli_server.executor import Executor

logger = logging.getLogger(__name__)


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self,
                 worker_config_store: WorkerConfigStore,
                 root_scheduler: BackgroundScheduler,
                 executor: Executor
                 ):
        self.worker_config_store = worker_config_store
        self.root_scheduler = root_scheduler
        self.root_scheduler.add_job(
            self.reconcile,
            id=self.RECONCILE_JOB_ID,
            trigger='interval',
            seconds=10
        )
        self.executor = executor

    def start(self):
        # Less verbose logging from apscheduler
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.ERROR)

        self.root_scheduler.start()

    def stop(self):
        self.root_scheduler.shutdown(wait=False)

    def reconcile(self):
        actual_job_ids = set(self.executor.get_job_ids()) - {self.RECONCILE_JOB_ID}  # type: Set[str]
        desired_jobs = self.worker_config_store.get_all()
        desired_job_ids = set(desired_jobs.keys())  # type: Set[str]

        self.remove_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids)
        self.add_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids, desired_jobs=desired_jobs)
        self.configure_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids, desired_jobs=desired_jobs)

    def remove_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str]):
        removed_job_ids = actual_job_ids - desired_job_ids
        if not removed_job_ids:
            logger.debug(f"No job to remove")
            return
        logger.info(f"Going to remove jobs with id {removed_job_ids}")
        for removed_job_id in removed_job_ids:
            self.executor.remove_job(removed_job_id)

    def add_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs: Dict[str, WorkerMetadata]):
        added_job_ids = desired_job_ids - actual_job_ids
        if not added_job_ids:
            logger.debug(f"No job to add")
            return
        logger.info(f"Going to add jobs with id {added_job_ids}")
        for added_job_id in added_job_ids:
            self.add_job(added_job_id, desired_jobs)

    def add_job(self, added_job_id: str, desired_jobs: Dict[str, WorkerMetadata]):
        worker_metadata = desired_jobs[added_job_id]

        self.executor.add_job(added_job_id, worker_metadata)

    def configure_jobs(self,
                       actual_job_ids: Set[str],
                       desired_job_ids: Set[str],
                       desired_jobs: Dict[str, WorkerMetadata]
                       ):
        # todo: configure job if worker.work bytecode changes..?
        same_job_ids = actual_job_ids.intersection(desired_job_ids)
        for job_id in same_job_ids:
            desired_interval_seconds = desired_jobs[job_id].interval_seconds
            actual_interval_seconds = self.executor.get_job_interval_seconds(job_id)
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure job interval with id {job_id} to {desired_interval_seconds} seconds")
                self.executor.set_job_interval_seconds(job_id, desired_interval_seconds)
