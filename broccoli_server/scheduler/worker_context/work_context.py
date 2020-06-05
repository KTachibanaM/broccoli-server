import logging
from .metadata_store import MetadataStore
from broccoli_server.utils import DefaultHandler, get_logging_level
from broccoli_server.utils.getenv_or_raise import getenv_or_raise
from broccoli_server.content import ContentStore


class WorkContext(object):
    def __init__(self, worker_id: str, content_store: ContentStore):
        self._logger = logging.getLogger(worker_id)
        self._logger.setLevel(get_logging_level())
        self._logger.addHandler(DefaultHandler)

        self._content_store = content_store
        self._metadata_store = MetadataStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_id=worker_id
        )

    @property
    def content_store(self) -> ContentStore:
        return self._content_store

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def metadata_store(self) -> MetadataStore:
        return self._metadata_store
