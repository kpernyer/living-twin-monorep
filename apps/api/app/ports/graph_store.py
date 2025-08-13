"""Graph store port interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.models import Document


class IGraphStore(ABC):
    """Abstract interface for graph storage operations."""

    @abstractmethod
    async def store_document_relations(
        self, 
        document: Document, 
        relations: List[Dict[str, Any]]
    ) -> None:
        """Store document and its relations in the graph."""
        pass

    @abstractmethod
    async def find_related_documents(
        self, 
        document_id: str, 
        relation_types: Optional[List[str]] = None,
        max_depth: int = 2
    ) -> List[Document]:
        """Find documents related to the given document."""
        pass

    @abstractmethod
    async def create_entity_relation(
        self, 
        entity1: str, 
        entity2: str, 
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a relation between two entities."""
        pass

    @abstractmethod
    async def query_graph(
        self, 
        cypher_query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query against the graph."""
        pass

    @abstractmethod
    async def get_document_context(
        self, 
        document_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get contextual information for a document from the graph."""
        pass
