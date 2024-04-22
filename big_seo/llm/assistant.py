from dataclasses import dataclass
from abc import ABC, abstractmethod

from big_seo.llm.retriever import IRetriever
from big_seo.llm.llmodel import ILLModel
from big_seo.llm.embedding_model import IEmbedding


class IAssistant(ABC):
    llmodel: ILLModel = None
    retrievers: list[IRetriever] = None
    system_instructions: list[str] = None

    @abstractmethod
    def invoke(self, text: str) -> list:
        pass

    @abstractmethod
    def sake(self, **kwargs):
        pass
