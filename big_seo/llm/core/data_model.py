from abc import ABC, abstractmethod
from big_seo.llm.core.common import Document
from dataclasses import dataclass

from big_seo.storage.vector_db import (IVectorDB,
                                       BaseDataType,
                                       VectorType,
                                       VectorDBField,
                                       IVectorDBCollection)
from enum import Enum

from datetime import datetime
import uuid


class SchemaConvertor:
    @abstractmethod
    def convert_python_to_db_schema(self, collection_model):
        pass

    @abstractmethod
    def convert_db_to_python_schema(self, val):
        pass

    @abstractmethod
    def check_db_schema(self, one, two) -> bool:
        pass

    @abstractmethod
    def convert_python_to_point(self, point):
        pass


class BaseVectorStoreModel(type):
    """subclass must also implement __init_subclass__"""
    __db_name__ = 'default'
    __name__ = __db_name__
    _object_collections: dict
    _storage_collections: dict
    _schema_handler: dict

    @staticmethod
    def init_instance(vec_db: IVectorDB):
        pass

    @staticmethod
    def query(vec_db: IVectorDB):
        pass

    @staticmethod
    def close_instance(vec_db: IVectorDB):
        pass

    @staticmethod
    def commit(vec_db: IVectorDB):
        pass

    @staticmethod
    def add(point):
        pass


def declare_online_model_base(convertor: SchemaConvertor, db_name='online'):
    class BaseOnlineDataModel(BaseVectorStoreModel):
        __db_name__ = db_name
        __name__ = __db_name__
        _object_collections: dict = {}
        _storage_collections: dict[str, IVectorDBCollection] = {}
        _convertor = convertor
        _vec_db = None
        _session_data = []

        def __init__(cls, name, bases, dct) -> None:
            collection_name = cls._collection().to_native_format() if hasattr(
                cls, '_collection') else name
            cls.__getitem__ = BaseOnlineDataModel.child_getitem_fn
            BaseOnlineDataModel._object_collections[collection_name] = cls

        @staticmethod
        def init_instance(vec_db: IVectorDB):
            BaseOnlineDataModel._vec_db = vec_db
            for collection in BaseOnlineDataModel._object_collections:
                schema = BaseOnlineDataModel._convertor.convert_python_to_db_schema(
                    BaseOnlineDataModel._object_collections[collection])
                BaseOnlineDataModel._storage_collections[collection] = vec_db.get_collection(
                    collection_name=collection, schema=schema)

        @staticmethod
        def query(collection_model, limit=10, **kwargs: dict[str, VectorType.python_type]):
            collection_name = collection_model._collection().to_native_format()
            assert len(kwargs) == 1, 'support only single vector search'
            vec = {}
            for k in kwargs:
                vec_val = getattr(collection_model, k)(
                    kwargs[k]).to_native_format()

            return BaseOnlineDataModel._storage_collections[collection_name].search_vec(vector_name=getattr(collection_model, k).field_name, vector_value=vec_val, limit=limit)

        @staticmethod
        def close_instance(delete_model=False):
            if delete_model:
                for collection in BaseOnlineDataModel._object_collections:
                    BaseOnlineDataModel._vec_db.delete_collection(collection)
            BaseOnlineDataModel._vec_db.disconnect()

        @staticmethod
        def add(point):
            BaseOnlineDataModel._session_data.append(point)
            if len(BaseOnlineDataModel._session_data) > 9:
                BaseOnlineDataModel.commit()
            return None

        @staticmethod
        def commit():
            for point in BaseOnlineDataModel._session_data:
                collection = BaseOnlineDataModel._storage_collections[point._collection(
                ).to_native_format()]
                collection.add(
                    **BaseOnlineDataModel._convertor.convert_python_to_point(point))
            BaseOnlineDataModel._session_data = []

        @staticmethod
        def child_getitem_fn(self, key):
            return self.kwargs[key]

    return BaseOnlineDataModel
