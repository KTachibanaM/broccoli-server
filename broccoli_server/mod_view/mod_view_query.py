from typing import Dict, Optional, List
from dataclasses import dataclass
from broccoli_server.interface.mod_view import ModViewColumn


@dataclass
class NamedModViewColumn:
    name: str
    column: ModViewColumn

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass
class ModViewQuery:
    query: Dict
    projections: List[NamedModViewColumn]
    limit: Optional[int] = None
    sort: Optional[Dict] = None

    def to_dict(self):
        d = {
            "q": self.query,
            "projections": list(map(lambda p: p.to_dict(), self.projections))
        }
        if self.limit:
            d["limit"] = self.limit
        if self.sort:
            d["sort"] = self.sort
        return d
