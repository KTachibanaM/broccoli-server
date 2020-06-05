import pymongo
from typing import Dict


class GlobalMetadataStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.workers_collection = self.db["workers"]

    def get_all(self, worker_id: str) -> Dict:
        worker = self.workers_collection.find_one({"worker_id": worker_id})
        if "state" not in worker:
            return {}
        return worker['state']

    def set_all(self, worker_id: str, metadata: Dict):
        self.workers_collection.update_one(
            {"worker_id": worker_id},
            {"$set": {"state": metadata}},
            upsert=False
        )
