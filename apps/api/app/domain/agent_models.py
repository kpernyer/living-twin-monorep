"""AI Agent domain models for the Living Twin application."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of AI agents."""

    TENANT_SPECIFIC = "tenant_specific"
    SHARED = "shared"


class AgentStatus(str, Enum):
    """Agent status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RUNNING = "running"


class AgentCapability(str, Enum):
    """Agent capabilities."""

    NEWS_MONITORING = "news_monitoring"
    TREND_ANALYSIS = "trend_analysis"
    COMPETITOR_TRACKING = "competitor_tracking"
    TECHNOLOGY_TRENDS = "technology_trends"
    MARKET_ANALYSIS = "market_analysis"
    CUSTOM_KEYWORD_MONITORING = "custom_keyword_monitoring"


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    keywords: List[str] = Field(default_factory=list, max_items=10)
    sources: List[str] = Field(default_factory=list)
    update_frequency_minutes: int = Field(default=60, ge=5)
    max_results_per_update: int = Field(default=20, ge=1, le=100)
    isolation_mode: bool = Field(default=False)
    custom_prompt: Optional[str] = None
    api_keys: Dict[str, str] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)


class Agent(BaseModel):
    """AI Agent model."""

    id: str
    name: str
    description: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.INACTIVE
    config: AgentConfig
    tenant_id: Optional[str] = None  # None for shared agents
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentExecution(BaseModel):
    """Agent execution record."""

    id: str
    agent_id: str
    tenant_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed
    results_count: int = 0
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Result from an agent execution."""

    id: str
    agent_id: str
    execution_id: str
    tenant_id: Optional[str] = None
    title: str
    content: str
    source_url: Optional[str] = None
    source_name: str
    published_at: Optional[datetime] = None
    relevance_score: Optional[float] = None
    keywords_matched: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None  # positive, negative, neutral
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    """Request to create or update an agent."""

    name: str
    description: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    config: AgentConfig
    tenant_id: Optional[str] = None


class AgentExecutionRequest(BaseModel):
    """Request to execute an agent."""

    agent_id: str
    tenant_id: Optional[str] = None
    force_run: bool = False
    isolation_mode: Optional[bool] = None


class AgentResultQuery(BaseModel):
    """Query for agent results."""

    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    agent_type: Optional[AgentType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    keywords: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class AgentHealthCheck(BaseModel):
    """Agent health check result."""

    agent_id: str
    status: AgentStatus
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    error_count: int = 0
    success_rate: float = 0.0
    average_execution_time: Optional[float] = None
    is_healthy: bool = True
    issues: List[str] = Field(default_factory=list)
