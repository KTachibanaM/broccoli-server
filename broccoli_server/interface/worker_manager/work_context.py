import logging
from abc import ABCMeta
from broccoli_server.content import ContentStore
from .metadata_store import MetadataStore


class WorkContext(metaclass=ABCMeta):
    @property
    def metadata_store(self) -> MetadataStore:
        pass

    @property
    def content_store(self) -> ContentStore:
        pass

    @property
    def logger(self) -> logging.Logger:
        pass
