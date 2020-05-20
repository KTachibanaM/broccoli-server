from abc import ABCMeta, abstractmethod
from typing import Dict, List


class ModViewColumnRender(metaclass=ABCMeta):
    @abstractmethod
    def render_type(self) -> str:
        pass

    @abstractmethod
    def render_data(self) -> Dict:
        pass


class Text(ModViewColumnRender):
    def __init__(self, text: str):
        self.text = text

    def render_type(self) -> str:
        return "text"

    def render_data(self) -> Dict:
        return {
            "text": self.text
        }


class Image(ModViewColumnRender):
    def __init__(self, url: str):
        self.url = url

    def render_type(self) -> str:
        return "image"

    def render_data(self) -> Dict:
        return {
            "url": self.url
        }


class ImageList(ModViewColumnRender):
    def __init__(self, urls: List[str]):
        self.urls = urls

    def render_type(self) -> str:
        return "image_list"

    def render_data(self) -> Dict:
        return {
            "urls": self.urls
        }


class Button(ModViewColumnRender):
    def __init__(self, text: str, reload_after_callback: bool):
        self.text = text
        self.reload_after_callback = reload_after_callback

    def render_type(self) -> str:
        return "button"

    def render_data(self) -> Dict:
        return {
            "text": self.text,
            "reload_after_callback": self.reload_after_callback
        }


class Video(ModViewColumnRender):
    def __init__(self, url: str):
        self.url = url

    def render_type(self) -> str:
        return "video"

    def render_data(self) -> Dict:
        return {
            "url": self.url
        }
