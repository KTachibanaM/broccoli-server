import logging
from typing import Set, Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from broccoli_server.worker import WorkerMetadata, WorkerConfigStore
from broccoli_server.executor import Executor

logger = logging.getLogger(__name__)


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self, worker_config_store: WorkerConfigStore,
                 executors: List[Executor]):
        self.worker_config_store = worker_config_store
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
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

        # starting executors before master scheduler otherwise workers might not be actually added
        for e in self.executors:
            e.start()
        self.scheduler.start()

    def stop(self):
        for e in self.executors:
            e.stop()
        self.scheduler.shutdown(wait=False)

    def reconcile(self):
        for e in self.executors:
            self.reconcile_by_executor(e)

    def reconcile_by_executor(self, executor: Executor):
        actual_worker_ids = set(executor.get_worker_ids()) - {self.RECONCILE_JOB_ID}  # type: Set[str]
        desired_workers = self.worker_config_store.get_all_by_executor_slug(executor.get_slug())
        desired_worker_ids = set(desired_workers.keys())  # type: Set[str]

        Reconciler.remove_workers(executor, actual_worker_ids=actual_worker_ids, desired_worker_ids=desired_worker_ids)
        Reconciler.add_workers(executor, actual_worker_ids=actual_worker_ids, desired_worker_ids=desired_worker_ids,
                               desired_workers=desired_workers)
        Reconciler.configure_workers(executor, actual_worker_ids=actual_worker_ids,
                                     desired_worker_ids=desired_worker_ids, desired_workers=desired_workers)

    @staticmethod
    def remove_workers(executor: Executor, actual_worker_ids: Set[str], desired_worker_ids: Set[str]):
        removed_worker_ids = actual_worker_ids - desired_worker_ids
        if not removed_worker_ids:
            logger.debug(f"No worker to remove")
            return
        logger.info(f"Going to remove workers with id {removed_worker_ids} in executor {executor.get_slug()}")
        for removed_worker_id in removed_worker_ids:
            executor.remove_worker(removed_worker_id)

    @staticmethod
    def add_workers(executor: Executor, actual_worker_ids: Set[str], desired_worker_ids: Set[str],
                    desired_workers: Dict[str, WorkerMetadata]):
        added_worker_ids = desired_worker_ids - actual_worker_ids
        if not added_worker_ids:
            logger.debug(f"No workers to add")
            return
        logger.info(f"Going to add workers with id {added_worker_ids} in executor {executor.get_slug()}")
        for added_worker_id in added_worker_ids:
            Reconciler.add_worker(executor, added_worker_id, desired_workers)

    @staticmethod
    def add_worker(executor: Executor, added_worker_id: str, desired_workers: Dict[str, WorkerMetadata]):
        worker_metadata = desired_workers[added_worker_id]
        executor.add_worker(added_worker_id, worker_metadata)

    @staticmethod
    def configure_workers(executor: Executor, actual_worker_ids: Set[str], desired_worker_ids: Set[str],
                          desired_workers: Dict[str, WorkerMetadata]):
        # todo: configure worker if worker bytecode changes..?
        same_worker_ids = actual_worker_ids.intersection(desired_worker_ids)
        for worker_id in same_worker_ids:
            desired_interval_seconds = desired_workers[worker_id].interval_seconds
            actual_interval_seconds = executor.get_worker_interval_seconds(worker_id)
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure worker interval with id {worker_id} to {desired_interval_seconds} "
                            f"seconds in executor {executor.get_slug()}")
                executor.set_worker_interval_seconds(worker_id, desired_interval_seconds)
