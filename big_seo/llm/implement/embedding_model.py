from big_seo.llm.embedding_model import IEmbedding
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from llama_index.core.embeddings import BaseEmbedding


class VertexAIEmbedding(IEmbedding):
    def __init__(self, model: TextEmbeddingModel, task_type: str = 'RETRIEVAL_DOCUMENT'):
        self.model = model

    def get_embedding(self, text: str) -> list:
        in_text = TextEmbeddingInput(
            text=text, task_type='RETRIEVAL_DOCUMENT')
        embeddings = self.model.get_embeddings([in_text])
        vector = embeddings[0].values
        return vector


class VertexAIEmbeddingBatchPrediction(IEmbedding):
    def __init__(self, model: TextEmbeddingModel, task_type: str = 'RETRIEVAL_DOCUMENT'):
        # TODO
        self.model = model

    def get_embedding(self, text: str) -> list:

        pass


class LLamaIndexEmbedding(IEmbedding):
    def __init__(self, model: BaseEmbedding) -> None:
        self.model = model

    def get_embedding(self, text: str) -> list:
        return self.model.get_text_embedding(text)
