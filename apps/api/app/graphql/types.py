"""
GraphQL types for Living Twin Strategic Intelligence Platform.

These types correspond to domain models and provide a GraphQL interface
over the existing REST API services.
"""
import strawberry
from datetime import datetime
from typing import List, Optional
from enum import Enum

from ..domain.intelligence_models import (
    TruthCategory as DomainTruthCategory,
    ImpactLevel as DomainImpactLevel,
    CommunicationType as DomainCommunicationType,
    AnalysisDepth as DomainAnalysisDepth,
    StrategicAlignmentZone as DomainStrategicAlignmentZone,
)


# Enums
@strawberry.enum
class TruthCategory(Enum):
    MARKET = "market"
    COMPETITIVE = "competitive"
    TECHNOLOGY = "technology"
    REGULATORY = "regulatory"
    ORGANIZATIONAL = "organizational"
    FINANCIAL = "financial"


@strawberry.enum
class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@strawberry.enum
class CommunicationType(Enum):
    INSIGHT = "insight"
    ALERT = "alert"
    RECOMMENDATION = "recommendation"
    BRIEFING = "briefing"


@strawberry.enum
class AnalysisDepth(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@strawberry.enum
class StrategicAlignmentZone(Enum):
    CRITICAL = "critical"
    DEGRADED = "degraded" 
    HEALTHY = "healthy"
    OPTIMAL = "optimal"


# Core Types
@strawberry.type
class OrganizationalTruth:
    """Strategic insight representing fundamental organizational knowledge."""
    
    id: str
    statement: str
    confidence: float
    evidence_count: int
    last_updated: datetime
    version: int
    category: TruthCategory
    impact_level: ImpactLevel
    tenant_id: str
    created_at: datetime
    strategic_goals: List[str]
    related_truths: List[str]
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class CommunicationQueue:
    """Priority communication item in the queue."""
    
    id: str
    user_id: str
    tenant_id: str
    topic: str
    content: str
    type: CommunicationType
    priority: int
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    attempts: int = 0
    escalation_level: int = 0
    related_truths: List[str] = strawberry.field(default_factory=list)
    related_goals: List[str] = strawberry.field(default_factory=list)
    source_report: Optional[str] = None
    delivered: bool = False
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class CompiledReport:
    """Compiled analysis report based on agent results."""
    
    id: str
    title: str
    summary: str
    insights: List[str]
    recommendations: List[str]
    data_sources: List[str]
    analysis_depth: AnalysisDepth
    tenant_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    priority: Optional[str] = None
    related_truths: List[str] = strawberry.field(default_factory=list)
    agent_results: List[str] = strawberry.field(default_factory=list)
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class StrategicAlignmentScorecard:
    """Comprehensive strategic alignment scorecard for an organization."""
    
    id: str
    tenant_id: str
    measurement_date: datetime
    strategic_initiative_velocity: float
    goal_cascade_alignment: float
    decision_strategy_consistency: float
    resource_allocation_efficiency: float
    strategic_response_time: float
    cross_functional_alignment: float
    strategic_communication_effectiveness: float
    adaptation_speed: float
    overall_alignment_score: float
    alignment_zone: StrategicAlignmentZone
    strategic_velocity: float
    trend_30_days: Optional[str] = None
    trend_60_days: Optional[str] = None
    trend_90_days: Optional[str] = None
    risk_indicators: List[str] = strawberry.field(default_factory=list)
    priority_interventions: List[str] = strawberry.field(default_factory=list)
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class DocumentInfo:
    """Information about ingested documents."""
    
    id: str
    title: str
    type: str
    created_at: datetime
    chunks: int


@strawberry.type
class QueryResult:
    """Result from a document query."""
    
    answer: str
    sources: List[strawberry.scalars.JSON]
    confidence: Optional[float] = None
    query_id: str


@strawberry.type
class SystemHealth:
    """System health information."""
    
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    services: List[strawberry.scalars.JSON]
    system_metrics: strawberry.scalars.JSON


# Dashboard aggregation type
@strawberry.type
class StrategicIntelligenceDashboard:
    """Aggregated dashboard data for strategic intelligence."""
    
    recent_truths: List[OrganizationalTruth]
    pending_communications: List[CommunicationQueue]
    high_impact_truths: List[OrganizationalTruth]
    recent_reports: List[CompiledReport]
    alignment_scorecard: Optional[StrategicAlignmentScorecard] = None
    total_truths: int
    queue_length: int
    system_health: SystemHealth


# Input types
@strawberry.input
class TruthsFilter:
    """Filter for querying organizational truths."""
    
    categories: Optional[List[TruthCategory]] = None
    impact_levels: Optional[List[ImpactLevel]] = None
    confidence_min: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


@strawberry.input
class CommunicationsFilter:
    """Filter for querying priority communications."""
    
    types: Optional[List[CommunicationType]] = None
    priority_min: Optional[int] = None
    delivered: Optional[bool] = None
    acknowledged: Optional[bool] = None
    limit: int = 20
    offset: int = 0


@strawberry.input
class DocumentQueryInput:
    """Input for document querying."""
    
    question: str
    k: int = 5
    tenant_id: Optional[str] = None


@strawberry.input
class IntelligenceGenerationInput:
    """Input for generating strategic intelligence."""
    
    agent_ids: List[str]
    template_id: str
    analysis_depth: Optional[AnalysisDepth] = None
    variables: Optional[strawberry.scalars.JSON] = None
    priority: Optional[str] = None


# Response types
@strawberry.type
class IntelligenceGenerationResponse:
    """Response from intelligence generation."""
    
    id: str
    request_id: str
    truths: List[OrganizationalTruth]
    reports: List[CompiledReport]
    communications: List[CommunicationQueue]
    generated_at: datetime
    processing_time_seconds: Optional[float] = None
    token_count: Optional[int] = None
