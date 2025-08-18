"""Redis cache adapter implementation."""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import numpy as np
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from ..ports.cache import ICache, ISemanticCache, IVectorCache

logger = logging.getLogger(__name__)


class RedisConnectionPool:
    """Redis connection pool manager."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_connections: int = 50,
        decode_responses: bool = False,
    ):
        """Initialize Redis connection pool."""
        self.pool = ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            decode_responses=decode_responses,
            socket_keepalive=True,
            socket_keepalive_options={
                1: 3,  # TCP_KEEPIDLE
                2: 3,  # TCP_KEEPINTVL
                3: 3,  # TCP_KEEPCNT
            },
        )
        self._client = None

    async def get_client(self) -> redis.Redis:
        """Get Redis client with connection pooling."""
        if not self._client:
            self._client = redis.Redis(connection_pool=self.pool)
        return self._client

    async def close(self):
        """Close all connections in the pool."""
        if self._client:
            await self._client.close()
        await self.pool.disconnect()


class RedisCache(ICache):
    """Redis cache implementation with connection pooling."""

    def __init__(self, pool: RedisConnectionPool):
        """Initialize with connection pool."""
        self.pool = pool
        self._default_ttl = 3600  # 1 hour default

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            client = await self.pool.get_client()
            value = await client.get(key)
            if value:
                # Try to deserialize JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value.decode() if isinstance(value, bytes) else value
            return None
        except RedisError as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            client = await self.pool.get_client()
            # Serialize value to JSON if it's not a string
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)
            
            if ttl:
                return await client.setex(key, ttl, value)
            else:
                return await client.setex(key, self._default_ttl, value)
        except RedisError as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            client = await self.pool.get_client()
            result = await client.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = await self.pool.get_client()
            return await client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        try:
            client = await self.pool.get_client()
            return await client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis expire error for key {key}: {e}")
            return False

    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            client = await self.pool.get_client()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis flush_pattern error for pattern {pattern}: {e}")
            return 0


class SemanticCache(ISemanticCache):
    """Semantic cache for RAG queries using Redis."""

    def __init__(self, pool: RedisConnectionPool, embedding_dimensions: int = 1536):
        """Initialize semantic cache."""
        self.pool = pool
        self.embedding_dimensions = embedding_dimensions
        self._cache_prefix = "semantic:"
        self._index_prefix = "semantic_idx:"
        self._ttl = 3600 * 24  # 24 hours for semantic cache

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    async def get_similar(
        self, query_embedding: np.ndarray, threshold: float = 0.95
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for semantically similar query."""
        try:
            client = await self.pool.get_client()
            
            # Get all semantic cache keys
            keys = []
            async for key in client.scan_iter(match=f"{self._cache_prefix}*"):
                keys.append(key)
            
            # Check similarity for each cached query
            for key in keys:
                cached_data = await client.get(key)
                if cached_data:
                    try:
                        data = json.loads(cached_data)
                        cached_embedding = np.array(data.get("embedding", []))
                        
                        if cached_embedding.shape[0] == query_embedding.shape[0]:
                            similarity = self._cosine_similarity(query_embedding, cached_embedding)
                            
                            if similarity >= threshold:
                                # Update hit count and last access time
                                data["hits"] = data.get("hits", 0) + 1
                                data["last_accessed"] = json.dumps(
                                    {"timestamp": np.datetime64("now").item()}
                                )
                                await client.setex(key, self._ttl, json.dumps(data))
                                
                                return {
                                    "response": data.get("response"),
                                    "similarity": similarity,
                                    "metadata": data.get("metadata", {}),
                                    "hits": data["hits"],
                                }
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.error(f"Error processing cached data: {e}")
                        continue
            
            return None
            
        except RedisError as e:
            logger.error(f"Redis error in get_similar: {e}")
            return None

    async def store(
        self, query: str, query_embedding: np.ndarray, response: str, metadata: Dict[str, Any]
    ) -> bool:
        """Store query and response with embedding."""
        try:
            client = await self.pool.get_client()
            
            # Generate cache key from query hash
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_key = f"{self._cache_prefix}{query_hash}"
            
            # Prepare data for storage
            cache_data = {
                "query": query,
                "embedding": query_embedding.tolist(),
                "response": response,
                "metadata": metadata,
                "hits": 0,
                "created_at": json.dumps({"timestamp": np.datetime64("now").item()}),
            }
            
            # Store in Redis with TTL
            result = await client.setex(cache_key, self._ttl, json.dumps(cache_data))
            
            # Also store in index for tenant-based clearing
            if metadata.get("tenant_id"):
                index_key = f"{self._index_prefix}{metadata['tenant_id']}"
                await client.sadd(index_key, cache_key)
                await client.expire(index_key, self._ttl)
            
            return result
            
        except RedisError as e:
            logger.error(f"Redis error in store: {e}")
            return False

    async def clear_tenant_cache(self, tenant_id: str) -> int:
        """Clear all cache entries for a tenant."""
        try:
            client = await self.pool.get_client()
            
            # Get tenant index key
            index_key = f"{self._index_prefix}{tenant_id}"
            
            # Get all cache keys for this tenant
            cache_keys = await client.smembers(index_key)
            
            deleted_count = 0
            if cache_keys:
                # Delete all cache entries
                deleted_count = await client.delete(*cache_keys)
                
                # Delete the index key itself
                await client.delete(index_key)
            
            return deleted_count
            
        except RedisError as e:
            logger.error(f"Redis error in clear_tenant_cache: {e}")
            return 0


