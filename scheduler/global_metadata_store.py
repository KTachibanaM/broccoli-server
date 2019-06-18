import pymongo
from typing import List, Dict


class GlobalMetadataStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
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
