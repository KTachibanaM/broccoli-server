import json
from typing import Optional, Dict, List, Tuple, Callable
from broccoli_interface.rpc import RpcClient
from broccoli_interface.board import BoardColumn
from broccoli_interface.board import Render
from .objects.board_query import BoardQuery, BoardProjection


class BoardsRenderer(object):
    def __init__(self, rpc_client: RpcClient):
        self.rpc_client = rpc_client
        self.callbacks = {}  # type: Dict[str, BoardColumn]
        self._columns = {}  # type: Dict[Tuple[str, str], Callable]

    def add_column(self, module: str, class_name: str, constructor: Callable):
        self._columns[(module, class_name)] = constructor

    def render_as_dict(self, board_query: BoardQuery) -> List[Dict[str, Optional[Dict]]]:
        # load board columns
        board_columns = {}
        for p in board_query.projections:
            column = self._load_board_column(p)
            if not column:
                # TODO: return some error
                continue
            board_columns[p.name] = column
            if column.has_callback():
                self.callbacks[column.callback_id()] = column

        # do the query
        documents = self.rpc_client.blocking_query(
            q=json.loads(board_query.q),
            limit=board_query.limit,
            sort=board_query.sort
        )

        # render rows
        rows = []
        for d in documents:
            row_renders = {}
            for column_name, column in board_columns.items():
                row_renders[column_name] = self._render_to_dict(column.render(d, self.rpc_client))
                if column.has_callback():
                    row_renders[column_name]["callback_id"] = column.callback_id()
            rows.append({
                "renders": row_renders,
                "raw_document": d
            })

        return rows

    def callback(self, callback_id: str, document: Dict):
        if callback_id in self.callbacks:
            self.callbacks[callback_id].callback(document, self.rpc_client)
        # TODO: error here

    def _load_board_column(self, projection: BoardProjection) -> Optional[BoardColumn]:
        if (projection.module, projection.class_name) not in self._columns:
            return None
        clazz = self._columns[(projection.module, projection.class_name)]
        try:
            return clazz(**projection.args)  # type: BoardColumn
        except Exception as e:
            return None

    @staticmethod
    def _render_to_dict(render: Render) -> Dict:
        return {
            "type": render.render_type(),
            "data": render.render_data()
        }
