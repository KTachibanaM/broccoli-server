import pymongo
from typing import List, Dict


class GlobalMetadataStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.workers_collection = self.db["workers"]

    def get_all(self, worker_id: str) -> List[Dict]:
        worker = self.workers_collection.find_one({"worker_id": worker_id})
        if "state" not in worker:
            return []
        result = []
        for key, value in worker["state"].items():
            result.append({
                "key": key,
                "value": value
            })
        return result

    def set_all(self, worker_id: str, metadata: List[Dict]):
        self.workers_collection.update_one(
            {"worker_id": worker_id},
            {"$set": {"state": metadata}},
            upsert=False
        )
