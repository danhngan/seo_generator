from abc import ABC, abstractmethod
from enum import Enum
from big_seo.common.lang import DocumentLang


class Document:
    doc_id: bytes
    meta_data: dict
    doc_lang: DocumentLang

    @abstractmethod
    def get_doc_content(self):
        pass

    @abstractmethod
    def get_doc_meta(self):
        pass

    def __hash__(self):
        return hash(self.doc_id)

    def __eq__(self, __value: object) -> bool:
        return hash(self.doc_id) == hash(__value)


class IDocumentCreator(ABC):
    @abstractmethod
    def create(self, **kwargs) -> Document:
        pass


class IPrompt(ABC):
    @abstractmethod
    def get_prompt(self) -> str:
        pass


class IBaseTool(ABC):
    @abstractmethod
    def __call__(self):
        pass


class Prompt(IPrompt):
    def __init__(self, prompt) -> None:
        self.prompt = prompt

    def get_prompt(self) -> str:
        return self.prompt
