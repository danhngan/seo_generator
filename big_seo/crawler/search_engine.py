from abc import ABC, abstractmethod
from big_seo.crawler.proxy_service import IProxy
from big_seo.crawler.core import WebPage, WebPageDataController
from big_seo.crawler.constants import *


import os
import uuid
import json
from datetime import datetime, timedelta


class ISearchEngine(ABC):
    proxy: IProxy
    base_se_url: str

    @abstractmethod
    def get_top_seo(self, keyword, n) -> list[WebPage]:
        pass


class GoogleCSEParser:
    def parse(self, search_result, web_page_data_controller: WebPageDataController) -> WebPage:
        res = json.loads(search_result.text)
        pages = res['items']

        for page in pages:
            yield web_page_data_controller.create(page_id=uuid.uuid4().bytes,
                                                  url=page['link'],
                                                  domain=page['link'].split(
                                                      '/')[2],
                                                  title=page['title'],
                                                  ingestion_time=datetime.now(),
                                                  full_content='',
                                                  headings='{}',
                                                  main_content='',
                                                  keywords=[
                                                      res['queries']['request'][0]['searchTerms']],
                                                  rank=0)


class GoogleCSE(ISearchEngine):
    """Google custom search engine"""

    def __init__(self, proxy: IProxy,
                 parser: GoogleCSEParser,
                 web_page_data_controller: WebPageDataController) -> None:
        self.proxy = proxy
        self.parser = parser
        self.web_page_data_controller = web_page_data_controller
        self.base_se_url = GOOGLE_SEARCH_BASE_URL

    def get_top_seo(self, keyword, n) -> list[WebPage]:
        search_result = self.proxy.request(method='get',
                                           url=self.base_se_url,
                                           params=self.__gen_url_params(keyword=keyword, n=n))
        res = []
        for page in self.parser.parse(search_result, web_page_data_controller=self.web_page_data_controller):
            res.append(page)
        return res

    @staticmethod
    def __gen_url_params(keyword, n):
        """maximum 10 results"""
        return {'q': keyword,
                'key': os.environ.get('GG_CUSTOM_SEARCH_API_KEY'),
                'cx': os.environ.get('GG_CUSTOM_SEARCH_ENGINE_ID'),
                'num': min(10, n)}


class UpToDateSEParser:
    def parse(self, search_result, web_page_data_controller: WebPageDataController) -> WebPage:
        res = json.loads(search_result.text)
        search_res = res['data']['searchResults']
        url_prefix = 'https://www.uptodate.com'

        for res in search_res:
            if 'searchResults' not in res:
                continue
            page = res['searchResults'][0]
            yield web_page_data_controller.create(page_id=uuid.uuid4().bytes,
                                                  url=url_prefix +
                                                  page['url'].split('?')[0],
                                                  domain='www.uptodate.com',
                                                  title=page['title'],
                                                  ingestion_time=datetime.now(),
                                                  full_content='',
                                                  headings='{}',
                                                  main_content='',
                                                  keywords=[],
                                                  rank=0)


class UpToDateSE(ISearchEngine):
    """Google custom search engine"""

    def __init__(self, proxy: IProxy,
                 parser: UpToDateSEParser,
                 web_page_data_controller: WebPageDataController) -> None:
        self.proxy = proxy
        self.parser = parser
        self.web_page_data_controller = web_page_data_controller
        self.base_se_url = UPTODATE_SEARCH_BASE_URL

    def get_top_seo(self, keyword, n) -> list[WebPage]:
        search_result = self.proxy.request(method='get',
                                           url=self.base_se_url,
                                           params=self._gen_url_params(keyword=keyword, n=n))
        res = []
        for page in self.parser.parse(search_result, web_page_data_controller=self.web_page_data_controller):
            page.keywords.append(keyword)
            res.append(page)
        return res

    @staticmethod
    def _gen_url_params(keyword, n):
        """maximum 10 results"""
        return {'search': keyword,
                'sp': 0,
                'searchType': 'PLAIN_TEXT',
                'source': 'USER_INPUT',
                'searchControl': 'TOP_PULLDOWN',
                'searchOffset': 1,
                'autoComplete': 'true',
                'language': 'en',
                'max': min(10, n),
                'index': '',
                'autoCompleteTerm': ''}
