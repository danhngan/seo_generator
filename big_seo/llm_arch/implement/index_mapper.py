import uuid
from big_seo.llm_arch.indexer import (IIndexMapper,
                                      IIndexMapperCell,
                                      IParser,
                                      IIndexMapperCreator
                                      )
from big_seo.llm_arch.implement.indexer import (WebPageDocument,
                                                OutlineDocument)

from big_seo.llm_arch.core.common import (Document)

from qdrant_client.http.models import (Distance,
                                       VectorParams,
                                       PointStruct,
                                       NamedVector,
                                       ScoredPoint)

from big_seo.storage.qdrant import QdrantDB
from big_seo.storage.vector_db import IVectorDB


class WebPageMapperCell(IIndexMapperCell):
    def __init__(self, vec: list, webpage_meta, _id: bytes = None):
        if not _id:
            self._id = uuid.uuid4().bytes
        else:
            self._id = _id
        self.vec = vec
        self.webpage_meta = webpage_meta

    def get_doc(self) -> Document:
        return self.webpage_meta['full_content']

    def get_doc_meta(self) -> dict:
        return {'title': self.webpage_meta['header']}

    def get_vec(self) -> list:
        return self.vec


class OutlineMapperCell(IIndexMapperCell):
    def __init__(self, vec: list, outline_meta, _id: bytes = None):
        if not _id:
            self._id = uuid.uuid4().bytes
        else:
            self._id = _id
        self.vec = vec
        self.outline_meta = outline_meta
        self.doc = OutlineDocument(header=self.outline_meta['header'],
                                   content=self.outline_meta['full_content'],
                                   doc_id=uuid.UUID(self.outline_meta['doc_id']).bytes)

    def get_doc(self) -> Document:
        return self.doc

    def get_doc_meta(self) -> dict:
        return {'title': self.outline_meta['header']}

    def get_vec(self) -> list:
        return self.vec


class WebPageIndexMapperCellCreator:

    def create(self, point: ScoredPoint) -> IIndexMapperCell:
        point_id = point.id
        vector = point.vector
        payload = point.payload
        return WebPageMapperCell(vector, payload, point_id)


class OutlineIndexMapperCellCreator:
    def __init__(self, in_doc: bool = True):
        self.in_doc = in_doc

    def create(self, point: ScoredPoint) -> IIndexMapperCell:
        point_id = point.id
        vector = point.vector
        payload = point.payload
        return OutlineMapperCell(vector, payload, uuid.UUID(payload['doc_id']).bytes)


class SimpleQdrantHuggingFaceIndexMapperCreator(IIndexMapperCreator):

    def __init__(self, in_doc=False):
        self.in_doc = in_doc
        if self.in_doc:
            self.vec_name = 'headline'
            self.host = "localhost"
            self.collection = 'in_page_collection'
        else:
            self.vec_name = 'concat_headline'
            self.host = 'localhost'
            self.collection = 'webpage_collection'
        self.port = 6333

        self.vectors_config = {self.vec_name: VectorParams(
            size=1024, distance=Distance.DOT)}

        self.vec_db = None

    def set_collection(self, collection):
        self.collection = collection

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def get_db_familiar_vector(self, vec, get=False):
        if get:
            return NamedVector(name=self.vec_name, vector=vec)
        return {self.vec_name: vec}

    def get_vector_db(self) -> IVectorDB:
        if not self.vec_db:
            self.vec_db = self._create_vector_db()
        return self.vec_db

    def _create_vector_db(self) -> IVectorDB:
        return QdrantDB(host=self.host,
                        port=self.port,
                        vectors_config=self.vectors_config,
                        collection=self.collection)

    def create(self) -> IIndexMapper:
        if self.in_doc:
            mapper_cell_creator = OutlineIndexMapperCellCreator()
        else:
            mapper_cell_creator = WebPageIndexMapperCellCreator()

        vec_db = self.get_vector_db()
        if self.in_doc:
            vec_db.connect()
            vec_db.remove('*')
        return QdrantHuggingFaceIndexMapper(in_doc=self.in_doc, vec_db=vec_db,
                                            mapper_cell_creator=mapper_cell_creator)


class QdrantHuggingFaceIndexMapper(IIndexMapper):
    def __init__(self, vec_db: IVectorDB, in_doc=False, mapper_cell_creator=None):
        self.in_doc = in_doc
        self.vec_db = vec_db
        self.vec_db.connect()
        self.mapper_cell_creator = mapper_cell_creator

    def search_doc(self, vec, limit=10) -> list[IIndexMapperCell]:
        res = self.vec_db.get(vec, limit=limit)

        return [self.mapper_cell_creator.create(point) for point in res]
