from big_seo.llm_arch.indexer import (IIndexer,
                                      IIndexMapper,
                                      IIndexMapperCell,
                                      IParser,
                                      IIndexMapperCreator
                                      )

from big_seo.llm_arch.core.common import Document
from big_seo.common.lang import DocumentLang


from html.parser import HTMLParser
from bs4 import BeautifulSoup

from big_seo.llm_arch.embedding_model import (IEmbedding)
from big_seo.crawler.core import (WebPage)

from qdrant_client.http.models import (Distance,
                                       VectorParams,
                                       PointStruct,
                                       NamedVector,
                                       ScoredPoint)
from big_seo.storage.qdrant import QdrantDB
from big_seo.storage.vector_db import IVectorDB


import uuid


class WebPageDocument(Document):
    def __init__(self, webpage: WebPage, doc_id=None, doc_lang=DocumentLang.VI):
        if not doc_id:
            doc_id = uuid.uuid4().bytes
        self.webpage = webpage
        self.doc_id = doc_id
        self.doc_lang = doc_lang

        # TODO
        self.meta_data = webpage.title

    def get_doc_content(self):
        if not self.webpage.full_content or len(self.webpage.full_content) == 0:
            self.webpage.full_content = self._get_doc_from_storage()
        return self.webpage.full_content

    def get_doc_meta(self):
        # TODO
        return self.meta_data

    def _get_doc_from_storage(self):
        # TODO
        return self.webpage.full_content


class OutlineDocument(Document):
    def __init__(self, header: str, content: str, doc_id: bytes = None, doc_lang=DocumentLang.VI):
        if not doc_id:
            doc_id = uuid.uuid4().bytes
        self.header = header
        self.content = content
        self.doc_id = doc_id
        self.doc_lang = doc_lang

        # TODO
        self.meta_data = header

    def get_doc_content(self):
        if self.content:
            return self.content
        else:
            return self._get_doc_from_storage()

    def get_doc_meta(self):
        # TODO
        return {'header': self.header}

    def _get_doc_from_storage(self):
        # TODO
        return self.content


class WebPageIndexer(IIndexer):
    def __init__(self, embedding_model: IEmbedding,
                 parser: IParser,
                 index_mapper_creator: IIndexMapperCreator):
        self.embedding_model = embedding_model
        self.parser = parser
        self.index_mapper_creator = index_mapper_creator
        self.index_mapper: IIndexMapper = self.index_mapper_creator.create()
        self.vec_db: IVectorDB = self.index_mapper_creator.get_vector_db()

    def invoke(self, doc: list[Document]) -> IIndexMapper:
        # TODO
        self.parser.feed(doc)
        outline = self.parser.parse()
        self.vec_db.add_batch(data=map(lambda x: (str(uuid.uuid4()), self.index_mapper_creator.get_db_familiar_vector(vec=self.embedding_model.get_embedding(x[0])),
                                                  {'doc_id': str(uuid.UUID(bytes=x[1].doc_id)),
                                                   'full_content': x[1].get_doc_content(),
                                                   'type': 'full_page',
                                                   'header': x[0]}), outline))

    def get_index_mapper(self):
        return self.index_mapper


class InPageIndexer(WebPageIndexer):
    def invoke(self, doc: Document) -> IIndexMapper:
        # TODO
        self.parser.feed(doc)
        outline = self.parser.parse()
        data = []
        for o in outline:
            outline_id = str(uuid.uuid4())
            header_vec = self.index_mapper_creator.get_db_familiar_vector(
                vec=self.embedding_model.get_embedding(o[0]))
            content_vec = self.index_mapper_creator.get_db_familiar_vector(
                vec=self.embedding_model.get_embedding(o[1].get_doc_content()))
            data.append((str(uuid.uuid4()),
                         header_vec,
                         {'doc_id': outline_id,
                          'full_content': o[1].get_doc_content(),
                          'type': 'in_page',
                          'header': o[0]}
                         ))
            data.append((str(uuid.uuid4()),
                         content_vec,
                         {'doc_id': outline_id,
                          'full_content': o[1].get_doc_content(),
                          'type': 'in_page',
                          'header': o[0]}
                         ))
        self.vec_db.add_batch(data=data)
        return self.index_mapper


class UpToDateInPageIndexer(WebPageIndexer):
    def invoke(self, doc: Document) -> IIndexMapper:
        # TODO
        self.parser.feed(doc)
        outline = self.parser.parse()
        data = []
        for o in outline:
            outline_id = str(uuid.uuid4())
            header_vec = self.index_mapper_creator.get_db_familiar_vector(
                vec=self.embedding_model.get_embedding(o[0]))
            content_vec = self.index_mapper_creator.get_db_familiar_vector(
                vec=self.embedding_model.get_embedding(o[1].get_doc_content()))
            data.append((str(uuid.uuid4()),
                         header_vec,
                         {'doc_id': outline_id,
                          'full_content': o[1].get_doc_content(),
                          'type': 'in_page',
                          'header': o[0]}
                         ))
            data.append((str(uuid.uuid4()),
                         content_vec,
                         {'doc_id': outline_id,
                          'full_content': o[1].get_doc_content(),
                          'type': 'in_page',
                          'header': o[0]}
                         ))
        self.vec_db.add_batch(data=data)
        return self.index_mapper
