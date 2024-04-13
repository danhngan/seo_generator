from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass
class WebPage:
    page_id: bytes
    url: str
    domain: str
    title: str
    ingestion_time: datetime
    full_content: str
    headings: dict
    main_content: str
    keywords: list[str]
    rank: int


class WebPageDataController(ABC):
    @abstractmethod
    def create(self) -> WebPage:
        pass
