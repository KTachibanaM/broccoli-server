import unittest
import mongomock
import freezegun
import datetime
from content.content_store import ContentStore


class TestContentStore(unittest.TestCase):
    @classmethod
    @mongomock.patch("mongodb://localhost:27017/test_db")
    def setUpClass(cls) -> None:
        cls.content_store = ContentStore("localhost:27017", "test_db")

    def test_append_idempotency_key_absent(self):
        self.content_store.append({}, "idempotency_key")
        assert self.content_store.collection.count_documents({}) == 0

    def test_append_idempotency_key_exists(self):
        self.content_store.append({"idempotency_key": "some_value"}, "idempotency_key")
        self.content_store.append({"idempotency_key": "some_value"}, "idempotency_key")
        assert self.content_store.collection.count_documents({"idempotency_key": "some_value"}) == 1

    @freezegun.freeze_time("2019-05-14 23:15:10", tz_offset=0)
    def test_append_succeed(self):
        self.content_store.append({"key": "value_1"}, "key")
        self.content_store.append({"key": "value_2"}, "key")
        actual_cursor = self.content_store.collection.find({})
        actual_documents = []
        for actual_document in actual_cursor:
            del actual_document["_id"]
            actual_documents.append(actual_document)
        assert actual_documents == [
            {
                "key": "value_1",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            },
            {
                "key": "value_2",
                "created_at": datetime.datetime(2019, 5, 14, 23, 15, 10)
            }
        ]

    def tearDown(self) -> None:
        self.content_store.client.drop_database("test_db")
