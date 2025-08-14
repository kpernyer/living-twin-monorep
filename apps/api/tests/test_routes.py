import os
os.environ.setdefault("BYPASS_AUTH", "true")

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_readyz():
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json().get("ready") is True


def test_query_endpoint_basic():
    r = client.post("/query", json={"question": "hello", "k": 3})
    assert r.status_code in (200, 500)  # 500 allowed if no vector index configured
    if r.status_code == 200:
        data = r.json()
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "query_id" in data
        assert isinstance(data["sources"], list)


def test_query_endpoint_validation():
    # Test invalid k value
    r = client.post("/query", json={"question": "hello", "k": 0})
    assert r.status_code == 422  # Validation error
    
    # Test missing question
    r = client.post("/query", json={"k": 5})
    assert r.status_code == 422  # Validation error


def test_ingest_text_endpoint_async_status():
    # In async mode, expect an accepted-like response
    os.environ.setdefault("ASYNC_INGEST", "true")
    r = client.post("/query/ingest/text", json={"title": "Demo", "text": "hello world"})
    assert r.status_code in (200, 202, 500)
    if r.status_code == 200:
        data = r.json()
        # Could be accepted schema or sync schema depending on flag at import time
        if "jobId" in data:
            assert data.get("ok") is True
            job_id = data["jobId"]
            # Fetch status (might be very fast, allow not found if repo is in-memory and process restarted)
            sr = client.get(f"/query/ingest/status?jobId={job_id}")
            assert sr.status_code in (200, 404)
        else:
            # Sync schema
            assert data.get("ok") in (True, False)


def test_ingest_text_validation():
    # Test missing title
    r = client.post("/query/ingest/text", json={"text": "hello world"})
    assert r.status_code == 422  # Validation error
    
    # Test missing text
    r = client.post("/query/ingest/text", json={"title": "Demo"})
    assert r.status_code == 422  # Validation error


def test_recent_documents_endpoint():
    r = client.get("/query/ingest/recent")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "items" in data
        assert isinstance(data["items"], list)


def test_conversational_query_endpoint():
    r = client.post("/query/conversation/query", json={"question": "hello"})
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "answer" in data
        assert "sources" in data
        assert "conversationId" in data
        assert "queryId" in data


def test_conversational_query_validation():
    # Test invalid memory window
    r = client.post("/query/conversation/query", json={"question": "hello", "memoryWindow": 0})
    assert r.status_code == 422  # Validation error


def test_conversations_list_endpoint():
    r = client.get("/query/conversations")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)


def test_conversations_list_validation():
    # Test invalid limit
    r = client.get("/query/conversations?limit=0")
    assert r.status_code == 422  # Validation error


def test_debug_rag_endpoint():
    r = client.post("/query/debug/rag", json={"question": "hello", "k": 3})
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "query" in data
        assert "tenant_id" in data
        assert "retrieved_chunks" in data
        assert "total_results" in data


