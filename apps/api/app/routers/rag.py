from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from ..di import container
from ..domain.models import QueryRequest, QueryResponse, ConversationalQueryRequest
import tempfile
import os

router = APIRouter()

class Query(BaseModel):
    question: str
    k: int = 5
    tenantId: str | None = None

class Ingest(BaseModel):
    title: str
    text: str
    tenantId: str | None = None

class ConversationalQuery(BaseModel):
    conversationId: Optional[str] = None
    question: str
    k: int = 5
    tenantId: Optional[str] = None
    memoryWindow: Optional[int] = 10

@router.post("/query")
def query(q: Query, request: Request):
    """Query endpoint - thin HTTP layer delegating to domain service."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = q.tenantId or user["tenantId"]
    
    # Authorization check using domain service
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"], 
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Create domain request
    domain_request = QueryRequest(
        query=q.question,
        tenant_id=tenant,
        user_id=user["uid"],
        context_limit=q.k
    )
    
    # Delegate to domain service
    response = container.rag.query_documents(domain_request)
    
    # Convert domain response to HTTP response
    return {
        "answer": response.answer,
        "sources": [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "score": doc.metadata.get("score", 0.0)
            }
            for doc in response.sources
        ],
        "confidence": response.confidence,
        "query_id": response.query_id
    }

@router.post("/ingest/text")
def ingest(payload: Ingest, request: Request):
    """Ingest endpoint - thin HTTP layer delegating to domain service."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = payload.tenantId or user["tenantId"]
    
    # Authorization check using domain service
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"],
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Delegate to domain service (business logic moved out of router)
    result = container.rag.ingest_text(
        title=payload.title,
        text=payload.text,
        tenant_id=tenant
    )
    
    return {
        "ok": result["success"],
        "sourceId": result["source_id"],
        "chunks": result["chunks_created"]
    }

@router.post("/ingest/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    tenantId: Optional[str] = Form(None)
):
    """Upload and ingest a document file (PDF, DOCX, TXT, MD)."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = tenantId or user["tenantId"]
    
    # Authorization check
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"],
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    file_ext = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Delegate to domain service for file processing
        result = container.rag.ingest_file(
            file_path=tmp_file_path,
            title=title,
            tenant_id=tenant,
            original_filename=file.filename
        )
        
        return {
            "ok": result["success"],
            "sourceId": result["source_id"],
            "chunks": result["chunks_created"],
            "fileType": file_ext,
            "embeddingProvider": result.get("embedding_provider", "unknown")
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@router.get("/ingest/recent")
def get_recent_documents(request: Request, tenantId: Optional[str] = None):
    """Get recently ingested documents."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = tenantId or user["tenantId"]
    
    # Authorization check
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"],
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Get recent documents from domain service
    documents = container.rag.get_recent_documents(tenant_id=tenant, limit=20)
    
    return {
        "items": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "type": doc.get("type", "text"),
                "createdAt": doc.get("created_at", ""),
                "chunks": doc.get("chunk_count", 0)
            }
            for doc in documents
        ]
    }

@router.post("/debug/rag")
def debug_rag(q: Query, request: Request):
    """Debug RAG pipeline - returns detailed retrieval information."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = q.tenantId or user["tenantId"]
    
    # Authorization check
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"],
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Get debug information from domain service
    debug_info = container.rag.debug_query(
        query=q.question,
        tenant_id=tenant,
        k=q.k
    )
    
    return debug_info


# Conversational endpoints
@router.post("/conversation/query")
def conversational_query(payload: ConversationalQuery, request: Request):
    """Conversational query endpoint with memory."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = payload.tenantId or user["tenantId"]
    
    # Authorization check
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"], 
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")
    
    # Create domain request
    domain_request = ConversationalQueryRequest(
        conversation_id=payload.conversationId,
        query=payload.question,
        tenant_id=tenant,
        user_id=user["uid"],
        context_limit=payload.k,
        memory_window=payload.memoryWindow or 10
    )
    
    # Delegate to conversational service
    response = container.conversational_rag.conversational_query(domain_request)
    
    return {
        "answer": response.answer,
        "sources": [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "score": doc.metadata.get("score", 0.0)
            }
            for doc in response.sources
        ],
        "confidence": response.confidence,
        "conversationId": response.conversation_id,
        "queryId": response.query_id
    }


@router.get("/conversations")
def list_conversations(request: Request, limit: int = 20):
    """List user's conversations."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})
    
    conversations = container.conversation_store.list_conversations(
        tenant_id=user["tenantId"],
        user_id=user["uid"],
        limit=limit
    )
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "createdAt": conv.created_at.isoformat(),
                "updatedAt": conv.updated_at.isoformat(),
                "messageCount": conv.metadata.get("message_count", 0)
            }
            for conv in conversations
        ]
    }


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, request: Request):
    """Get conversation with full message history."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})
    
    conversation = container.conversation_store.get_conversation(
        conversation_id, 
        user["tenantId"]
    )
    
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    
    # Verify user owns this conversation
    if conversation.user_id != user["uid"]:
        raise HTTPException(403, "Access denied")
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in conversation.messages
        ]
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, request: Request):
    """Delete a conversation."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})
    
    # First verify the conversation exists and user owns it
    conversation = container.conversation_store.get_conversation(
        conversation_id, 
        user["tenantId"]
    )
    
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    
    if conversation.user_id != user["uid"]:
        raise HTTPException(403, "Access denied")
    
    # Delete the conversation
    success = container.conversation_store.delete_conversation(
        conversation_id, 
        user["tenantId"]
    )
    
    return {"success": success}
