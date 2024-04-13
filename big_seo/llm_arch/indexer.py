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


class IIndexMapperCell(ABC):
    # TODO: implement
    _id: bytes
    vec: list

    @abstractmethod
    def get_doc(self) -> Document:
        pass

    @abstractmethod
    def get_doc_meta(self) -> dict:
        pass


class IIndexMapper(ABC):

    @abstractmethod
    def search_doc(self, vec, limit) -> list[IIndexMapperCell]:
        pass


class IIndexer(ABC):
    embedding_model: IEmbedding = None
    parser: IParser = None

    @abstractmethod
    def invoke(self, doc: Document) -> IIndexMapper:
        """save"""
        pass

    @abstractmethod
    def get_index_mapper(self) -> IIndexMapper:
        pass


class IIndexMapperCreator(ABC):
    @abstractmethod
    def create(self) -> IIndexMapper:
        pass

    def get_vector_db(self) -> IVectorDB:
        pass

    def get_embedding_model(self) -> IEmbedding:
        pass

    def get_db_familiar_vector(self, vec: list, get: bool):
        pass
