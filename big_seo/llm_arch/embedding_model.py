from dataclasses import dataclass
from abc import ABC, abstractmethod


class IEmbedding(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> list:
        pass
