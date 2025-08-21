"""Porter's Five Forces analysis models for strategic signal detection."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PortersForce(str, Enum):
    """Porter's Five Forces categories."""
    
    COMPETITIVE_RIVALRY = "competitive_rivalry"
    NEW_ENTRANTS = "new_entrants"
    SUBSTITUTE_PRODUCTS = "substitute_products"
    SUPPLIER_POWER = "supplier_power"
    BUYER_POWER = "buyer_power"


class ForceIntensity(str, Enum):
    """Intensity levels for Porter's forces."""
    
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class PortersElement(BaseModel):
    """Individual Porter's force element with analysis."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    force: PortersForce
    title: str = Field(..., description="Short, clear title")
    description: str = Field(..., description="Detailed analysis")
    intensity: ForceIntensity = Field(..., description="Current intensity level")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Strategic impact score")
    keywords: List[str] = Field(default_factory=list, description="Keywords for signal detection")
    factors: List[str] = Field(default_factory=list, description="Key factors affecting this force")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class PortersAnalysis(BaseModel):
    """Complete Porter's Five Forces analysis for a tenant."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str = Field(..., description="Analysis name (e.g., 'Q1 2024 Competitive Landscape')")
    description: str = Field(..., description="Analysis description")
    
    # Porter's forces (max 3-5 elements each)
    competitive_rivalry: List[PortersElement] = Field(default_factory=list, max_items=5)
    new_entrants: List[PortersElement] = Field(default_factory=list, max_items=5)
    substitute_products: List[PortersElement] = Field(default_factory=list, max_items=5)
    supplier_power: List[PortersElement] = Field(default_factory=list, max_items=5)
    buyer_power: List[PortersElement] = Field(default_factory=list, max_items=5)
    
    # Analysis metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = Field(default=True)
    version: int = Field(default=1, ge=1)
    
    # Strategic context
    industry: str = Field(default="", description="Primary industry focus")
    market_position: str = Field(default="", description="Current market position")
    geographic_scope: List[str] = Field(default_factory=list, description="Geographic markets")
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class PortersRequest(BaseModel):
    """Request to create or update Porter's analysis."""
    
    name: str
    description: str
    industry: Optional[str] = None
    market_position: Optional[str] = None
    geographic_scope: Optional[List[str]] = None
    
    # Porter's forces
    competitive_rivalry: Optional[List[Dict[str, Any]]] = None
    new_entrants: Optional[List[Dict[str, Any]]] = None
    substitute_products: Optional[List[Dict[str, Any]]] = None
    supplier_power: Optional[List[Dict[str, Any]]] = None
    buyer_power: Optional[List[Dict[str, Any]]] = None
