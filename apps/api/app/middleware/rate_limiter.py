"""Rate limiting middleware for API protection."""

import logging
from typing import Callable, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis.asyncio as redis

logger = logging.getLogger(__name__)


def get_real_client_ip(request: Request) -> str:
    """Get the real client IP address, considering proxies."""
    # Check for common proxy headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to the remote address
    return get_remote_address(request)


def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting (user ID if authenticated, IP otherwise)."""
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user and user.get("uid"):
        return f"user:{user['uid']}"
    
    # Fall back to IP address
    return f"ip:{get_real_client_ip(request)}"


class RateLimiter:
    """Enhanced rate limiter with Redis backend and multiple strategies."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_limits: list = None,
        storage_uri: Optional[str] = None,
    ):
        """Initialize rate limiter with Redis backend."""
        # Set default limits if not provided
        if default_limits is None:
            default_limits = ["100 per minute", "1000 per hour"]
        
        # Configure storage backend
        if redis_url:
            storage_uri = redis_url
        elif not storage_uri:
            # Fall back to in-memory storage (not recommended for production)
            storage_uri = "memory://"
            logger.warning("Using in-memory rate limit storage. Use Redis for production.")
        
        # Create limiter with custom key function
        self.limiter = Limiter(
            key_func=get_user_identifier,
            default_limits=default_limits,
            storage_uri=storage_uri,
            strategy="fixed-window",  # Can be "fixed-window" or "moving-window"
        )
        
        # Store limits for different endpoint categories
        self.endpoint_limits = {
            # Critical endpoints - strict limits
            "/api/query": "10 per minute",
            "/api/query/ingest": "5 per minute",
            "/api/intelligence": "5 per minute",
            
            # Moderate endpoints
            "/api/query/conversation": "30 per minute",
            "/api/conversations": "50 per minute",
            
            # High-frequency endpoints - relaxed limits
            "/api/health": "100 per minute",
            "/api/health/ready": "100 per minute",
        }
        
        # Tenant-specific limits
        self.tenant_limits = {}
        
        # IP-based burst protection
        self.burst_limits = {
            "default": "20 per second",
            "authenticated": "30 per second",
        }

    def get_limit_for_endpoint(self, path: str) -> Optional[str]:
        """Get rate limit for specific endpoint."""
        # Check exact match first
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Check prefix matches
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        
        return None

    def limit(self, limit_string: str):
        """Decorator for applying rate limits to endpoints."""
        return self.limiter.limit(limit_string)

    def shared_limit(self, limit_string: str, scope: str):
        """Decorator for shared rate limits across multiple endpoints."""
        return self.limiter.shared_limit(limit_string, scope)

    def exempt(self, func: Callable):
        """Decorator to exempt an endpoint from rate limiting."""
        return self.limiter.exempt(func)


class RateLimitMiddleware:
    """Custom middleware for handling rate limiting with enhanced features."""
    
    def __init__(
        self,
        app,
        rate_limiter: RateLimiter,
        exclude_paths: list = None,
    ):
        """Initialize rate limit middleware."""
        self.app = app
        self.rate_limiter = rate_limiter
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

    async def __call__(self, request: Request, call_next):
        """Process request through rate limiter."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get user/IP identifier
        identifier = get_user_identifier(request)
        
        # Check burst protection
        try:
            # This would integrate with the rate limiter
            # For now, we'll rely on the decorator-based approach
            response = await call_next(request)
            
            # Add rate limit headers to response
            if hasattr(request.state, "view_rate_limit"):
                limit_info = request.state.view_rate_limit
                response.headers["X-RateLimit-Limit"] = str(limit_info.get("limit", ""))
                response.headers["X-RateLimit-Remaining"] = str(limit_info.get("remaining", ""))
                response.headers["X-RateLimit-Reset"] = str(limit_info.get("reset", ""))
            
            return response
            
        except RateLimitExceeded as e:
            # Custom error response for rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests from {identifier}",
                    "retry_after": e.retry_after if hasattr(e, "retry_after") else 60,
                },
                headers={
                    "Retry-After": str(e.retry_after if hasattr(e, "retry_after") else 60),
                    "X-RateLimit-Limit": str(e.limit if hasattr(e, "limit") else ""),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(e.reset if hasattr(e, "reset") else ""),
                },
            )


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    identifier = get_user_identifier(request)
    
    # Log rate limit violation
    logger.warning(
        f"Rate limit exceeded for {identifier} on {request.url.path}",
        extra={
            "identifier": identifier,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    # Return custom error response
    response = JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "API rate limit exceeded. Please retry after some time.",
            "path": request.url.path,
            "retry_after": 60,
        },
    )
    response.headers["Retry-After"] = "60"
    return response


class TenantRateLimiter:
    """Tenant-specific rate limiting."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize tenant rate limiter."""
        self.redis = redis_client
        self.default_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 10000,
        }

    async def check_tenant_limit(
        self,
        tenant_id: str,
        custom_limits: Optional[dict] = None,
    ) -> tuple[bool, dict]:
        """Check if tenant has exceeded rate limits."""
        limits = custom_limits or self.default_limits
        
        # Check each time window
        for window, limit in limits.items():
            key = f"rate_limit:{tenant_id}:{window}"
            
            # Get current count
            count = await self.redis.get(key)
            if count and int(count) >= limit:
                return False, {
                    "exceeded": window,
                    "limit": limit,
                    "current": int(count),
                }
        
        # Increment counters
        pipe = self.redis.pipeline()
        for window, limit in limits.items():
            key = f"rate_limit:{tenant_id}:{window}"
            pipe.incr(key)
            
            # Set expiration based on window
            if window == "requests_per_minute":
                pipe.expire(key, 60)
            elif window == "requests_per_hour":
                pipe.expire(key, 3600)
            elif window == "requests_per_day":
                pipe.expire(key, 86400)
        
        await pipe.execute()
        
        return True, {"status": "ok", "tenant_id": tenant_id}


def setup_rate_limiting(app, redis_url: Optional[str] = None) -> RateLimiter:
    """Set up rate limiting for the FastAPI application."""
    # Create rate limiter
    rate_limiter = RateLimiter(redis_url=redis_url)
    
    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    
    # Add middleware
    app.add_middleware(
        RateLimitMiddleware,
        rate_limiter=rate_limiter,
    )
    
    # Store limiter in app state for access in routes
    app.state.limiter = rate_limiter.limiter
    
    logger.info("Rate limiting configured successfully")
    
    return rate_limiter
