import logging
import uuid
from typing import Dict, Optional, Tuple, Callable
from broccoli_server.content import ContentStore
from broccoli_server.interface.job import Job
from .job_context import JobContextImpl
from .job_run import JobRun
from .job_scheduler import JobScheduler
from .job_runs_store import JobRunsStore

logger = logging.getLogger(__name__)


class JobFactory(object):
    def __init__(self, job_scheduler: JobScheduler, content_store: ContentStore, job_runs_store: JobRunsStore):
        self.job_scheduler = job_scheduler
        self.content_store = content_store
        self.job_runs_store = job_runs_store

    def get_job_func(self, module_name: str, args: Dict) -> Optional[Tuple[Callable, str]]:
        status, job_or_message = self.job_scheduler.load_module(module_name, args)
        if not status:
            logger.error("Fails to load worker", extra={
                'module_name': module_name,
                'args': args,
                'message': job_or_message
            })
            return None
        job = job_or_message  # type: Job
        job_id = f"{module_name}.{str(uuid.uuid4())}"
        context = JobContextImpl(job_id, self.content_store)
        job_run = JobRun(job_id, "scheduled", [])
        self.job_runs_store.add_job_run(job_run)

        def _run_job():
            job_run.state = "started"
            self.job_runs_store.update_job_run(job_id, job_run)

            job.work(context)

            job_run.state = "completed"
            job_run.drained_log_lines = context.drain_log_lines()
            self.job_runs_store.update_job_run(job_id, job_run)

        return _run_job, job_id
