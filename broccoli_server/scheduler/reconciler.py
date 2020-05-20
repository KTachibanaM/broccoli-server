import traceback
from typing import Set, Dict
from apscheduler.schedulers.base import BaseScheduler
from sentry_sdk import capture_exception
from .worker_config_store import WorkerConfigStore
from .logging import logger
from .worker_context.work_context_impl import WorkContextImpl
from .worker_cache import WorkerCache
from .worker import Worker
from broccoli_server.interface.rpc import RpcClient


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

    def add_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs: Dict[str, Worker]):
        added_job_ids = desired_job_ids - actual_job_ids
        if not added_job_ids:
            logger.debug(f"No job to add")
            return
        logger.info(f"Going to add jobs with id {added_job_ids}")
        for added_job_id in added_job_ids:
            self.add_job(added_job_id, desired_jobs)

    def add_job(self, added_job_id: str, desired_jobs: Dict[str, Worker]):
        worker = desired_jobs[added_job_id]
        module, class_name, args, interval_seconds, error_resiliency \
            = worker.module, worker.class_name, worker.args, worker.interval_seconds, worker.error_resiliency
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
                # always reset error count
                ok, err = self.worker_config_store.reset_error_count(added_job_id)
                if not ok:
                    logger.error("Fails to reset error count", extra={
                        'worker_id': added_job_id,
                        'reason': err
                    })
            except Exception as e:
                report_ex = True
                if error_resiliency != -1:
                    ok, error_count, err = self.worker_config_store.get_error_count(added_job_id)
                    if not ok:
                        logger.error("Fails to get error count", extra={
                            'worker_id': added_job_id,
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
                            'worker_id': added_job_id,
                        })
                else:
                    print(str(e))
                    logger.info("Not reporting exception because of error resiliency", extra={
                        'worker_id': added_job_id
                    })

                if error_resiliency != -1:
                    # only to touch error count if error resiliency is set
                    ok, err = self.worker_config_store.increment_error_count(added_job_id)
                    if not ok:
                        logger.error('Fails to increment error count', extra={
                            'worker_id': added_job_id,
                            'reason': err
                        })

        self.scheduler.add_job(
            work_wrap,
            id=added_job_id,
            trigger='interval',
            seconds=interval_seconds
        )

    def configure_jobs(self, actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs: Dict[str, Worker]):
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
