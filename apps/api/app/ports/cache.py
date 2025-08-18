"""Cache port definitions for clean architecture."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np


class ICache(ABC):
    """Abstract cache interface for dependency inversion."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        pass

    @abstractmethod
    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        pass


class ISemanticCache(ABC):
    """Abstract semantic cache interface for RAG queries."""

    @abstractmethod
    async def get_similar(
        self, query_embedding: np.ndarray, threshold: float = 0.95
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for semantically similar query."""
        pass

    @abstractmethod
    async def store(
        self, query: str, query_embedding: np.ndarray, response: str, metadata: Dict[str, Any]
    ) -> bool:
        """Store query and response with embedding."""
        pass

    @abstractmethod
    async def clear_tenant_cache(self, tenant_id: str) -> int:
        """Clear all cache entries for a tenant."""
        pass


class IVectorCache(ABC):
    """Abstract vector cache interface for embeddings."""

    @abstractmethod
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text."""
        pass

    @abstractmethod
    async def store_embedding(self, text: str, embedding: List[float]) -> bool:
        """Store text embedding in cache."""
        pass

    @abstractmethod
    async def get_batch_embeddings(self, texts: List[str]) -> Dict[str, List[float]]:
        """Get cached embeddings for multiple texts."""
        pass

    @abstractmethod
    async def store_batch_embeddings(self, embeddings: Dict[str, List[float]]) -> bool:
        """Store multiple text embeddings in cache."""
        pass
