"""Health check endpoints for operational monitoring."""

import asyncio
import logging
import os
import psutil
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


class HealthStatus(BaseModel):
    """Health status model."""
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Timestamp of health check")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class SystemMetrics(BaseModel):
    """System metrics model."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_mb: float = Field(..., description="Memory used in MB")
    memory_available_mb: float = Field(..., description="Available memory in MB")
    disk_percent: float = Field(..., description="Disk usage percentage")
    disk_used_gb: float = Field(..., description="Disk used in GB")
    disk_free_gb: float = Field(..., description="Free disk space in GB")
    active_connections: int = Field(..., description="Number of active connections")
    process_count: int = Field(..., description="Number of running processes")


class ServiceHealth(BaseModel):
    """Individual service health status."""
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status (healthy/degraded/unhealthy)")
    latency_ms: Optional[float] = Field(None, description="Service latency in milliseconds")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional service metadata")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Timestamp of health check")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    services: List[ServiceHealth] = Field(..., description="Individual service health")
    system: SystemMetrics = Field(..., description="System metrics")
    checks_passed: int = Field(..., description="Number of health checks passed")
    checks_failed: int = Field(..., description="Number of health checks failed")


class HealthChecker:
    """Health check service for monitoring system components."""
    
    def __init__(self):
        """Initialize health checker."""
        self.start_time = datetime.utcnow()
        self.version = os.getenv("API_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self._cache = {}
        self._cache_ttl = 5  # Cache health results for 5 seconds

    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
            active_connections=len(psutil.net_connections()),
            process_count=len(psutil.pids()),
        )

    async def check_database(self, di_container) -> ServiceHealth:
        """Check database health."""
        try:
            if hasattr(di_container, 'neo4j_pool'):
                result = await di_container.neo4j_pool.health_check()
                return ServiceHealth(
                    name="neo4j",
                    status=result.get("status", "unknown"),
                    latency_ms=result.get("latency_ms"),
                    error=result.get("error"),
                    metadata=result.get("metrics"),
                )
            else:
                # Fallback for legacy Neo4j connection
                # Simplified health check
                return ServiceHealth(
                    name="neo4j",
                    status="unknown",
                    error="Connection pool not available",
                )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ServiceHealth(
                name="neo4j",
                status="unhealthy",
                error=str(e),
            )

    async def check_redis(self, di_container) -> ServiceHealth:
        """Check Redis cache health."""
        try:
            if hasattr(di_container, 'redis_pool'):
                start = asyncio.get_event_loop().time()
                client = await di_container.redis_pool.get_client()
                await client.ping()
                latency_ms = (asyncio.get_event_loop().time() - start) * 1000
                
                return ServiceHealth(
                    name="redis",
                    status="healthy",
                    latency_ms=round(latency_ms, 2),
                )
            else:
                return ServiceHealth(
                    name="redis",
                    status="not_configured",
                    error="Redis not configured",
                )
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return ServiceHealth(
                name="redis",
                status="unhealthy",
                error=str(e),
            )

    async def check_firebase(self, di_container) -> ServiceHealth:
        """Check Firebase/Auth health."""
        try:
            if hasattr(di_container, 'auth') and di_container.auth:
                # Simple check - verify Firebase Admin SDK is initialized
                return ServiceHealth(
                    name="firebase",
                    status="healthy",
                    metadata={"project_id": getattr(di_container.auth, 'project_id', 'unknown')},
                )
            else:
                return ServiceHealth(
                    name="firebase",
                    status="not_configured",
                    error="Firebase not configured",
                )
        except Exception as e:
            logger.error(f"Firebase health check failed: {e}")
            return ServiceHealth(
                name="firebase",
                status="unhealthy",
                error=str(e),
            )

    async def check_openai(self, di_container) -> ServiceHealth:
        """Check OpenAI API health."""
        try:
            if hasattr(di_container, 'llm'):
                # Could make a minimal API call to check connectivity
                # For now, just check if configured
                return ServiceHealth(
                    name="openai",
                    status="configured",
                    metadata={"provider": "openai"},
                )
            else:
                return ServiceHealth(
                    name="llm",
                    status="not_configured",
                    error="LLM provider not configured",
                )
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return ServiceHealth(
                name="openai",
                status="unhealthy",
                error=str(e),
            )

    async def check_all_services(self, di_container) -> List[ServiceHealth]:
        """Check all services health."""
        # Run all checks concurrently
        results = await asyncio.gather(
            self.check_database(di_container),
            self.check_redis(di_container),
            self.check_firebase(di_container),
            self.check_openai(di_container),
            return_exceptions=True,
        )
        
        # Handle any exceptions
        services = []
        for result in results:
            if isinstance(result, Exception):
                services.append(ServiceHealth(
                    name="unknown",
                    status="error",
                    error=str(result),
                ))
            else:
                services.append(result)
        
        return services

    def determine_overall_status(self, services: List[ServiceHealth]) -> str:
        """Determine overall health status based on service statuses."""
        statuses = [s.status for s in services]
        
        if all(s in ["healthy", "configured", "not_configured"] for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        else:
            return "degraded"


# Global health checker instance
health_checker = HealthChecker()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint for load balancers."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=health_checker.version,
        uptime_seconds=health_checker.get_uptime(),
    )


@router.get("/healthz")
async def healthz():
    """Simple health check endpoint (Kubernetes style)."""
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/readyz")
async def readyz():
    """Simple readiness check endpoint (Kubernetes style)."""
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/live", response_model=HealthStatus)
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    return HealthStatus(
        status="alive",
        timestamp=datetime.utcnow().isoformat(),
        version=health_checker.version,
        uptime_seconds=health_checker.get_uptime(),
    )


@router.get("/health/ready", response_model=DetailedHealthResponse)
async def readiness_probe(request):
    """Kubernetes readiness probe with detailed service checks."""
    from .. import di
    
    # Get DI container
    container = di.container if hasattr(di, 'container') else None
    if not container:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dependency injection container not initialized",
        )
    
    # Check all services
    services = await health_checker.check_all_services(container)
    
    # Get system metrics
    system_metrics = health_checker.get_system_metrics()
    
    # Count passed/failed checks
    checks_passed = sum(1 for s in services if s.status in ["healthy", "configured"])
    checks_failed = sum(1 for s in services if s.status in ["unhealthy", "error"])
    
    # Determine overall status
    overall_status = health_checker.determine_overall_status(services)
    
    response = DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=health_checker.version,
        environment=health_checker.environment,
        uptime_seconds=health_checker.get_uptime(),
        services=services,
        system=system_metrics,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
    )
    
    # Return appropriate status code
    if overall_status == "unhealthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.dict(),
        )
    elif overall_status == "degraded":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict(),
            headers={"X-Health-Status": "degraded"},
        )
    else:
        return response


@router.get("/health/metrics")
async def get_metrics():
    """Get detailed system and application metrics."""
    from .. import di
    
    container = di.container if hasattr(di, 'container') else None
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": health_checker.get_system_metrics().dict(),
        "application": {
            "version": health_checker.version,
            "environment": health_checker.environment,
            "uptime_seconds": health_checker.get_uptime(),
        },
    }
    
    # Add Neo4j pool metrics if available
    if container and hasattr(container, 'neo4j_pool'):
        metrics["neo4j"] = await container.neo4j_pool.get_pool_metrics()
    
    # Add Redis metrics if available
    if container and hasattr(container, 'redis_pool'):
        # Could add Redis-specific metrics here
        metrics["redis"] = {"status": "configured"}
    
    return metrics


@router.post("/health/shutdown")
async def shutdown():
    """Graceful shutdown endpoint (should be protected in production)."""
    # This would typically be protected by authentication
    # and only accessible from internal networks
    
    logger.info("Shutdown requested via health endpoint")
    
    # Perform cleanup
    from .. import di
    container = di.container if hasattr(di, 'container') else None
    
    if container:
        # Close database connections
        if hasattr(container, 'neo4j_pool'):
            await container.neo4j_pool.close()
        
        # Close Redis connections
        if hasattr(container, 'redis_pool'):
            await container.redis_pool.close()
    
    return {"status": "shutting_down", "message": "Graceful shutdown initiated"}
