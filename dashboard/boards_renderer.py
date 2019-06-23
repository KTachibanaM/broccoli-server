import importlib
import json
from typing import Optional, Dict, List
from broccoli_plugin_interface.rpc_client import RpcClient
from broccoli_plugin_interface.board.column import BoardColumn, CallbackBoardColumn
from broccoli_plugin_interface.board.render import Render, CallbackRender
from .objects.board_query import BoardQuery, BoardProjection


class BoardsRenderer(object):
    def __init__(self, rpc_client: RpcClient):
        self.rpc_client = rpc_client

    def render_as_dict(self, board_query: BoardQuery) -> List[Dict[str, Optional[Dict]]]:
        # do the query
        documents = self.rpc_client.blocking_query(
            q=json.loads(board_query.q),
            limit=board_query.limit,
            sort=board_query.sort
        )

        # load board columns
        board_columns = {}
        for p in board_query.projections:
            board_columns[p.name] = self._load_board_column(p)

        # render rows
        rows = []
        for d in documents:
            row = {}
            for column_name, column in board_columns.items():
                if not column:
                    # TODO: return some error
                    continue
                row[column_name] = self._render_to_dict(column.render(d, self.rpc_client))
            rows.append(row)

        return rows

    @staticmethod
    def _load_board_column(projection: BoardProjection) -> Optional[BoardColumn]:
        try:
            clazz = getattr(importlib.import_module(projection.module), projection.class_name)
        except Exception as e:
            return None
        try:
            return clazz(**projection.args)  # type: BoardColumn
        except Exception as e:
            return None

    @staticmethod
    def _render_to_dict(render: Render):
        return {
            "type": render.render_type(),
            "data": render.render_data()
        }
