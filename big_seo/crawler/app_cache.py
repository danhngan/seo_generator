from abc import ABC, abstractmethod

from datetime import datetime


class IAppCache(ABC):
    @abstractmethod
    def get(self, **key):
        pass

    @abstractmethod
    def set(self, dict_map: dict):
        pass


class KeywordAppCache(IAppCache):
    def __init__(self):
        self.cache = {}

    def get_last_time(self, *, keyword, n, **kwargs):
        return datetime.fromtimestamp(0)

    def get(self, *, keyword, n, **kwargs):
        return {}

    def set(self, key, value):
        return {}
