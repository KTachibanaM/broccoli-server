import logging
from abc import ABCMeta, abstractmethod
from broccoli_server.content import ContentStore
from .metadata_store import MetadataStore


class WorkContext(metaclass=ABCMeta):
    @abstractmethod
    def logger(self) -> logging.Logger:
        pass

    @abstractmethod
    def content_store(self) -> ContentStore:
        pass

    @abstractmethod
    def metadata_store(self) -> MetadataStore:
        pass
