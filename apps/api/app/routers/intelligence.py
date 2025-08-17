"""API router for the Intelligence system."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

from ..domain.intelligence_models import (
    IntelligenceRequest, IntelligenceResponse, TruthQuery, CommunicationQuery,
    OrganizationalTruth, CommunicationQueue, PromptTemplate,
    TruthCategory, ImpactLevel, AnalysisDepth, CommunicationType,
    StrategicAlignmentScorecard, StrategicAlignmentQuery
)
from ..domain.intelligence_service import IntelligenceService
from ..domain.agent_service import AgentService
from ..adapters.firebase_auth import get_current_user, get_current_tenant

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def get_intelligence_service() -> IntelligenceService:
    """Get intelligence service instance."""
    agent_service = AgentService()
    return IntelligenceService(agent_service)


@router.post("/generate", response_model=IntelligenceResponse)
async def generate_strategic_intelligence(
    request: IntelligenceRequest,
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """Generate strategic intelligence from market intelligence data."""
    try:
        # Set tenant_id from current tenant
        request.tenant_id = current_tenant.id
        request.user_id = current_user.id
        
        response = await intelligence_service.generate_intelligence(request)
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate intelligence: {str(e)}")


@router.get("/truths", response_model=List[OrganizationalTruth])
async def get_strategic_insights(
    categories: Optional[List[TruthCategory]] = Query(None),
    impact_levels: Optional[List[ImpactLevel]] = Query(None),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get strategic insights based on query criteria."""
    try:
        query = TruthQuery(
            tenant_id=current_tenant.id,
            categories=categories,
            impact_levels=impact_levels,
            confidence_min=confidence_min,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        truths = await intelligence_service.get_truths(query)
        return truths
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get truths: {str(e)}")


@router.get("/communications", response_model=List[CommunicationQueue])
async def get_priority_communications(
    types: Optional[List[CommunicationType]] = Query(None),
    priority_min: Optional[int] = Query(None, ge=1, le=10),
    delivered: Optional[bool] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """Get priority communications for the current user."""
    try:
        query = CommunicationQuery(
            user_id=current_user.id,
            tenant_id=current_tenant.id,
            types=types,
            priority_min=priority_min,
            delivered=delivered,
            acknowledged=acknowledged,
            limit=limit,
            offset=offset
        )
        
        communications = await intelligence_service.get_communications(query)
        return communications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get communications: {str(e)}")


@router.post("/communications/{communication_id}/acknowledge")
async def acknowledge_priority_communication(
    communication_id: str,
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_user = Depends(get_current_user)
):
    """Acknowledge a priority communication."""
    try:
        success = await intelligence_service.acknowledge_communication(communication_id, current_user.id)
        
        if success:
            return {"message": "Communication acknowledged successfully"}
        else:
            raise HTTPException(status_code=404, detail="Communication not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge communication: {str(e)}")


@router.get("/templates", response_model=List[PromptTemplate])
async def get_templates(
    role: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get available prompt templates."""
    try:
        templates = list(intelligence_service.templates.values())
        
        # Apply filters
        if role:
            templates = [t for t in templates if t.role == role]
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        # Filter by tenant (shared templates + tenant-specific)
        templates = [
            t for t in templates 
            if t.tenant_id is None or t.tenant_id == current_tenant.id
        ]
        
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/templates", response_model=PromptTemplate)
async def create_template(
    template: PromptTemplate,
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Create a new prompt template."""
    try:
        # Set tenant_id for tenant-specific templates
        if template.tenant_id is None:
            template.tenant_id = current_tenant.id
        
        # Add to service
        intelligence_service.templates[template.id] = template
        
        return template
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("/dashboard")
async def get_strategic_intelligence_dashboard(
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """Get strategic intelligence dashboard data."""
    try:
        # Get recent truths
        recent_truths = await intelligence_service.get_truths(
            TruthQuery(
                tenant_id=current_tenant.id,
                limit=10
            )
        )
        
        # Get pending communications
        pending_communications = await intelligence_service.get_communications(
            CommunicationQuery(
                user_id=current_user.id,
                tenant_id=current_tenant.id,
                acknowledged=False,
                limit=10
            )
        )
        
        # Get high-impact truths
        high_impact_truths = await intelligence_service.get_truths(
            TruthQuery(
                tenant_id=current_tenant.id,
                impact_levels=[ImpactLevel.HIGH, ImpactLevel.CRITICAL],
                limit=5
            )
        )
        
        return {
            "recent_truths": recent_truths,
            "pending_communications": pending_communications,
            "high_impact_truths": high_impact_truths,
            "total_truths": len(intelligence_service.truths_cache),
            "queue_length": len(intelligence_service.communication_queue)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@router.post("/process-escalations")
async def process_escalations(
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Process escalation rules for communications."""
    try:
        await intelligence_service.process_escalations()
        return {"message": "Escalations processed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process escalations: {str(e)}")


@router.get("/metrics")
async def get_intelligence_metrics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get intelligence system metrics."""
    try:
        # Calculate metrics from service data
        total_truths = len(intelligence_service.truths_cache)
        total_communications = len(intelligence_service.communication_queue)
        
        # Filter by date range if provided
        if date_from:
            truths_in_range = [
                t for t in intelligence_service.truths_cache.values()
                if t.created_at >= date_from
            ]
            total_truths = len(truths_in_range)
        
        if date_to:
            truths_in_range = [
                t for t in intelligence_service.truths_cache.values()
                if t.created_at <= date_to
            ]
            total_truths = len(truths_in_range)
        
        # Calculate average confidence
        if intelligence_service.truths_cache:
            avg_confidence = sum(t.confidence for t in intelligence_service.truths_cache.values()) / len(intelligence_service.truths_cache)
        else:
            avg_confidence = 0.0
        
        # Count by category
        category_counts = {}
        for truth in intelligence_service.truths_cache.values():
            category = truth.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by impact level
        impact_counts = {}
        for truth in intelligence_service.truths_cache.values():
            impact = truth.impact_level.value
            impact_counts[impact] = impact_counts.get(impact, 0) + 1
        
        return {
            "total_truths": total_truths,
            "total_communications": total_communications,
            "average_confidence": avg_confidence,
            "category_distribution": category_counts,
            "impact_distribution": impact_counts,
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/setup-demo")
async def setup_demo_strategic_intelligence(
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Setup demo strategic intelligence data."""
    try:
        # Create demo request
        demo_request = IntelligenceRequest(
            agent_ids=["demo_agent_1", "demo_agent_2"],
            template_id="ceo_strategic_truths",
            analysis_depth=AnalysisDepth.WEEKLY,
            variables={
                "industry": "technology",
                "company_size": "mid-size"
            },
            tenant_id=current_tenant.id,
            user_id="demo_user",
            priority="medium"
        )
        
        # Generate demo intelligence
        response = await intelligence_service.generate_intelligence(demo_request)
        
        return {
            "message": "Demo strategic intelligence generated successfully",
            "truths_count": len(response.truths),
            "reports_count": len(response.reports),
            "communications_count": len(response.communications)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup demo: {str(e)}")


@router.get("/alignment/scorecard", response_model=StrategicAlignmentScorecard)
async def get_strategic_alignment_scorecard(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    include_details: bool = Query(False),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get strategic alignment scorecard for the current tenant."""
    try:
        query = StrategicAlignmentQuery(
            tenant_id=current_tenant.id,
            date_from=date_from,
            date_to=date_to,
            include_details=include_details
        )
        
        scorecard = await intelligence_service.get_strategic_alignment_scorecard(query)
        return scorecard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategic alignment scorecard: {str(e)}")


@router.get("/alignment/history", response_model=List[StrategicAlignmentScorecard])
async def get_strategic_alignment_history(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Get historical strategic alignment data."""
    try:
        query = StrategicAlignmentQuery(
            tenant_id=current_tenant.id,
            date_from=date_from,
            date_to=date_to,
            include_details=False,
            limit=limit,
            offset=offset
        )
        
        history = await intelligence_service.get_strategic_alignment_history(query)
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategic alignment history: {str(e)}")


@router.post("/alignment/calculate")
async def calculate_strategic_alignment(
    intelligence_service: IntelligenceService = Depends(get_intelligence_service),
    current_tenant = Depends(get_current_tenant)
):
    """Calculate and update strategic alignment scorecard."""
    try:
        scorecard = await intelligence_service.calculate_strategic_alignment_scorecard(current_tenant.id)
        
        return {
            "message": "Strategic alignment scorecard calculated successfully",
            "overall_score": scorecard.overall_alignment_score,
            "alignment_zone": scorecard.alignment_zone.value,
            "strategic_velocity": scorecard.strategic_velocity,
            "risk_indicators_count": len(scorecard.risk_indicators),
            "priority_interventions_count": len(scorecard.priority_interventions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate strategic alignment: {str(e)}")
