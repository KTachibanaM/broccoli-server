import uuid
import threading
from typing import Callable, Dict, List
from broccoli_server.content import ContentStore
from broccoli_server.interface.job import Job
from .job_context import JobContextImpl
from .job_run import JobRun
from .job_runs_store import JobRunsStore


class JobScheduler(object):
    def __init__(self, content_store: ContentStore, job_runs_store: JobRunsStore):
        self.content_store = content_store
        self.job_modules = {}  # type: Dict[str, Callable]
        self.job_runs_store = job_runs_store

    def register_job_module(self, module_name: str, constructor: Callable):
        self.job_modules[module_name] = constructor

    def get_job_modules(self) -> List[str]:
        return list(sorted(self.job_modules.keys()))

    def run_job(self, module_name: str, args: Dict):
        job = self.job_modules[module_name](**args)  # type: Job
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

        threading.Thread(target=_run_job).start()
