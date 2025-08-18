from typing import List

from sentence_transformers import SentenceTransformer

from ..ports.llm import IEmbedder


class LocalEmbedder(IEmbedder):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def embed_batch(self, chunks: List[str]) -> List[list[float]]:
        return self.model.encode(chunks).tolist()
