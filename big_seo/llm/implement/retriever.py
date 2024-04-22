from abc import ABC, abstractmethod

from big_seo.llm.retriever import IRetriever
from big_seo.llm.indexer import (IEmbedding,
                                 IIndexer)

from big_seo.llm.core.common import IPrompt, Document


class HashableIndexMapperCellDocID(IIndexMapperCell):
    def __init__(self, index_mapper_cell: IIndexMapperCell) -> None:
        self.index_mapper_cell = index_mapper_cell

    def get_doc(self) -> Document:
        self.index_mapper_cell.get_doc()

    def get_doc_meta(self) -> dict:
        self.index_mapper_cell.get_doc_meta()

    def __hash__(self) -> int:
        return hash(self.get_doc().doc_id)

    def __eq__(self, obj: IIndexMapperCell) -> bool:
        return hash(self.get_doc().doc_id) == hash(obj.get_doc().doc_id)


class BaseRetriever(IRetriever):
    @abstractmethod
    def invoke(self, prompt: IPrompt, limit=5) -> IIndexMapper:
        pass

    def _get_unique_retrieved_docs(self, retrieved_docs: list[IIndexMapperCell]):
        docs = set([HashableIndexMapperCellDocID(mapper_cell)
                   for mapper_cell in retrieved_docs])
        return docs


class DirectRetriever(BaseRetriever):
    def __init__(self, embedding_model: IEmbedding,
                 indexer: IIndexer,
                 index_mapper_creator: IIndexMapperCreator):
        self.embedding_model = embedding_model
        self.indexer = indexer
        self.index_mapper_creator = index_mapper_creator

    def invoke(self, prompt: IPrompt, limit=5) -> set[IIndexMapperCell]:
        vec = self.embedding_model.get_embedding(prompt.get_prompt())
        db_vec = self.index_mapper_creator.get_db_familiar_vector(
            vec=vec, get=True)
        retrieved_docs: list[IIndexMapperCell] = self.indexer.get_index_mapper(
        ).search_doc(vec=db_vec, limit=limit)
        return self._get_unique_retrieved_docs(retrieved_docs)
