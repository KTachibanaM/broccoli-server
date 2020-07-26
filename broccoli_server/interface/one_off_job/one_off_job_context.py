import logging
from typing import List
from abc import ABCMeta, abstractmethod
from broccoli_server.content import ContentStore


class OneOffJobContext(metaclass=ABCMeta):
    @abstractmethod
    def logger(self) -> logging.Logger:
        pass

    @abstractmethod
    def content_store(self) -> ContentStore:
        pass

    @abstractmethod
    def drain_log_lines(self) -> List[str]:
        pass
