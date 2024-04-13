from abc import ABC, abstractmethod
from big_seo.crawler.core import WebPageDataController, WebPage
from big_seo.storage.mongo_data_model import WebPageMongo, connect_db


class IOController(ABC):
    @abstractmethod
    def dumps_to_db(self):
        pass

    @abstractmethod
    def read_from_db(self):
        pass


class DemoWebPage(WebPage):
    def to_dict(self):
        return {
            'url': self.url,
            'domain': self.domain,
            'ingestion_time': self.ingestion_time,
            'key_words': self.keywords,
            'full_content': self.full_content[:100]
        }


class NoneDBWebPageDataController(WebPageDataController, IOController):
    """For testing purposes only"""

    def create(self, **data) -> WebPage:
        return DemoWebPage(**data)

    def dumps_to_db(self, data: WebPage, metadata_only=False) -> None:
        print('OK', data.page_id)

    def read_from_db(self, metadata_only=False) -> WebPage:
        return {'ok': ''}


class MongoWebPageDataController(WebPageDataController, IOController):
    """For testing purposes only"""

    def create(self, **data) -> WebPage:
        return WebPageMongo(**data)

    def dumps_to_db(self, data: WebPageMongo, metadata_only=False) -> None:
        return data.save()

    def read_from_db(self, domain) -> WebPage:
        return WebPageMongo.objects(domain=domain)
