import pymongo
from typing import Dict, Tuple
from .logging import logger
from .worker_cache import WorkerCache
from .worker import Worker


class WorkerConfigStore(object):
    def __init__(self, connection_string: str, db: str, worker_cache: WorkerCache):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db['workers']
        self.worker_cache = worker_cache

    def add(self, worker: Worker) -> Tuple[bool, str]:
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
            return False, worker_or_message
        worker_id = f"broccoli.worker.{worker_or_message.get_id()}"
        existing_doc_count = self.collection.count_documents({"worker_id": worker_id})
        if existing_doc_count != 0:
            return False, f"Worker with id {worker_id} already exists"
        # todo: insert fails?
        self.collection.insert({
            "worker_id": worker_id,
            "module": module,
            "class_name": class_name,
            "args": args,
            "interval_seconds": interval_seconds,
            'error_resiliency': error_resiliency,
            # those two fields are for runtime
            'error_count': 0,
            "state": {}
        })
        return True, worker_id

    def get_all(self) -> Dict[str, Worker]:
        res = {}
        # todo: find fails?
        for document in self.collection.find():
            res[document["worker_id"]] = Worker(
                module=document["module"],
                class_name=document["class_name"],
                args=document["args"],
                interval_seconds=document["interval_seconds"],
                error_resiliency=document.get('error_resiliency', -1)
            )
        return res

    def _if_worker_exists(self, worker_id: str) -> bool:
        return self.collection.count_documents({"worker_id": worker_id}) != 0

    def remove(self, worker_id: str) -> Tuple[bool, str]:
        if self._if_worker_exists(worker_id) == 0:
            return False, f"Worker with id {worker_id} does not exist"
        # todo: delete_one fails?
        self.collection.delete_one({"worker_id": worker_id})
        return True, ""

    def update_interval_seconds(self, worker_id: str, interval_seconds: int) -> Tuple[bool, str]:
        if self._if_worker_exists(worker_id) == 0:
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

    def increment_error_count(self, worker_id: str) -> Tuple[bool, str]:
        if self._if_worker_exists(worker_id) == 0:
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
        if self._if_worker_exists(worker_id) == 0:
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
