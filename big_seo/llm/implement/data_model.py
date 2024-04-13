from big_seo.llm.core.data_model import (Document,
                                         BaseVectorStoreModel,
                                         VectorDBField,
                                         SchemaConvertor,
                                         declare_online_model_base)


from big_seo.storage.vector_db import (IVectorDB,
                                       VectorDBField,
                                       IVectorDBCollection,
                                       BaseDataType)
import big_seo.storage.vector_db as vector_db_type

from big_seo.crawler.core import WebPage
from big_seo.common.lang import DocumentLang

from qdrant_client.http import models

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


class OutlineDocumentDBType(BaseDataType, Document):
    def __init__(self, header: str = None, content: str = None, doc_id: bytes = None, doc_lang=DocumentLang.VI, doc: Document = None):
        if not doc_id:
            doc_id = uuid.uuid4().bytes

        if doc is not None \
                and hasattr(doc, 'header') \
                and hasattr(doc, 'content') \
                and hasattr(doc, 'doc_id') \
                and hasattr(doc, 'doc_lang'):
            self.header = doc.header
            self.content = doc.content
            self.doc_id = doc.doc_id
            self.doc_lang = doc.doc_lang
        else:
            self.header = header
            self.content = content
            self.doc_id = doc_id
            self.doc_lang = doc_lang

        # TODO
        self.meta_data = header

    def get_doc_content(self):
        if self.content is not None:
            return self.content
        else:
            return ''

    def get_doc_meta(self):
        # TODO
        return {'header': self.header}

    def to_native_format(self):
        doc_data = {}
        doc_data['header'] = self.header
        doc_data['content'] = self.get_doc_content()
        doc_data['doc_id'] = str(uuid.UUID(bytes=self.doc_id))
        doc_data['doc_lang'] = str(self.doc_lang)

        return doc_data

    @staticmethod
    def to_object_format(db_data):
        obj_data = {
            'header': db_data['header'],
            'content': db_data['content'],
            'doc_id': uuid.UUID(db_data['doc_id']).bytes,
            'doc_lang': db_data['doc_lang']
        }
        return OutlineDocumentDBType(**obj_data)

    def __call__(self, *args, **kwargs):
        return OutlineDocumentDBType(*args, **kwargs)


class QdrantConvertor(SchemaConvertor):

    def convert_python_to_db_schema(self, collection_model):
        schema = {'collection_name': collection_model._collection().to_native_format(),
                  'vectors_config': {}}
        for attr in collection_model.__dict__:
            if attr.startswith('_'):
                continue
            elif isinstance(collection_model.__dict__[attr], VectorDBField):
                if isinstance(collection_model.__dict__[attr].field_type, vector_db_type.VectorType):
                    schema['vectors_config'][collection_model.__dict__[attr].field_name] = models.VectorParams(
                        size=collection_model.__dict__[attr].field_type.vec_length, distance=models.Distance.DOT)
        return schema

    def convert_db_to_python_schema(self, val: models.ScoredPoint):
        # TODO
        doc = val.payload['doc']
        doc_id = uuid.UUID(doc['doc_id']).bytes
        header = doc['header']
        content = doc['content']
        doc_lang = DocumentLang.get_lang_from_abbrev(doc['doc_lang'])
        return (val.score, InPageCollection(point_id=val.id,
                                            vector=InPageCollection.vector.field_type(
                                                val.vector),
                                            doc=OutlineDocumentDBType(doc_id=doc_id,
                                                                      header=header,
                                                                      content=content,
                                                                      doc_lang=doc_lang)))

    def check_db_schema(self, one, two) -> bool:
        # TODO
        return True

    def convert_python_to_point(self, val):
        # TODO
        point_id = val.kwargs['point_id']
        vector = {'in_page': val.kwargs['vector']}
        payload = {'doc': val.kwargs['doc'].to_native_format()}
        return {'_id': point_id,
                'vector': vector,
                'payload': payload}


Base = declare_online_model_base(QdrantConvertor())


class InPageCollection(metaclass=Base):
    _collection = VectorDBField(
        field_name=None, field_type=vector_db_type.String, default_val='in_page')
    point_id = VectorDBField(
        'id', field_type=vector_db_type.String, default_val=str(uuid.uuid4()))
    vector = VectorDBField(
        'in_page', field_type=vector_db_type.VectorType(1024))
    doc = VectorDBField('doc', field_type=OutlineDocumentDBType)

    _meta: dict = None

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


class UpToDateCollection(metaclass=Base):
    _collection = VectorDBField(
        field_name=None, field_type=vector_db_type.String, default_val='up_to_date')
    point_id = VectorDBField(
        'id', field_type=vector_db_type.String, default_val=str(uuid.uuid4()))
    vector = VectorDBField(
        'in_page', field_type=vector_db_type.VectorType(1024))
    doc = VectorDBField('doc', field_type=OutlineDocumentDBType)

    _meta: dict = None

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
