"""Strategic test router for immediate round-trip testing of SWOT + Porter's signal detection."""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..domain.test_data_loader import TestDataLoader
from ..domain.swot_models import SWOTAnalysis, StrategicSignal, SignalAnalysis
from ..domain.porters_models import PortersAnalysis
from ..domain.swot_signal_service import SWOTSignalService
from ..domain.swot_agent_integration import SWOTAgentIntegration
from ..domain.agent_models import AgentResult, AgentConfig, AgentCapability
from ..adapters.firebase_auth import get_current_user, get_current_tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategic-test", tags=["Strategic Test"])


class TestSetupRequest(BaseModel):
    """Request to set up test data."""
    
    tenant_id: str
    user_id: str
    industry: str = "fintech"
    test_scenario: str = "fintech"
    scope: str = "industry"  # megatrends, regional, industry, company


class TestSignalDetectionRequest(BaseModel):
    """Request to test signal detection."""
    
    tenant_id: str
    swot_analysis_id: str
    porters_analysis_id: str
    test_agent_results: bool = True


class TestResult(BaseModel):
    """Test result summary."""
    
    success: bool
    message: str
    data: Dict[str, Any]
    execution_time_ms: float


@router.post("/setup", response_model=TestResult)
async def setup_test_data(
    request: TestSetupRequest,
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Set up comprehensive test data for strategic signal detection."""
    
    try:
        import time
        start_time = time.time()
        
        # Initialize test data loader
        test_loader = TestDataLoader()
        
        # Load SWOT analysis from YAML
        scenario = request.test_scenario or "fintech"
        scope = request.scope or "industry"
        swot_analysis = test_loader.load_swot_analysis(scenario, request.tenant_id, request.user_id, scope)
        
        # Load Porter's analysis from YAML (if available for this scope)
        try:
            porters_analysis = test_loader.load_porters_analysis(scenario, request.tenant_id, request.user_id, scope)
        except FileNotFoundError:
            porters_analysis = None
        
        # Get test sources
        test_sources = test_loader.load_strategic_sources()
        
        # Get test agent results
        test_agent_results = test_loader.load_agent_results()
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Test data setup completed successfully",
            data={
                "swot_analysis": {
                    "id": swot_analysis.id,
                    "name": swot_analysis.name,
                    "elements_count": {
                        "strengths": len(swot_analysis.strengths),
                        "weaknesses": len(swot_analysis.weaknesses),
                        "opportunities": len(swot_analysis.opportunities),
                        "threats": len(swot_analysis.threats)
                    }
                },
                "porters_analysis": {
                    "id": porters_analysis.id if porters_analysis else None,
                    "name": porters_analysis.name if porters_analysis else None,
                    "forces_count": {
                        "competitive_rivalry": len(porters_analysis.competitive_rivalry) if porters_analysis else 0,
                        "new_entrants": len(porters_analysis.new_entrants) if porters_analysis else 0,
                        "substitute_products": len(porters_analysis.substitute_products) if porters_analysis else 0,
                        "supplier_power": len(porters_analysis.supplier_power) if porters_analysis else 0,
                        "buyer_power": len(porters_analysis.buyer_power) if porters_analysis else 0
                    }
                } if porters_analysis else None,
                "test_sources": {
                    "high_frequency": len(test_sources["high_frequency"]),
                    "medium_frequency": len(test_sources["medium_frequency"]),
                    "low_frequency": len(test_sources["low_frequency"]),
                    "megatrends": len(test_sources["megatrends"])
                },
                "test_agent_results": len(test_agent_results)
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error setting up test data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup test data: {str(e)}")


@router.post("/signal-detection", response_model=TestResult)
async def test_signal_detection(
    request: TestSignalDetectionRequest,
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Test the complete signal detection pipeline."""
    
    try:
        import time
        start_time = time.time()
        
        # Initialize test data loader
        test_loader = TestDataLoader()
        
        # Load SWOT and Porter's analyses from YAML
        scenario = "fintech"  # Default scenario
        swot_analysis = test_loader.load_swot_analysis(scenario, request.tenant_id, current_user.uid)
        porters_analysis = test_loader.load_porters_analysis(scenario, request.tenant_id, current_user.uid)
        
        # Create SWOT signal service
        swot_signal_service = SWOTSignalService()
        
        # Create agent integration service
        agent_integration = SWOTAgentIntegration()
        
        # Generate strategic keywords
        strategic_keywords = agent_integration.generate_agent_keywords_from_swot(
            swot_analysis, [AgentCapability.NEWS_MONITORING, AgentCapability.COMPETITIVE_INTELLIGENCE]
        )
        
        # Load test agent results from YAML
        agent_results = test_loader.load_agent_results()
        
        # Detect strategic signals
        strategic_signals = await swot_signal_service.detect_signals_from_agent_results(
            agent_results, swot_analysis, request.tenant_id
        )
        
        # Analyze signal impacts
        signal_analyses = []
        for signal in strategic_signals:
            analysis = await swot_signal_service.analyze_signal_impact(signal, swot_analysis)
            signal_analyses.append(analysis)
        
        # Generate dashboard data
        dashboard_data = {
            "signal_counts": {
                "total": len(strategic_signals),
                "critical": len([s for s in strategic_signals if s.priority.value == "critical"]),
                "high": len([s for s in strategic_signals if s.priority.value == "high"]),
                "medium": len([s for s in strategic_signals if s.priority.value == "medium"]),
                "low": len([s for s in strategic_signals if s.priority.value == "low"])
            },
            "swot_categories": {
                "strengths": len([s for s in strategic_signals if "strength" in [c.value for c in s.swot_categories]]),
                "weaknesses": len([s for s in strategic_signals if "weakness" in [c.value for c in s.swot_categories]]),
                "opportunities": len([s for s in strategic_signals if "opportunity" in [c.value for c in s.swot_categories]]),
                "threats": len([s for s in strategic_signals if "threat" in [c.value for c in s.swot_categories]])
            },
            "impact_directions": {
                "positive": len([s for s in strategic_signals if s.impact_direction.value == "positive"]),
                "negative": len([s for s in strategic_signals if s.impact_direction.value == "negative"]),
                "neutral": len([s for s in strategic_signals if s.impact_direction.value == "neutral"]),
                "mixed": len([s for s in strategic_signals if s.impact_direction.value == "mixed"])
            }
        }
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Signal detection test completed successfully",
            data={
                "strategic_keywords_generated": len(strategic_keywords),
                "agent_results_processed": len(agent_results),
                "strategic_signals_detected": len(strategic_signals),
                "signal_analyses_created": len(signal_analyses),
                "dashboard_data": dashboard_data,
                "sample_signals": [
                    {
                        "title": signal.title,
                        "priority": signal.priority.value,
                        "swot_categories": [c.value for c in signal.swot_categories],
                        "impact_direction": signal.impact_direction.value,
                        "strategic_impact_score": signal.strategic_impact_score,
                        "affected_elements": len(signal.affected_elements)
                    }
                    for signal in strategic_signals[:3]  # Show first 3 signals
                ],
                "sample_analyses": [
                    {
                        "signal_id": analysis.signal_id,
                        "strategic_implications": len(analysis.strategic_implications),
                        "recommended_actions": len(analysis.recommended_actions),
                        "risk_assessment": analysis.risk_assessment
                    }
                    for analysis in signal_analyses[:3]  # Show first 3 analyses
                ]
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error testing signal detection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test signal detection: {str(e)}")


@router.get("/sources", response_model=TestResult)
async def get_test_sources(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get strategic test sources with different update frequencies."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        test_sources = test_loader.load_strategic_sources()
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Test sources retrieved successfully",
            data={
                "sources": test_sources,
                "summary": {
                    "high_frequency": len(test_sources["high_frequency"]),
                    "medium_frequency": len(test_sources["medium_frequency"]),
                    "low_frequency": len(test_sources["low_frequency"]),
                    "megatrends": len(test_sources["megatrends"])
                }
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting test sources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get test sources: {str(e)}")


@router.get("/taxonomy", response_model=TestResult)
async def get_taxonomy(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get the strategic intelligence taxonomy structure."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        taxonomy = test_loader.get_taxonomy()
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Taxonomy retrieved successfully",
            data={
                "taxonomy": taxonomy,
                "structure": {
                    "megatrends": "Global factors affecting all regions and industries",
                    "regional": "Regional factors affecting all industries in a geography",
                    "industry": "Industry-specific factors (global or regional scope)",
                    "company": "Company-specific factors within an industry and region"
                }
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting taxonomy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get taxonomy: {str(e)}")


@router.get("/scenarios", response_model=TestResult)
async def get_available_scenarios(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get list of available test scenarios."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        scenarios = test_loader.get_available_scenarios()
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Available scenarios retrieved successfully",
            data={
                "scenarios": scenarios,
                "total_count": sum(len(scenarios[scope]) for scope in scenarios),
                "by_scope": {
                    scope: {"count": len(scenarios[scope]), "scenarios": scenarios[scope]}
                    for scope in scenarios
                },
                "default": "fintech"
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting available scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get available scenarios: {str(e)}")


@router.get("/megatrend/{trend_name}", response_model=TestResult)
async def get_megatrend(
    trend_name: str,
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get a specific megatrend analysis."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        megatrend = test_loader.load_megatrend(trend_name)
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message=f"Megatrend '{trend_name}' retrieved successfully",
            data={
                "megatrend": megatrend,
                "scope": "global",
                "impact": "universal"
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting megatrend {trend_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get megatrend: {str(e)}")


@router.get("/regional/{region_name}/{factor_type}", response_model=TestResult)
async def get_regional_factor(
    region_name: str,
    factor_type: str,
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get a specific regional factor analysis."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        regional_factor = test_loader.load_regional_factor(region_name, factor_type)
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message=f"Regional factor '{region_name}/{factor_type}' retrieved successfully",
            data={
                "regional_factor": regional_factor,
                "scope": "regional",
                "impact": "cross_industry"
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting regional factor {region_name}/{factor_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get regional factor: {str(e)}")


@router.get("/agent-results", response_model=TestResult)
async def get_test_agent_results(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Get test agent results for signal detection."""
    
    try:
        import time
        start_time = time.time()
        
        test_loader = TestDataLoader()
        agent_results = test_loader.load_agent_results()
        
        # Convert to dict format for response
        test_agent_results = []
        for result in agent_results:
            test_agent_results.append({
                "title": result.title,
                "content": result.content,
                "source_name": result.source_name,
                "source_url": result.source_url,
                "keywords_matched": result.keywords_matched,
                "sentiment": result.sentiment,
                "published_at": result.published_at.isoformat()
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Test agent results retrieved successfully",
            data={
                "agent_results": test_agent_results,
                "count": len(test_agent_results),
                "sources": list(set([r["source_name"] for r in test_agent_results])),
                "sentiments": {
                    "positive": len([r for r in test_agent_results if r["sentiment"] == "positive"]),
                    "negative": len([r for r in test_agent_results if r["sentiment"] == "negative"]),
                    "neutral": len([r for r in test_agent_results if r["sentiment"] == "neutral"])
                }
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting test agent results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get test agent results: {str(e)}")


@router.post("/round-trip", response_model=TestResult)
async def test_complete_round_trip(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    """Test the complete round-trip: setup → signal detection → analysis."""
    
    try:
        import time
        start_time = time.time()
        
        # Initialize test data loader
        test_loader = TestDataLoader()
        
        # Step 1: Setup test data from YAML
        swot_analysis = test_loader.load_swot_analysis("fintech", current_tenant.id, current_user.id)
        porters_analysis = test_loader.load_porters_analysis("fintech", current_tenant.id, current_user.id)
        
        # Step 2: Generate strategic keywords
        agent_integration = SWOTAgentIntegration()
        strategic_keywords = agent_integration.generate_agent_keywords_from_swot(
            swot_analysis, [AgentCapability.NEWS_MONITORING, AgentCapability.COMPETITOR_TRACKING]
        )
        
        # Step 3: Process agent results from YAML
        agent_results = test_loader.load_agent_results()
        
        # Step 4: Detect signals
        swot_signal_service = SWOTSignalService()
        strategic_signals = await swot_signal_service.detect_signals_from_agent_results(
            agent_results, swot_analysis, current_tenant.id
        )
        
        # Step 5: Analyze signals
        signal_analyses = []
        for signal in strategic_signals:
            analysis = await swot_signal_service.analyze_signal_impact(signal, swot_analysis)
            signal_analyses.append(analysis)
        
        execution_time = (time.time() - start_time) * 1000
        
        return TestResult(
            success=True,
            message="Complete round-trip test successful",
            data={
                "setup": {
                    "swot_elements": len(swot_analysis.strengths) + len(swot_analysis.weaknesses) + 
                                   len(swot_analysis.opportunities) + len(swot_analysis.threats),
                    "porters_elements": len(porters_analysis.competitive_rivalry) + 
                                      len(porters_analysis.new_entrants) + 
                                      len(porters_analysis.substitute_products) + 
                                      len(porters_analysis.supplier_power) + 
                                      len(porters_analysis.buyer_power)
                },
                "keyword_generation": {
                    "strategic_keywords": len(strategic_keywords),
                    "sample_keywords": strategic_keywords[:10]
                },
                "signal_detection": {
                    "agent_results_processed": len(agent_results),
                    "strategic_signals_detected": len(strategic_signals),
                    "detection_rate": len(strategic_signals) / len(agent_results) if agent_results else 0
                },
                "signal_analysis": {
                    "analyses_created": len(signal_analyses),
                    "average_implications": sum(len(a.strategic_implications) for a in signal_analyses) / len(signal_analyses) if signal_analyses else 0,
                    "average_actions": sum(len(a.recommended_actions) for a in signal_analyses) / len(signal_analyses) if signal_analyses else 0
                },
                "performance": {
                    "execution_time_ms": execution_time,
                    "signals_per_second": len(strategic_signals) / (execution_time / 1000) if execution_time > 0 else 0
                }
            },
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error in round-trip test: {e}")
        raise HTTPException(status_code=500, detail=f"Round-trip test failed: {str(e)}")
