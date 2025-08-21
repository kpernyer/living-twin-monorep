#!/usr/bin/env python3
"""
Test script for the enhanced AI agent with real web crawling capabilities.
"""

import asyncio
import logging
from datetime import datetime
from app.domain.agent_models import Agent, AgentConfig, AgentType, AgentStatus, AgentCapability
from app.domain.agents import NewsMonitoringAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_news_monitoring_agent():
    """Test the news monitoring agent with real web crawling."""
    
    # Create a test agent configuration
    agent_config = AgentConfig(
        keywords=["AI", "artificial intelligence", "machine learning", "technology"],
        sources=["https://techcrunch.com", "https://www.theverge.com"],
        update_frequency_minutes=60,
        max_results_per_update=10,
        isolation_mode=False,
    )
    
    # Create a test agent
    test_agent = Agent(
        id="test-news-agent",
        name="Test News Monitoring Agent",
        description="Test agent for monitoring AI and technology news",
        agent_type=AgentType.TENANT_SPECIFIC,
        capabilities=[AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING],
        status=AgentStatus.ACTIVE,
        config=agent_config,
        tenant_id="test-tenant",
        created_at=datetime.utcnow(),
    )
    
    # Create agent instance
    agent = NewsMonitoringAgent(test_agent)
    
    logger.info("Starting news monitoring agent test...")
    logger.info(f"Agent: {agent.agent.name}")
    logger.info(f"Keywords: {agent.agent.config.keywords}")
    logger.info(f"Max results: {agent.agent.config.max_results_per_update}")
    
    try:
        # Execute the agent
        results = await agent.execute(isolation_mode=True)
        
        logger.info(f"Agent execution completed. Found {len(results)} results.")
        
        # Display results
        for i, result in enumerate(results, 1):
            logger.info(f"\n--- Result {i} ---")
            logger.info(f"Title: {result.title}")
            logger.info(f"Source: {result.source_name}")
            logger.info(f"URL: {result.source_url}")
            logger.info(f"Keywords matched: {result.keywords_matched}")
            logger.info(f"Sentiment: {result.sentiment}")
            logger.info(f"Relevance score: {result.relevance_score}")
            logger.info(f"Content preview: {result.content[:200]}...")
            
        # Summary statistics
        if results:
            avg_relevance = sum(r.relevance_score or 0 for r in results) / len(results)
            sentiment_counts = {}
            for result in results:
                sentiment = result.sentiment or "unknown"
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            logger.info(f"\n--- Summary ---")
            logger.info(f"Average relevance score: {avg_relevance:.2f}")
            logger.info(f"Sentiment distribution: {sentiment_counts}")
            logger.info(f"Total keywords found: {len(set(kw for r in results for kw in r.keywords_matched))}")
        
        return results
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise


async def test_agent_with_different_keywords():
    """Test the agent with different keyword sets."""
    
    test_cases = [
        {
            "name": "AI and ML Focus",
            "keywords": ["artificial intelligence", "machine learning", "AI", "ML"],
        },
        {
            "name": "Business Technology",
            "keywords": ["digital transformation", "cloud computing", "enterprise"],
        },
        {
            "name": "Startup Focus",
            "keywords": ["startup", "funding", "venture capital", "innovation"],
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {test_case['name']}")
        logger.info(f"Keywords: {test_case['keywords']}")
        logger.info(f"{'='*50}")
        
        # Create agent config
        agent_config = AgentConfig(
            keywords=test_case["keywords"],
            sources=["https://techcrunch.com"],
            update_frequency_minutes=60,
            max_results_per_update=5,
            isolation_mode=False,
        )
        
        # Create agent
        test_agent = Agent(
            id=f"test-{test_case['name'].lower().replace(' ', '-')}",
            name=f"Test {test_case['name']} Agent",
            description=f"Test agent for {test_case['name']}",
            agent_type=AgentType.TENANT_SPECIFIC,
            capabilities=[AgentCapability.NEWS_MONITORING],
            status=AgentStatus.ACTIVE,
            config=agent_config,
            tenant_id="test-tenant",
            created_at=datetime.utcnow(),
        )
        
        agent = NewsMonitoringAgent(test_agent)
        
        try:
            results = await agent.execute(isolation_mode=True)
            logger.info(f"Found {len(results)} results for {test_case['name']}")
            
            # Show top result
            if results:
                top_result = max(results, key=lambda r: r.relevance_score or 0)
                logger.info(f"Top result: {top_result.title}")
                logger.info(f"Relevance: {top_result.relevance_score:.2f}")
                logger.info(f"Keywords matched: {top_result.keywords_matched}")
                
        except Exception as e:
            logger.error(f"Failed for {test_case['name']}: {e}")


async def main():
    """Main test function."""
    logger.info("Starting AI Agent Web Crawling Tests")
    logger.info("=" * 60)
    
    # Test 1: Basic news monitoring
    logger.info("\n1. Testing basic news monitoring agent...")
    await test_news_monitoring_agent()
    
    # Test 2: Different keyword sets
    logger.info("\n2. Testing different keyword sets...")
    await test_agent_with_different_keywords()
    
    logger.info("\n" + "=" * 60)
    logger.info("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
