"""SWOT-based strategic signal detection service."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter

from .swot_models import (
    SWOTAnalysis, SWOTElement, StrategicSignal, SignalAnalysis,
    SWOTCategory, SignalPriority, SignalImpact, SignalQuery,
    SignalDashboard
)
from .content_analyzer import ContentAnalyzer
from .agent_models import AgentResult

logger = logging.getLogger(__name__)


class SWOTSignalService:
    """Service for detecting and analyzing strategic signals based on SWOT analysis."""
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        
        # Source credibility weights
        self.source_credibility_weights = {
            "government": 1.0,
            "academic": 0.9,
            "industry_report": 0.8,
            "major_news": 0.7,
            "specialist_blog": 0.5,
            "social_media": 0.3
        }
        
        # SWOT keyword patterns for each category
        self.swot_keyword_patterns = {
            SWOTCategory.STRENGTH: {
                "positive": ["strong", "leading", "advantage", "superior", "excellent", "best", "top"],
                "competitive": ["market leader", "competitive advantage", "unique", "differentiated"],
                "capability": ["expertise", "capability", "skill", "talent", "experience"]
            },
            SWOTCategory.WEAKNESS: {
                "negative": ["weak", "poor", "limited", "lack", "deficient", "inadequate"],
                "competitive": ["behind", "lagging", "catch up", "struggle", "challenge"],
                "resource": ["resource constraint", "budget limitation", "skill gap", "technology debt"]
            },
            SWOTCategory.OPPORTUNITY: {
                "positive": ["opportunity", "potential", "growth", "expansion", "new market"],
                "trend": ["trend", "emerging", "growing", "increasing", "rising"],
                "innovation": ["innovation", "breakthrough", "disruption", "new technology"]
            },
            SWOTCategory.THREAT: {
                "negative": ["threat", "risk", "danger", "challenge", "problem", "issue"],
                "competitive": ["competitor", "rival", "new entrant", "substitute", "disruption"],
                "external": ["regulation", "policy", "economic", "market change", "technology shift"]
            }
        }
    
    async def detect_signals_from_agent_results(
        self,
        agent_results: List[AgentResult],
        swot_analysis: SWOTAnalysis,
        tenant_id: str
    ) -> List[StrategicSignal]:
        """Detect strategic signals from agent results using SWOT analysis."""
        
        signals = []
        
        for result in agent_results:
            # Analyze content for SWOT relevance
            swot_relevance = self._analyze_swot_relevance(result, swot_analysis)
            
            if swot_relevance["has_relevance"]:
                # Create strategic signal
                signal = await self._create_strategic_signal(result, swot_relevance, swot_analysis, tenant_id)
                signals.append(signal)
        
        return signals
    
    def _analyze_swot_relevance(
        self,
        agent_result: AgentResult,
        swot_analysis: SWOTAnalysis
    ) -> Dict[str, Any]:
        """Analyze how relevant an agent result is to SWOT elements."""
        
        # Get all SWOT elements
        all_elements = (
            swot_analysis.strengths + 
            swot_analysis.weaknesses + 
            swot_analysis.opportunities + 
            swot_analysis.threats
        )
        
        # Analyze content
        content_analysis = self.content_analyzer.analyze_content(
            agent_result.content,
            agent_result.title,
            agent_result.keywords_matched
        )
        
        # Check relevance to each SWOT element
        element_matches = []
        total_relevance_score = 0.0
        
        for element in all_elements:
            if not element.is_active:
                continue
                
            # Check keyword matches
            keyword_matches = self._check_keyword_matches(
                content_analysis, element.keywords
            )
            
            # Check semantic similarity
            semantic_score = self._calculate_semantic_similarity(
                agent_result.content, element.description
            )
            
            # Calculate element relevance
            element_relevance = self._calculate_element_relevance(
                keyword_matches, semantic_score, element.priority
            )
            
            if element_relevance > 0.3:  # Threshold for relevance
                element_matches.append({
                    "element_id": element.id,
                    "element_title": element.title,
                    "category": element.category,
                    "relevance_score": element_relevance,
                    "keyword_matches": keyword_matches,
                    "semantic_score": semantic_score
                })
                total_relevance_score += element_relevance
        
        # Determine SWOT categories and impact direction
        swot_categories = self._determine_swot_categories(element_matches)
        impact_direction = self._determine_impact_direction(
            swot_categories, content_analysis.sentiment_score
        )
        
        return {
            "has_relevance": len(element_matches) > 0,
            "element_matches": element_matches,
            "total_relevance_score": total_relevance_score,
            "swot_categories": swot_categories,
            "impact_direction": impact_direction,
            "content_analysis": content_analysis
        }
    
    def _check_keyword_matches(
        self,
        content_analysis: Any,
        element_keywords: List[str]
    ) -> List[str]:
        """Check which SWOT element keywords match the content."""
        
        matched_keywords = []
        content_text = f"{content_analysis.keywords_found} {' '.join(content_analysis.themes)}"
        content_lower = content_text.lower()
        
        for keyword in element_keywords:
            if keyword.lower() in content_lower:
                matched_keywords.append(keyword)
        
        return matched_keywords
    
    def _calculate_semantic_similarity(self, content: str, element_description: str) -> float:
        """Calculate semantic similarity between content and SWOT element."""
        
        # Simple word overlap similarity for now
        # TODO: Implement proper embedding-based similarity
        content_words = set(content.lower().split())
        element_words = set(element_description.lower().split())
        
        if not element_words:
            return 0.0
        
        overlap = len(content_words.intersection(element_words))
        similarity = overlap / len(element_words)
        
        return min(1.0, similarity)
    
    def _calculate_element_relevance(
        self,
        keyword_matches: List[str],
        semantic_score: float,
        element_priority: int
    ) -> float:
        """Calculate relevance score for a SWOT element."""
        
        # Keyword match weight
        keyword_weight = len(keyword_matches) * 0.3
        
        # Semantic similarity weight
        semantic_weight = semantic_score * 0.4
        
        # Priority weight (higher priority = higher relevance)
        priority_weight = (6 - element_priority) * 0.1  # 1=highest priority, 5=lowest
        
        total_score = keyword_weight + semantic_weight + priority_weight
        return min(1.0, total_score)
    
    def _determine_swot_categories(
        self,
        element_matches: List[Dict[str, Any]]
    ) -> List[SWOTCategory]:
        """Determine which SWOT categories the signal affects."""
        
        categories = set()
        for match in element_matches:
            categories.add(match["category"])
        
        return list(categories)
    
    def _determine_impact_direction(
        self,
        swot_categories: List[SWOTCategory],
        sentiment_score: float
    ) -> SignalImpact:
        """Determine the impact direction of the signal."""
        
        # Positive sentiment + strengths/opportunities = positive impact
        if sentiment_score > 0.3:
            if any(cat in [SWOTCategory.STRENGTH, SWOTCategory.OPPORTUNITY] for cat in swot_categories):
                return SignalImpact.POSITIVE
        
        # Negative sentiment + weaknesses/threats = negative impact
        if sentiment_score < -0.3:
            if any(cat in [SWOTCategory.WEAKNESS, SWOTCategory.THREAT] for cat in swot_categories):
                return SignalImpact.NEGATIVE
        
        # Mixed categories or neutral sentiment
        if len(swot_categories) > 1:
            return SignalImpact.MIXED
        
        return SignalImpact.NEUTRAL
    
    async def _create_strategic_signal(
        self,
        agent_result: AgentResult,
        swot_relevance: Dict[str, Any],
        swot_analysis: SWOTAnalysis,
        tenant_id: str
    ) -> StrategicSignal:
        """Create a strategic signal from agent result and SWOT analysis."""
        
        # Calculate scores
        relevance_score = min(1.0, swot_relevance["total_relevance_score"])  # Cap at 1.0
        urgency_score = self._calculate_urgency_score(agent_result, swot_relevance)
        confidence_score = self._calculate_confidence_score(agent_result, swot_relevance)
        strategic_impact_score = min(1.0, self._calculate_strategic_impact_score(
            relevance_score, urgency_score, confidence_score
        ))  # Cap at 1.0
        
        # Determine priority
        priority = self._determine_priority(strategic_impact_score, swot_relevance["impact_direction"])
        
        # Generate summary
        summary = self._generate_signal_summary(agent_result, swot_relevance)
        
        # Get affected elements
        affected_elements = [match["element_id"] for match in swot_relevance["element_matches"]]
        
        return StrategicSignal(
            tenant_id=tenant_id,
            title=agent_result.title,
            content=agent_result.content,
            summary=summary,
            source_url=agent_result.source_url,
            source_name=agent_result.source_name,
            source_credibility=self._get_source_credibility(agent_result.source_name),
            published_at=agent_result.published_at,
            swot_categories=swot_relevance["swot_categories"],
            affected_elements=affected_elements,
            impact_direction=swot_relevance["impact_direction"],
            priority=priority,
            relevance_score=relevance_score,
            urgency_score=urgency_score,
            confidence_score=confidence_score,
            strategic_impact_score=strategic_impact_score,
            keywords_matched=agent_result.keywords_matched,
            entities=swot_relevance["content_analysis"].entities,
            themes=swot_relevance["content_analysis"].themes,
            sentiment=swot_relevance["content_analysis"].sentiment_label,
            first_detected=agent_result.created_at,
            metadata={
                "agent_result_id": agent_result.id,
                "agent_id": agent_result.agent_id,
                "swot_analysis_id": swot_analysis.id,
                "content_analysis": {
                    "word_count": swot_relevance["content_analysis"].word_count,
                    "readability_score": swot_relevance["content_analysis"].readability_score,
                    "content_type": swot_relevance["content_analysis"].content_type
                }
            }
        )
    
    def _calculate_urgency_score(
        self,
        agent_result: AgentResult,
        swot_relevance: Dict[str, Any]
    ) -> float:
        """Calculate urgency score based on recency and impact."""
        
        # Recency factor (newer = more urgent)
        hours_old = (datetime.utcnow() - agent_result.created_at).total_seconds() / 3600
        recency_factor = max(0, 1.0 - (hours_old / 168))  # Decay over 1 week
        
        # Impact factor (critical categories = more urgent)
        impact_factor = 0.5
        if SWOTCategory.THREAT in swot_relevance["swot_categories"]:
            impact_factor = 1.0
        elif SWOTCategory.OPPORTUNITY in swot_relevance["swot_categories"]:
            impact_factor = 0.8
        
        return (recency_factor + impact_factor) / 2
    
    def _calculate_confidence_score(
        self,
        agent_result: AgentResult,
        swot_relevance: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on source and analysis quality."""
        
        # Source credibility
        source_credibility = self._get_source_credibility(agent_result.source_name)
        
        # Analysis confidence
        analysis_confidence = swot_relevance["content_analysis"].confidence
        
        # Element match confidence
        element_confidence = sum(match["relevance_score"] for match in swot_relevance["element_matches"]) / len(swot_relevance["element_matches"]) if swot_relevance["element_matches"] else 0
        
        return (source_credibility + analysis_confidence + element_confidence) / 3
    
    def _calculate_strategic_impact_score(
        self,
        relevance_score: float,
        urgency_score: float,
        confidence_score: float
    ) -> float:
        """Calculate overall strategic impact score."""
        
        # Weighted combination
        return (
            relevance_score * 0.4 +
            urgency_score * 0.3 +
            confidence_score * 0.3
        )
    
    def _determine_priority(
        self,
        strategic_impact_score: float,
        impact_direction: SignalImpact
    ) -> SignalPriority:
        """Determine priority based on strategic impact score and direction."""
        
        if strategic_impact_score >= 0.8:
            return SignalPriority.CRITICAL
        elif strategic_impact_score >= 0.6:
            return SignalPriority.HIGH
        elif strategic_impact_score >= 0.4:
            return SignalPriority.MEDIUM
        elif strategic_impact_score >= 0.2:
            return SignalPriority.LOW
        else:
            return SignalPriority.MONITOR
    
    def _generate_signal_summary(
        self,
        agent_result: AgentResult,
        swot_relevance: Dict[str, Any]
    ) -> str:
        """Generate a summary of the strategic signal."""
        
        # Handle both enum objects and string values
        categories = []
        for cat in swot_relevance["swot_categories"]:
            if hasattr(cat, 'value'):
                categories.append(cat.value)
            else:
                categories.append(cat)
        
        impact = swot_relevance["impact_direction"]
        if hasattr(impact, 'value'):
            impact = impact.value
        
        summary = f"Signal detected affecting {', '.join(categories)} with {impact} impact. "
        
        if swot_relevance["element_matches"]:
            top_element = max(swot_relevance["element_matches"], key=lambda x: x["relevance_score"])
            summary += f"Most relevant to: {top_element['element_title']}."
        
        return summary
    
    def _get_source_credibility(self, source_name: str) -> float:
        """Get credibility score for a source."""
        
        source_lower = source_name.lower()
        
        for source_type, credibility in self.source_credibility_weights.items():
            if source_type in source_lower:
                return credibility
        
        return 0.5  # Default credibility
    
    async def analyze_signal_impact(
        self,
        signal: StrategicSignal,
        swot_analysis: SWOTAnalysis
    ) -> SignalAnalysis:
        """Analyze the strategic impact of a signal on SWOT elements."""
        
        # Get affected elements
        affected_elements = []
        for element_id in signal.affected_elements:
            for element in (swot_analysis.strengths + swot_analysis.weaknesses + 
                          swot_analysis.opportunities + swot_analysis.threats):
                if element.id == element_id:
                    affected_elements.append(element)
                    break
        
        # Analyze impact by SWOT category
        swot_impacts = defaultdict(list)
        strategic_implications = []
        recommended_actions = []
        
        for element in affected_elements:
            impact_analysis = self._analyze_element_impact(signal, element)
            swot_impacts[element.category].append(impact_analysis)
            
            if impact_analysis["implications"]:
                strategic_implications.extend(impact_analysis["implications"])
            
            if impact_analysis["actions"]:
                recommended_actions.extend(impact_analysis["actions"])
        
        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(signal, affected_elements)
        
        return SignalAnalysis(
            signal_id=signal.id,
            tenant_id=signal.tenant_id,
            swot_impacts=dict(swot_impacts),
            strategic_implications=list(set(strategic_implications)),  # Remove duplicates
            recommended_actions=list(set(recommended_actions)),  # Remove duplicates
            risk_assessment=risk_assessment,
            confidence=signal.confidence_score
        )
    
    def _analyze_element_impact(
        self,
        signal: StrategicSignal,
        element: SWOTElement
    ) -> Dict[str, Any]:
        """Analyze how a signal impacts a specific SWOT element."""
        
        impact_strength = "moderate"
        if signal.strategic_impact_score >= 0.8:
            impact_strength = "strong"
        elif signal.strategic_impact_score <= 0.3:
            impact_strength = "weak"
        
        implications = []
        actions = []
        
        # Generate implications based on category and impact
        if element.category == SWOTCategory.STRENGTH:
            if signal.impact_direction == SignalImpact.POSITIVE:
                implications.append(f"Strengthens our {element.title}")
                actions.append(f"Leverage this to enhance {element.title}")
            else:
                implications.append(f"May weaken our {element.title}")
                actions.append(f"Monitor and protect {element.title}")
        
        elif element.category == SWOTCategory.WEAKNESS:
            if signal.impact_direction == SignalImpact.POSITIVE:
                implications.append(f"May help address {element.title}")
                actions.append(f"Explore how to leverage this to improve {element.title}")
            else:
                implications.append(f"Exacerbates our {element.title}")
                actions.append(f"Develop mitigation strategies for {element.title}")
        
        elif element.category == SWOTCategory.OPPORTUNITY:
            if signal.impact_direction == SignalImpact.POSITIVE:
                implications.append(f"Enhances opportunity in {element.title}")
                actions.append(f"Act quickly to capitalize on {element.title}")
            else:
                implications.append(f"May reduce opportunity in {element.title}")
                actions.append(f"Reassess strategy for {element.title}")
        
        elif element.category == SWOTCategory.THREAT:
            if signal.impact_direction == SignalImpact.POSITIVE:
                implications.append(f"May help mitigate threat in {element.title}")
                actions.append(f"Explore defensive strategies for {element.title}")
            else:
                implications.append(f"Increases threat level in {element.title}")
                actions.append(f"Develop urgent response plan for {element.title}")
        
        return {
            "element_id": element.id,
            "element_title": element.title,
            "impact_strength": impact_strength,
            "implications": implications,
            "actions": actions
        }
    
    def _generate_risk_assessment(
        self,
        signal: StrategicSignal,
        affected_elements: List[SWOTElement]
    ) -> str:
        """Generate a risk assessment summary."""
        
        if signal.priority == SignalPriority.CRITICAL:
            risk_level = "High"
            urgency = "Immediate action required"
        elif signal.priority == SignalPriority.HIGH:
            risk_level = "Medium-High"
            urgency = "Prompt attention needed"
        elif signal.priority == SignalPriority.MEDIUM:
            risk_level = "Medium"
            urgency = "Monitor closely"
        else:
            risk_level = "Low"
            urgency = "Continue monitoring"
        
        element_count = len(affected_elements)
        categories = []
        for elem in affected_elements:
            if hasattr(elem.category, 'value'):
                categories.append(elem.category.value)
            else:
                categories.append(elem.category)
        
        return f"{risk_level} risk level. {urgency}. Affects {element_count} SWOT elements across {', '.join(set(categories))} categories."
