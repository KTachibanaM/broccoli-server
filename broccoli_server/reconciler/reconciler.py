import logging
from typing import Set, Dict
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from broccoli_server.worker import WorkerMetadata, WorkerConfigStore
from broccoli_server.utils import WorkerQueue, WorkerPayload

logger = logging.getLogger(__name__)


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self, worker_config_store: WorkerConfigStore, worker_queue: WorkerQueue, pause_workers: bool):
        self.worker_config_store = worker_config_store
        self.worker_queue = worker_queue
        self.pause_workers = pause_workers
        self.reconcile_scheduler = BlockingScheduler()
        self.reconcile_scheduler.add_job(
            self.reconcile,
            id=self.RECONCILE_JOB_ID,
            trigger='interval',
            seconds=10
        )
        self.trigger_scheduler = BackgroundScheduler()

    def start(self):
        # Less verbose logging from apscheduler
        logging.getLogger("apscheduler").setLevel(logging.ERROR)
        # start trigger scheduler before reconcile scheduler otherwise triggers might not be actually added
        self.trigger_scheduler.start()
        self.reconcile_scheduler.start()

    def stop(self):
        self.trigger_scheduler.shutdown(wait=False)
        self.reconcile_scheduler.shutdown(wait=False)

    def reconcile(self):
        if self.pause_workers:
            logger.info("Workers have been globally paused")
            return
        actual_worker_ids = set(map(lambda j: j.id, self.trigger_scheduler.get_jobs()))  # type: Set[str]
        desired_workers = self.worker_config_store.get_all()
        desired_worker_ids = set(desired_workers.keys())  # type: Set[str]

        self.remove_workers(actual_worker_ids=actual_worker_ids, desired_worker_ids=desired_worker_ids)
        self.add_workers(actual_worker_ids=actual_worker_ids, desired_worker_ids=desired_worker_ids,
                         desired_workers=desired_workers)
        self.configure_workers(actual_worker_ids=actual_worker_ids, desired_worker_ids=desired_worker_ids,
                               desired_workers=desired_workers)

    def remove_workers(self, actual_worker_ids: Set[str], desired_worker_ids: Set[str]):
        removed_worker_ids = actual_worker_ids - desired_worker_ids
        if not removed_worker_ids:
            logger.debug(f"No worker to remove")
            return
        logger.info(f"Going to remove workers with id {removed_worker_ids}")
        for removed_worker_id in removed_worker_ids:
            self.trigger_scheduler.remove_job(removed_worker_id)

    def add_workers(self, actual_worker_ids: Set[str], desired_worker_ids: Set[str],
                    desired_workers: Dict[str, WorkerMetadata]):
        added_worker_ids = desired_worker_ids - actual_worker_ids
        if not added_worker_ids:
            logger.debug(f"No workers to add")
            return
        logger.info(f"Going to add workers with id {added_worker_ids}")
        for added_worker_id in added_worker_ids:
            self.add_worker(added_worker_id, desired_workers)

    def add_worker(self, added_worker_id: str, desired_workers: Dict[str, WorkerMetadata]):
        worker_metadata = desired_workers[added_worker_id]

        def _trigger():
            logger.info(f"Enqueuing worker {added_worker_id}")
            self.worker_queue.enqueue(WorkerPayload(
                type="worker",
                module_name=worker_metadata.module_name,
                args=worker_metadata.args
            ))

        self.trigger_scheduler.add_job(
            _trigger,
            id=added_worker_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )

    def configure_workers(self, actual_worker_ids: Set[str], desired_worker_ids: Set[str],
                          desired_workers: Dict[str, WorkerMetadata]):
        same_worker_ids = actual_worker_ids.intersection(desired_worker_ids)
        for worker_id in same_worker_ids:
            desired_interval_seconds = desired_workers[worker_id].interval_seconds
            actual_interval_seconds = self.trigger_scheduler.get_job(worker_id).trigger.interval.seconds
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure worker interval with id {worker_id} to {desired_interval_seconds} "
                            f"seconds")
                self.trigger_scheduler.reschedule_job(
                    job_id=worker_id,
                    trigger='interval',
                    seconds=desired_interval_seconds
                )
