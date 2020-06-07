from typing import Set, Dict, Callable
from .logging import logger
from apscheduler.schedulers.base import BaseScheduler
from sentry_sdk import capture_exception
from broccoli_server.worker import WorkerCache, WorkerMetadata, WorkerConfigStore, WorkContext, MetadataStoreFactory
from broccoli_server.content import ContentStore
from broccoli_server.interface.worker import Worker


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self,
                 worker_config_store: WorkerConfigStore,
                 content_store: ContentStore,
                 metadata_store_factory: MetadataStoreFactory,
                 worker_cache: WorkerCache,
                 sentry_enabled: bool,
                 pause_workers: bool
                 ):
        self.worker_config_store = worker_config_store
        self.scheduler = None
        self.content_store = content_store
        self.metadata_store_factory = metadata_store_factory
        self.worker_cache = worker_cache
        self.sentry_enabled = sentry_enabled
        self.pause_workers = pause_workers

    def set_scheduler(self, scheduler: BaseScheduler):
        self.scheduler = scheduler

    def reconcile(self):
        if not self.scheduler:
            logger.error("Scheduler is not configured!")
            return
        actual_job_ids = set(map(lambda j: j.id, self.scheduler.get_jobs())) - {self.RECONCILE_JOB_ID}  # type: Set[str]
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
            self.scheduler.remove_job(job_id=removed_job_id)

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
        module, class_name, args = worker_metadata.module, worker_metadata.class_name, worker_metadata.args
        status, worker_or_message = self.worker_cache.load(module, class_name, args)
        if not status:
            logger.error("Fails to load worker", extra={
                'module': module,
                'class_name': class_name,
                'args': args,
                'message': worker_or_message
            })
            return
        worker = worker_or_message  # type: Worker
        work_context = WorkContext(added_job_id, self.content_store, self.metadata_store_factory)
        worker.pre_work(work_context)
        work_wrap = self.wrap_work(worker, work_context, worker_metadata.error_resiliency)

        self.scheduler.add_job(
            work_wrap,
            id=added_job_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )

    def configure_jobs(self,
                       actual_job_ids: Set[str],
                       desired_job_ids: Set[str],
                       desired_jobs: Dict[str, WorkerMetadata]
                       ):
        # todo: configure job if worker.work bytecode changes..?
        same_job_ids = actual_job_ids.intersection(desired_job_ids)
        for job_id in same_job_ids:
            desired_interval_seconds = desired_jobs[job_id].interval_seconds
            actual_interval_seconds = self.scheduler.get_job(job_id).trigger.interval.seconds
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure job interval with id {job_id} to {desired_interval_seconds} seconds")
                self.scheduler.reschedule_job(
                    job_id=job_id,
                    trigger='interval',
                    seconds=desired_interval_seconds
                )

    def wrap_work(self, worker: Worker, work_context: WorkContext, error_resiliency: int) -> Callable:
        worker_id = f"broccoli.worker.{worker.get_id()}"

        def work_wrap():
            try:
                if self.pause_workers:
                    logger.info("Workers have been globally paused")
                    return

                worker.work(work_context)
                # always reset error count
                ok, err = self.worker_config_store.reset_error_count(worker_id)
                if not ok:
                    logger.error("Fails to reset error count", extra={
                        'worker_id': worker_id,
                        'reason': err
                    })
            except Exception as e:
                report_ex = True
                if error_resiliency != -1:
                    ok, error_count, err = self.worker_config_store.get_error_count(worker_id)
                    if not ok:
                        logger.error("Fails to get error count", extra={
                            'worker_id': worker_id,
                            'reason': err
                        })
                    if error_count < error_resiliency:
                        # only not to report exception when error resiliency is set and error count is below resiliency
                        report_ex = False

                if report_ex:
                    if self.sentry_enabled:
                        capture_exception(e)
                    else:
                        print(str(e))
                        logger.exception("Fails to execute work", extra={
                            'worker_id': worker_id,
                        })
                else:
                    print(str(e))
                    logger.info("Not reporting exception because of error resiliency", extra={
                        'worker_id': worker_id
                    })

                if error_resiliency != -1:
                    # only to touch error count if error resiliency is set
                    ok, err = self.worker_config_store.increment_error_count(worker_id)
                    if not ok:
                        logger.error('Fails to increment error count', extra={
                            'worker_id': worker_id,
                            'reason': err
                        })

        return work_wrap
