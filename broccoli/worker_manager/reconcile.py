from typing import Set, Dict
from apscheduler.schedulers.blocking import BlockingScheduler
from worker_manager.config_store import ConfigStore
from worker_manager.load_object import load_object
from worker_manager.logger import logger


RECONCILE_JOB_ID = "broccoli.worker_reconcile"


def reconcile(configs_store: ConfigStore, scheduler: BlockingScheduler, worker_globals: Dict):
    actual_job_ids = set(map(lambda j: j.id, scheduler.get_jobs())) - {RECONCILE_JOB_ID}  # type: Set[str]
    desired_jobs = configs_store.get_all()
    desired_job_ids = desired_jobs.keys()  # type: Set[str]

    remove_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids, scheduler=scheduler)
    add_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids, desired_jobs=desired_jobs,
             worker_globals=worker_globals, scheduler=scheduler)
    configure_jobs(actual_job_ids=actual_job_ids, desired_job_ids=desired_job_ids, desired_jobs=desired_jobs,
                   scheduler=scheduler)


def remove_jobs(actual_job_ids: Set[str], desired_job_ids: Set[str], scheduler: BlockingScheduler):
    removed_job_ids = actual_job_ids - desired_job_ids
    if not removed_job_ids:
        logger.debug(f"No job to remove")
        return
    logger.info(f"Going to remove jobs with id {removed_job_ids}")
    for removed_job_id in removed_job_ids:
        scheduler.remove_job(job_id=removed_job_id)


def add_jobs(actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs, worker_globals,
             scheduler: BlockingScheduler):
    added_job_ids = desired_job_ids - actual_job_ids
    if not added_job_ids:
        logger.debug(f"No job to add")
        return
    logger.info(f"Going to add jobs with id {added_job_ids}")
    for added_job_id in added_job_ids:
        module, class_name, args, global_args, interval_seconds = desired_jobs[added_job_id]
        status, worker_or_message = load_object(module, class_name, args, global_args, worker_globals)
        if not status:
            logger.error(f"Fails to add worker module={module} class_name={class_name} args={args} "
                         f"global_args={global_args}, message {worker_or_message}")
            continue
        worker_or_message.pre_work_wrap()
        scheduler.add_job(
            worker_or_message.work_wrap,
            id=added_job_id,
            trigger='interval',
            seconds=interval_seconds
        )


def configure_jobs(actual_job_ids: Set[str], desired_job_ids: Set[str], desired_jobs, scheduler: BlockingScheduler):
    # todo: configure job if worker.work bytecode changes..?
    same_job_ids = actual_job_ids.intersection(desired_job_ids)
    for job_id in same_job_ids:
        _1, _2, _3, _4, desired_interval_seconds = desired_jobs[job_id]
        actual_interval_seconds = scheduler.get_job(job_id).trigger.interval.seconds
        if desired_interval_seconds != actual_interval_seconds:
            logger.info(f"Going to reconfigure job interval with id {job_id} to {desired_interval_seconds} seconds")
            scheduler.reschedule_job(
                job_id=job_id,
                trigger='interval',
                seconds=desired_interval_seconds
            )
