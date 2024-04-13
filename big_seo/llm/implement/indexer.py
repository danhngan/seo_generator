from big_seo.llm.indexer import (IIndexer,
                                 IndexMapperCell,
                                 IParser
                                 )

from big_seo.llm.core.data_model import (Document)
from big_seo.llm.implement.data_model import (Base,
                                              InPageCollection,
                                              UpToDateCollection)


from html.parser import HTMLParser
from bs4 import BeautifulSoup

from big_seo.llm.embedding_model import (IEmbedding)

from qdrant_client.http.models import (Distance,
                                       VectorParams,
                                       PointStruct,
                                       NamedVector,
                                       ScoredPoint)
from big_seo.storage.qdrant import QdrantDB
from big_seo.storage.vector_db import IVectorDB


from abc import ABC, abstractmethod


import uuid


class BaseIndexer(IIndexer):

    def __init__(self, embedding_model: IEmbedding = None,
                 parser: IParser = None,
                 Base_model=None) -> None:

        self.embedding_model = embedding_model
        self.parser = parser
        self.Base_model = Base_model

    @abstractmethod
    def index(self):
        pass

    @abstractmethod
    def search(self):
        pass


class WebPageIndexer(BaseIndexer):
    def index(self):
        pass

    def search(self):
        pass


class InPageIndexer(BaseIndexer):
    def index(self, doc: Document):
        # TODO
        self.parser.feed(doc)
        outline = self.parser.parse()
        for o in outline:
            header_vec = self.embedding_model.get_embedding(o[0])
            content_vec = self.embedding_model.get_embedding(
                o[1].get_doc_content())

            # TODO make Collection dependency
            header_point = InPageCollection(point_id=str(uuid.uuid4()),
                                            vector=header_vec,
                                            doc=o[1])
            self.Base_model.add(header_point)
            content_point = InPageCollection(point_id=str(uuid.uuid4()),
                                             vector=content_vec,
                                             doc=o[1])
            self.Base_model.add(content_point)
            self.Base_model.commit()

    def search(self, prompt: str):
        vec = self.embedding_model.get_embedding(prompt)
        res = self.Base_model.query(InPageCollection, vector=vec)
        return [Base._convertor.convert_db_to_python_schema(item) for item in res]


class UpToDateInPageIndexer(BaseIndexer):
    def index(self, doc: Document):
        # TODO
        self.parser.feed(doc)
        outline = self.parser.parse()
        for o in outline:
            header_vec = self.embedding_model.get_embedding(o[0])
            content_vec = self.embedding_model.get_embedding(
                o[1].get_doc_content())

            # TODO make Collection dependency
            header_point = UpToDateCollection(point_id=str(uuid.uuid4()),
                                              vector=header_vec,
                                              doc=o[1])
            self.Base_model.add(header_point)
            content_point = UpToDateCollection(point_id=str(uuid.uuid4()),
                                               vector=content_vec,
                                               doc=o[1])
            self.Base_model.add(content_point)
            self.Base_model.commit()

    def search(self, prompt: str):
        vec = self.embedding_model.get_embedding(prompt)
        res = self.Base_model.query(UpToDateCollection, vector=vec)
        return [Base._convertor.convert_db_to_python_schema(item) for item in res]
