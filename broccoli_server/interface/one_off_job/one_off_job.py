from abc import ABCMeta, abstractmethod
from .one_off_job_context import OneOffJobContext


class OneOffJob(metaclass=ABCMeta):
    @abstractmethod
    def work(self, context: OneOffJobContext):
        pass
