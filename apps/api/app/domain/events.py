"""Domain events for the Living Twin system."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Event types in the system."""
    # Document events
    DOCUMENT_INGESTED = "document.ingested"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_DELETED = "document.deleted"
    
    # Query events
    QUERY_EXECUTED = "query.executed"
    QUERY_FAILED = "query.failed"
    
    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    
    # Organization events
    ORGANIZATION_CREATED = "organization.created"
    ORGANIZATION_UPDATED = "organization.updated"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_HEALTH_CHECK = "system.health_check"


@dataclass
class DomainEvent:
    """Base domain event."""
    event_id: str
    event_type: EventType
    tenant_id: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        if not self.idempotency_key:
            self.idempotency_key = f"{self.event_type.value}:{self.tenant_id}:{self.event_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary."""
        data['event_type'] = EventType(data['event_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class DocumentIngestedEvent(DomainEvent):
    """Event fired when a document is ingested."""
    
    def __init__(
        self,
        tenant_id: str,
        document_id: str,
        document_title: str,
        document_type: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        data = {
            'document_id': document_id,
            'document_title': document_title,
            'document_type': document_type
        }
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.DOCUMENT_INGESTED,
            tenant_id=tenant_id,
            timestamp=kwargs.get('timestamp', datetime.utcnow()),
            data=data,
            user_id=user_id,
            **{k: v for k, v in kwargs.items() if k not in ['event_id', 'timestamp']}
        )


@dataclass
class QueryExecutedEvent(DomainEvent):
    """Event fired when a query is executed."""
    
    def __init__(
        self,
        tenant_id: str,
        query_id: str,
        query_text: str,
        user_id: str,
        response_time_ms: int,
        **kwargs
    ):
        data = {
            'query_id': query_id,
            'query_text': query_text,
            'response_time_ms': response_time_ms
        }
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.QUERY_EXECUTED,
            tenant_id=tenant_id,
            timestamp=kwargs.get('timestamp', datetime.utcnow()),
            data=data,
            user_id=user_id,
            **{k: v for k, v in kwargs.items() if k not in ['event_id', 'timestamp']}
        )


@dataclass
class UserRegisteredEvent(DomainEvent):
    """Event fired when a user registers."""
    
    def __init__(
        self,
        tenant_id: str,
        user_id: str,
        email: str,
        organization_id: str,
        **kwargs
    ):
        data = {
            'user_id': user_id,
            'email': email,
            'organization_id': organization_id
        }
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.USER_REGISTERED,
            tenant_id=tenant_id,
            timestamp=kwargs.get('timestamp', datetime.utcnow()),
            data=data,
            user_id=user_id,
            **{k: v for k, v in kwargs.items() if k not in ['event_id', 'timestamp']}
        )


class EventFactory:
    """Factory for creating domain events."""
    
    @staticmethod
    def create_document_ingested(
        tenant_id: str,
        document_id: str,
        document_title: str,
        document_type: str,
        user_id: Optional[str] = None
    ) -> DocumentIngestedEvent:
        """Create a document ingested event."""
        return DocumentIngestedEvent(
            tenant_id=tenant_id,
            document_id=document_id,
            document_title=document_title,
            document_type=document_type,
            user_id=user_id
        )
    
    @staticmethod
    def create_query_executed(
        tenant_id: str,
        query_id: str,
        query_text: str,
        user_id: str,
        response_time_ms: int
    ) -> QueryExecutedEvent:
        """Create a query executed event."""
        return QueryExecutedEvent(
            tenant_id=tenant_id,
            query_id=query_id,
            query_text=query_text,
            user_id=user_id,
            response_time_ms=response_time_ms
        )
    
    @staticmethod
    def create_user_registered(
        tenant_id: str,
        user_id: str,
        email: str,
        organization_id: str
    ) -> UserRegisteredEvent:
        """Create a user registered event."""
        return UserRegisteredEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            email=email,
            organization_id=organization_id
        )
