from dataclasses import dataclass
from abc import ABC, abstractmethod

from big_seo.llm.core.common import IPrompt


class ILLModel(ABC):
    base_model = None

    @abstractmethod
    def invoke(self, prompt: IPrompt) -> list:
        pass
