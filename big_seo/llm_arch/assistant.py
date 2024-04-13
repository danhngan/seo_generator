from dataclasses import dataclass
from abc import ABC, abstractmethod

from big_seo.llm_arch.retriever import IRetriever
from big_seo.llm_arch.llmodel import ILLModel
from big_seo.llm_arch.embedding_model import IEmbedding


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
