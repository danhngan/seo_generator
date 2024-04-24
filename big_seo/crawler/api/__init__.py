from big_seo.crawler.search_engine import (GoogleCSE,
                                           GoogleCSEParser,
                                           UpToDateSEParser,
                                           UpToDateSE)
from big_seo.crawler.proxy_service import NoneProxy
from big_seo.crawler.selenium_proxy import SeleniumProxy
from big_seo.storage.db_io import (NoneDBWebPageDataController,
                                   MongoWebPageDataController,
                                   connect_db)
from big_seo.storage.mongo_data_model import WebPageMongo

from big_seo.crawler.app import GGCrawler, DirectUrlCrawler, UpToDateCrawler as U2DCrawlerBackEnd
from dotenv import load_dotenv
import sys
import os
import uuid

load_dotenv(r'D:\workspace\engineering\seo_creator\.env')


class Crawler:
    def __init__(self):
        self.proxy = NoneProxy()
        connect_db()
        self.web_page_data_controller = MongoWebPageDataController()
        self.search_engine = GoogleCSE(proxy=self.proxy,
                                       parser=GoogleCSEParser(),
                                       web_page_data_controller=self.web_page_data_controller)

        self.crawler = GGCrawler(search_engine=self.search_engine,
                                 db_io_controller=self.web_page_data_controller,
                                 proxy=self.proxy)

    def search(self, q: str, n: int):
        return self.crawler.crawl(keyword=q, number_of_pages=n)


class DirectCrawler:
    def __init__(self):
        self.proxy = NoneProxy()
        connect_db()
        self.webpage_data_controller = MongoWebPageDataController()

        self.crawler = DirectUrlCrawler(
            db_io_controller=self.webpage_data_controller,
            webpage_data_controller=self.webpage_data_controller,
            proxy=self.proxy)

    def search(self, urls: list[str]):
        return self.crawler.crawl(urls=urls)


class UpToDateCrawler:
    def __init__(self) -> None:
        self.selenium_proxy = SeleniumProxy()
        self.proxy = NoneProxy()
        connect_db()
        self.web_page_data_controller = MongoWebPageDataController()
        self.search_engine = UpToDateSE(proxy=self.proxy,
                                        parser=UpToDateSEParser(),
                                        web_page_data_controller=self.web_page_data_controller)

        self.crawler = U2DCrawlerBackEnd(search_engine=self.search_engine,
                                         db_io_controller=self.web_page_data_controller,
                                         proxy=self.selenium_proxy)

    def search(self, q: str, n: int):
        return self.crawler.crawl(keyword=q, number_of_pages=n)
