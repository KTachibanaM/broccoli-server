import subprocess
import sys
import os
import json
import base64
from .aps_executor import ApsExecutor
from broccoli_server.worker import WorkerMetadata
from apscheduler.schedulers.background import BackgroundScheduler


class ApsSubprocessExecutor(ApsExecutor):
    def __init__(self, scheduler: BackgroundScheduler, worker_invocation_py_path: str):
        super(ApsSubprocessExecutor, self).__init__(scheduler)
        self.worker_invocation_py_path = worker_invocation_py_path

    def add_job(self, job_id: str, worker_metadata: WorkerMetadata):
        def sp_work_wrap():
            env = os.environ.copy()
            env['WORKER_MODULE'] = worker_metadata.module
            env['WORKER_CLASS_NAME'] = worker_metadata.class_name
            env['WORKER_ARGS_BASE64'] = base64.b64encode(json.dumps(worker_metadata.args))
            env['WORKER_INTERVAL_SECONDS'] = str(worker_metadata.interval_seconds)
            env['WORKER_ERROR_RESILIENCY'] = str(worker_metadata.error_resiliency)
            try:
                output = subprocess.check_output(
                    [
                        sys.executable,
                        self.worker_invocation_py_path,
                    ],
                    env=env,
                    stderr=subprocess.STDOUT
                )
                for line in str(output).split("\n"):
                    print(f"{job_id}: {line}")
            except subprocess.CalledProcessError as e:
                print(f"{job_id} fails to execute, error {str(e)}")

        self.scheduler.add_job(
            sp_work_wrap,
            id=job_id,
            trigger='interval',
            seconds=worker_metadata.interval_seconds
        )
