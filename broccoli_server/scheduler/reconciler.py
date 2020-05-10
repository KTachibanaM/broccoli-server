import traceback
from typing import Set
from apscheduler.schedulers.base import BaseScheduler
from sentry_sdk import capture_exception
from .worker_config_store import WorkerConfigStore
from .logging import logger
from .worker_context.work_context_impl import WorkContextImpl
from .worker_cache import WorkerCache
from broccoli_interface.rpc import RpcClient


class Reconciler(object):
    RECONCILE_JOB_ID = "broccoli.worker_reconcile"

    def __init__(self,
                 worker_config_store: WorkerConfigStore,
                 rpc_client: RpcClient,
                 worker_cache: WorkerCache,
                 sentry_enabled: bool
                 ):
        self.worker_config_store = worker_config_store
        self.scheduler = None
        self.rpc_client = rpc_client
        self.worker_cache = worker_cache
        self.sentry_enabled = sentry_enabled

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

    def add_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs):
        added_job_ids = desired_job_ids - actual_job_ids
        if not added_job_ids:
            logger.debug(f"No job to add")
            return
        logger.info(f"Going to add jobs with id {added_job_ids}")
        for added_job_id in added_job_ids:
            self.add_job(added_job_id, desired_jobs)

    def add_job(self, added_job_id: str, desired_jobs):
        module, class_name, args, interval_seconds = desired_jobs[added_job_id]
        status, worker_or_message = self.worker_cache.load(module, class_name, args)
        if not status:
            logger.error("Fails to add worker", extra={
                'module': module,
                'class_name': class_name,
                'args': args,
                'message': worker_or_message
            })
            return
        work_context = WorkContextImpl(added_job_id, self.rpc_client)
        worker_or_message.pre_work(work_context)

        def work_wrap():
            try:
                worker_or_message.work(work_context)
            except Exception as e:
                traceback.print_exc()
                if self.sentry_enabled:
                    capture_exception(e)
                logger.error("Fails to execute work", extra={
                    'job_id': added_job_id,
                    'message': e
                })

        self.scheduler.add_job(
            work_wrap,
            id=added_job_id,
            trigger='interval',
            seconds=interval_seconds
        )

    def configure_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs):
        # todo: configure job if worker.work bytecode changes..?
        same_job_ids = actual_job_ids.intersection(desired_job_ids)
        for job_id in same_job_ids:
            _1, _2, _3, desired_interval_seconds = desired_jobs[job_id]
            actual_interval_seconds = self.scheduler.get_job(job_id).trigger.interval.seconds
            if desired_interval_seconds != actual_interval_seconds:
                logger.info(f"Going to reconfigure job interval with id {job_id} to {desired_interval_seconds} seconds")
                self.scheduler.reschedule_job(
                    job_id=job_id,
                    trigger='interval',
                    seconds=desired_interval_seconds
                )
