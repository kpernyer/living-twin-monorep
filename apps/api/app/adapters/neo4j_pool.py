"""Neo4j connection pool implementation."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired

logger = logging.getLogger(__name__)


class Neo4jConnectionPool:
    """Neo4j connection pool with async support and health checking."""
    
    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        max_connections: int = 50,
        connection_acquisition_timeout: float = 30.0,
        max_transaction_retry_time: float = 30.0,
    ):
        """Initialize Neo4j connection pool."""
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: Optional[AsyncDriver] = None
        self._config = {
            "max_connection_pool_size": max_connections,
            "connection_acquisition_timeout": connection_acquisition_timeout,
            "max_transaction_retry_time": max_transaction_retry_time,
            "keep_alive": True,
            "encrypted": False if "localhost" in uri or "127.0.0.1" in uri else True,
        }
        self._health_check_query = "RETURN 1 as health"
        self._pool_metrics = {
            "connections_created": 0,
            "connections_closed": 0,
            "connections_failed": 0,
            "queries_executed": 0,
            "queries_failed": 0,
        }

    async def connect(self) -> None:
        """Initialize the driver and connection pool."""
        if not self._driver:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    **self._config
                )
                # Verify connection
                await self.health_check()
                logger.info(f"Neo4j connection pool initialized: {self.uri}")
            except Exception as e:
                logger.error(f"Failed to initialize Neo4j connection pool: {e}")
                raise

    async def close(self) -> None:
        """Close the driver and all connections."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection pool closed")

    @asynccontextmanager
    async def get_session(self, database: Optional[str] = None):
        """Get a session from the pool with automatic resource management."""
        if not self._driver:
            await self.connect()
        
        session = None
        try:
            session = self._driver.session(
                database=database or self.database,
                default_access_mode="WRITE"
            )
            self._pool_metrics["connections_created"] += 1
            yield session
        except (ServiceUnavailable, SessionExpired) as e:
            self._pool_metrics["connections_failed"] += 1
            logger.error(f"Neo4j session error: {e}")
            # Attempt to reconnect
            await self.reconnect()
            raise
        except Neo4jError as e:
            self._pool_metrics["queries_failed"] += 1
            logger.error(f"Neo4j query error: {e}")
            raise
        finally:
            if session:
                await session.close()
                self._pool_metrics["connections_closed"] += 1

    async def reconnect(self) -> None:
        """Reconnect to Neo4j after connection failure."""
        logger.info("Attempting to reconnect to Neo4j...")
        await self.close()
        await asyncio.sleep(1)  # Brief delay before reconnecting
        await self.connect()

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a query with automatic session management."""
        async with self.get_session(database) as session:
            try:
                result = await session.run(query, parameters or {})
                records = await result.data()
                self._pool_metrics["queries_executed"] += 1
                return records
            except Exception as e:
                self._pool_metrics["queries_failed"] += 1
                logger.error(f"Query execution failed: {e}")
                raise

    async def execute_write_transaction(
        self,
        transaction_function,
        *args,
        database: Optional[str] = None,
        **kwargs
    ):
        """Execute a write transaction with automatic retry."""
        async with self.get_session(database) as session:
            try:
                result = await session.execute_write(
                    transaction_function, *args, **kwargs
                )
                self._pool_metrics["queries_executed"] += 1
                return result
            except Exception as e:
                self._pool_metrics["queries_failed"] += 1
                logger.error(f"Write transaction failed: {e}")
                raise

    async def execute_read_transaction(
        self,
        transaction_function,
        *args,
        database: Optional[str] = None,
        **kwargs
    ):
        """Execute a read transaction with automatic retry."""
        async with self.get_session(database) as session:
            try:
                result = await session.execute_read(
                    transaction_function, *args, **kwargs
                )
                self._pool_metrics["queries_executed"] += 1
                return result
            except Exception as e:
                self._pool_metrics["queries_failed"] += 1
                logger.error(f"Read transaction failed: {e}")
                raise

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Neo4j connection."""
        try:
            start_time = asyncio.get_event_loop().time()
            result = await self.execute_query(self._health_check_query)
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "database": self.database,
                "uri": self.uri,
                "metrics": self._pool_metrics,
            }
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": self.database,
                "uri": self.uri,
                "metrics": self._pool_metrics,
            }

    async def get_pool_metrics(self) -> Dict[str, Any]:
        """Get connection pool metrics."""
        if self._driver:
            # Get driver metrics if available
            return {
                **self._pool_metrics,
                "pool_size": self._config["max_connection_pool_size"],
                "status": "active",
            }
        return {
            **self._pool_metrics,
            "pool_size": 0,
            "status": "inactive",
        }

    async def create_indexes(self, indexes: List[str]) -> None:
        """Create database indexes for optimization."""
        for index_query in indexes:
            try:
                await self.execute_query(index_query)
                logger.info(f"Created index: {index_query[:50]}...")
            except Neo4jError as e:
                if "already exists" in str(e).lower():
                    logger.debug(f"Index already exists: {index_query[:50]}...")
                else:
                    logger.error(f"Failed to create index: {e}")
                    raise


class Neo4jBatchProcessor:
    """Batch processing utilities for Neo4j operations."""
    
    def __init__(self, pool: Neo4jConnectionPool, batch_size: int = 1000):
        """Initialize batch processor."""
        self.pool = pool
        self.batch_size = batch_size

    async def batch_write(
        self,
        query: str,
        data: List[Dict[str, Any]],
        database: Optional[str] = None,
    ) -> int:
        """Execute batch write operations."""
        total_processed = 0
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            
            async def write_batch(tx):
                result = await tx.run(query, {"batch": batch})
                summary = await result.consume()
                return summary.counters
            
            counters = await self.pool.execute_write_transaction(
                write_batch, database=database
            )
            total_processed += len(batch)
            
            logger.debug(f"Processed batch {i // self.batch_size + 1}: {len(batch)} items")
        
        return total_processed

    async def batch_read(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        page_size: int = 1000,
    ):
        """Execute paginated read operations."""
        skip = 0
        all_results = []
        
        while True:
            paginated_query = f"{query} SKIP {skip} LIMIT {page_size}"
            results = await self.pool.execute_query(
                paginated_query, parameters, database
            )
            
            if not results:
                break
            
            all_results.extend(results)
            skip += page_size
            
            if len(results) < page_size:
                break
        
        return all_results


class Neo4jTransactionManager:
    """Manage complex transactions with rollback support."""
    
    def __init__(self, session: AsyncSession):
        """Initialize transaction manager."""
        self.session = session
        self.transaction = None

    async def __aenter__(self):
        """Start a transaction."""
        self.transaction = await self.session.begin_transaction()
        return self.transaction

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction based on exceptions."""
        if self.transaction:
            if exc_type:
                await self.transaction.rollback()
                logger.warning(f"Transaction rolled back due to: {exc_val}")
            else:
                await self.transaction.commit()
                logger.debug("Transaction committed successfully")
