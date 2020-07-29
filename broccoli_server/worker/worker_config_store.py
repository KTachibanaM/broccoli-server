import pymongo
import logging
from typing import Dict, Tuple
from .worker_cache import WorkerCache
from .worker_metadata import WorkerMetadata
from broccoli_server.interface.worker import Worker

logger = logging.getLogger(__name__)


class WorkerConfigStore(object):
    def __init__(self, connection_string: str, db: str, worker_cache: WorkerCache):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db['workers']
        self.worker_cache = worker_cache
        self.worker_last_executed_seconds = {}

    def add(self, worker_metadata: WorkerMetadata) -> Tuple[bool, str]:
        module_name, args = worker_metadata.module_name, worker_metadata.args
        status, worker_or_message = self.worker_cache.load(module_name, args)
        if not status:
            logger.error("Fails to load worker", extra={
                'module_name': module_name,
                'args': args,
                'message': worker_or_message
            })
            return False, worker_or_message
        worker = worker_or_message  # type: Worker
        worker_id = worker.get_id()
        if self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} already exists"
        # todo: insert fails?
        self.collection.insert({
            "worker_id": worker_id,
            "module_name": module_name,
            "args": args,
            "interval_seconds": worker_metadata.interval_seconds,
            'error_resiliency': worker_metadata.error_resiliency,
            'executor_slug': worker_metadata.executor_slug,
            # those two fields are for runtime
            'error_count': 0,
            "state": {}
        })
        return True, worker_id

    def get_all(self) -> Dict[str, WorkerMetadata]:
        res = {}
        # todo: find fails?
        for document in self.collection.find():
            res[document["worker_id"]] = WorkerMetadata(
                module_name=document["module_name"],
                args=document["args"],
                interval_seconds=document["interval_seconds"],
                error_resiliency=document.get('error_resiliency', -1),
                executor_slug=document.get("executor_slug", "aps_native")
            )
        return res

    def get_all_by_executor_slug(self, executor_slug: str) -> Dict[str, WorkerMetadata]:
        res = {}
        for worker_id, worker_metadata in self.get_all().items():
            if worker_metadata.executor_slug == executor_slug:
                res[worker_id] = worker_metadata
        return res

    def _if_worker_exists(self, worker_id: str) -> bool:
        return self.collection.count_documents({"worker_id": worker_id}) != 0

    def remove(self, worker_id: str) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        # todo: delete_one fails?
        self.collection.delete_one({"worker_id": worker_id})
        return True, ""

    def update_interval_seconds(self, worker_id: str, interval_seconds: int) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        # todo: update_one fails
        self.collection.update_one(
            filter={
                "worker_id": worker_id
            },
            update={
                "$set": {
                    "interval_seconds": interval_seconds
                }
            }
        )
        return True, ""

    def update_error_resiliency(self, worker_id: str, error_resiliency: int) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        # todo: update_one fails
        self.collection.update_one(
            filter={
                "worker_id": worker_id
            },
            update={
                "$set": {
                    "error_resiliency": error_resiliency
                }
            }
        )
        return True, ""

    def update_executor_slug(self, worker_id: str, executor_slug: str) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        # todo: update_one fails
        self.collection.update_one(
            filter={
                "worker_id": worker_id
            },
            update={
                "$set": {
                    "executor_slug": executor_slug
                }
            }
        )
        return True, ""

    def increment_error_count(self, worker_id: str) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        self.collection.update_one(
            filter={
                "worker_id": worker_id
            },
            update={
                "$inc": {
                    "error_count": 1
                }
            }
        )
        return True, ""

    def reset_error_count(self, worker_id: str) -> Tuple[bool, str]:
        if not self._if_worker_exists(worker_id):
            return False, f"Worker with id {worker_id} does not exist"
        self.collection.update_one(
            filter={
                "worker_id": worker_id
            },
            update={
                "$set": {
                    "error_count": 0
                }
            }
        )
        return True, ""

    def get_error_count(self, worker_id: str) -> Tuple[bool, int, str]:
        document = self.collection.find_one(
            filter={
                "worker_id": worker_id
            }
        )
        if not document:
            return False, -1, f"Worker with id {worker_id} does not exist"
        return True, document.get("error_count", 0), ""

    def get_last_executed_seconds(self, worker_id: str) -> int:
        return self.worker_last_executed_seconds.get(worker_id, -1)

    def set_last_executed_seconds(self, worker_id: str, last_executed_seconds: int):
        self.worker_last_executed_seconds[worker_id] = last_executed_seconds
