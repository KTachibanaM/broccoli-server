import queue
import logging.handlers
from typing import List
from broccoli_server.content import ContentStore
from broccoli_server.interface.job import JobContext


class JobContextImpl(JobContext):
    def __init__(self, job_id: str, content_store: ContentStore):
        # still need the prefix to globally configure logging for all broccoli workers
        self._logger = logging.getLogger(f"broccoli.job.{job_id}")
        self.q = queue.SimpleQueue()
        mem_handler = logging.handlers.QueueHandler(self.q)
        self._logger.addHandler(mem_handler)
        self._content_store = content_store

    def logger(self) -> logging.Logger:
        return self._logger

    def content_store(self) -> ContentStore:
        return self._content_store

    def drain_log_lines(self) -> List[str]:
        lines = []
        while not self.q.empty():
            lines.append(self.q.get().getMessage())
        return lines
