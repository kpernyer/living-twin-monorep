from typing import Any, Dict, List, Protocol


class IEmbedder(Protocol):
    def embed_query(self, text: str) -> list[float]: ...

    def embed_batch(self, chunks: list[str]) -> list[list[float]]: ...


class IChatLLM(Protocol):
    def answer(self, hits: List[Dict[str, Any]], question: str, rag_only: bool = False) -> str: ...
