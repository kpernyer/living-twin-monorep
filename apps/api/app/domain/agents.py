"""AI Agent base classes and interfaces."""

import logging
import uuid
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

from .agent_models import (
    Agent,
    AgentCapability,
    AgentConfig,
    AgentExecution,
    AgentResult,
    AgentStatus,
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.execution_id: Optional[str] = None
        self.is_running = False

    @abstractmethod
    async def execute(self, isolation_mode: bool = False) -> List[AgentResult]:
        """Execute the agent and return results."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get the capabilities this agent supports."""
        pass

    @abstractmethod
    def validate_config(self, config: AgentConfig) -> bool:
        """Validate agent configuration."""
        pass

    async def run(self, isolation_mode: bool = False) -> AgentExecution:
        """Run the agent and return execution record."""
        if self.is_running:
            raise RuntimeError(f"Agent {self.agent.id} is already running")

        self.is_running = True
        self.execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        execution = AgentExecution(
            id=self.execution_id,
            agent_id=self.agent.id,
            tenant_id=self.agent.tenant_id,
            started_at=start_time,
            status="running",
        )

        try:
            logger.info(f"Starting agent execution {self.execution_id} for agent {self.agent.id}")

            # Execute the agent
            results = await self.execute(isolation_mode=isolation_mode)

            # Update execution record
            end_time = datetime.utcnow()
            execution.completed_at = end_time
            execution.status = "completed"
            execution.results_count = len(results)
            execution.execution_time_seconds = (end_time - start_time).total_seconds()
            execution.metadata = {
                "isolation_mode": isolation_mode,
                "capabilities_used": [cap.value for cap in self.get_capabilities()],
            }

            logger.info(
                f"Agent execution {self.execution_id} completed with {len(results)} results"
            )

        except Exception as e:
            logger.error(f"Agent execution {self.execution_id} failed: {e}")
            end_time = datetime.utcnow()
            execution.completed_at = end_time
            execution.status = "failed"
            execution.error_message = str(e)
            execution.execution_time_seconds = (end_time - start_time).total_seconds()

        finally:
            self.is_running = False

        return execution

    def get_next_run_time(self) -> Optional[datetime]:
        """Calculate next run time based on frequency."""
        if not self.agent.last_run:
            return datetime.utcnow()

        frequency_minutes = self.agent.config.update_frequency_minutes
        next_run = self.agent.last_run + timedelta(minutes=frequency_minutes)
        return next_run

    def should_run(self) -> bool:
        """Check if the agent should run based on schedule."""
        next_run = self.get_next_run_time()
        return next_run and next_run <= datetime.utcnow()


class NewsMonitoringAgent(BaseAgent):
    """Agent for monitoring news and articles with real web crawling."""

    def get_capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING]

    def validate_config(self, config: AgentConfig) -> bool:
        return (
            len(config.keywords) > 0
            and config.update_frequency_minutes >= 5
            and config.max_results_per_update <= 100
        )

    async def execute(self, isolation_mode: bool = False) -> List[AgentResult]:
        """Execute news monitoring using real web crawling."""
        results = []

        try:
            # Use NewsAPI (free tier available)
            if "newsapi" in self.agent.config.api_keys:
                results.extend(await self._fetch_newsapi_results())

            # Use RSS feeds as fallback
            if not results and self.agent.config.sources:
                results.extend(await self._fetch_rss_results())

            # Use real web scraping for demo sites
            if not results:
                results.extend(await self._fetch_web_results())

        except Exception as e:
            logger.error(f"Error in news monitoring execution: {e}")
            if not isolation_mode:
                raise

        return results[:self.agent.config.max_results_per_update]

    async def _fetch_newsapi_results(self) -> List[AgentResult]:
        """Fetch results from NewsAPI."""
        # Implementation would use NewsAPI
        # For now, return demo data
        return [
            AgentResult(
                id=str(uuid.uuid4()),
                agent_id=self.agent.id,
                execution_id=self.execution_id,
                tenant_id=self.agent.tenant_id,
                title="Sample News Article",
                content="This is a sample news article about technology trends.",
                source_name="Tech News",
                source_url="https://example.com/article",
                published_at=datetime.utcnow(),
                keywords_matched=self.agent.config.keywords[:2],
                sentiment="positive",
                created_at=datetime.utcnow(),
            )
        ]

    async def _fetch_rss_results(self) -> List[AgentResult]:
        """Fetch results from RSS feeds."""
        # Implementation would parse RSS feeds
        return []

    async def _fetch_web_results(self) -> List[AgentResult]:
        """Fetch results from real web scraping."""
        results = []
        
        # Demo sites to crawl (replace with real news sites)
        demo_sites = [
            "https://techcrunch.com",
            "https://www.theverge.com",
            "https://www.wired.com",
        ]
        
        async with aiohttp.ClientSession() as session:
            for site in demo_sites:
                try:
                    site_results = await self._scrape_site(session, site)
                    results.extend(site_results)
                except Exception as e:
                    logger.warning(f"Failed to scrape {site}: {e}")
                    continue
                
                # Limit results per site
                if len(results) >= self.agent.config.max_results_per_update:
                    break
        
        return results

    async def _scrape_site(self, session: aiohttp.ClientSession, base_url: str) -> List[AgentResult]:
        """Scrape a specific site for articles."""
        results = []
        
        try:
            # Get the main page
            async with session.get(base_url, timeout=10) as response:
                if response.status != 200:
                    return results
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find article links (this is a simplified approach)
                article_links = []
                
                # Look for common article link patterns
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and self._is_article_link(href, base_url):
                        full_url = urljoin(base_url, href)
                        title = link.get_text(strip=True)
                        if title and len(title) > 10:  # Basic title validation
                            article_links.append((full_url, title))
                
                # Limit articles to process
                article_links = article_links[:5]
                
                # Process each article
                for url, title in article_links:
                    try:
                        article_result = await self._scrape_article(session, url, title, base_url)
                        if article_result:
                            results.append(article_result)
                    except Exception as e:
                        logger.warning(f"Failed to scrape article {url}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to scrape site {base_url}: {e}")
        
        return results

    async def _scrape_article(self, session: aiohttp.ClientSession, url: str, title: str, source_name: str) -> Optional[AgentResult]:
        """Scrape a specific article."""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract article content
                content = self._extract_article_content(soup)
                if not content or len(content) < 50:  # Basic content validation
                    return None
                
                # Check if content matches keywords
                keywords_matched = self._find_matching_keywords(content, title)
                if not keywords_matched:
                    return None
                
                # Perform comprehensive content analysis
                from .content_analyzer import ContentAnalyzer
                analyzer = ContentAnalyzer()
                analysis = analyzer.analyze_content(content, title, self.agent.config.keywords)
                
                # Extract publication date
                published_at = self._extract_publication_date(soup)
                
                return AgentResult(
                    id=str(uuid.uuid4()),
                    agent_id=self.agent.id,
                    execution_id=self.execution_id or str(uuid.uuid4()),
                    tenant_id=self.agent.tenant_id,
                    title=title,
                    content=content[:1000],  # Limit content length
                    source_name=source_name,
                    source_url=url,
                    published_at=published_at,
                    keywords_matched=keywords_matched,
                    sentiment=analysis.sentiment_label,
                    relevance_score=self._calculate_relevance_score(content, keywords_matched),
                    created_at=datetime.utcnow(),
                    metadata={
                        "content_analysis": {
                            "themes": analysis.themes,
                            "theme_confidence": analysis.theme_confidence,
                            "entities": analysis.entities,
                            "entity_confidence": analysis.entity_confidence,
                            "readability_score": analysis.readability_score,
                            "content_type": analysis.content_type,
                            "sentiment_score": analysis.sentiment_score,
                            "sentiment_confidence": analysis.confidence,
                            "word_count": analysis.word_count,
                            "sentence_count": analysis.sentence_count,
                        }
                    }
                )
                
        except Exception as e:
            logger.warning(f"Failed to scrape article {url}: {e}")
            return None

    def _is_article_link(self, href: str, base_url: str) -> bool:
        """Check if a link is likely an article link."""
        # Simple heuristics for article links
        article_patterns = [
            r'/article/',
            r'/post/',
            r'/story/',
            r'/news/',
            r'/202[0-9]/',  # Year patterns
            r'/[0-9]{4}/[0-9]{2}/',  # Date patterns
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        return False

    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """Extract article content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for common article content containers
        content_selectors = [
            'article',
            '[class*="article"]',
            '[class*="content"]',
            '[class*="post"]',
            '[class*="entry"]',
            'main',
            '.post-content',
            '.article-content',
            '.entry-content',
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 100:  # Basic content validation
                    return text
        
        # Fallback: get all text
        return soup.get_text(separator=' ', strip=True)

    def _find_matching_keywords(self, content: str, title: str) -> List[str]:
        """Find keywords that match in the content."""
        matched = []
        content_lower = (content + " " + title).lower()
        
        for keyword in self.agent.config.keywords:
            if keyword.lower() in content_lower:
                matched.append(keyword)
        
        return matched

    def _analyze_sentiment(self, content: str) -> str:
        """Simple sentiment analysis."""
        # Use the content analyzer for better sentiment analysis
        from .content_analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
        analysis = analyzer.analyze_content(content)
        return analysis.sentiment_label

    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date from article."""
        # Look for common date selectors
        date_selectors = [
            'time[datetime]',
            '[class*="date"]',
            '[class*="published"]',
            'meta[property="article:published_time"]',
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                try:
                    if date_elem.name == 'meta':
                        date_str = date_elem.get('content')
                    else:
                        date_str = date_elem.get('datetime') or date_elem.get_text()
                    
                    if date_str:
                        # Try to parse the date
                        from dateutil import parser
                        return parser.parse(date_str)
                except Exception:
                    continue
        
        return datetime.utcnow()

    def _calculate_relevance_score(self, content: str, keywords_matched: List[str]) -> float:
        """Calculate relevance score based on keyword matches."""
        if not keywords_matched:
            return 0.0
        
        # Simple scoring: more keywords = higher score
        keyword_density = len(keywords_matched) / len(self.agent.config.keywords)
        return min(1.0, keyword_density * 2.0)  # Scale to 0-1 range


class TechnologyTrendsAgent(BaseAgent):
    """Shared agent for monitoring global technology trends."""

    def get_capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.TECHNOLOGY_TRENDS, AgentCapability.TREND_ANALYSIS]

    def validate_config(self, config: AgentConfig) -> bool:
        return (
            config.update_frequency_minutes >= 30  # Less frequent for global trends
            and config.max_results_per_update <= 50
        )

    async def execute(self, isolation_mode: bool = False) -> List[AgentResult]:
        """Execute technology trends monitoring."""
        # Similar implementation to NewsMonitoringAgent but focused on tech trends
        return await self._fetch_tech_trends()

    async def _fetch_tech_trends(self) -> List[AgentResult]:
        """Fetch technology trends from various sources."""
        # Implementation for tech trends
        return [
            AgentResult(
                id=str(uuid.uuid4()),
                agent_id=self.agent.id,
                execution_id=self.execution_id,
                tenant_id=self.agent.tenant_id,
                title="AI and Machine Learning Trends",
                content="Recent developments in AI and ML show increasing adoption in enterprise applications.",
                source_name="Tech Trends Analysis",
                source_url="https://tech-trends.com/ai-ml",
                published_at=datetime.utcnow(),
                keywords_matched=["AI", "machine learning"],
                sentiment="positive",
                created_at=datetime.utcnow(),
            )
        ]


class AgentFactory:
    """Factory for creating agent instances."""

    @staticmethod
    def create_agent(agent: Agent) -> BaseAgent:
        """Create an agent instance based on agent type."""
        # This would be extended with more agent types
        if "news" in agent.name.lower() or AgentCapability.NEWS_MONITORING in agent.capabilities:
            return NewsMonitoringAgent(agent)
        elif "tech" in agent.name.lower() or AgentCapability.TECHNOLOGY_TRENDS in agent.capabilities:
            return TechnologyTrendsAgent(agent)
        else:
            # Default to news monitoring
            return NewsMonitoringAgent(agent)
