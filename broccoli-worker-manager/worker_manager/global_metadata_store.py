import pymongo
from typing import List, Dict


class GlobalMetadataStore(object):
    def __init__(self, hostname: str, port: int, db: str, username: str, password: str):
        # todo: properly close all resources
        self.client = pymongo.MongoClient(
            host=hostname,
            port=port,
            username=username,
            password=password,
            authSource=db,
            authMechanism='SCRAM-SHA-256'
        )
        self.db = self.client[db]

    def get_all(self, worker_id: str) -> List[Dict]:
        collection = self.db[worker_id]
        result = []
        for document in collection.find({}):
            result.append({
                "key": document["key"],
                "value": document["value"]
            })
        return result

    def set_all(self, worker_id: str, metadata: List[Dict]):
        collection = self.db[worker_id]
        for m in metadata:
            collection.update(
                {"key": m["key"]},
                {"$set": {
                    "value": m["value"]
                }},
                upsert=True
            )