"""Intelligent source discovery for AI agents based on tenant context."""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SourceRecommendation:
    """A recommended source for monitoring."""
    
    name: str
    url: str
    category: str  # "news", "research", "financial", "social", "competitive"
    relevance_score: float  # 0.0 to 1.0
    cost_tier: str  # "free", "low", "medium", "high"
    update_frequency: str  # "real_time", "daily", "weekly", "monthly"
    coverage_areas: List[str]  # e.g., ["AI", "fintech", "enterprise"]
    api_available: bool
    rss_available: bool
    web_scraping_allowed: bool
    description: str
    recommended_keywords: List[str]


class SourceDiscoveryService:
    """Service for discovering and recommending relevant sources."""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.tenant_sources_cache: Dict[str, List[SourceRecommendation]] = {}
        
        # Curated source database
        self.curated_sources = {
            "tech_general": [
                SourceRecommendation(
                    name="TechCrunch",
                    url="https://techcrunch.com",
                    category="news",
                    relevance_score=0.8,
                    cost_tier="free",
                    update_frequency="real_time",
                    coverage_areas=["startups", "tech", "AI", "funding"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="Leading technology news and startup coverage",
                    recommended_keywords=["startup", "funding", "AI", "technology"]
                ),
                SourceRecommendation(
                    name="The Verge",
                    url="https://www.theverge.com",
                    category="news",
                    relevance_score=0.7,
                    cost_tier="free",
                    update_frequency="real_time",
                    coverage_areas=["tech", "AI", "consumer", "policy"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="Technology, science, art, and culture coverage",
                    recommended_keywords=["technology", "AI", "policy", "consumer"]
                ),
                SourceRecommendation(
                    name="Wired",
                    url="https://www.wired.com",
                    category="news",
                    relevance_score=0.7,
                    cost_tier="free",
                    update_frequency="daily",
                    coverage_areas=["tech", "AI", "cybersecurity", "business"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="In-depth technology and business analysis",
                    recommended_keywords=["technology", "AI", "cybersecurity", "business"]
                ),
            ],
            "ai_ml": [
                SourceRecommendation(
                    name="AI News",
                    url="https://artificialintelligence-news.com",
                    category="news",
                    relevance_score=0.9,
                    cost_tier="free",
                    update_frequency="daily",
                    coverage_areas=["AI", "machine learning", "deep learning"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="Dedicated AI and machine learning news",
                    recommended_keywords=["AI", "artificial intelligence", "machine learning", "deep learning"]
                ),
                SourceRecommendation(
                    name="MIT Technology Review",
                    url="https://www.technologyreview.com",
                    category="research",
                    relevance_score=0.9,
                    cost_tier="low",
                    update_frequency="weekly",
                    coverage_areas=["AI", "technology", "research", "innovation"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="In-depth technology research and analysis",
                    recommended_keywords=["AI", "technology", "research", "innovation"]
                ),
            ],
            "startup_ecosystem": [
                SourceRecommendation(
                    name="Crunchbase",
                    url="https://www.crunchbase.com",
                    category="competitive",
                    relevance_score=0.9,
                    cost_tier="medium",
                    update_frequency="real_time",
                    coverage_areas=["startups", "funding", "investments", "companies"],
                    api_available=True,
                    rss_available=False,
                    web_scraping_allowed=False,
                    description="Comprehensive startup and investment database",
                    recommended_keywords=["startup", "funding", "investment", "venture capital"]
                ),
                SourceRecommendation(
                    name="AngelList",
                    url="https://angel.co",
                    category="competitive",
                    relevance_score=0.8,
                    cost_tier="free",
                    update_frequency="daily",
                    coverage_areas=["startups", "jobs", "investments"],
                    api_available=False,
                    rss_available=False,
                    web_scraping_allowed=True,
                    description="Startup job board and investment platform",
                    recommended_keywords=["startup", "hiring", "investment", "jobs"]
                ),
            ],
            "enterprise_tech": [
                SourceRecommendation(
                    name="CIO.com",
                    url="https://www.cio.com",
                    category="news",
                    relevance_score=0.8,
                    cost_tier="free",
                    update_frequency="daily",
                    coverage_areas=["enterprise", "IT", "digital transformation", "leadership"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="Enterprise IT leadership and strategy",
                    recommended_keywords=["enterprise", "IT", "digital transformation", "leadership"]
                ),
                SourceRecommendation(
                    name="ZDNet",
                    url="https://www.zdnet.com",
                    category="news",
                    relevance_score=0.7,
                    cost_tier="free",
                    update_frequency="real_time",
                    coverage_areas=["enterprise", "tech", "business", "security"],
                    api_available=False,
                    rss_available=True,
                    web_scraping_allowed=True,
                    description="Technology news for business professionals",
                    recommended_keywords=["enterprise", "technology", "business", "security"]
                ),
            ],
        }
    
    async def discover_sources_for_tenant(
        self, 
        tenant_id: str, 
        industry: str, 
        strategic_focus: List[str],
        budget_tier: str = "low"
    ) -> List[SourceRecommendation]:
        """Discover relevant sources for a specific tenant."""
        
        # Check cache first
        cache_key = f"{tenant_id}_{industry}_{budget_tier}"
        if cache_key in self.tenant_sources_cache:
            return self.tenant_sources_cache[cache_key]
        
        # Use LLM to analyze tenant context and recommend sources
        llm_recommendations = await self._get_llm_source_recommendations(
            industry, strategic_focus, budget_tier
        )
        
        # Combine LLM recommendations with curated sources
        all_sources = self._combine_sources(llm_recommendations, industry, budget_tier)
        
        # Filter and rank sources
        ranked_sources = self._rank_sources(all_sources, strategic_focus, budget_tier)
        
        # Cache results
        self.tenant_sources_cache[cache_key] = ranked_sources
        
        return ranked_sources
    
    async def _get_llm_source_recommendations(
        self, 
        industry: str, 
        strategic_focus: List[str], 
        budget_tier: str
    ) -> List[Dict]:
        """Use LLM to recommend sources based on tenant context."""
        
        prompt = f"""
        You are a strategic intelligence expert. Recommend 5-10 high-quality sources for monitoring 
        {industry} industry with focus on {', '.join(strategic_focus)}.
        
        Budget tier: {budget_tier}
        
        For each source, provide:
        - name: Source name
        - url: Website URL
        - category: news/research/financial/social/competitive
        - relevance_score: 0.0-1.0
        - cost_tier: free/low/medium/high
        - update_frequency: real_time/daily/weekly/monthly
        - coverage_areas: List of topics covered
        - description: Brief description
        - recommended_keywords: List of keywords to monitor
        
        Focus on sources that provide:
        1. Industry-specific news and analysis
        2. Competitive intelligence
        3. Market research and trends
        4. Financial performance data
        5. Regulatory and policy updates
        
        Return as JSON array of source objects.
        """
        
        try:
            response = await self.llm_service.answer([], prompt, rag_only=False)
            # Parse JSON response and return structured data
            # This is a simplified version - in practice, you'd parse the JSON response
            return []
        except Exception as e:
            logger.warning(f"LLM source discovery failed: {e}")
            return []
    
    def _combine_sources(
        self, 
        llm_recommendations: List[Dict], 
        industry: str, 
        budget_tier: str
    ) -> List[SourceRecommendation]:
        """Combine LLM recommendations with curated sources."""
        
        combined_sources = []
        
        # Always include general tech sources for technology companies
        combined_sources.extend(self.curated_sources["tech_general"])
        
        # Add industry-specific sources
        industry_lower = industry.lower()
        
        if any(keyword in industry_lower for keyword in ["ai", "artificial intelligence", "machine learning"]):
            combined_sources.extend(self.curated_sources["ai_ml"])
        
        if any(keyword in industry_lower for keyword in ["startup", "venture", "funding"]):
            combined_sources.extend(self.curated_sources["startup_ecosystem"])
        
        if any(keyword in industry_lower for keyword in ["enterprise", "business", "corporate"]):
            combined_sources.extend(self.curated_sources["enterprise_tech"])
        
        # Add LLM recommendations (converted to SourceRecommendation objects)
        for rec in llm_recommendations:
            # Convert LLM recommendation to SourceRecommendation
            # This would be implemented based on the actual LLM response format
            pass
        
        return combined_sources
    
    def _rank_sources(
        self, 
        sources: List[SourceRecommendation], 
        strategic_focus: List[str], 
        budget_tier: str
    ) -> List[SourceRecommendation]:
        """Rank sources by relevance and budget constraints."""
        
        # Filter by budget
        budget_filters = {
            "free": ["free"],
            "low": ["free", "low"],
            "medium": ["free", "low", "medium"],
            "high": ["free", "low", "medium", "high"]
        }
        
        allowed_cost_tiers = budget_filters.get(budget_tier, ["free"])
        filtered_sources = [s for s in sources if s.cost_tier in allowed_cost_tiers]
        
        # Score sources based on strategic focus alignment
        scored_sources = []
        for source in filtered_sources:
            score = self._calculate_strategic_alignment_score(source, strategic_focus)
            scored_sources.append((score, source))
        
        # Sort by score (highest first) and return top sources
        scored_sources.sort(key=lambda x: x[0], reverse=True)
        return [source for score, source in scored_sources[:10]]  # Top 10
    
    def _calculate_strategic_alignment_score(
        self, 
        source: SourceRecommendation, 
        strategic_focus: List[str]
    ) -> float:
        """Calculate how well a source aligns with strategic focus."""
        
        # Base score from relevance
        score = source.relevance_score
        
        # Bonus for coverage area overlap
        focus_lower = [f.lower() for f in strategic_focus]
        coverage_lower = [c.lower() for c in source.coverage_areas]
        
        overlap = len(set(focus_lower) & set(coverage_lower))
        if overlap > 0:
            score += overlap * 0.1  # 0.1 bonus per matching area
        
        # Bonus for real-time updates
        if source.update_frequency == "real_time":
            score += 0.1
        
        # Bonus for API availability
        if source.api_available:
            score += 0.2
        
        return min(1.0, score)  # Cap at 1.0
    
    def get_source_config_for_agent(
        self, 
        source: SourceRecommendation
    ) -> Dict:
        """Get configuration for using a source in an agent."""
        
        return {
            "name": source.name,
            "url": source.url,
            "category": source.category,
            "update_frequency": source.update_frequency,
            "keywords": source.recommended_keywords,
            "api_available": source.api_available,
            "rss_available": source.rss_available,
            "web_scraping_allowed": source.web_scraping_allowed,
            "rate_limit": self._get_rate_limit_for_source(source),
            "headers": self._get_headers_for_source(source),
        }
    
    def _get_rate_limit_for_source(self, source: SourceRecommendation) -> Dict:
        """Get rate limiting configuration for a source."""
        
        # Default rate limits
        default_limits = {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "requests_per_day": 1000,
        }
        
        # Adjust based on source characteristics
        if source.api_available:
            default_limits["requests_per_minute"] = 30
            default_limits["requests_per_hour"] = 300
        
        if source.cost_tier == "high":
            default_limits["requests_per_minute"] = 60
            default_limits["requests_per_hour"] = 1000
        
        return default_limits
    
    def _get_headers_for_source(self, source: SourceRecommendation) -> Dict:
        """Get appropriate headers for scraping a source."""
        
        return {
            "User-Agent": "LivingTwin-Agent/1.0 (Strategic Intelligence Bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
