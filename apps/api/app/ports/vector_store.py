from typing import Any, Dict, List, Protocol


class IVectorStore(Protocol):
    def search(
        self, tenant_id: str, query_vector: list[float], k: int = 5
    ) -> List[Dict[str, Any]]:
        ...

    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]
    ) -> str:
        ...

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        ...
