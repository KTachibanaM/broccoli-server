from typing import Dict
from broccoli_server.interface.mod_view import ModViewColumn
from broccoli_server.interface.mod_view.column_render import Button
from broccoli_server.content import ContentStore


class UpdateOneButton(ModViewColumn):
    def __init__(self,
                 text: str,
                 callback_id: str,
                 filter_q_key: str,
                 update_set_doc: Dict,
                 allow_many: bool = False
                 ):
        self.text = text
        self._callback_id = callback_id
        self.filter_q_key = filter_q_key
        self.update_set_doc = update_set_doc
        self.allow_many = allow_many

    def render(self, document: Dict, content_store: ContentStore) -> Button:
        return Button(
            text=self.text,
            reload_after_callback=True
        )

    def has_callback(self) -> bool:
        return True

    def callback_id(self) -> str:
        return self._callback_id

    def callback(self, document: Dict, content_store: ContentStore):
        content_store.update_one(
            filter_q={
                self.filter_q_key: document[self.filter_q_key]
            },
            update_doc={
                "$set": self.update_set_doc
            },
            allow_many=self.allow_many
        )
