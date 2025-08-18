"""Domain models for the Living Twin application."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Document(BaseModel):
    """Document model representing ingested content."""

    id: str
    title: str
    content: str
    source: str
    metadata: Dict[str, Any] = {}
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class Source(BaseModel):
    """Source model representing document sources."""

    id: str
    name: str
    type: str  # file, url, api, etc.
    location: str
    tenant_id: str
    created_at: datetime
    last_synced: Optional[datetime] = None


class Goal(BaseModel):
    """Goal model representing user objectives."""

    id: str
    title: str
    description: str
    user_id: str
    tenant_id: str
    status: str = "active"  # active, completed, archived
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(BaseModel):
    """User model."""

    id: str
    email: str
    name: Optional[str] = None
    tenant_id: str
    roles: List[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None


class Tenant(BaseModel):
    """Tenant model for multi-tenancy."""

    id: str
    name: str
    domain: Optional[str] = None
    settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True


class QueryRequest(BaseModel):
    """Request model for RAG queries."""

    query: str
    tenant_id: str
    user_id: str
    context_limit: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for RAG queries."""

    answer: str
    sources: List[Document]
    confidence: Optional[float] = None
    query_id: str
    tenant_id: str
    conversation_id: Optional[str] = None


class ConversationMessage(BaseModel):
    """Message within a conversation."""

    id: str
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class Conversation(BaseModel):
    """Conversation model for multi-turn interactions."""

    id: str
    tenant_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage] = []
    metadata: Dict[str, Any] = {}


class ConversationalQueryRequest(BaseModel):
    """Request model for conversational RAG queries."""

    conversation_id: Optional[str] = None  # None for new conversation
    query: str
    tenant_id: str
    user_id: str
    context_limit: Optional[int] = 5
    memory_window: Optional[int] = 10  # How many previous messages to consider
    filters: Optional[Dict[str, Any]] = None
