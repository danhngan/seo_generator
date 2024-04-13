from abc import ABC, abstractmethod

from big_seo.crawler.core import WebPage, WebPageDataController
from big_seo.crawler.search_engine import ISearchEngine
from big_seo.crawler.proxy_service import IProxy
from big_seo.storage.db_io import IOController

import uuid
from datetime import datetime


# crawler interface


class ICrawler(ABC):
    search_engine: ISearchEngine
    db_io_controller: IOController

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def dumps_to_db(self):
        pass


# crawler class

class AbstractSimpleCrawler(ICrawler):
    def __init__(self, *, search_engine: ISearchEngine, db_io_controller: IOController, proxy: IProxy):
        self.search_engine = search_engine
        self.db_io_controller = db_io_controller
        self.proxy = proxy

    @abstractmethod
    def crawl(self):
        pass

    def _get_full_result_content(self, result: WebPage, stream=False) -> None:
        """return None, update input full_content instead"""
        res = self.proxy.request('get', result.url, stream=stream)
        if res.status_code == 200:
            result.full_content = res.text
        return None

    def dumps_to_db(self, result: WebPage):
        self.db_io_controller.dumps_to_db(result)


class GGCrawler(AbstractSimpleCrawler):

    def crawl(self, keyword, number_of_pages=3, get_full_content: bool = True):
        """max 10 pages"""
        results = self.search_engine.get_top_seo(
            keyword, min(10, number_of_pages))

        for result in results:
            if get_full_content:
                self._get_full_result_content(result)
            self.dumps_to_db(result)
        return results


class DirectUrlCrawler(AbstractSimpleCrawler):
    def __init__(self, *, db_io_controller: IOController, proxy: IProxy, webpage_data_controller: WebPageDataController):
        self.db_io_controller = db_io_controller
        self.proxy = proxy
        self.webpage_data_controller = webpage_data_controller

    def crawl(self, url: str):
        if not DirectUrlCrawler.check_valid_url(url):
            raise TypeError('not a url')
        page = self.webpage_data_controller.create(page_id=uuid.uuid4().bytes,
                                                   url=url,
                                                   domain=url.split('/')[2],
                                                   title=url,
                                                   ingestion_time=datetime.now(),
                                                   full_content='',
                                                   headings='{}',
                                                   main_content='',
                                                   keywords=[''],
                                                   rank=0)
        self._get_full_result_content(page)
        return [page]

    @classmethod
    def check_valid_url(url: str):
        if isinstance(url, str) \
                and url.startswith('http') \
                and len(url.split('/')) > 2:
            return True
        return False


class UpToDateCrawler(AbstractSimpleCrawler):
    def crawl(self, keyword, number_of_pages=3, get_full_content: bool = True):
        """max 10 pages"""
        results = self.search_engine.get_top_seo(
            keyword, min(10, number_of_pages))

        for result in results:
            if get_full_content:
                self._get_full_result_content(result, stream=True)
            self.dumps_to_db(result)
        if hasattr(self.proxy, 'close'):
            self.proxy.close()
        return results
