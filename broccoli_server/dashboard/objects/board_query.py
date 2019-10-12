from typing import Dict


class BoardProjection(object):
    def __init__(self, d: Dict):
        self.name = d["name"]
        self.module = d.get("module", "")
        self.class_name = d.get("class_name", "")
        self.args = d["args"]

    def to_dict(self):
        d = {
            "name": self.name,
            "module": self.module,
            "class_name": self.class_name,
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
        if "sort" in d:
            self.sort = d["sort"]
        else:
            self.sort = None
        self.projections = list(map(lambda pd: BoardProjection(pd), d["projections"]))

    def to_dict(self):
        d = {
            "q": self.q,
            "projections": list(map(lambda p: p.to_dict(), self.projections))
        }
        if self.limit:
            d["limit"] = self.limit
        if self.sort:
            d["sort"] = self.sort
        return d
