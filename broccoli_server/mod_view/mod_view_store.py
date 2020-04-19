import pymongo
from .objects.mod_view_query import ModViewQuery
from typing import List, Tuple


class ModViewStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db["boards"]

    def upsert(self, mod_view_id: str, mod_view_query: ModViewQuery):
        existing_mod_views = []
        # todo: dup with get_all
        for d in self.collection.find():
            del d["_id"]
            existing_mod_views.append(d)
        for mod_view in existing_mod_views:
            if mod_view["board_id"] == mod_view_id:
                self.collection.update_one(
                    filter={
                        "board_id": mod_view_id
                    },
                    update={
                        "$set": {
                            "board_query": mod_view_query.to_dict()
                        }
                    }
                )
                return
        new_position = 0
        if existing_mod_views:
            new_position = max(map(lambda b: b["position"], existing_mod_views)) + 1
        self.collection.insert_one({
            "position": new_position,
            "board_id": mod_view_id,
            "board_query": mod_view_query.to_dict()
        })

    def get_all(self) -> List[Tuple[str, ModViewQuery]]:
        existing_mod_views = []
        for d in self.collection.find().sort("position", pymongo.ASCENDING):
            existing_mod_views.append(
                (d["board_id"], ModViewQuery(d["board_query"]))
            )
        return existing_mod_views

    def get(self, mod_view_id: str) -> ModViewQuery:
        doc = self.collection.find_one({"board_id": mod_view_id})
        return ModViewQuery(doc["board_query"])

    def swap(self, mod_view_id: str, another_mod_view_id: str):
        # todo: find one dups with get()
        mod_view_position = self.collection.find_one({"board_id": mod_view_id})["position"]
        another_mod_view_position = self.collection.find_one({"board_id": another_mod_view_id})["position"]
        self.collection.update_one(
            filter={"board_id": mod_view_id},
            update={"$set": {"position": another_mod_view_position}}
        )
        self.collection.update_one(
            filter={"board_id": another_mod_view_id},
            update={"$set": {"position": mod_view_position}}
        )

    def remove(self, mod_view_id: str):
        # todo: shred positions afterwards
        self.collection.delete_one({"board_id": mod_view_id})

    def remove_all(self, actual_run: bool = False):
        if not actual_run:
            print(f"Going to remove {self.collection.count_documents({})} documents")
        else:
            self.collection.delete_many({})
