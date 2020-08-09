from typing import Dict, Optional, List
from broccoli_server.content import ContentStore


def query(
        content_store: ContentStore,
        query_params: Dict,
        projection: List[str],
        limit: int,
        additional_q: Optional[Dict] = None
) -> Dict:
    if additional_q is None:
        additional_q = {}
    from_timestamp = int(query_params["from"]) if "from" in query_params else None
    to_timestamp = int(query_params["to"]) if "to" in query_params else None

    # get results
    if from_timestamp:
        results = content_store.query(
            q=additional_q,
            projection=projection,
            limit=limit,
            sort={
                "created_at": -1
            },
            datetime_q=[
                {
                    "key": "created_at",
                    "op": "lte",
                    "value": from_timestamp
                }
            ],
        )
    elif to_timestamp:
        results = content_store.query(
            q=additional_q,
            projection=projection,
            limit=limit,
            sort={
                "created_at": 1
            },
            datetime_q=[
                {
                    "key": "created_at",
                    "op": "gte",
                    "value": to_timestamp
                }
            ]
        )
        results = list(reversed(results))
    else:
        results = content_store.query(
            q=additional_q,
            projection=projection,
            limit=limit,
            sort={
                "created_at": -1
            },
            datetime_q=None
        )

    if not results:
        return {
            "has_prev": False,
            "has_next": False,
            "results": results
        }

    # get prev
    prev_to = results[0]["created_at"] + 1
    has_prev = content_store.count(
        q=additional_q,
        datetime_q=[
            {
                "key": "created_at",
                "op": "gte",
                "value": prev_to
            }
        ]
    ) != 0

    # get next
    next_from = results[-1]["created_at"] - 1
    has_next = content_store.count(
        q=additional_q,
        datetime_q=[
            {
                "key": "created_at",
                "op": "lte",
                "value": next_from
            }
        ],
    ) != 0

    return {
        "has_prev": has_prev,
        "prev_to": prev_to,
        "has_next": has_next,
        "next_from": next_from,
        "results": results
    }
