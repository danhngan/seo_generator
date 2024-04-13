"""create multiple vector indexes for each doc based on multi-factor such as title, keywords, content, problem"""


from dataclasses import dataclass
from abc import ABC, abstractmethod
from big_seo.llm_arch.core.common import Document
from big_seo.llm_arch.embedding_model import IEmbedding
from big_seo.storage.vector_db import IVectorDB


class IParser(ABC):
    @abstractmethod
    def feed(self, doc: Document) -> None:
        pass

    @abstractmethod
    def parse(self) -> list[tuple[str, Document]]:
        pass


class IndexMapperCell:
    # TODO: implement
    _id: bytes
    vec: list
    doc: Document

    def get_doc(self) -> Document:
        return self.doc

    @abstractmethod
    def get_doc_meta(self) -> dict:
        pass


class IIndexer(ABC):
    embedding_model: IEmbedding = None
    parser: IParser = None
    db_config: dict

    @abstractmethod
    def index(self, doc: Document):
        """save"""
        pass

    @abstractmethod
    def search(self) -> list[IndexMapperCell]:
        pass
