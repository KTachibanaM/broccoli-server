import logging
from .metadata_store import MetadataStoreFactory
from broccoli_server.interface.worker import WorkContext, MetadataStore
from broccoli_server.content import ContentStore


class WorkContextImpl(WorkContext):
    def __init__(self, worker_id: str, content_store: ContentStore, metadata_store_factory: MetadataStoreFactory):
        # still need the prefix to globally configure logging for all broccoli workers
        self._logger = logging.getLogger(f"broccoli.worker.{worker_id}")
        self._content_store = content_store
        self._metadata_store = metadata_store_factory.build(worker_id)

    def logger(self) -> logging.Logger:
        return self._logger

    def content_store(self) -> ContentStore:
        return self._content_store

    def metadata_store(self) -> MetadataStore:
        return self._metadata_store


class WorkContextFactory(object):
    def __init__(self, content_store: ContentStore, metadata_store_factory: MetadataStoreFactory):
        self.content_store = content_store
        self.metadata_store_factory = metadata_store_factory
        
    def build(self, worker_id: str) -> WorkContext:
        return WorkContextImpl(
            worker_id=worker_id,
            content_store=self.content_store,
            metadata_store_factory=self.metadata_store_factory
        )
