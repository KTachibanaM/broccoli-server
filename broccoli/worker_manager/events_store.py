import datetime
import pytz
import pymongo
from typing import Dict, List, Tuple, Optional

# todo: abstract it out
# todo: properly close all resources
client = pymongo.MongoClient('localhost', 27017)
db = client['broccoli']
collection = db['broccoli.worker_events']
# todo: configure expireAfterSeconds. 432000 is 5 days
collection.create_index([("timestamp", pymongo.DESCENDING)], expireAfterSeconds=432000)


def add_event(worker_id: str, state: str, metadata: Dict):
    collection.insert_one({
        "worker_id": worker_id,
        "timestamp": datetime.datetime.utcnow(),
        "state": state,
        "metadata": metadata
    })


def get_events_by_timestamp_descending(
    worker_id: str,
    from_milliseconds: Optional[int],
    to_milliseconds: Optional[int],
    limit: Optional[int]
) -> List[Tuple[int, str, Dict]]:
    if not from_milliseconds and not to_milliseconds:
        documents = collection.find({"worker_id": worker_id})
    else:
        timestamp_q = {}
        if from_milliseconds:
            timestamp_q["$gte"] = milliseconds_to_datetime(from_milliseconds)
        if to_milliseconds:
            timestamp_q["$lte"] = milliseconds_to_datetime(to_milliseconds)
        documents = collection.find(
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


def milliseconds_to_datetime(milliseconds: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(milliseconds // 1000).replace(microsecond=milliseconds % 1000 * 1000)


def datetime_to_milliseconds(dt: datetime.datetime) -> int:
    return int(dt.replace(tzinfo=pytz.utc).timestamp() * 1000)
