from typing import Dict


class BoardProjection(object):
    def __init__(self, d: Dict):
        self.name = d["name"]
        self.js_filename = d["js_filename"]
        self.args = d["args"]

    def to_dict(self):
        d = {
            "name": self.name,
            "js_filename": self.js_filename,
            "args": self.args,
        }
        return d


class BoardQuery(object):
    def __init__(self, d: Dict):
        self.q = d["q"]
        if "limit" in d:
            self.limit = d["limit"]
        else:
            self.limit = None
        self.projections = list(map(lambda pd: BoardProjection(pd), d["projections"]))

    def to_dict(self):
        d = {
            "q": self.q,
            "projections": list(map(lambda p: p.to_dict(), self.projections))
        }
        if self.limit:
            d["limit"] = self.limit
        return d
