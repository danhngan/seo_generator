from big_seo.llm_arch.core.common import Document
from abc import abstractmethod


class NestedIndexDocument(Document):
    def get_doc_content(self):
        pass

    def get_doc_meta(self):
        pass

    @abstractmethod
    def get_nested_dict(self):
        pass

    @abstractmethod
    def get_flat_dict(self):
        pass
