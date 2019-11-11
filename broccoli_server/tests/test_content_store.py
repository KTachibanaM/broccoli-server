import unittest
import mongomock
import freezegun
import datetime
from typing import Dict, List
from broccoli_server.content import ContentStore


class TestContentStore(unittest.TestCase):
    @classmethod
    @mongomock.patch("mongodb://localhost:27017/test_db")
    def setUpClass(cls) -> None:
        cls.content_store = ContentStore("localhost:27017", "test_db")

    def tearDown(self) -> None:
        self.content_store.client.drop_database("test_db")

    def actual_documents_without_id(self) -> List[Dict]:
        actual_cursor = self.content_store.collection.find({})
        actual_documents = []
        for actual_document in actual_cursor:
            del actual_document["_id"]
            actual_documents.append(actual_document)
        return actual_documents


class TestContentStoreAppend(TestContentStore):
    def test_idempotency_key_absent(self):
        self.content_store.append({}, "idempotency_key")
        assert self.content_store.collection.count_documents({}) == 0

    def test_idempotency_value_exists(self):
        self.content_store.append({"idempotency_key": "some_value"}, "idempotency_key")
        self.content_store.append({"idempotency_key": "some_value"}, "idempotency_key")
        assert self.content_store.collection.count_documents({"idempotency_key": "some_value"}) == 1

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_succeed(self):
        self.content_store.append({"key": "value_1"}, "key")
        self.content_store.append({"key": "value_2"}, "key")
        assert self.actual_documents_without_id() == [
            {
                "key": "value_1",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value_2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]


class TestContentStoreAppendMultiple(TestContentStore):
    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_idempotency_key_absent(self):
        self.content_store.append_multiple([
            {"key": "value1"},
            {"key2": "value2"}
        ], "key2")
        assert self.actual_documents_without_id() == [
            {
                "key2": "value2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_idempotency_value_exists_in_persistence(self):
        self.content_store.append({"key": "value"}, "key")
        self.content_store.append_multiple([
            {"key": "value"},
            {"key": "value2"}
        ], "key")
        assert self.actual_documents_without_id() == [
            {
                "key": "value",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_idempotency_value_exists_in_persistence_and_nothing_to_append(self):
        self.content_store.append({"key": "value"}, "key")
        self.content_store.append_multiple([
            {"key": "value"},
        ], "key")
        assert self.actual_documents_without_id() == [
            {
                "key": "value",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_idempotency_value_exists_in_batch(self):
        self.content_store.append_multiple([
            {"key": "value", "foo": "bar"},
            {"key": "value"},
            {"key": "value2"}
        ], "key")
        assert self.actual_documents_without_id() == [
            {
                "key": "value",
                "foo": "bar",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_succeed(self):
        self.content_store.append({"key": "value"}, "key")
        self.content_store.append_multiple([
            {"key": "value2"},
            {"key": "value3"}
        ], "key")
        assert self.actual_documents_without_id() == [
            {
                "key": "value",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value3",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
        ]


class TestContentStoreQueryNearestNeighbors(TestContentStore):
    def test_invalid_from_binary_string(self):
        assert self.content_store.query_nearest_hamming_neighbors(
            q={},
            binary_string_key="binary_string_key",
            from_binary_string="abc",
            max_distance=5
        ) == []

    def test_query_do_not_match(self):
        self.content_store.append({"key": "value_1", "bs": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs": "0000"}, "key")
        assert self.content_store.query_nearest_hamming_neighbors(
            q={"key": "value_3"},
            binary_string_key="bs",
            from_binary_string="0000",
            max_distance=1
        ) == []

    def test_query_results_do_not_have_field(self):
        self.content_store.append({"key": "value_1", "bs_key_2": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs_key_2": "0000"}, "key")
        assert self.content_store.query_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="0000",
            max_distance=1
        ) == []

    def test_query_results_do_not_have_same_length_string(self):
        self.content_store.append({"key": "value_1", "bs": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs": "0000"}, "key")
        assert self.content_store.query_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="00001",
            max_distance=1
        ) == []

    def test_query_results_do_not_have_valid_binary_string(self):
        self.content_store.append({"key": "value_1", "bs": "abcd"}, "key")
        self.content_store.append({"key": "value_2", "bs": "abcd"}, "key")
        assert self.content_store.query_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="0000",
            max_distance=1
        ) == []

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_succeed(self):
        self.content_store.append({"key": "value_1", "attr": True, "bs": "0000"}, "key")
        self.content_store.append({"key": "value_2", "attr": True, "bs": "0001"}, "key")
        self.content_store.append({"key": "value_3", "attr": True, "bs": "1111"}, "key")
        self.content_store.append({"key": "value_4", "attr": False, "bs": "0000"}, "key")
        actual_documents = self.content_store.query_nearest_hamming_neighbors(
            q={"attr": True},
            binary_string_key="bs",
            from_binary_string="0000",
            max_distance=1
        )
        for i in range(len(actual_documents)):
            del actual_documents[i]["_id"]
        assert actual_documents == [
            {
                "key": "value_1",
                "attr": True,
                "bs": "0000",
                "created_at": 1557875710000
            },
            {
                "key": "value_2",
                "attr": True,
                "bs": "0001",
                "created_at": 1557875710000
            }
        ]


class TestContentStoreQueryNNearestNeighbors(TestContentStore):
    def test_invalid_from_binary_string(self):
        assert self.content_store.query_n_nearest_hamming_neighbors(
            q={},
            binary_string_key="binary_string_key",
            from_binary_string="abc",
            pick_n=0
        ) == []

    def test_query_do_not_match(self):
        self.content_store.append({"key": "value_1", "bs": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs": "0001"}, "key")
        assert self.content_store.query_n_nearest_hamming_neighbors(
            q={"key": "value_3"},
            binary_string_key="bs",
            from_binary_string="0000",
            pick_n=1
        ) == []

    def test_query_results_do_not_have_field(self):
        self.content_store.append({"key": "value_1", "bs_key_2": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs_key_2": "0001"}, "key")
        assert self.content_store.query_n_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="0000",
            pick_n=1
        ) == []

    def test_query_results_do_not_have_same_length_string(self):
        self.content_store.append({"key": "value_1", "bs": "0000"}, "key")
        self.content_store.append({"key": "value_2", "bs": "0001"}, "key")
        assert self.content_store.query_n_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="00001",
            pick_n=1
        ) == []

    def test_query_results_do_not_have_valid_binary_string(self):
        self.content_store.append({"key": "value_1", "bs": "abcd"}, "key")
        self.content_store.append({"key": "value_2", "bs": "abcd"}, "key")
        assert self.content_store.query_n_nearest_hamming_neighbors(
            q={},
            binary_string_key="bs",
            from_binary_string="0000",
            pick_n=1
        ) == []

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_succeed(self):
        self.content_store.append({"key": "value_1", "attr": True, "bs": "0001"}, "key")
        self.content_store.append({"key": "value_2", "attr": True, "bs": "0011"}, "key")
        self.content_store.append({"key": "value_3", "attr": True, "bs": "0011"}, "key")
        self.content_store.append({"key": "value_4", "attr": True, "bs": "0111"}, "key")
        self.content_store.append({"key": "value_5", "attr": False, "bs": "0000"}, "key")
        actual_documents = self.content_store.query_n_nearest_hamming_neighbors(
            q={"attr": True},
            binary_string_key="bs",
            from_binary_string="0000",
            pick_n=2
        )
        for i in range(len(actual_documents)):
            del actual_documents[i]["_id"]
        assert actual_documents == [
            {
                "key": "value_3",
                "attr": True,
                "bs": "0011",
                "created_at": 1557875710000
            },
            {
                "key": "value_1",
                "attr": True,
                "bs": "0001",
                "created_at": 1557875710000
            }
        ]
