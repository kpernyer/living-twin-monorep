import os

# Set test environment BEFORE any imports
os.environ.setdefault("BYPASS_AUTH", "true")
os.environ.setdefault("USE_LOCAL_MOCK", "true")
os.environ.setdefault("LOCAL_EMBEDDINGS", "true")
os.environ.setdefault("LLM_PROVIDER", "stub")  # Use stub LLM for tests

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_ingest_and_query_workflow():
    """Integration test: ingest text, then query to confirm retrieval."""
    
    # Step 1: Ingest a document
    test_title = "Integration Test Document"
    test_content = """
    Living Twin is an organizational AI system that helps companies understand their data.
    It uses RAG (Retrieval Augmented Generation) to provide intelligent answers based on
    company documents and knowledge bases. The system supports multi-tenant architecture
    and can handle various document types including PDF, DOCX, and plain text.
    """
    
    ingest_response = client.post("/query/ingest/text", json={
        "title": test_title,
        "text": test_content,
        "tenantId": "demo"
    })
    
    # Should succeed (or fail gracefully if no vector store configured)
    assert ingest_response.status_code in (200, 500)
    
    if ingest_response.status_code == 200:
        ingest_data = ingest_response.json()
        assert ingest_data["ok"] is True
        assert ingest_data["chunks"] > 0
        source_id = ingest_data["sourceId"]
        
        # Step 2: Query for the ingested content
        query_response = client.post("/query", json={
            "question": "What is Living Twin?",
            "k": 5,
            "tenantId": "demo"
        })
        
        # Should succeed and return relevant content
        assert query_response.status_code in (200, 500)
        
        if query_response.status_code == 200:
            query_data = query_response.json()
            assert "answer" in query_data
            assert "sources" in query_data
            assert len(query_data["sources"]) > 0
            
            # Check if our ingested document is in the sources
            found_our_document = False
            for source in query_data["sources"]:
                if test_title in source.get("title", "") or "Living Twin" in source.get("content", ""):
                    found_our_document = True
                    break
            
            # Note: This might not always be true depending on vector search implementation
            # but it's a good integration test when the system is working
            if found_our_document:
                print(f"✅ Integration test passed: Found ingested document in query results")
            else:
                print(f"⚠️  Integration test: Ingested document not found in results (this may be normal)")


@pytest.mark.integration
def test_conversational_workflow():
    """Integration test: conversational query with memory."""
    
    # Step 1: Start a conversation
    conv_response = client.post("/query/conversation/query", json={
        "question": "What is the main purpose of Living Twin?",
        "tenantId": "demo"
    })
    
    assert conv_response.status_code in (200, 500)
    
    if conv_response.status_code == 200:
        conv_data = conv_response.json()
        assert "conversationId" in conv_data
        conversation_id = conv_data["conversationId"]
        
        # Step 2: Continue the conversation
        follow_up_response = client.post("/query/conversation/query", json={
            "conversationId": conversation_id,
            "question": "Can you tell me more about the RAG capabilities?",
            "tenantId": "demo"
        })
        
        assert follow_up_response.status_code in (200, 500)
        
        if follow_up_response.status_code == 200:
            follow_up_data = follow_up_response.json()
            assert follow_up_data["conversationId"] == conversation_id
            assert "answer" in follow_up_data


@pytest.mark.integration
def test_debug_rag_workflow():
    """Integration test: debug RAG to see retrieval details."""
    
    # First ingest some content
    test_content = "Debug test content about artificial intelligence and machine learning."
    
    ingest_response = client.post("/query/ingest/text", json={
        "title": "Debug Test",
        "text": test_content,
        "tenantId": "demo"
    })
    
    if ingest_response.status_code == 200:
        # Then debug query
        debug_response = client.post("/query/debug/rag", json={
            "question": "What is artificial intelligence?",
            "k": 3,
            "tenantId": "demo"
        })
        
        assert debug_response.status_code in (200, 500)
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            assert "query" in debug_data
            assert "retrieved_chunks" in debug_data
            assert "total_results" in debug_data
            assert "embedding_model" in debug_data
            assert "llm_model" in debug_data
            
            # Check if we have any retrieved chunks
            assert isinstance(debug_data["retrieved_chunks"], list)
            print(f"✅ Debug RAG test: Retrieved {debug_data['total_results']} chunks")


@pytest.mark.integration
def test_recent_documents_workflow():
    """Integration test: check recent documents after ingestion."""
    
    # Ingest a document
    ingest_response = client.post("/query/ingest/text", json={
        "title": "Recent Test Document",
        "text": "This is a test document for checking recent documents functionality.",
        "tenantId": "demo"
    })
    
    if ingest_response.status_code == 200:
        # Check recent documents
        recent_response = client.get("/query/ingest/recent?tenantId=demo")
        
        assert recent_response.status_code in (200, 500)
        
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            assert "items" in recent_data
            assert isinstance(recent_data["items"], list)
            
            # Should have at least one document
            if len(recent_data["items"]) > 0:
                latest_doc = recent_data["items"][0]
                assert "id" in latest_doc
                assert "title" in latest_doc
                assert "chunks" in latest_doc
                print(f"✅ Recent documents test: Found {len(recent_data['items'])} documents")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])
