from abc import ABC, abstractmethod
from datetime import datetime

from big_seo.storage.db_io import IOController


class IKeywordCacheSearch(ABC):
    keyword_io_controller: IOController

    @abstractmethod
    def get_latest_search_time(self, keyword, n):
        pass

    @abstractmethod
    def get_cache_result(self, keyword, n):
        pass


class KeywordCacheSearch(IKeywordCacheSearch):
    def __init__(self, keyword_io_controller: IOController) -> None:
        self.keyword_io_controller = keyword_io_controller

    def get_latest_search_time(self, keyword):
        return datetime.fromtimestamp(0)

    def get_cache_result(self, keyword, n):
        return self.keyword_io_controller.read_from_db(keyword)
