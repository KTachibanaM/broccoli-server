import logging
from typing import Callable, Dict, List, Tuple, Union
from broccoli_server.utils import WorkerQueue, WorkerPayload
from broccoli_server.interface.job import Job

logger = logging.getLogger(__name__)


class JobScheduler(object):
    def __init__(self, worker_queue: WorkerQueue):
        self.job_modules = {}  # type: Dict[str, Callable]
        self.worker_queue = worker_queue

    def register_job_module(self, module_name: str, constructor: Callable):
        self.job_modules[module_name] = constructor

    def get_job_modules(self) -> List[str]:
        return list(sorted(self.job_modules.keys()))

    def load_module(self, module_name: str, args: Dict) -> Tuple[bool, Union[str, Job]]:
        if module_name not in self.job_modules:
            return False, f"Module {module_name} not found"

        clazz = self.job_modules[module_name]
        final_args = {}
        for arg_name, arg_value in args.items():
            final_args[arg_name] = arg_value
        try:
            obj = clazz(**final_args)
        except Exception as e:
            return False, str(e)
        return True, obj

    def schedule_job(self, module_name: str, args: Dict):
        logger.info(f"Enqueuing job {module_name} with args {str(args)}")
        self.worker_queue.enqueue(WorkerPayload(
            type="job",
            module_name=module_name,
            args=args
        ))
