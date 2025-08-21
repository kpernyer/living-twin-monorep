#!/usr/bin/env python3
"""
Enhanced test script for AI agent with comprehensive content analysis.
"""

import asyncio
import logging
from datetime import datetime
from app.domain.agent_models import Agent, AgentConfig, AgentType, AgentStatus, AgentCapability
from app.domain.agents import NewsMonitoringAgent
from app.domain.content_analyzer import ContentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_enhanced_news_monitoring():
    """Test the enhanced news monitoring agent with full content analysis."""
    
    # Create a test agent configuration
    agent_config = AgentConfig(
        keywords=["AI", "artificial intelligence", "machine learning", "technology", "startup", "funding"],
        sources=["https://techcrunch.com"],
        update_frequency_minutes=60,
        max_results_per_update=5,
        isolation_mode=False,
    )
    
    # Create a test agent
    test_agent = Agent(
        id="test-enhanced-agent",
        name="Enhanced News Monitoring Agent",
        description="Test agent with comprehensive content analysis",
        agent_type=AgentType.TENANT_SPECIFIC,
        capabilities=[AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING],
        status=AgentStatus.ACTIVE,
        config=agent_config,
        tenant_id="test-tenant",
        created_at=datetime.utcnow(),
    )
    
    # Create agent instance
    agent = NewsMonitoringAgent(test_agent)
    
    logger.info("Starting enhanced news monitoring agent test...")
    logger.info(f"Agent: {agent.agent.name}")
    logger.info(f"Keywords: {agent.agent.config.keywords}")
    
    try:
        # Execute the agent
        results = await agent.execute(isolation_mode=True)
        
        logger.info(f"Agent execution completed. Found {len(results)} results.")
        
        # Display enhanced results
        for i, result in enumerate(results, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"RESULT {i}: {result.title}")
            logger.info(f"{'='*60}")
            
            # Basic info
            logger.info(f"Source: {result.source_name}")
            logger.info(f"URL: {result.source_url}")
            logger.info(f"Published: {result.published_at}")
            logger.info(f"Keywords matched: {result.keywords_matched}")
            logger.info(f"Relevance score: {result.relevance_score:.2f}")
            
            # Content analysis
            if "content_analysis" in result.metadata:
                analysis = result.metadata["content_analysis"]
                
                logger.info(f"\n📊 CONTENT ANALYSIS:")
                logger.info(f"  Sentiment: {result.sentiment} (score: {analysis['sentiment_score']:.2f}, confidence: {analysis['sentiment_confidence']:.2f})")
                logger.info(f"  Content type: {analysis['content_type']}")
                logger.info(f"  Readability: {analysis['readability_score']:.1f}/100")
                logger.info(f"  Word count: {analysis['word_count']}")
                logger.info(f"  Sentence count: {analysis['sentence_count']}")
                
                # Themes
                if analysis['themes']:
                    logger.info(f"  Themes: {', '.join(analysis['themes'])}")
                    for theme in analysis['themes']:
                        confidence = analysis['theme_confidence'].get(theme, 0)
                        logger.info(f"    - {theme}: {confidence:.2f} confidence")
                
                # Entities
                if analysis['entities']:
                    logger.info(f"  Entities found:")
                    for entity_type, entities in analysis['entities'].items():
                        confidence = analysis['entity_confidence'].get(entity_type, 0)
                        logger.info(f"    - {entity_type}: {', '.join(entities[:3])} (confidence: {confidence:.2f})")
            
            # Content preview
            logger.info(f"\n📝 CONTENT PREVIEW:")
            logger.info(f"{result.content[:300]}...")
            
        # Summary statistics
        if results:
            logger.info(f"\n{'='*60}")
            logger.info(f"SUMMARY STATISTICS")
            logger.info(f"{'='*60}")
            
            # Sentiment distribution
            sentiment_counts = {}
            for result in results:
                sentiment = result.sentiment
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            logger.info(f"Sentiment distribution: {sentiment_counts}")
            
            # Theme distribution
            all_themes = []
            for result in results:
                if "content_analysis" in result.metadata:
                    all_themes.extend(result.metadata["content_analysis"]["themes"])
            
            if all_themes:
                theme_counts = {}
                for theme in all_themes:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
                
                logger.info(f"Theme distribution: {theme_counts}")
            
            # Average metrics
            avg_relevance = sum(r.relevance_score or 0 for r in results) / len(results)
            avg_readability = 0
            readable_count = 0
            
            for result in results:
                if "content_analysis" in result.metadata:
                    avg_readability += result.metadata["content_analysis"]["readability_score"]
                    readable_count += 1
            
            if readable_count > 0:
                avg_readability /= readable_count
            
            logger.info(f"Average relevance score: {avg_relevance:.2f}")
            logger.info(f"Average readability score: {avg_readability:.1f}/100")
        
        return results
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise


