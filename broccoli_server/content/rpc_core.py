from typing import Dict, Tuple, Union, List
from broccoli_server.utils import validate_schema_or_not
from .content_store import ContentStore
from .rpc_schemas import SCHEMAS
from .logging import logger


class RpcCore(object):
    def __init__(self, content_store: ContentStore):
        self.content_store = content_store

    def call(self, parsed_body: Dict) -> Tuple[bool, Union[str, Dict, List]]:
        if not parsed_body \
                or "verb" not in parsed_body or type(parsed_body["verb"]) != str \
                or "metadata" not in parsed_body or type(parsed_body["metadata"]) != dict \
                or "payload" not in parsed_body or type(parsed_body["payload"]) != dict:
            logger.error(f"Invalid message body", extra={
                'parsed_body': parsed_body
            })
            return False, 'Invalid message body'

        verb = parsed_body["verb"]  # type: str
        metadata = parsed_body["metadata"]  # type: Dict
        payload = parsed_body['payload']  # type: Dict
        logger.debug(f"Received rpc request verb={verb} metadata={metadata} payload={payload}")

        if verb == "append":
            return self.append(metadata, payload)
        if verb == "query":
            return self.query(metadata, payload)
        if verb == "update_one":
            return self.update_one(metadata, payload)
        if verb == 'update_one_binary_string':
            return self.update_one_binary_string(metadata, payload)
        if verb == 'query_nearest_hamming_neighbors':
            return self.query_nearest_hamming_neighbors(metadata, payload)
        if verb == 'random_one':
            return self.random_one(metadata, payload)
        if verb == 'count':
            return self.count(metadata, payload)
        return False, 'Unknown verb'

    def append(self, metadata: Dict, payload: Dict) -> Tuple[bool, str]:
        logger.debug(f"Calling append metadata={metadata}, payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS["append"]["payload"])
        if not status:
            logger.info(f"Fails to validate query payload={payload}, message {message}")
            return False, message

        # todo: failure
        self.content_store.append(payload["doc"], payload["idempotency_key"])
        return True, ''

    def query(self, metadata: Dict, payload: Dict) -> Tuple[bool, List[Dict]]:
        logger.debug(f"Calling query metadata={metadata}, payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS["query"]["payload"])
        if not status:
            logger.info(f"Fails to validate query payload={payload}, message {message}")
            return False, []

        limit = payload["limit"] if "limit" in payload else None
        projection = payload["projection"] if "projection" in payload else None
        sort = payload["sort"] if "sort" in payload else None
        datetime_q = payload["datetime_q"] if "datetime_q" in payload else None
        # todo: query failure
        return True, self.content_store.query(payload["q"], limit=limit, projection=projection, sort=sort,
                                              datetime_q=datetime_q)

    def update_one(self, metadata: Dict, payload: Dict) -> Tuple[bool, str]:
        logger.debug(f"Calling update_one metadata={metadata}, payload={payload}")

        if "filter_q" not in payload:
            return False, "filter_q not found in payload"
        if type(payload["filter_q"]) != dict:
            return False, "filter_q in payload is not a dict"

        if "update_doc" not in payload:
            return False, "update_doc not found in payload"
        if type(payload["update_doc"]) != dict:
            return False, "update_doc in payload is not a dict"

        # todo: failure
        self.content_store.update_one(filter_q=payload["filter_q"], update_doc=payload["update_doc"])
        return True, ''

    def update_one_binary_string(self, metadata: Dict, payload: Dict) -> Tuple[bool, str]:
        logger.debug(f"Calling update_one_binary_string metadata={metadata}, payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS["update_one_binary_string"]["payload"])
        if not status:
            return False, message

        # todo: failure
        self.content_store.update_one_binary_string(payload["filter_q"], payload["key"], payload["binary_string"])
        return True, ''

    def query_nearest_hamming_neighbors(self, metadata: Dict, payload: Dict) -> Tuple[bool, List[Dict]]:
        logger.debug(f"Calling query_nearest_hamming_neighbors metadata={metadata}, payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS["query_nearest_hamming_neighbors"]["payload"])
        if not status:
            logger.info(f"Fails to validate query_nearest_hamming_neighbors payload={payload}, message {message}")
            return False, []

        # todo: failure
        return True, self.content_store.query_nearest_hamming_neighbors(
            q=payload["q"],
            binary_string_key=payload["binary_string_key"],
            from_binary_string=payload["from_binary_string"],
            max_distance=payload["max_distance"]
        )

    def random_one(self, metadata: Dict, payload: Dict) -> Tuple[bool, Union[Dict, str]]:
        logger.debug(f"Calling random_one metadata={metadata}, payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS["random_one"]["payload"])
        if not status:
            return False, message

        # todo: failure
        return True, self.content_store.random_one(
            q=payload["q"],
            projection=payload["projection"]
        )

    def count(self, metadata: Dict, payload: Dict) -> Tuple[bool, Union[int, str]]:
        logger.debug(f"Calling count metadata={metadata} payload={payload}")

        status, message = validate_schema_or_not(payload, SCHEMAS['count']['payload'])
        if not status:
            logger.info(f"Fails to validate count metadata={metadata} payload={payload}")
            return False, message

        # todo: failure
        return True, self.content_store.count(payload['q'])
