from big_seo.storage.vector_db import IVectorDB, IVectorDBCollection
from big_seo.llm.core.data_model import (BaseDataType,
                                         BaseVectorStoreModel)
from qdrant_client import QdrantClient
from qdrant_client.http.models import (Distance,
                                       VectorParams,
                                       PointStruct,
                                       PointIdsList,
                                       Filter,
                                       FilterSelector,
                                       IsNullCondition,
                                       FieldCondition,
                                       NamedVector)


import os

import uuid


class QdrantCollection(IVectorDBCollection):
    def __init__(self, client: QdrantClient, collection_name: str, schema) -> None:
        self.client = client
        self.collection_name = collection_name
        self.schema = schema

    def add(self, vector, payload, _id: int = None):
        """
        :param vec: vector, for named vectors, use {vec_name: vec_value}
        :param payload: payload
        """
        if not _id:
            _id = str(uuid.uuid4())
        point = PointStruct(
            id=_id,
            payload=payload,
            vector=vector
        )
        self._upsert([point])

    def add_batch(self, data):
        """
        :param data: list of (vec, payload)
        For named vectors, use {vec_name: vec_value}
        """
        points = []
        for id, vec, payload in data:
            point = PointStruct(
                id=id if id else str(uuid.uuid4()),
                payload=payload,
                vector=vec
            )
            points.append(point)
        self._upsert(points)

    def _upsert(self, points):
        return self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points
        )

    def remove(self, _id):
        self.client.delete(
            collection_name=self.collection_name,
            wait=True,
            points_selector=PointIdsList(
                points=[_id],
            ),
        )

    def search_vec(self, vector_name, vector_value, limit=10) -> list:
        """:param vec: dictionary of vector name and vector value"""
        named_vec = NamedVector(name=vector_name, vector=vector_value)
        search_result = self.client.search(
            collection_name=self.collection_name, query_vector=named_vec, limit=limit
        )
        return search_result


class QdrantDB(IVectorDB):
    def __init__(self, host: str = ":memory:",
                 port: int = 6333):
        self._id = uuid.uuid4().bytes
        self.host = host
        self.port = port
        if host == ":memory:":
            self.client = QdrantClient(
                location=self.host, port=self.port)
        else:
            self.client = QdrantClient(
                host=self.host, port=self.port)

    def connect(self):
        return True

    def create_collection(self, schema):
        collection_name = schema['collection_name']
        vectors_config = schema['vectors_config']
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config
        )

    def disconnect(self):
        self.client.close()

    def get_collection(self, collection_name, schema) -> IVectorDBCollection:
        try:
            self.client.get_collection(collection_name=collection_name)
        except:
            self.create_collection(schema=schema)
        return QdrantCollection(self.client, collection_name=collection_name, schema=schema)

    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name=collection_name)
