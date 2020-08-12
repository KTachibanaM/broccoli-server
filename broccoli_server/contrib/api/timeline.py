import bson
from typing import Dict, Optional, List
from broccoli_server.content import ContentStore
from broccoli_server.utils import datetime_to_milliseconds


def add_created_at(d: Dict) -> Dict:
    new_d = d.copy()
    new_d["created_at"] = datetime_to_milliseconds(bson.ObjectId(d["_id"]).generation_time)
    return new_d


def query(
        content_store: ContentStore,
        query_params: Dict,
        projection: List[str],
        limit: int,
        additional_q: Optional[Dict] = None
) -> Dict:
    if additional_q is None:
        additional_q = {}

    # get results
    if "from" in query_params:
        from_id = bson.ObjectId(query_params["from"])
        q = additional_q.copy()
        q["_id"] = {"$lt": from_id}

        results = content_store.query(
            q=q,
            projection=projection,
            limit=limit,
            sort={
                "_id": -1
            },
        )
    elif "to" in query_params:
        to_id = bson.ObjectId(query_params["to"])
        q = additional_q.copy()
        q["_id"] = {"$gt": to_id}

        results = content_store.query(
            q=q,
            projection=projection,
            limit=limit,
            sort={
                "_id": 1
            },
        )
        results = list(reversed(results))
    else:
        results = content_store.query(
            q=additional_q,
            projection=projection,
            limit=limit,
            sort={
                "_id": -1
            }
        )

    if not results:
        return {
            "has_prev": False,
            "has_next": False,
            "results": list(map(add_created_at, results))
        }

    # get next
    next_from_id = bson.ObjectId(results[-1]["_id"])
    q = additional_q.copy()
    q["_id"] = {"$lt": next_from_id}
    has_next = content_store.count(q) != 0

    # get prev
    prev_to_id = bson.ObjectId(results[0]["_id"])
    q = additional_q.copy()
    q["_id"] = {"$gt": prev_to_id}
    has_prev = content_store.count(q) != 0

    return {
        "has_prev": has_prev,
        "prev_to": str(prev_to_id),
        "has_next": has_next,
        "next_from": str(next_from_id),
        "results": list(map(add_created_at, results))
    }
