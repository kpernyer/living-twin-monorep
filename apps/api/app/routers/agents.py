"""API router for AI agent management."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

from ..domain.agent_models import (
    Agent, AgentRequest, AgentExecutionRequest, AgentResultQuery,
    AgentHealthCheck, AgentType, AgentCapability
)
from ..domain.agent_service import AgentService
from ..adapters.firebase_auth import get_current_user, get_current_tenant

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_service() -> AgentService:
    """Get agent service instance."""
    # This would be injected via DI in a real implementation
    return AgentService()


@router.post("/", response_model=Agent)
async def create_agent(
    request: AgentRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """Create a new AI agent."""
    try:
        # Set tenant_id from current tenant if not provided
        if not request.tenant_id:
            request.tenant_id = current_tenant.id
        
        # Validate tenant access for tenant-specific agents
        if request.agent_type == AgentType.TENANT_SPECIFIC and request.tenant_id != current_tenant.id:
            raise HTTPException(status_code=403, detail="Cannot create agent for different tenant")
        
        agent = await agent_service.create_agent(request)
        return agent
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/", response_model=List[Agent])
async def list_agents(
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """List agents for the current tenant and shared agents."""
    try:
        # Get tenant-specific agents
        tenant_agents = agent_service.get_agents_by_tenant(current_tenant.id)
        
        # Get shared agents
        shared_agents = agent_service.get_shared_agents()
        
        # Combine and filter
        all_agents = tenant_agents + shared_agents
        
        if agent_type:
            all_agents = [agent for agent in all_agents if agent.agent_type == agent_type]
        
        return all_agents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get a specific agent by ID."""
    try:
        # This would need to be implemented in the service
        # For now, return a mock response
        raise HTTPException(status_code=501, detail="Not implemented yet")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    request: AgentRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Update an existing agent."""
    try:
        # Set tenant_id from current tenant if not provided
        if not request.tenant_id:
            request.tenant_id = current_tenant.id
        
        # Validate tenant access
        if request.agent_type == AgentType.TENANT_SPECIFIC and request.tenant_id != current_tenant.id:
            raise HTTPException(status_code=403, detail="Cannot update agent for different tenant")
        
        agent = await agent_service.update_agent(agent_id, request)
        return agent
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Delete an agent."""
    try:
        await agent_service.delete_agent(agent_id)
        return {"message": "Agent deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Activate an agent."""
    try:
        await agent_service.activate_agent(agent_id)
        return {"message": "Agent activated successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate agent: {str(e)}")


@router.post("/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Deactivate an agent."""
    try:
        await agent_service.deactivate_agent(agent_id)
        return {"message": "Agent deactivated successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate agent: {str(e)}")


@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: str,
    request: AgentExecutionRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Execute an agent manually."""
    try:
        # Set agent_id from path
        request.agent_id = agent_id
        
        execution = await agent_service.execute_agent(request)
        return execution
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute agent: {str(e)}")


@router.get("/{agent_id}/results")
async def get_agent_results(
    agent_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    agent_type: Optional[AgentType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    keywords: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get agent results with filtering and pagination."""
    try:
        # Parse keywords from query string
        keyword_list = keywords.split(",") if keywords else None
        
        query = AgentResultQuery(
            agent_id=agent_id,
            tenant_id=tenant_id or current_tenant.id,
            agent_type=agent_type,
            date_from=date_from,
            date_to=date_to,
            keywords=keyword_list,
            limit=limit,
            offset=offset
        )
        
        results = await agent_service.get_agent_results(query)
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent results: {str(e)}")


@router.get("/{agent_id}/health", response_model=AgentHealthCheck)
async def get_agent_health(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get health status for an agent."""
    try:
        health = await agent_service.get_agent_health(agent_id)
        return health
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent health: {str(e)}")


@router.get("/capabilities")
async def get_available_capabilities():
    """Get list of available agent capabilities."""
    return {
        "capabilities": [
            {
                "value": capability.value,
                "name": capability.name,
                "description": capability.__doc__ or f"Agent capability: {capability.value}"
            }
            for capability in AgentCapability
        ]
    }


@router.post("/setup-demo")
async def setup_demo_agents(
    agent_service: AgentService = Depends(get_agent_service),
    current_tenant = Depends(get_current_tenant)
):
    """Setup demo agents for testing."""
    try:
        from ..domain.agent_models import AgentConfig
        
        # Create a tenant-specific news monitoring agent
        tenant_agent_request = AgentRequest(
            name="Competitor News Monitor",
            description="Monitors news about competitors and industry keywords",
            agent_type=AgentType.TENANT_SPECIFIC,
            capabilities=[AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING],
            config=AgentConfig(
                keywords=["competitor", "industry", "market trends"],
                update_frequency_minutes=30,
                max_results_per_update=10,
                isolation_mode=False
            ),
            tenant_id=current_tenant.id
        )
        
        tenant_agent = await agent_service.create_agent(tenant_agent_request)
        await agent_service.activate_agent(tenant_agent.id)
        
        # Create a shared technology trends agent
        shared_agent_request = AgentRequest(
            name="Global Tech Trends",
            description="Monitors global technology trends and innovations",
            agent_type=AgentType.SHARED,
            capabilities=[AgentCapability.TECHNOLOGY_TRENDS, AgentCapability.TREND_ANALYSIS],
            config=AgentConfig(
                keywords=["artificial intelligence", "machine learning", "cloud computing"],
                update_frequency_minutes=60,
                max_results_per_update=20,
                isolation_mode=False
            ),
            tenant_id=None
        )
        
        shared_agent = await agent_service.create_agent(shared_agent_request)
        await agent_service.activate_agent(shared_agent.id)
        
        return {
            "message": "Demo agents created successfully",
            "tenant_agent": tenant_agent,
            "shared_agent": shared_agent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup demo agents: {str(e)}")
