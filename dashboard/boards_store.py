import pymongo
from .objects.board_query import BoardQuery
from typing import List, Tuple


class BoardsStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db["boards"]

    def upsert(self, board_id: str, board_query: BoardQuery):
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
                            "board_query": board_query.to_dict()
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
            "board_query": board_query.to_dict()
        })

    def get_all(self) -> List[Tuple[str, BoardQuery]]:
        existing_boards = []
        for d in self.collection.find().sort("position", pymongo.ASCENDING):
            existing_boards.append(
                (d["board_id"], BoardQuery(d["board_query"]))
            )
        return existing_boards

    def get(self, board_id: str) -> BoardQuery:
        doc = self.collection.find_one({"board_id": board_id})
        return BoardQuery(doc["board_query"])

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