async def test_content_analyzer_directly():
    """Test the content analyzer directly with sample content."""
    
    logger.info(f"\n{'='*60}")
    logger.info("TESTING CONTENT ANALYZER DIRECTLY")
    logger.info(f"{'='*60}")
    
    analyzer = ContentAnalyzer()
    
    # Sample content for testing
    sample_content = """
    Artificial Intelligence Breakthrough: OpenAI Announces GPT-5
    
    OpenAI has announced a revolutionary new language model called GPT-5, which represents 
    a significant breakthrough in artificial intelligence technology. The new model shows 
    unprecedented capabilities in understanding context and generating human-like responses.
    
    According to OpenAI CEO Sam Altman, GPT-5 demonstrates remarkable improvements in 
    reasoning abilities and can now handle complex multi-step problems with greater accuracy. 
    The company claims this represents a major step forward in the field of machine learning.
    
    Industry experts believe this development could accelerate the adoption of AI technologies 
    across various sectors, from healthcare to finance. However, some researchers have expressed 
    concerns about the potential risks associated with such advanced AI systems.
    
    The new model is expected to be available to enterprise customers starting next quarter, 
    with pricing starting at $10,000 per month for basic access. OpenAI has also announced 
    partnerships with Microsoft and Google Cloud to provide infrastructure support.
    """
    
    keywords = ["AI", "artificial intelligence", "machine learning", "OpenAI", "GPT"]
    
    # Analyze the content
    analysis = analyzer.analyze_content(sample_content, "AI Breakthrough: GPT-5 Announcement", keywords)
    
    # Display results
    logger.info("Sample Content Analysis Results:")
    logger.info(f"Word count: {analysis.word_count}")
    logger.info(f"Sentiment: {analysis.sentiment_label} (score: {analysis.sentiment_score:.2f}, confidence: {analysis.confidence:.2f})")
    logger.info(f"Content type: {analysis.content_type}")
    logger.info(f"Readability: {analysis.readability_score:.1f}/100")
    
    if analysis.themes:
        logger.info(f"Themes: {', '.join(analysis.themes)}")
        for theme in analysis.themes:
            confidence = analysis.theme_confidence.get(theme, 0)
            logger.info(f"  - {theme}: {confidence:.2f} confidence")
    
    if analysis.entities:
        logger.info("Entities found:")
        for entity_type, entities in analysis.entities.items():
            confidence = analysis.entity_confidence.get(entity_type, 0)
            logger.info(f"  - {entity_type}: {', '.join(entities)} (confidence: {confidence:.2f})")
    
    # Generate summary
    logger.info(f"\n{analyzer.generate_summary(analysis)}")


async def main():
    """Main test function."""
    logger.info("Starting Enhanced AI Agent Content Analysis Tests")
    logger.info("=" * 80)
    
    # Test 1: Direct content analyzer
    await test_content_analyzer_directly()
    
    # Test 2: Enhanced news monitoring
    logger.info("\n" + "="*80)
    await test_enhanced_news_monitoring()
    
    logger.info("\n" + "=" * 80)
    logger.info("All enhanced tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
