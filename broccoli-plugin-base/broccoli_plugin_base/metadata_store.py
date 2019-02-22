import pymongo


class MetadataStore(object):
    def __init__(self, hostname: str, port: int, db: str, collection_name: str):
        # todo: properly close all resources
        self.client = pymongo.MongoClient(hostname, port)
        self.db = self.client[db]
        self.collection = self.db[collection_name]

    def exists(self, key: str) -> bool:
        count = self.collection.count_documents({'key': key})
        return count != 0

    def get(self, key: str):
        doc = self.collection.find_one({'key': key})
        return doc['value']

    def set(self, key: str, value):
        self.collection.update_one({'key': key}, {'$set': {'value': value}}, upsert=True)

    def get_from_another_worker(self, worker_id: str, key: str):
        collection = self.db[worker_id]
        doc = collection.find_one({'key': key})
        return doc['value']

    def exists_in_another_worker(self, worker_id: str, key: str):
        collection = self.db[worker_id]
        count = collection.count_documents({'key': key})
        return count != 0
