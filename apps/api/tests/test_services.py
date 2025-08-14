from app.domain.services import RagService, TenantService


class DummyStore:
    def __init__(self, hits=None):
        self._hits = hits or []

    def search(self, tenant_id: str, query_vector, k: int = 5):
        return self._hits[:k]

    def upsert_chunks(self, tenant_id: str, title: str, chunks, embeddings):
        return "source-123"

    def get_recent_sources(self, tenant_id: str, limit: int = 20):
        return [{"id": "s1", "title": "Doc", "created_at": "", "chunk_count": 3, "type": "document"}]


class DummyEmbedder:
    def embed_query(self, text: str):
        return [0.1, 0.2, 0.3]

    def embed_batch(self, chunks):
        return [[0.1] * 3 for _ in chunks]


class DummyLLM:
    def answer(self, hits, question: str, rag_only: bool = False) -> str:
        if rag_only:
            return "RAG_ONLY"
        return f"Answer to: {question} with {len(hits)} hits"


def test_rag_service_query_basic():
    store = DummyStore(hits=[{"id": "1", "text": "alpha", "source": "doc1", "score": 0.8}])
    rag = RagService(store=store, llm=DummyLLM(), embed=DummyEmbedder())

    resp = rag.query_documents(
        request=type("Req", (), {"query": "hello", "tenant_id": "demo", "context_limit": 5})
    )

    assert resp.answer.startswith("Answer to: hello")
    assert resp.confidence is not None and 0.0 <= resp.confidence <= 1.0
    assert len(resp.sources) == 1


def test_rag_service_ingest_text():
    store = DummyStore()
    rag = RagService(store=store, llm=DummyLLM(), embed=DummyEmbedder())

    result = rag.ingest_text(title="T", text="abcdef" * 200, tenant_id="demo")
    assert result["success"] is True
    assert result["chunks_created"] > 0
    assert result["source_id"] == "source-123"


def test_tenant_service_access():
    svc = TenantService()
    # Same-tenant always allowed
    assert svc.validate_cross_tenant_access("viewer", "a", "a") is True
    # Cross-tenant only owner
    assert svc.validate_cross_tenant_access("admin", "a", "b") is False
    assert svc.validate_cross_tenant_access("owner", "a", "b") is True


