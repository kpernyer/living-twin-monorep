"""Domain models for the Strategic Intelligence system."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class TruthCategory(str, Enum):
    """Categories for strategic insights."""
    TECHNOLOGY = "technology"
    MARKET = "market"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"
    SOCIAL = "social"
    OPERATIONAL = "operational"


class ImpactLevel(str, Enum):
    """Impact levels for strategic insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisDepth(str, Enum):
    """Analysis depth levels."""
    SHALLOW = "shallow"
    DEEP = "deep"
    COMPREHENSIVE = "comprehensive"


class PriorityLevel(str, Enum):
    """Priority levels for priority communications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CommunicationType(str, Enum):
    """Types of priority communications."""
    NUDGE = "nudge"
    RECOMMENDATION = "recommendation"
    ORDER = "order"


class OrganizationalTruth(BaseModel):
    """Strategic insight entity representing fundamental organizational knowledge."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = Field(..., description="Clear, actionable statement")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    evidence_count: int = Field(default=0, ge=0, description="Number of supporting data points")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, ge=1)
    category: TruthCategory
    impact_level: ImpactLevel
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (stored as IDs, resolved by service layer)
    strategic_goals: List[str] = Field(default_factory=list)
    compiled_reports: List[str] = Field(default_factory=list)
    raw_data_sources: List[str] = Field(default_factory=list)
    related_truths: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class CompiledReport(BaseModel):
    """Compiled analysis report based on agent results."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    analysis_depth: AnalysisDepth
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    
    # Relationships
    related_truths: List[str] = Field(default_factory=list)
    agent_results: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class CommunicationQueue(BaseModel):
    """Priority communication item in the queue."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tenant_id: str
    topic: str
    content: str
    type: CommunicationType = CommunicationType.NUDGE
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10, higher = more important")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: datetime = Field(default_factory=datetime.utcnow)
    attempts: int = Field(default=0, ge=0)
    escalation_level: int = Field(default=0, ge=0, le=2, description="0=nudge, 1=recommendation, 2=order")
    
    # Relationships
    related_truths: List[str] = Field(default_factory=list)
    related_goals: List[str] = Field(default_factory=list)
    source_report: Optional[str] = None
    
    # Status
    delivered: bool = Field(default=False)
    acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class PromptTemplate(BaseModel):
    """Template for generating insights from agent results."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    role: str = Field(..., description="Target role: ceo, cto, cfo, etc.")
    category: str = Field(..., description="Category: technology, market, competitive, etc.")
    template: str = Field(..., description="Prompt template with variables")
    variables: List[str] = Field(default_factory=list)
    analysis_depth: str = Field(default="daily", description="daily, weekly, monthly")
    output_format: str = Field(default="truth", description="truth, report, insight")
    tenant_id: Optional[str] = None  # None for shared templates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Config:
        use_enum_values = True


class IntelligenceRequest(BaseModel):
    """Request to generate strategic intelligence from market intelligence data."""
    agent_ids: List[str] = Field(..., description="Agent IDs to analyze")
    template_id: str = Field(..., description="Prompt template to use")
    analysis_depth: AnalysisDepth = AnalysisDepth.SHALLOW
    variables: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str
    user_id: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    
    class Config:
        use_enum_values = True


class IntelligenceResponse(BaseModel):
    """Response from strategic intelligence generation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    truths: List[OrganizationalTruth] = Field(default_factory=list)
    reports: List[CompiledReport] = Field(default_factory=list)
    communications: List[CommunicationQueue] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: Optional[float] = None
    token_count: Optional[int] = None
    
    class Config:
        use_enum_values = True


class TruthQuery(BaseModel):
    """Query for retrieving strategic insights."""
    tenant_id: str
    categories: Optional[List[TruthCategory]] = None
    impact_levels: Optional[List[ImpactLevel]] = None
    confidence_min: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    
    class Config:
        use_enum_values = True


class CommunicationQuery(BaseModel):
    """Query for retrieving priority communications."""
    user_id: str
    tenant_id: str
    types: Optional[List[CommunicationType]] = None
    priority_min: Optional[int] = None
    delivered: Optional[bool] = None
    acknowledged: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    
    class Config:
        use_enum_values = True


class EscalationRule(BaseModel):
    """Rule for escalating communications."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    description: str
    condition_type: str = Field(..., description="attempts, time, priority")
    condition_value: Any
    action_type: str = Field(..., description="escalate, reschedule, notify")
    action_value: Any
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class IntelligenceMetrics(BaseModel):
    """Metrics for intelligence system performance."""
    tenant_id: str
    date: datetime
    truths_generated: int = 0
    reports_generated: int = 0
    communications_queued: int = 0
    communications_delivered: int = 0
    communications_acknowledged: int = 0
    escalations_triggered: int = 0
    average_confidence: float = 0.0
    processing_time_avg: float = 0.0
    token_usage_total: int = 0
    
    class Config:
        use_enum_values = True


class StrategicAlignmentZone(str, Enum):
    """Strategic alignment health zones."""
    RED = "red"      # 0-59% - Strategic execution at risk
    YELLOW = "yellow"  # 60-79% - Strategic execution good
    GREEN = "green"    # 80-100% - Strategic execution excellence


class StrategicAlignmentKPI(BaseModel):
    """Individual Strategic Alignment KPI measurement."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    kpi_name: str = Field(..., description="Name of the KPI")
    kpi_category: str = Field(..., description="alignment or execution")
    current_value: float = Field(..., description="Current KPI value (0-100)")
    target_value: float = Field(default=80.0, description="Target value for this KPI")
    measurement_date: datetime = Field(default_factory=datetime.utcnow)
    trend: str = Field(default="stable", description="improving, declining, stable")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata for KPI calculation
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    calculation_method: str = Field(default="", description="How this KPI is calculated")
    
    class Config:
        use_enum_values = True


class StrategicAlignmentScorecard(BaseModel):
    """Comprehensive strategic alignment scorecard for an organization."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    measurement_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Alignment KPIs
    strategic_initiative_velocity: float = Field(default=0.0, ge=0.0, le=100.0)
    goal_cascade_alignment: float = Field(default=0.0, ge=0.0, le=100.0)
    decision_strategy_consistency: float = Field(default=0.0, ge=0.0, le=100.0)
    resource_allocation_efficiency: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Execution KPIs
    strategic_response_time: float = Field(default=0.0, ge=0.0, le=100.0)
    cross_functional_alignment: float = Field(default=0.0, ge=0.0, le=100.0)
    strategic_communication_effectiveness: float = Field(default=0.0, ge=0.0, le=100.0)
    adaptation_speed: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Calculated scores
    overall_alignment_score: float = Field(default=0.0, ge=0.0, le=100.0)
    alignment_zone: StrategicAlignmentZone = StrategicAlignmentZone.RED
    strategic_velocity: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Trend analysis
    trend_30_days: str = Field(default="stable", description="improving, declining, stable")
    trend_60_days: str = Field(default="stable", description="improving, declining, stable")
    trend_90_days: str = Field(default="stable", description="improving, declining, stable")
    
    # Risk indicators
    risk_indicators: List[str] = Field(default_factory=list)
    priority_interventions: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class StrategicAlignmentQuery(BaseModel):
    """Query for retrieving strategic alignment data."""
    tenant_id: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_details: bool = Field(default=False, description="Include individual KPI details")
    limit: int = Field(default=30, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    
    class Config:
        use_enum_values = True
