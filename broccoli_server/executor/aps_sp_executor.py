import subprocess
import sys
import os
import json
import base64
from typing import Callable
from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata


class ApsSubprocessExecutor(ApsExecutor):
    def __init__(self, run_worker_invocation_py_path: str):
        super(ApsSubprocessExecutor, self).__init__()
        self.run_worker_invocation_py_path = run_worker_invocation_py_path

    def get_worker_func(self, worker_id: str, worker_metadata: WorkerMetadata) -> Callable:
        def sp_work_func():
            args = worker_metadata.args
            args = json.dumps(args)
            args = args.encode('utf-8')
            args = base64.b64encode(args)
            args = args.decode('utf-8')

            env = os.environ.copy()
            env['WORKER_MODULE'] = worker_metadata.module
            env['WORKER_CLASS_NAME'] = worker_metadata.class_name
            env['WORKER_ARGS_BASE64'] = args
            env['WORKER_INTERVAL_SECONDS'] = str(worker_metadata.interval_seconds)
            env['WORKER_ERROR_RESILIENCY'] = str(worker_metadata.error_resiliency)
            try:
                output = subprocess.check_output(
                    [
                        sys.executable,
                        self.run_worker_invocation_py_path,
                    ],
                    env=env,
                    stderr=subprocess.STDOUT
                )
                for line in output.decode('utf-8').split("\n"):
                    line = line.strip()
                    if line:
                        print(f"{worker_id}: {line}")
            except subprocess.CalledProcessError as e:
                print(f"{worker_id} fails to execute, error {str(e)}")

        return sp_work_func

    def get_slug(self) -> str:
        return "aps_sp"
