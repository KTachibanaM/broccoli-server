from typing import Dict
from broccoli_server.interface.mod_view import ModViewColumn
from broccoli_server.interface.mod_view.column_render import Button
from broccoli_server.interface.rpc import RpcClient


class UpdateOneButton(ModViewColumn):
    def __init__(self,
                 text: str,
                 callback_id: str,
                 filter_q_key: str,
                 update_set_doc: str):
        self.text = text
        self._callback_id = callback_id
        self.filter_q_key = filter_q_key
        self.update_set_doc = update_set_doc

    def render(self, document: Dict, rpc_client: RpcClient) -> Button:
        return Button(
            text=self.text,
            reload_after_callback=True
        )

    def has_callback(self) -> bool:
        return True

    def callback_id(self) -> str:
        return self._callback_id

    def callback(self, document: Dict, rpc_client: RpcClient):
        rpc_client.blocking_update_one(
            filter_q={
                self.filter_q_key: document[self.filter_q_key]
            },
            update_doc={
                "$set": self.update_set_doc
            }
        )
