#!/usr/bin/env python3
"""
Test script for intelligent source discovery system.
"""

import asyncio
import logging
from datetime import datetime
from app.domain.source_discovery import SourceDiscoveryService, SourceRecommendation
from app.domain.agents import NewsMonitoringAgent
from app.domain.agent_models import Agent, AgentConfig, AgentType, AgentStatus, AgentCapability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockLLMService:
    """Mock LLM service for testing."""
    
    async def answer(self, hits, prompt, rag_only=False):
        """Mock LLM response."""
        return "Mock LLM response for source discovery"


async def test_source_discovery():
    """Test the source discovery system."""
    
    logger.info("Testing Intelligent Source Discovery System")
    logger.info("=" * 60)
    
    # Create mock LLM service
    mock_llm = MockLLMService()
    
    # Create source discovery service
    discovery_service = SourceDiscoveryService(mock_llm)
    
    # Test different tenant scenarios
    test_scenarios = [
        {
            "name": "AI Startup",
            "tenant_id": "ai-startup-001",
            "industry": "Artificial Intelligence",
            "strategic_focus": ["AI", "machine learning", "startup ecosystem", "funding"],
            "budget_tier": "low"
        },
        {
            "name": "Enterprise Tech Company",
            "tenant_id": "enterprise-tech-001", 
            "industry": "Enterprise Technology",
            "strategic_focus": ["digital transformation", "enterprise software", "cloud computing", "cybersecurity"],
            "budget_tier": "medium"
        },
        {
            "name": "Fintech Company",
            "tenant_id": "fintech-001",
            "industry": "Financial Technology", 
            "strategic_focus": ["fintech", "blockchain", "digital payments", "regulatory compliance"],
            "budget_tier": "high"
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n{'='*40}")
        logger.info(f"SCENARIO: {scenario['name']}")
        logger.info(f"{'='*40}")
        logger.info(f"Industry: {scenario['industry']}")
        logger.info(f"Strategic Focus: {', '.join(scenario['strategic_focus'])}")
        logger.info(f"Budget Tier: {scenario['budget_tier']}")
        
        # Discover sources
        sources = await discovery_service.discover_sources_for_tenant(
            tenant_id=scenario['tenant_id'],
            industry=scenario['industry'],
            strategic_focus=scenario['strategic_focus'],
            budget_tier=scenario['budget_tier']
        )
        
        logger.info(f"\n📊 DISCOVERED SOURCES ({len(sources)} total):")
        
        for i, source in enumerate(sources, 1):
            logger.info(f"\n{i}. {source.name}")
            logger.info(f"   URL: {source.url}")
            logger.info(f"   Category: {source.category}")
            logger.info(f"   Relevance: {source.relevance_score:.2f}")
            logger.info(f"   Cost: {source.cost_tier}")
            logger.info(f"   Update Frequency: {source.update_frequency}")
            logger.info(f"   Coverage: {', '.join(source.coverage_areas)}")
            logger.info(f"   API: {'Yes' if source.api_available else 'No'}")
            logger.info(f"   RSS: {'Yes' if source.rss_available else 'No'}")
            logger.info(f"   Web Scraping: {'Yes' if source.web_scraping_allowed else 'No'}")
            logger.info(f"   Keywords: {', '.join(source.recommended_keywords[:3])}...")
        
        # Test agent configuration generation
        if sources:
            logger.info(f"\n🔧 AGENT CONFIGURATION FOR TOP SOURCE:")
            top_source = sources[0]
            config = discovery_service.get_source_config_for_agent(top_source)
            
            logger.info(f"Source: {config['name']}")
            logger.info(f"Rate Limits: {config['rate_limit']}")
            logger.info(f"Keywords: {config['keywords']}")
            logger.info(f"Category: {config['category']}")


async def test_agent_with_discovered_sources():
    """Test creating an agent with discovered sources."""
    
    logger.info(f"\n{'='*60}")
    logger.info("TESTING AGENT WITH DISCOVERED SOURCES")
    logger.info(f"{'='*60}")
    
    # Mock source discovery
    mock_llm = MockLLMService()
    discovery_service = SourceDiscoveryService(mock_llm)
    
    # Discover sources for AI startup
    sources = await discovery_service.discover_sources_for_tenant(
        tenant_id="test-ai-startup",
        industry="Artificial Intelligence",
        strategic_focus=["AI", "machine learning", "startup funding"],
        budget_tier="low"
    )
    
    if not sources:
        logger.warning("No sources discovered, using fallback")
        return
    
    # Create agent with discovered sources
    source_urls = [source.url for source in sources[:3]]  # Use top 3 sources
    keywords = []
    for source in sources[:3]:
        keywords.extend(source.recommended_keywords[:2])  # Use top 2 keywords per source
    
    # Remove duplicates
    keywords = list(set(keywords))
    
    logger.info(f"Creating agent with {len(source_urls)} sources and {len(keywords)} keywords")
    logger.info(f"Sources: {', '.join(source_urls)}")
    logger.info(f"Keywords: {', '.join(keywords)}")
    
    # Create agent configuration
    agent_config = AgentConfig(
        keywords=keywords,
        sources=source_urls,
        update_frequency_minutes=60,
        max_results_per_update=10,
        isolation_mode=False,
    )
    
    # Create agent
    test_agent = Agent(
        id="discovered-sources-agent",
        name="AI Startup Intelligence Agent",
        description="Agent using discovered sources for AI startup monitoring",
        agent_type=AgentType.TENANT_SPECIFIC,
        capabilities=[AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING],
        status=AgentStatus.ACTIVE,
        config=agent_config,
        tenant_id="test-ai-startup",
        created_at=datetime.utcnow(),
    )
    
    # Create and test agent
    agent = NewsMonitoringAgent(test_agent)
    
    logger.info("Executing agent with discovered sources...")
    
    try:
        results = await agent.execute(isolation_mode=True)
        logger.info(f"Agent execution completed. Found {len(results)} results.")
        
        # Show top results
        for i, result in enumerate(results[:3], 1):
            logger.info(f"\n{i}. {result.title}")
            logger.info(f"   Source: {result.source_name}")
            logger.info(f"   Keywords: {result.keywords_matched}")
            logger.info(f"   Sentiment: {result.sentiment}")
            logger.info(f"   Relevance: {result.relevance_score:.2f}")
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")


async def test_source_ranking():
    """Test source ranking and filtering."""
    
    logger.info(f"\n{'='*60}")
    logger.info("TESTING SOURCE RANKING AND FILTERING")
    logger.info(f"{'='*60}")
    
    # Create discovery service
    mock_llm = MockLLMService()
    discovery_service = SourceDiscoveryService(mock_llm)
    
    # Test different budget tiers
    budget_tiers = ["free", "low", "medium", "high"]
    strategic_focus = ["AI", "machine learning", "startup funding"]
    
    for budget_tier in budget_tiers:
        logger.info(f"\n💰 BUDGET TIER: {budget_tier.upper()}")
        logger.info("-" * 30)
        
        sources = await discovery_service.discover_sources_for_tenant(
            tenant_id=f"test-{budget_tier}",
            industry="Artificial Intelligence",
            strategic_focus=strategic_focus,
            budget_tier=budget_tier
        )
        
        logger.info(f"Sources available: {len(sources)}")
        
        # Show cost distribution
        cost_distribution = {}
        for source in sources:
            cost_distribution[source.cost_tier] = cost_distribution.get(source.cost_tier, 0) + 1
        
        logger.info(f"Cost distribution: {cost_distribution}")
        
        # Show top 3 sources
        for i, source in enumerate(sources[:3], 1):
            logger.info(f"{i}. {source.name} ({source.cost_tier}) - {source.relevance_score:.2f}")


async def main():
    """Main test function."""
    logger.info("Starting Source Discovery System Tests")
    logger.info("=" * 80)
    
    # Test 1: Basic source discovery
    await test_source_discovery()
    
    # Test 2: Agent with discovered sources
    await test_agent_with_discovered_sources()
    
    # Test 3: Source ranking and filtering
    await test_source_ranking()
    
    logger.info("\n" + "=" * 80)
    logger.info("All source discovery tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
