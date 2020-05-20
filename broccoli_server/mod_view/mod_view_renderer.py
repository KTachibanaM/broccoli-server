import json
from typing import Optional, Dict, List, Tuple, Callable
from broccoli_server.interface.rpc import RpcClient
from broccoli_server.interface.mod_view import ModViewColumn
from broccoli_server.interface.mod_view import ModViewColumnRender
from .objects.mod_view_query import ModViewQuery, ModViewColumnConstruct


class ModViewRenderer(object):
    def __init__(self, rpc_client: RpcClient):
        self.rpc_client = rpc_client
        self.callbacks = {}  # type: Dict[str, ModViewColumn]
        self._columns = {}  # type: Dict[Tuple[str, str], Callable]

    def add_column(self, module: str, class_name: str, constructor: Callable):
        self._columns[(module, class_name)] = constructor

    def render_as_dict(self, mod_view_query: ModViewQuery) -> List[Dict[str, Optional[Dict]]]:
        # load mod view columns
        mod_view_columns = {}
        for p in mod_view_query.column_constructs:
            column = self._load_mod_view_column(p)
            if not column:
                # TODO: return some error
                continue
            mod_view_columns[p.name] = column
            if column.has_callback():
                self.callbacks[column.callback_id()] = column

        # do the query
        documents = self.rpc_client.blocking_query(
            q=json.loads(mod_view_query.q),
            limit=mod_view_query.limit,
            sort=mod_view_query.sort
        )

        # render rows
        rows = []
        for d in documents:
            row_renders = {}
            for column_name, column in mod_view_columns.items():
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

    def _load_mod_view_column(self, column_construct: ModViewColumnConstruct) -> Optional[ModViewColumn]:
        if (column_construct.module, column_construct.class_name) not in self._columns:
            return None
        clazz = self._columns[(column_construct.module, column_construct.class_name)]
        try:
            return clazz(**column_construct.args)  # type: ModViewColumn
        except Exception as e:
            return None

    @staticmethod
    def _render_to_dict(render: ModViewColumnRender) -> Dict:
        return {
            "type": render.render_type(),
            "data": render.render_data()
        }
