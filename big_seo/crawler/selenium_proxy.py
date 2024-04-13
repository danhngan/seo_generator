from abc import ABC, abstractmethod
from big_seo.common.rest import Response
from big_seo.common.error import NotSupported
from datetime import datetime, timedelta
import urllib
from big_seo.crawler.proxy_service import IProxy, SingletonProxyMeta
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class SeleniumProxy(metaclass=SingletonProxyMeta):
    # minimum interval between 2 request in second
    min_interval = timedelta(seconds=0.5)
    last_request_time = datetime.fromtimestamp(0)

    def __init__(self) -> None:
        self.driver = webdriver.Firefox()

    def request(self, method: str, url: str, params={}, stream=False) -> Response:
        while (datetime.now() - self.last_request_time) < self.min_interval:
            time.sleep(self.min_interval.total_seconds())
        if method == 'get':
            res = self.get(url=url, params=params, stream=stream)
            last_request_time = datetime.now()
            return res
        else:
            raise NotSupported(method)

    def get(self, url, params, stream) -> Response:
        res = self.driver.get(url=self.parse_url(url, params=params))
        res_content = self.driver.find_element(
            value='body', by=By.TAG_NAME).get_attribute("outerHTML")
        if not stream:
            self.driver.close()
        return Response(status_code=200,
                        text=res_content,
                        raw_data=b'')

    def parse_url(self, url, params: dict):
        if len(params) > 0:
            return url + '?' + urllib.parse.urlencode(params)
        else:
            return url

    def close(self):
        self.driver.close()

    def set_interval(self, interval_in_second: float):
        self.min_interval = timedelta(seconds=interval_in_second)
