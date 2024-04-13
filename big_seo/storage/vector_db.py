from abc import ABC, abstractmethod, abstractclassmethod
from datetime import datetime
from typing import overload


class BaseTypeConvertor(ABC):
    @abstractmethod
    def to_native_format(val: type):
        """from python types to db familiar types"""
        pass

    @abstractmethod
    def to_object_format(val):
        """from db familiar types to python types"""
        pass


class BaseSchemaConvertor(ABC):
    @abstractmethod
    def to_native_schema(val):
        """from python types to db familiar types"""
        pass

    @abstractmethod
    def to_object_schema(val):
        """from db familiar types to python types"""
        pass


class BaseDataType(ABC):
    python_type: type

    def get_python_type(self):
        return self.python_type

    def to_native_format(self, dbtype_mapper):
        return dbtype_mapper(self)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class VectorType(BaseDataType):
    python_type = list

    def __init__(self, vec_length) -> None:
        self.vec_length = vec_length
        self.val = None

    def to_native_format(self):
        return super().to_native_format(lambda x: x.val)

    def to_object_format(self, db_val):
        return VectorType(db_val)

    def __call__(self, val=None):
        if val is not None:
            self.val = val
        return self


class PythonNativeType(BaseDataType):
    python_type: type

    def __init__(self, val) -> None:
        self.val = val

    def to_native_format(self):
        """most of db support python native formats"""
        return super().to_native_format(lambda x: x.val)

    def to_object_format(self, db_val):
        return VectorType(db_val)

    def __call__(self, val=None):
        if val is not None:
            self.val = val
        return self


class Integer(PythonNativeType):
    python_type = int


class String(PythonNativeType):
    python_type = str


class Float(PythonNativeType):
    python_type = float


class Array(PythonNativeType):
    python_type = list


class Datetime(PythonNativeType):
    python_type = datetime


class VectorDBField:
    """default val is in python object type"""

    def __init__(self, field_name: str, field_type: BaseDataType, default_val=None) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.default_val = default_val

    def __call__(self, *args):
        if len(args) > 0:
            return self.field_type(args[0])
        else:
            return self.field_type(self.default_val)


class IVectorDBCollection(ABC):
    _id: bytes

    @abstractmethod
    def add(self, _id, vector, payload: dict):
        pass

    @abstractmethod
    def add_batch(self, data: list[tuple]):
        pass

    @abstractmethod
    def remove(self, _id: bytes):
        pass

    @abstractmethod
    def search_vec(self, vector_name, vector_value) -> list:
        pass


class IVectorDB(ABC):
    _id: bytes

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def get_collection(self, collection, schema) -> IVectorDBCollection:
        pass

    @abstractmethod
    def create_collection(self, collection, schema) -> IVectorDBCollection:
        pass

    @abstractmethod
    def delete_collection(self):
        pass
