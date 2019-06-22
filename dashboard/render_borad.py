from typing import List, Union
from broccoli_plugin_interface.board.render import Render, CallbackRender
from .objects.board_query import BoardQuery


def render_board(board_query: BoardQuery) -> List[Union[Render, CallbackRender]]:
    pass
