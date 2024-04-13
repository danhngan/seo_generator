from dataclasses import dataclass
from abc import ABC, abstractmethod
from big_seo.llm_arch.indexer import (IIndexMapper,
                                      IIndexMapperCreator,
                                      IIndexer,
                                      IIndexMapperCell)
from big_seo.llm_arch.embedding_model import IEmbedding
from big_seo.llm_arch.core.common import IPrompt


@dataclass
class IRetriever(ABC):
    embedding_model: IEmbedding
    indexer: IIndexer

    @abstractmethod
    def invoke(self, prompt: IPrompt, n: int) -> set[IIndexMapperCell]:
        pass
