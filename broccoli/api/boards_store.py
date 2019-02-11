import pymongo
import json
from typing import List, Dict, Tuple


class BoardsStore(object):
    def __init__(self, hostname: str, port: int, db: str):
        self.client = pymongo.MongoClient(hostname, port)
        self.db = self.client[db]
        self.collection = self.db["broccoli.api.boards"]

    def upsert(self, board_id: str, q: Dict):
        existing_boards = []
        # todo: dup with get_all
        for d in self.collection.find():
            del d["_id"]
            existing_boards.append(d)
        for board in existing_boards:
            if board["board_id"] == board_id:
                self.collection.update_one(
                    filter={
                        "board_id": board_id
                    },
                    update={
                        "$set": {
                            "q": json.dumps(q)
                        }
                    }
                )
                return
        new_position = 0
        if existing_boards:
            new_position = max(map(lambda b: b["position"], existing_boards)) + 1
        self.collection.insert_one({
            "position": new_position,
            "board_id": board_id,
            "q": json.dumps(q)
        })

    def get_all(self) -> List[Tuple[str, Dict]]:
        existing_boards = []
        for d in self.collection.find().sort("position", pymongo.ASCENDING):
            existing_boards.append(
                (d["board_id"], json.loads(d["q"]))
            )
        return existing_boards

    def get(self, board_id: str) -> Tuple[str, Dict]:
        doc = self.collection.find_one({"board_id": board_id})
        return doc["board_id"], json.loads(doc["q"])

    def swap(self, board_id: str, another_board_id: str):
        # todo: find one dups with get()
        board_position = self.collection.find_one({"board_id": board_id})["position"]
        another_board_position = self.collection.find_one({"board_id": another_board_id})["position"]
        self.collection.update_one(
            filter={"board_id": board_id},
            update={"$set": {"position": another_board_position}}
        )
        self.collection.update_one(
            filter={"board_id": another_board_id},
            update={"$set": {"position": board_position}}
        )

    def remove(self, board_id: str):
        # todo: shred positions afterwards
        self.collection.delete_one({"board_id": board_id})