class VectorCache(IVectorCache):
    """Vector cache for embeddings using Redis."""

    def __init__(self, pool: RedisConnectionPool):
        """Initialize vector cache."""
        self.pool = pool
        self._cache_prefix = "vector:"
        self._ttl = 3600 * 24 * 7  # 7 days for vector cache

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{self._cache_prefix}{text_hash}"

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text."""
        try:
            client = await self.pool.get_client()
            cache_key = self._get_cache_key(text)
            
            cached_data = await client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Update hit count
                data["hits"] = data.get("hits", 0) + 1
                await client.setex(cache_key, self._ttl, json.dumps(data))
                return data.get("embedding")
            
            return None
            
        except RedisError as e:
            logger.error(f"Redis error in get_embedding: {e}")
            return None

    async def store_embedding(self, text: str, embedding: List[float]) -> bool:
        """Store text embedding in cache."""
        try:
            client = await self.pool.get_client()
            cache_key = self._get_cache_key(text)
            
            cache_data = {
                "text": text[:200],  # Store first 200 chars for reference
                "embedding": embedding,
                "hits": 0,
                "created_at": json.dumps({"timestamp": np.datetime64("now").item()}),
            }
            
            return await client.setex(cache_key, self._ttl, json.dumps(cache_data))
            
        except RedisError as e:
            logger.error(f"Redis error in store_embedding: {e}")
            return False

    async def get_batch_embeddings(self, texts: List[str]) -> Dict[str, List[float]]:
        """Get cached embeddings for multiple texts."""
        try:
            client = await self.pool.get_client()
            
            # Prepare cache keys
            cache_keys = [self._get_cache_key(text) for text in texts]
            
            # Get all values in a pipeline for efficiency
            pipe = client.pipeline()
            for key in cache_keys:
                pipe.get(key)
            
            results = await pipe.execute()
            
            # Build response dictionary
            embeddings = {}
            for text, result in zip(texts, results):
                if result:
                    try:
                        data = json.loads(result)
                        embeddings[text] = data.get("embedding")
                    except json.JSONDecodeError:
                        continue
            
            return embeddings
            
        except RedisError as e:
            logger.error(f"Redis error in get_batch_embeddings: {e}")
            return {}

    async def store_batch_embeddings(self, embeddings: Dict[str, List[float]]) -> bool:
        """Store multiple text embeddings in cache."""
        try:
            client = await self.pool.get_client()
            
            # Use pipeline for batch operations
            pipe = client.pipeline()
            
            for text, embedding in embeddings.items():
                cache_key = self._get_cache_key(text)
                cache_data = {
                    "text": text[:200],
                    "embedding": embedding,
                    "hits": 0,
                    "created_at": json.dumps({"timestamp": np.datetime64("now").item()}),
                }
                pipe.setex(cache_key, self._ttl, json.dumps(cache_data))
            
            results = await pipe.execute()
            return all(results)
            
        except RedisError as e:
            logger.error(f"Redis error in store_batch_embeddings: {e}")
            return False
