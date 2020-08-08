import json
import redis
from typing import Dict
from dataclasses import dataclass


@dataclass
class WorkerPayload:
    type: str
    module_name: str
    args: Dict

    def to_json(self):
        return {
            "type": self.type,
            "module_name": self.module_name,
            "args": self.args
        }

    @staticmethod
    def from_json(d: Dict):
        return WorkerPayload(
            d["type"],
            d["module_name"],
            d["args"]
        )


class WorkerQueue(object):
    def __init__(self, redis_url: str, key_prefix: str):
        self.db = redis.from_url(redis_url)
        self.key = f"{key_prefix}.worker_q"

    def enqueue(self, payload: WorkerPayload):
        self.db.rpush(self.key, json.dumps(payload.to_json()))

    def blocking_dequeue(self) -> WorkerPayload:
        item = self.db.blpop(self.key)
        if item:
            item = item[1]
        return WorkerPayload.from_json(json.loads(item))
