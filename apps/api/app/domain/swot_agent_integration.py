"""SWOT-based agent integration for automatic keyword generation and signal detection."""

import logging
from typing import Dict, List, Set, Any
from collections import defaultdict

from .swot_models import SWOTAnalysis, SWOTElement, SWOTCategory
from .agent_models import AgentConfig, AgentCapability

logger = logging.getLogger(__name__)


class SWOTAgentIntegration:
    """Integrates SWOT analysis with AI agents for strategic signal detection."""
    
    def __init__(self):
        # Keyword expansion patterns for each SWOT category
        self.keyword_expansion_patterns = {
            SWOTCategory.STRENGTH: {
                "synonyms": ["advantage", "capability", "expertise", "leadership", "superiority"],
                "related_terms": ["market leader", "competitive advantage", "unique selling point", "core competency"],
                "industry_terms": ["best practice", "benchmark", "excellence", "innovation leader"]
            },
            SWOTCategory.WEAKNESS: {
                "synonyms": ["limitation", "constraint", "gap", "deficiency", "challenge"],
                "related_terms": ["skill gap", "resource constraint", "technology debt", "process inefficiency"],
                "industry_terms": ["catch up", "improvement needed", "development area", "optimization opportunity"]
            },
            SWOTCategory.OPPORTUNITY: {
                "synonyms": ["potential", "prospect", "chance", "possibility", "growth area"],
                "related_terms": ["market expansion", "new technology", "trend", "emerging market"],
                "industry_terms": ["disruption", "innovation", "digital transformation", "market shift"]
            },
            SWOTCategory.THREAT: {
                "synonyms": ["risk", "danger", "challenge", "problem", "issue"],
                "related_terms": ["competitor", "market change", "regulation", "technology shift"],
                "industry_terms": ["disruption", "substitute", "new entrant", "economic downturn"]
            }
        }
        
        # Industry-specific keyword patterns
        self.industry_keywords = {
            "technology": ["AI", "machine learning", "cloud computing", "cybersecurity", "digital transformation"],
            "finance": ["fintech", "blockchain", "digital payments", "regulatory compliance", "risk management"],
            "healthcare": ["telemedicine", "digital health", "patient care", "medical technology", "healthcare AI"],
            "retail": ["ecommerce", "omnichannel", "customer experience", "supply chain", "digital commerce"],
            "manufacturing": ["Industry 4.0", "automation", "IoT", "supply chain", "quality control"],
            "energy": ["renewable energy", "sustainability", "clean tech", "energy efficiency", "carbon reduction"]
        }
    
    def generate_agent_keywords_from_swot(
        self,
        swot_analysis: SWOTAnalysis,
        agent_capabilities: List[AgentCapability]
    ) -> List[str]:
        """Generate agent keywords based on SWOT analysis."""
        
        keywords = set()
        
        # Extract keywords from SWOT elements
        for element in self._get_all_swot_elements(swot_analysis):
            if element.is_active:
                # Add element keywords
                keywords.update(element.keywords)
                
                # Add expanded keywords based on category
                expanded_keywords = self._expand_keywords_for_category(
                    element.keywords, element.category
                )
                keywords.update(expanded_keywords)
                
                # Add impact area keywords
                for impact_area in element.impact_areas:
                    area_keywords = self._get_impact_area_keywords(impact_area)
                    keywords.update(area_keywords)
        
        # Add industry-specific keywords
        industry_keywords = self._get_industry_keywords(swot_analysis.industry_focus)
        keywords.update(industry_keywords)
        
        # Add capability-specific keywords
        capability_keywords = self._get_capability_keywords(agent_capabilities)
        keywords.update(capability_keywords)
        
        # Filter and rank keywords
        ranked_keywords = self._rank_keywords_by_relevance(keywords, swot_analysis)
        
        return ranked_keywords[:50]  # Limit to top 50 keywords
    
    def _get_all_swot_elements(self, swot_analysis: SWOTAnalysis) -> List[SWOTElement]:
        """Get all SWOT elements from analysis."""
        return (
            swot_analysis.strengths +
            swot_analysis.weaknesses +
            swot_analysis.opportunities +
            swot_analysis.threats
        )
    
    def _expand_keywords_for_category(
        self,
        keywords: List[str],
        category: SWOTCategory
    ) -> List[str]:
        """Expand keywords based on SWOT category patterns."""
        
        expanded = []
        patterns = self.keyword_expansion_patterns.get(category, {})
        
        for keyword in keywords:
            # Add synonyms
            if "synonyms" in patterns:
                expanded.extend(patterns["synonyms"])
            
            # Add related terms
            if "related_terms" in patterns:
                expanded.extend(patterns["related_terms"])
            
            # Add industry terms
            if "industry_terms" in patterns:
                expanded.extend(patterns["industry_terms"])
        
        return expanded
    
    def _get_impact_area_keywords(self, impact_area: str) -> List[str]:
        """Get keywords related to an impact area."""
        
        impact_area_keywords = {
            "technology": ["AI", "automation", "digital", "innovation", "software"],
            "market": ["competition", "customer", "demand", "trend", "growth"],
            "operations": ["efficiency", "process", "workflow", "productivity", "optimization"],
            "finance": ["cost", "revenue", "investment", "budget", "profitability"],
            "talent": ["skills", "training", "recruitment", "retention", "development"],
            "compliance": ["regulation", "policy", "legal", "compliance", "governance"]
        }
        
        return impact_area_keywords.get(impact_area.lower(), [])
    
    def _get_industry_keywords(self, industry_focus: List[str]) -> List[str]:
        """Get industry-specific keywords."""
        
        keywords = []
        for industry in industry_focus:
            industry_lower = industry.lower()
            for industry_name, industry_keywords in self.industry_keywords.items():
                if industry_name in industry_lower:
                    keywords.extend(industry_keywords)
        
        return keywords
    
    def _get_capability_keywords(self, capabilities: List[AgentCapability]) -> List[str]:
        """Get keywords based on agent capabilities."""
        
        capability_keywords = {
            AgentCapability.NEWS_MONITORING: ["news", "announcement", "press release", "media"],
            AgentCapability.TECHNOLOGY_TRENDS: ["technology", "innovation", "trend", "emerging"],
            AgentCapability.COMPETITOR_TRACKING: ["competitor", "rival", "market share", "competitive"],
            AgentCapability.MARKET_ANALYSIS: ["market", "industry", "sector", "demand", "growth"],
            AgentCapability.TREND_ANALYSIS: ["trend", "analysis", "pattern", "forecast"],
            AgentCapability.CUSTOM_KEYWORD_MONITORING: ["custom", "specific", "targeted"]
        }
        
        keywords = []
        for capability in capabilities:
            if capability in capability_keywords:
                keywords.extend(capability_keywords[capability])
        
        return keywords
    
    def _rank_keywords_by_relevance(
        self,
        keywords: Set[str],
        swot_analysis: SWOTAnalysis
    ) -> List[str]:
        """Rank keywords by relevance to SWOT analysis."""
        
        keyword_scores = {}
        
        for keyword in keywords:
            score = 0
            
            # Check if keyword appears in SWOT elements
            for element in self._get_all_swot_elements(swot_analysis):
                if element.is_active:
                    # Direct match in element keywords
                    if keyword.lower() in [k.lower() for k in element.keywords]:
                        score += 10
                    
                    # Match in element title
                    if keyword.lower() in element.title.lower():
                        score += 8
                    
                    # Match in element description
                    if keyword.lower() in element.description.lower():
                        score += 5
                    
                    # Priority bonus (higher priority = higher score)
                    priority_bonus = (6 - element.priority) * 2
                    score += priority_bonus
            
            # Industry focus bonus
            for industry in swot_analysis.industry_focus:
                if keyword.lower() in industry.lower():
                    score += 3
            
            keyword_scores[keyword] = score
        
        # Sort by score (highest first)
        ranked_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, score in ranked_keywords if score > 0]
    
    def create_swot_aware_agent_config(
        self,
        swot_analysis: SWOTAnalysis,
        base_config: AgentConfig,
        agent_capabilities: List[AgentCapability]
    ) -> AgentConfig:
        """Create an agent configuration optimized for SWOT-based signal detection."""
        
        # Generate SWOT-aware keywords
        swot_keywords = self.generate_agent_keywords_from_swot(swot_analysis, agent_capabilities)
        
        # Combine with existing keywords
        all_keywords = list(set(base_config.keywords + swot_keywords))
        
        # Create enhanced configuration
        enhanced_config = AgentConfig(
            keywords=all_keywords,
            update_frequency_minutes=base_config.update_frequency_minutes,
            max_results_per_update=base_config.max_results_per_update,
            isolation_mode=base_config.isolation_mode,
            filters={
                **base_config.filters,
                "swot_analysis_id": swot_analysis.id,
                "strategic_focus": swot_analysis.industry_focus,
                "market_position": swot_analysis.market_position
            }
        )
        
        return enhanced_config
    
    def get_swot_monitoring_categories(
        self,
        swot_analysis: SWOTAnalysis
    ) -> Dict[str, List[str]]:
        """Get monitoring categories based on SWOT analysis."""
        
        categories = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        # Categorize elements by SWOT category
        for element in swot_analysis.strengths:
            if element.is_active:
                categories["strengths"].append(element.title)
        
        for element in swot_analysis.weaknesses:
            if element.is_active:
                categories["weaknesses"].append(element.title)
        
        for element in swot_analysis.opportunities:
            if element.is_active:
                categories["opportunities"].append(element.title)
        
        for element in swot_analysis.threats:
            if element.is_active:
                categories["threats"].append(element.title)
        
        return categories
    
    def generate_swot_alert_rules(
        self,
        swot_analysis: SWOTAnalysis
    ) -> Dict[str, Any]:
        """Generate alert rules based on SWOT analysis."""
        
        alert_rules = {
            "critical_thresholds": {},
            "priority_weights": {},
            "category_filters": {}
        }
        
        # Set critical thresholds based on element priorities
        for element in self._get_all_swot_elements(swot_analysis):
            if element.is_active:
                # Higher priority elements get lower thresholds (more sensitive)
                threshold = max(0.1, 1.0 - (element.priority * 0.15))
                alert_rules["critical_thresholds"][element.id] = threshold
                
                # Priority weights for scoring
                alert_rules["priority_weights"][element.id] = 6 - element.priority
        
        # Category-specific filters
        alert_rules["category_filters"] = {
            "threats": {"min_priority": "high", "min_confidence": 0.7},
            "opportunities": {"min_priority": "medium", "min_confidence": 0.6},
            "weaknesses": {"min_priority": "medium", "min_confidence": 0.6},
            "strengths": {"min_priority": "low", "min_confidence": 0.5}
        }
        
        return alert_rules
    
    def validate_swot_analysis_for_agents(
        self,
        swot_analysis: SWOTAnalysis
    ) -> Dict[str, Any]:
        """Validate SWOT analysis for agent integration."""
        
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "recommendations": []
        }
        
        # Check if SWOT analysis has enough elements
        total_elements = len(self._get_all_swot_elements(swot_analysis))
        if total_elements < 4:
            validation_result["warnings"].append(
                f"SWOT analysis has only {total_elements} elements. Consider adding more for better signal detection."
            )
        
        # Check if elements have keywords
        elements_without_keywords = []
        for element in self._get_all_swot_elements(swot_analysis):
            if element.is_active and not element.keywords:
                elements_without_keywords.append(element.title)
        
        if elements_without_keywords:
            validation_result["warnings"].append(
                f"Elements without keywords: {', '.join(elements_without_keywords)}. "
                "Keywords improve signal detection accuracy."
            )
        
        # Check priority distribution
        priority_counts = defaultdict(int)
        for element in self._get_all_swot_elements(swot_analysis):
            if element.is_active:
                priority_counts[element.priority] += 1
        
        if not priority_counts:
            validation_result["warnings"].append("No active SWOT elements found.")
            validation_result["is_valid"] = False
        else:
            # Recommend priority distribution
            if max(priority_counts.values()) > 3:
                validation_result["recommendations"].append(
                    "Consider distributing priorities more evenly for better signal prioritization."
                )
        
        # Check industry focus
        if not swot_analysis.industry_focus:
            validation_result["recommendations"].append(
                "Add industry focus areas to improve industry-specific signal detection."
            )
        
        return validation_result
