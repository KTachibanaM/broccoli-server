import logging
from .metadata_store import MetadataStore, MetadataStoreFactory
from broccoli_server.content import ContentStore


class WorkContext(object):
    def __init__(self, worker_id: str, content_store: ContentStore, metadata_store_factory: MetadataStoreFactory):
        self._logger = logging.getLogger(worker_id)
        self._content_store = content_store
        self._metadata_store = metadata_store_factory.build(worker_id)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def content_store(self) -> ContentStore:
        return self._content_store

    @property
    def metadata_store(self) -> MetadataStore:
        return self._metadata_store


class WorkContextFactory(object):
    def __init__(self, content_store: ContentStore, metadata_store_factory: MetadataStoreFactory):
        self.content_store = content_store
        self.metadata_store_factory = metadata_store_factory
        
    def build(self, worker_id: str):
        return WorkContext(
            worker_id=worker_id,
            content_store=self.content_store,
            metadata_store_factory=self.metadata_store_factory
        )
