import uuid
import threading
from typing import Callable, Dict, List
from dataclasses import dataclass
from broccoli_server.content import ContentStore
from broccoli_server.interface.one_off_job import OneOffJob
from .one_off_job_context import OneOffJobContextImpl


@dataclass
class JobRun:
    job_id: str
    state: str
    drained_log_lines: List[str]

    def to_json(self):
        return {
            "job_id": self.job_id,
            "state": self.state,
            "drained_log_lines": self.drained_log_lines
        }


class OneOffJobExecutor(object):
    def __init__(self, content_store: ContentStore):
        self.content_store = content_store
        self.job_modules = {}  # type: Dict[str, Callable]
        self.job_runs = []  # type: List[JobRun]

    def register_job_module(self, module_name: str, constructor: Callable):
        self.job_modules[module_name] = constructor

    def get_job_modules(self) -> List[str]:
        return list(sorted(self.job_modules.keys()))

    def run_job(self, module_name: str, args: Dict):
        job = self.job_modules[module_name](**args)  # type: OneOffJob
        job_id = f"{module_name}.{str(uuid.uuid4())}"
        context = OneOffJobContextImpl(job_id, self.content_store)
        job_run_index = len(self.job_runs)
        self.job_runs.append(JobRun(job_id, "scheduled", []))

        def _run_job():
            self.job_runs[job_run_index].state = "started"
            job.work(context)
            self.job_runs[job_run_index].state = "completed"
            self.job_runs[job_run_index].drained_log_lines = context.drain_log_lines()

        threading.Thread(target=_run_job).start()

    def get_job_runs(self) -> List[JobRun]:
        return list(reversed(self.job_runs))
