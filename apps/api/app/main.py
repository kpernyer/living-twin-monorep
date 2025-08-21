from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from .config import load_config
from .di import container, init_container
from .routers import health, intelligence, rag, strategic_test
from .graphql.schema import schema, get_context

# OpenAPI metadata and configuration
openapi_tags = [
    {
        "name": "Health",
        "description": "System health monitoring and operational status endpoints. Includes comprehensive health checks, system metrics, and service status monitoring for production deployments."
    },
    {
        "name": "intelligence", 
        "description": "Strategic intelligence operations including SWOT analysis, competitive intelligence, and organizational insights. Provides AI-powered strategic decision support and business intelligence capabilities."
    },
    {
        "name": "Query",
        "description": "RAG (Retrieval-Augmented Generation) system and conversational AI endpoints. Enables document ingestion, semantic search, and conversational queries with context-aware responses."
    },
    {
        "name": "Strategic Test",
        "description": "Testing framework for strategic intelligence and signal detection capabilities. Provides comprehensive test scenarios, data setup, and validation for the strategic intelligence pipeline."
    }
]

app = FastAPI(
    title="Living Twin API",
    description="""
# Living Twin Strategic Intelligence Platform

A comprehensive API for strategic intelligence, competitive analysis, and AI-powered business insights.

## Key Capabilities

* **Strategic Intelligence**: SWOT analysis, Porter's Five Forces, competitive intelligence
* **RAG System**: Document ingestion, semantic search, conversational AI
* **Health Monitoring**: Comprehensive system health and performance monitoring  
* **Testing Framework**: End-to-end testing for strategic intelligence workflows

## Authentication

All endpoints require Firebase authentication via the `Authorization` header:
```
Authorization: Bearer <firebase-jwt-token>
```

Development environments support bypass mode for testing.

## Tenant Isolation

All data is isolated by tenant. Cross-tenant access is controlled by role-based permissions.
""",
    version="2.0.0",
    openapi_tags=openapi_tags,
    contact={
        "name": "Living Twin API Support",
        "url": "https://github.com/kpernyer/living-twin-monorep",
        "email": "support@livingtwin.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://livingtwin.com/license"
    },
    servers=[
        {"url": "https://api.livingtwin.com", "description": "Production server"},
        {"url": "https://staging-api.livingtwin.com", "description": "Staging server"}, 
        {"url": "http://localhost:8000", "description": "Development server"}
    ]
)
cfg = load_config()
init_container(cfg)

if cfg.allow_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if cfg.bypass_auth or request.url.path in ("/healthz", "/readyz", "/graphql", "/docs", "/redoc", "/openapi.json"):
        request.state.user = {"uid": "dev", "tenantId": "demo", "role": "owner", "claims": {}}
        return await call_next(request)
    try:
        token = request.headers.get("Authorization", "")
        user = container.auth.verify(token)
        request.state.user = user
        return await call_next(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Include REST API routers
app.include_router(health.router)
app.include_router(rag.router)
app.include_router(intelligence.router)
app.include_router(strategic_test.router)

# Add GraphQL endpoint
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,  # Enable GraphiQL interface in development
)

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])
