import pymongo
import datetime
import random
import heapq
import logging
from functools import total_ordering
from typing import Dict, List, Optional
from broccoli_server.utils import datetime_to_milliseconds, milliseconds_to_datetime

logger = logging.getLogger(__name__)


@total_ordering
class ComparableQueryResult(object):
    def __init__(self, key, q_result):
        self.key = key
        self.q_result = q_result

    def __lt__(self, other):
        return self.key < other.key

    def __eq__(self, other):
        return self.key == other.key

    def __repr__(self):
        return '{0.__class__.__name__}(key={0.key}, q_result={0.q_result})'.format(self)


class ContentStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db['repo.default']

    def append(self, doc: Dict, idempotency_key: str):
        if idempotency_key not in doc:
            logger.error("Idempotency key is not found in payload", extra={
                'idempotency_key': idempotency_key,
                'payload': doc
            })
            return

        idempotency_value = doc[idempotency_key]
        existing_doc_count = self.collection.count_documents({idempotency_key: idempotency_value})
        if existing_doc_count != 0:
            logger.info(f"Document with {idempotency_key}={idempotency_value} is already present")
            return

        doc["created_at"] = datetime.datetime.utcnow()
        self.collection.insert_one(doc)

    def append_multiple(self, docs: List[Dict], idempotency_key: str):
        keyed_docs = []
        for doc in docs:
            if idempotency_key not in doc:
                logger.error("Idempotency key is not found in one of the payloads", extra={
                    'idempotency_key': idempotency_key,
                    'payload': doc
                })
            else:
                keyed_docs.append(doc)

        idempotent_docs = []
        for doc in keyed_docs:
            idempotency_value = doc[idempotency_key]
            existing_doc_count = self.collection.count_documents({idempotency_key: idempotency_value})
            if existing_doc_count != 0:
                logger.info(f"Document with {idempotency_key}={idempotency_value} is already present in persistence")
                continue
            doc_exists_in_batch = False
            for d in idempotent_docs:
                if d[idempotency_key] == idempotency_value:
                    doc_exists_in_batch = True
                    break
            if doc_exists_in_batch:
                logger.info(f"Document with {idempotency_key}={idempotency_value} is already present in current batch")
                continue
            idempotent_docs.append(doc)

        if not idempotent_docs:
            logger.info("There is nothing to be appended")
            return

        now = datetime.datetime.utcnow()
        for doc in idempotent_docs:
            doc["created_at"] = now

        self.collection.insert_many(idempotent_docs)

    def query(self, q: Dict, limit: Optional[int] = None, projection: Optional[List[str]] = None,
              sort: Optional[Dict[str, int]] = None, datetime_q: Optional[List[Dict]] = None) -> List[Dict]:
        # Append datetime query
        if datetime_q:
            for qd in datetime_q:
                q[qd["key"]] = {
                    "$" + qd["op"]: milliseconds_to_datetime(qd["value"])
                }

        # Append default projections
        if projection:
            projection += ["_id", "created_at"]
        cursor = self.collection.find(q, projection=projection)

        # Append limit
        if limit:
            cursor = cursor.limit(limit)

        # Append sort
        if sort:
            for sort_key, sort_order in sort.items():
                cursor = cursor.sort(sort_key, sort_order)

        res = []
        for document in cursor:
            document["_id"] = str(document["_id"])
            document["created_at"] = datetime_to_milliseconds(document["created_at"])
            res.append(document)
        return res

    def update_one(self, filter_q: Dict, update_doc: Dict, allow_many: bool = False):
        existing_doc_count = self.collection.count_documents(filter_q)
        if existing_doc_count == 0:
            logger.error(f"Document does not exist", extra={
                "query": filter_q
            })
            return

        more_than_one = existing_doc_count > 1
        if more_than_one and not allow_many:
            logger.error(f"More than one documents exist", extra={
                "query": filter_q
            })
            return

        if not more_than_one:
            self.collection.update_one(filter_q, update_doc, upsert=False)
            return

        logger.error(f"More than one document is updated because of allow_many", extra={
            'filter_q': filter_q
        })
        self.update_many(filter_q, update_doc)

    def update_many(self, filter_q: Dict, update_doc: Dict):
        existing_doc_count = self.collection.count_documents(filter_q)
        if existing_doc_count == 0:
            logger.error(f"Document does not exist", extra={
                "query": filter_q
            })
            return

        self.collection.update_many(filter_q, update_doc, upsert=False)

    def random_one(self, q: Dict, projection: List[str]) -> Dict:
        documents = self.query(q, projection=projection)
        random_index = random.randint(0, len(documents) - 1)
        return documents[random_index]

    def count(self, q: Dict) -> int:
        return self.collection.count_documents(q)

    def delete_many(self, q: Dict) -> int:
        return self.collection.delete_many(q).deleted_count

    def update_one_binary_string(self, filter_q: Dict, key: str, binary_string: str):
        if not ContentStore._check_if_string_is_binary(binary_string):
            logger.error(f"binary_string is not a 01 string", extra={
                "value": binary_string
            })
            return
        # todo: should not update an existing field
        self.update_one(filter_q, {
            "$set": {
                key: binary_string
            }
        })

    def query_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                        max_distance: int) -> List[Dict]:
        # todo: use a metric tree
        if not ContentStore._check_if_string_is_binary(from_binary_string):
            return []
        results = []
        for q_result in self.query(q, limit=None):
            if not ContentStore._check_if_q_result_has_valid_binary(q_result, binary_string_key, from_binary_string):
                continue
            q_binary_string = q_result[binary_string_key]
            distance = ContentStore._compute_binary_hamming_distance(q_binary_string, from_binary_string)
            if distance <= max_distance:
                results.append(q_result)
        return results

    def query_n_nearest_hamming_neighbors(self, q: Dict, binary_string_key: str, from_binary_string: str,
                                          pick_n: int) -> List[Dict]:
        # todo: use a metric tree
        if not ContentStore._check_if_string_is_binary(from_binary_string):
            logger.error(f"from_binary_string is not a 01 string", extra={
                "value": from_binary_string
            })
            return []
        q_results = self.query(q, limit=None)
        if len(q_results) < pick_n:
            return []
        results = []
        heapq.heapify(results)
        for q_result in q_results:
            if not ContentStore._check_if_q_result_has_valid_binary(q_result, binary_string_key, from_binary_string):
                continue
            q_binary_string = q_result[binary_string_key]
            distance = ContentStore._compute_binary_hamming_distance(q_binary_string, from_binary_string)
            heapq.heappush(results, ComparableQueryResult(-distance, q_result))
            if len(results) > pick_n:
                heapq.heappop(results)
        return list(map(lambda h_item: h_item.q_result, results))

    @staticmethod
    def _check_if_string_is_binary(string: str) -> bool:
        if not (set(string) <= set("01")):
            return False
        return True

    @staticmethod
    def _check_if_q_result_has_valid_binary(q_result: Dict, binary_string_key: str, from_binary_string: str) -> bool:
        if binary_string_key not in q_result:
            return False
        q_binary_string = q_result[binary_string_key]
        if len(q_binary_string) != len(from_binary_string):
            return False
        if not ContentStore._check_if_string_is_binary(q_binary_string):
            return False
        return True

    @staticmethod
    def _compute_binary_hamming_distance(s1: str, s2: str):
        distance = 0
        for i in range(len(s1)):
            if s1[i] != s2[i]:
                distance += 1
        return distance

