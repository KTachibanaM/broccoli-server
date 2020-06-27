from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class PaginationQuery:
    sort: Dict
    datetime_q: Optional[List[Dict]]
    reverse_results: bool


def query_params_to_pagination_query(query_params: Dict) -> PaginationQuery:
    from_timestamp = int(query_params["from"]) if "from" in query_params else None
    to_timestamp = int(query_params["to"]) if "to" in query_params else None
    if from_timestamp:
        return PaginationQuery(
            {
                "created_at": -1
            },
            [
                {
                    "key": "created_at",
                    "op": "lte",
                    "value": from_timestamp
                }
            ],
            False
        )
    elif to_timestamp:
        return PaginationQuery(
            {
                "created_at": 1
            },
            [
                {
                    "key": "created_at",
                    "op": "gte",
                    "value": to_timestamp
                }
            ],
            True
        )
    else:
        return PaginationQuery(
            {
                "created_at": -1
            },
            None,
            False
        )
