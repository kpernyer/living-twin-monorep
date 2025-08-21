"""SWOT-based strategic signal detection models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SWOTCategory(str, Enum):
    """SWOT analysis categories."""
    
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    OPPORTUNITY = "opportunity"
    THREAT = "threat"


class SignalPriority(str, Enum):
    """Signal priority levels based on SWOT impact."""
    
    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"             # High strategic importance
    MEDIUM = "medium"         # Moderate importance
    LOW = "low"               # Low priority
    MONITOR = "monitor"       # Watch for changes


class SignalImpact(str, Enum):
    """Impact direction of signals on SWOT elements."""
    
    POSITIVE = "positive"     # Strengthens/creates opportunity
    NEGATIVE = "negative"     # Weakens/creates threat
    NEUTRAL = "neutral"       # Informational only
    MIXED = "mixed"           # Both positive and negative aspects


class SWOTElement(BaseModel):
    """Individual SWOT element with prioritization."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    category: SWOTCategory
    title: str = Field(..., description="Short, clear title")
    description: str = Field(..., description="Detailed description")
    priority: int = Field(..., ge=1, le=5, description="Priority rank (1=highest, 5=lowest)")
    keywords: List[str] = Field(default_factory=list, description="Keywords for signal detection")
    impact_areas: List[str] = Field(default_factory=list, description="Areas this affects")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class SWOTAnalysis(BaseModel):
    """Complete SWOT analysis for a tenant."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str = Field(..., description="Analysis name (e.g., 'Q1 2024 Strategic Review')")
    description: str = Field(..., description="Analysis description")
    
    # SWOT elements (max 5 each)
    strengths: List[SWOTElement] = Field(default_factory=list, max_items=5)
    weaknesses: List[SWOTElement] = Field(default_factory=list, max_items=5)
    opportunities: List[SWOTElement] = Field(default_factory=list, max_items=5)
    threats: List[SWOTElement] = Field(default_factory=list, max_items=5)
    
    # Analysis metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = Field(default=True)
    version: int = Field(default=1, ge=1)
    
    # Strategic context
    strategic_period: str = Field(default="", description="e.g., 'Q1 2024', 'Annual 2024'")
    industry_focus: List[str] = Field(default_factory=list)
    market_position: str = Field(default="", description="Market position description")
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class StrategicSignal(BaseModel):
    """Strategic signal detected from external sources."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    
    # Signal content
    title: str = Field(..., description="Signal title")
    content: str = Field(..., description="Signal content")
    summary: str = Field(..., description="AI-generated summary")
    
    # Source information
    source_url: Optional[str] = None
    source_name: str
    source_credibility: float = Field(default=0.5, ge=0.0, le=1.0)
    published_at: Optional[datetime] = None
    
    # SWOT categorization
    swot_categories: List[SWOTCategory] = Field(default_factory=list)
    affected_elements: List[str] = Field(default_factory=list, description="SWOT element IDs")
    impact_direction: SignalImpact = SignalImpact.NEUTRAL
    priority: SignalPriority = SignalPriority.MEDIUM
    
    # Analysis scores
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    urgency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    strategic_impact_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Signal metadata
    keywords_matched: List[str] = Field(default_factory=list)
    entities: Dict[str, List[str]] = Field(default_factory=dict)
    themes: List[str] = Field(default_factory=list)
    sentiment: str = Field(default="neutral")
    
    # Tracking
    first_detected: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    mention_count: int = Field(default=1, ge=1)
    similar_signals: List[str] = Field(default_factory=list, description="Related signal IDs")
    
    # User feedback
    user_priority_override: Optional[SignalPriority] = None
    user_notes: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class SignalAnalysis(BaseModel):
    """Analysis of how a signal impacts SWOT elements."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_id: str
    tenant_id: str
    
    # SWOT impact analysis
    swot_impacts: Dict[SWOTCategory, List[Dict[str, Any]]] = Field(default_factory=dict)
    
    # Strategic implications
    strategic_implications: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    risk_assessment: str = Field(default="", description="Risk assessment summary")
    
    # Analysis metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_by: str = Field(default="ai_system")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class SWOTSignalRequest(BaseModel):
    """Request to create or update SWOT analysis."""
    
    name: str
    description: str
    strategic_period: Optional[str] = None
    industry_focus: Optional[List[str]] = None
    market_position: Optional[str] = None
    
    # SWOT elements
    strengths: Optional[List[Dict[str, Any]]] = None
    weaknesses: Optional[List[Dict[str, Any]]] = None
    opportunities: Optional[List[Dict[str, Any]]] = None
    threats: Optional[List[Dict[str, Any]]] = None


class SignalQuery(BaseModel):
    """Query for retrieving strategic signals."""
    
    tenant_id: str
    swot_categories: Optional[List[SWOTCategory]] = None
    priority_levels: Optional[List[SignalPriority]] = None
    impact_directions: Optional[List[SignalImpact]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    keywords: Optional[List[str]] = None
    affected_elements: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="strategic_impact_score", description="Field to sort by")
    sort_order: str = Field(default="desc", description="asc or desc")


class SignalDashboard(BaseModel):
    """Dashboard data for strategic signals."""
    
    tenant_id: str
    
    # Signal counts by category
    signal_counts: Dict[SWOTCategory, int] = Field(default_factory=dict)
    priority_counts: Dict[SignalPriority, int] = Field(default_factory=dict)
    impact_counts: Dict[SignalImpact, int] = Field(default_factory=dict)
    
    # Top signals
    critical_signals: List[StrategicSignal] = Field(default_factory=list)
    high_priority_signals: List[StrategicSignal] = Field(default_factory=list)
    
    # Trends
    signals_last_7_days: int = 0
    signals_last_30_days: int = 0
    trend_direction: str = Field(default="stable", description="improving, declining, stable")
    
    # SWOT element impact
    most_impacted_elements: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.utcnow)
