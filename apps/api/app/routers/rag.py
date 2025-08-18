import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field

from .. import di
from ..config import load_config
from ..domain.models import (
    ConversationalQueryRequest,
    ConversationsResponseSchema,
    QueryRequest,
)

# All RAG-related routes are grouped under the /query prefix
router = APIRouter(prefix="/query")


# Request/Response Schemas
class QueryRequestSchema(BaseModel):
    question: str = Field(..., description="The question to ask")
    k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")
    tenantId: Optional[str] = Field(
        None, description="Target tenant ID (defaults to user's tenant)"
    )


class QueryResponseSchema(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    query_id: str = Field(..., description="Unique query identifier")


class IngestRequestSchema(BaseModel):
    title: str = Field(..., description="Document title")
    text: str = Field(..., description="Document content")
    tenantId: Optional[str] = Field(None, description="Target tenant ID")


class IngestResponseSchema(BaseModel):
    ok: bool = Field(..., description="Success status")
    sourceId: str = Field(..., description="Generated source ID")
    chunks: int = Field(..., description="Number of chunks created")


class IngestAcceptedResponseSchema(BaseModel):
    ok: bool = Field(...)
    jobId: str = Field(...)
    status: str = Field(...)


class RecentDocumentSchema(BaseModel):
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    type: str = Field(..., description="Document type")
    createdAt: str = Field(..., description="Creation timestamp")
    chunks: int = Field(..., description="Number of chunks")


class RecentDocumentsResponseSchema(BaseModel):
    items: List[RecentDocumentSchema] = Field(..., description="List of recent documents")


class ConversationalQueryRequestSchema(BaseModel):
    conversationId: Optional[str] = Field(None, description="Existing conversation ID")
    question: str = Field(..., description="The question to ask")
    k: int = Field(5, ge=1, le=20, description="Number of context chunks")
    tenantId: Optional[str] = Field(None, description="Target tenant ID")
    memoryWindow: Optional[int] = Field(10, ge=1, le=50, description="Memory window size")


class ConversationalQueryResponseSchema(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    conversationId: str = Field(..., description="Conversation ID")
    queryId: str = Field(..., description="Query ID")


class ConversationSchema(BaseModel):
    id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")
    messageCount: int = Field(..., description="Number of messages")


class MessageSchema(BaseModel):
    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")


class ConversationDetailSchema(BaseModel):
    id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")
    messages: List[MessageSchema] = Field(..., description="Conversation messages")


class DeleteResponseSchema(BaseModel):
    success: bool = Field(..., description="Deletion success status")


class IngestJobStatusSchema(BaseModel):
    jobId: str = Field(...)
    status: str = Field(...)
    tenantId: str | None = None
    userId: str | None = None
    title: str | None = None
    sourceId: str | None = None
    chunkCount: int | None = None
    durationMs: int | None = None
    error: str | None = None
    createdAt: int | None = None
    updatedAt: int | None = None


@router.post("", response_model=QueryResponseSchema)
def query(q: QueryRequestSchema, request: Request):
    """Query endpoint - thin HTTP layer delegating to domain service."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = q.tenantId or user["tenantId"]

    # Authorization check using domain service
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Create domain request
    domain_request = QueryRequest(
        query=q.question, tenant_id=tenant, user_id=user["uid"], context_limit=q.k
    )

    # Delegate to domain service
    response = di.container.rag.query_documents(domain_request)

    # Convert domain response to HTTP response
    return QueryResponseSchema(
        answer=response.answer,
        sources=[
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "score": doc.metadata.get("score", 0.0),
            }
            for doc in response.sources
        ],
        confidence=response.confidence,
        query_id=response.query_id,
    )


@router.post("/ingest/text", response_model=IngestAcceptedResponseSchema | IngestResponseSchema)
def ingest(payload: IngestRequestSchema, request: Request):
    """Ingest endpoint - thin HTTP layer delegating to domain service."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = payload.tenantId or user["tenantId"]

    # Authorization check using domain service
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Delegate to domain service
    cfg = di.container.cfg if hasattr(di.container, "cfg") else load_config()
    if getattr(cfg, "async_ingest", False):
        # Fire-and-forget pattern with job tracking
        import threading
        import time
        import uuid

        job_id = str(uuid.uuid4())
        now_ms = int(time.time() * 1000)
        di.container.jobs.create_job(
            {
                "jobId": job_id,
                "tenantId": tenant,
                "userId": user["uid"],
                "title": payload.title,
                "status": "queued",
                "createdAt": now_ms,
                "updatedAt": now_ms,
            }
        )

        def _worker():
            try:
                di.container.jobs.update_job(
                    job_id, {"status": "processing", "startedAt": int(time.time() * 1000)}
                )
                start = time.time()
                result = di.container.rag.ingest_text(
                    title=payload.title, text=payload.text, tenant_id=tenant
                )
                duration_ms = int((time.time() - start) * 1000)
                di.container.jobs.update_job(
                    job_id,
                    {
                        "status": "completed",
                        "sourceId": result.get("source_id"),
                        "chunkCount": result.get("chunks_created", 0),
                        "durationMs": duration_ms,
                        "updatedAt": int(time.time() * 1000),
                    },
                )
                # Emit domain event if event bus available
                try:
                    if getattr(di.container, "event_bus", None):
                        # Fire-and-forget; don't await in thread
                        import asyncio

                        asyncio.get_event_loop().create_task(
                            di.container.event_bus.publish_document_ingested(
                                document_id=result.get("source_id", ""),
                                tenant_id=tenant,
                            )
                        )
                except Exception:
                    pass
            except Exception as e:
                di.container.jobs.update_job(
                    job_id,
                    {
                        "status": "failed",
                        "error": str(e),
                        "updatedAt": int(time.time() * 1000),
                    },
                )

        threading.Thread(target=_worker, daemon=True).start()
        return IngestAcceptedResponseSchema(ok=True, jobId=job_id, status="queued")
    else:
        result = di.container.rag.ingest_text(
            title=payload.title, text=payload.text, tenant_id=tenant
        )
        return IngestResponseSchema(
            ok=result["success"], sourceId=result["source_id"], chunks=result["chunks_created"]
        )


@router.post("/ingest/upload", response_model=IngestResponseSchema)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    tenantId: Optional[str] = Form(None),
):
    """Upload and ingest a document file (PDF, DOCX, TXT, MD)."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = tenantId or user["tenantId"]

    # Authorization check
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc", ".txt", ".md"}
    file_ext = os.path.splitext(file.filename.lower())[1] if file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            400, f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Delegate to domain service for file processing
        result = di.container.rag.ingest_file(
            file_path=tmp_file_path, title=title, tenant_id=tenant, original_filename=file.filename
        )

        return IngestResponseSchema(
            ok=result["success"], sourceId=result["source_id"], chunks=result["chunks_created"]
        )

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.get("/ingest/recent", response_model=RecentDocumentsResponseSchema)
def get_recent_documents(request: Request, tenantId: Optional[str] = None):
    """Get recently ingested documents."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner"})
    tenant = tenantId or user["tenantId"]

    # Authorization check
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Get recent documents from domain service
    documents = di.container.rag.get_recent_documents(tenant_id=tenant, limit=20)

    return RecentDocumentsResponseSchema(
        items=[
            RecentDocumentSchema(
                id=doc["id"],
                title=doc["title"],
                type=doc.get("type", "text"),
                createdAt=doc.get("created_at", ""),
                chunks=doc.get("chunk_count", 0),
            )
            for doc in documents
        ]
    )


