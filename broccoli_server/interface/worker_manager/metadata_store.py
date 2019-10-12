from abc import ABCMeta, abstractmethod


class MetadataStore(metaclass=ABCMeta):
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value):
        pass

    @abstractmethod
    def get_from_another_worker(self, worker_id: str, key: str):
        pass

    @abstractmethod
    def exists_in_another_worker(self, worker_id: str, key: str):
        pass
