import pymongo
from typing import Dict, Tuple
from .logging import logger
from .worker_cache import WorkerCache


class WorkerConfigStore(object):
    def __init__(self, connection_string: str, db: str, worker_cache: WorkerCache):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db['workers']
        self.worker_cache = worker_cache

    def add(self, module: str, class_name: str, args: Dict, interval_seconds: int) -> Tuple[bool, str]:
        # todo: garbage collect this w?
        status, worker_or_message = self.worker_cache.load(module, class_name, args)
        if not status:
            logger.error(f"Fails to add worker module={module} class_name={class_name} args={args}, "
                         f"message {worker_or_message}")
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
            "state": {}
        })
        return True, worker_id

    def get_all(self) -> Dict[str, Tuple[str, str, Dict, int]]:
        res = {}
        # todo: find fails?
        for document in self.collection.find():
            res[document["worker_id"]] = (
                document["module"],
                document["class_name"],
                document["args"],
                document["interval_seconds"]
            )
        return res

    def remove(self, worker_id: str) -> Tuple[bool, str]:
        existing_doc_count = self.collection.count_documents({"worker_id": worker_id})
        if existing_doc_count == 0:
            return False, f"Worker with id {worker_id} does not exist"
        # todo: delete_one fails?
        self.collection.delete_one({"worker_id": worker_id})
        return True, ""

    def update_interval_seconds(self, worker_id: str, interval_seconds: int) -> Tuple[bool, str]:
        existing_doc_count = self.collection.count_documents({"worker_id": worker_id})
        if existing_doc_count == 0:
            return False, f"Worker with id {worker_id} does not exist"
        # todo: update_one fails
        self.collection.update_one({"worker_id": worker_id}, {"$set": {"interval_seconds": interval_seconds}})
        return True, ""
