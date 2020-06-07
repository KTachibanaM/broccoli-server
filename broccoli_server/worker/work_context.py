import logging
from .metadata_store import MetadataStore, MetadataStoreFactory
from broccoli_server.utils import DefaultHandler, get_logging_level
from broccoli_server.content import ContentStore


class WorkContext(object):
    def __init__(self, worker_id: str, content_store: ContentStore, metadata_store_factory: MetadataStoreFactory):
        self._logger = logging.getLogger(worker_id)
        self._logger.setLevel(get_logging_level())
        self._logger.addHandler(DefaultHandler)

        self._content_store = content_store
        self._metadata_store = metadata_store_factory.build(worker_id)

    @property
    def content_store(self) -> ContentStore:
        return self._content_store

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def metadata_store(self) -> MetadataStore:
        return self._metadata_store