@router.post("/debug/rag", response_model=Dict[str, Any])
def debug_rag(q: QueryRequestSchema, request: Request):
    """Debug RAG pipeline - returns detailed retrieval information."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = q.tenantId or user["tenantId"]

    # Authorization check
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Get debug information from domain service
    debug_info = di.container.rag.debug_query(query=q.question, tenant_id=tenant, k=q.k)

    return debug_info


# Conversational endpoints
@router.post("/conversation/query", response_model=ConversationalQueryResponseSchema)
def conversational_query(payload: ConversationalQueryRequestSchema, request: Request):
    """Conversational query endpoint with memory."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = payload.tenantId or user["tenantId"]

    # Authorization check
    if not di.container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"], user_tenant=user["tenantId"], target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Create domain request
    domain_request = ConversationalQueryRequest(
        conversation_id=payload.conversationId,
        query=payload.question,
        tenant_id=tenant,
        user_id=user["uid"],
        context_limit=payload.k,
        memory_window=payload.memoryWindow or 10,
    )

    # Delegate to conversational service
    response = di.container.conversational_rag.conversational_query(domain_request)

    return ConversationalQueryResponseSchema(
        answer=response.answer,
        sources=[
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "score": doc.metadata.get("score", 0.0),
            }
            for doc in response.sources
        ],
        confidence=response.confidence,
        conversationId=response.conversation_id,
        queryId=response.query_id,
    )


@router.get("/conversations", response_model=ConversationsResponseSchema)
def list_conversations(request: Request, limit: int = Query(20, ge=1, le=100)):
    """List user's conversations."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})

    conversations = di.container.conversation_store.list_conversations(
        tenant_id=user["tenantId"], user_id=user["uid"], limit=limit
    )

    return ConversationsResponseSchema(
        conversations=[
            ConversationSchema(
                id=conv.id,
                title=conv.title,
                createdAt=conv.created_at.isoformat(),
                updatedAt=conv.updated_at.isoformat(),
                messageCount=conv.metadata.get("message_count", 0),
            )
            for conv in conversations
        ]
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
def get_conversation(conversation_id: str, request: Request):
    """Get conversation with full message history."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})

    conversation = di.container.conversation_store.get_conversation(
        conversation_id, user["tenantId"]
    )

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    # Verify user owns this conversation
    if conversation.user_id != user["uid"]:
        raise HTTPException(403, "Access denied")

    return ConversationDetailSchema(
        id=conversation.id,
        title=conversation.title,
        createdAt=conversation.created_at.isoformat(),
        updatedAt=conversation.updated_at.isoformat(),
        messages=[
            MessageSchema(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                metadata=msg.metadata,
            )
            for msg in conversation.messages
        ],
    )


@router.delete("/conversations/{conversation_id}", response_model=DeleteResponseSchema)
def delete_conversation(conversation_id: str, request: Request):
    """Delete a conversation."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})

    # First verify the conversation exists and user owns it
    conversation = di.container.conversation_store.get_conversation(
        conversation_id, user["tenantId"]
    )

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    if conversation.user_id != user["uid"]:
        raise HTTPException(403, "Access denied")

    # Delete the conversation
    success = di.container.conversation_store.delete_conversation(conversation_id, user["tenantId"])

    return DeleteResponseSchema(success=success)


@router.get("/ingest/status", response_model=IngestJobStatusSchema)
def get_ingest_status(jobId: str, request: Request):
    """Get ingest job status by jobId."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})
    job = di.container.jobs.get_job(jobId)
    if not job:
        raise HTTPException(404, "Job not found")
    # Enforce tenant/user ownership
    if job.get("tenantId") != user["tenantId"] or job.get("userId") != user["uid"]:
        raise HTTPException(403, "Access denied")
    return IngestJobStatusSchema(**job)
