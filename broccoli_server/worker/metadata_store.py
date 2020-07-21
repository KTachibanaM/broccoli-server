import pymongo
from broccoli_server.interface.worker import MetadataStore


class MetadataStoreImpl(MetadataStore):
    def __init__(self, connection_string: str, db: str, worker_id: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.workers_collection = self.db["workers"]
        self.worker_id = worker_id

    def _get_worker_state(self):
        return self.workers_collection.find_one({"worker_id": self.worker_id})["state"]

    def _get_another_worker_state(self, worker_id: str):
        return self.workers_collection.find_one({"worker_id": worker_id})["state"]

    def exists(self, key: str) -> bool:
        return key in self._get_worker_state()

    def get(self, key: str):
        return self._get_worker_state()[key]

    def set(self, key: str, value):
        state = self._get_worker_state()
        state[key] = value
        self.workers_collection.update_one(
            {"worker_id": self.worker_id},
            {"$set": {"state": state}},
            upsert=False
        )

    def get_from_another_worker(self, worker_id: str, key: str):
        return self._get_another_worker_state(worker_id)[key]

    def exists_in_another_worker(self, worker_id: str, key: str):
        return key in self._get_another_worker_state(worker_id)


class MetadataStoreFactory(object):
    def __init__(self, connection_string: str, db: str):
        self.connection_string = connection_string
        self.db = db

    def build(self, worker_id: str) -> MetadataStore:
        return MetadataStoreImpl(
            connection_string=self.connection_string,
            db=self.db,
            worker_id=worker_id
        )
