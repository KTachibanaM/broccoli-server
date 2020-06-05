from typing import Dict
import json
from broccoli_server.interface.mod_view import NonCallbackModViewColumn
from broccoli_server.interface.mod_view.column_render import Text
from broccoli_server.content import ContentStore


class Echo(NonCallbackModViewColumn):
    def __init__(self, key: str):
        self.key = key

    def render(self, document: Dict, content_store: ContentStore) -> Text:
        if self.key in document:
            return Text(
                text=json.dumps(document[self.key])
            )
        else:
            return Text(
                text="N/A"
            )
