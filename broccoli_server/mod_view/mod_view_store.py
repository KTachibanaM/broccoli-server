import logging
from broccoli_server.mod_view.mod_view_query import ModViewQuery
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class ModViewStore(object):
    def __init__(self):
        self.mod_views = []  # type: List[Tuple[str, ModViewQuery]]

    def get_all(self) -> List[Tuple[str, ModViewQuery]]:
        return self.mod_views

    def get(self, mod_view_id: str) -> Optional[ModViewQuery]:
        for _id, q in self.mod_views:
            if mod_view_id == _id:
                return q
        return None

    def declare_mod_views(self, mod_views: List[Tuple[str, ModViewQuery]]):
        self.mod_views = mod_views
