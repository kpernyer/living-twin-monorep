"""
GraphQL schema for Living Twin Strategic Intelligence Platform.
"""
import strawberry
from typing import Optional
from fastapi import Request

from .resolvers import Query, Mutation


def get_context(request: Request) -> dict:
    """
    Get GraphQL context from FastAPI request.
    
    This extracts user and tenant information from the request state
    and makes it available to GraphQL resolvers.
    """
    user = getattr(request.state, "user", {"uid": "dev", "tenantId": "demo", "role": "owner"})
    
    return {
        "request": request,
        "user_id": user.get("uid", "dev"),
        "tenant_id": user.get("tenantId", "demo"),
        "user_role": user.get("role", "owner"),
        "user_claims": user.get("claims", {}),
    }


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    description="""
    Living Twin Strategic Intelligence Platform GraphQL API
    
    This GraphQL API provides a unified interface for querying and managing
    strategic intelligence data, documents, and system health information.
    
    Key Features:
    - Strategic Intelligence Dashboard aggregation
    - Document querying with RAG
    - Priority communications management
    - System health monitoring
    - Strategic alignment analytics
    
    Authentication:
    All operations require Firebase JWT authentication via the Authorization header.
    User context is automatically injected into resolvers.
    """,
)
