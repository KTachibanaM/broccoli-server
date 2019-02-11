import datetime
import pymongo
from typing import Dict, List, Tuple, Optional
from common.datetime_utils import milliseconds_to_datetime, datetime_to_milliseconds


class EventsStore(object):
    def __init__(self, hostname: str, port: int, db: str):
        # todo: properly close all resources
        self.client = pymongo.MongoClient(hostname, port)
        self.db = self.client[db]
        self.collection = self.db['broccoli.worker_events']
        # todo: configure expireAfterSeconds. 432000 is 5 days
        self.collection.create_index([("timestamp", pymongo.DESCENDING)], expireAfterSeconds=432000)

    def add_event(self, worker_id: str, state: str, metadata: Dict):
        self.collection.insert_one({
            "worker_id": worker_id,
            "timestamp": datetime.datetime.utcnow(),
            "state": state,
            "metadata": metadata
        })

    def get_events_by_timestamp_descending(
        self,
        worker_id: str,
        from_milliseconds: Optional[int],
        to_milliseconds: Optional[int],
        limit: Optional[int]
    ) -> List[Tuple[int, str, Dict]]:
        if not from_milliseconds and not to_milliseconds:
            documents = self.collection.find({"worker_id": worker_id})
        else:
            timestamp_q = {}
            if from_milliseconds:
                timestamp_q["$gte"] = milliseconds_to_datetime(from_milliseconds)
            if to_milliseconds:
                timestamp_q["$lte"] = milliseconds_to_datetime(to_milliseconds)
            documents = self.collection.find(
                {
                    "worker_id": worker_id,
                    "timestamp": timestamp_q
                }
            )
        if limit:
            documents = documents.limit(limit)
        documents = documents.sort("timestamp", pymongo.DESCENDING)
        events = []
        for document in documents:
            events.append((
                datetime_to_milliseconds(document["timestamp"]),
                document["state"],
                document["metadata"]
            ))
        return events
