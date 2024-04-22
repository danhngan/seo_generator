from dataclasses import dataclass
from abc import ABC, abstractmethod
from big_seo.llm.indexer import (IIndexer)
from big_seo.llm.embedding_model import IEmbedding
from big_seo.llm.core.common import IPrompt


@dataclass
class IRetriever(ABC):
    embedding_model: IEmbedding
    indexer: IIndexer

    @abstractmethod
    def invoke(self, prompt: IPrompt, n: int):
        pass
