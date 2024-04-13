from abc import ABC, abstractmethod
from big_seo.common.rest import Response
from big_seo.common.error import NotSupported
from datetime import datetime, timedelta
import time


import requests


class IProxy(ABC):
    @abstractmethod
    def request(self) -> Response:
        pass


class SingletonProxyMeta(type, IProxy):
    """
    Using singleton for restrict proxy instances
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def request(self) -> Response:
        pass


class NoneProxy(metaclass=SingletonProxyMeta):
    # minimum interval between 2 request in second
    min_interval = timedelta(seconds=0.5)
    last_request_time = datetime.fromtimestamp(0)

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
        res = requests.get(url=url,
                           params=params,
                           stream=stream)
        return Response(status_code=res.status_code,
                        text=res.text,
                        raw_data=res.raw.data)

    def set_interval(self, interval_in_second: float):
        self.min_interval = timedelta(seconds=interval_in_second)
