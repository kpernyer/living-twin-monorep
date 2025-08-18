"""AI Agent base classes and interfaces."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

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
        return self.agent.last_run + timedelta(minutes=frequency_minutes)

    def should_run(self) -> bool:
        """Check if agent should run based on schedule."""
        if self.agent.status != AgentStatus.ACTIVE:
            return False

        next_run = self.get_next_run_time()
        return next_run and next_run <= datetime.utcnow()


class NewsMonitoringAgent(BaseAgent):
    """Agent for monitoring news and articles."""

    def get_capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING]

    def validate_config(self, config: AgentConfig) -> bool:
        return (
            len(config.keywords) > 0
            and config.update_frequency_minutes >= 5
            and config.max_results_per_update <= 100
        )

    async def execute(self, isolation_mode: bool = False) -> List[AgentResult]:
        """Execute news monitoring using free APIs."""
        results = []

        try:
            # Use NewsAPI (free tier available)
            if "newsapi" in self.agent.config.api_keys:
                results.extend(await self._fetch_newsapi_results())

            # Use RSS feeds as fallback
            if not results and self.agent.config.sources:
                results.extend(await self._fetch_rss_results())

            # Use a simple web scraping fallback for demo
            if not results:
                results.extend(await self._fetch_demo_results())

        except Exception as e:
            logger.error(f"Error in news monitoring execution: {e}")
            if not isolation_mode:
                raise

        return results

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

    async def _fetch_demo_results(self) -> List[AgentResult]:
        """Fetch demo results for testing."""
        return [
            AgentResult(
                id=str(uuid.uuid4()),
                agent_id=self.agent.id,
                execution_id=self.execution_id,
                tenant_id=self.agent.tenant_id,
                title=f"Demo Article for {', '.join(self.agent.config.keywords)}",
                content=(
                    f"This is a demo article monitoring keywords: "
                    f"{', '.join(self.agent.config.keywords)}"
                ),
                source_name="Demo Source",
                source_url="https://demo.com/article",
                published_at=datetime.utcnow(),
                keywords_matched=self.agent.config.keywords,
                sentiment="neutral",
                created_at=datetime.utcnow(),
            )
        ]


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
        results = []

        try:
            # Monitor major tech news sources
            tech_keywords = [
                "artificial intelligence",
                "machine learning",
                "cloud computing",
                "blockchain",
                "cybersecurity",
                "digital transformation",
                "IoT",
                "5G",
                "quantum computing",
                "edge computing",
            ]

            # Use free APIs or RSS feeds
            results.extend(await self._fetch_tech_trends(tech_keywords))

        except Exception as e:
            logger.error(f"Error in technology trends execution: {e}")
            if not isolation_mode:
                raise

        return results

    async def _fetch_tech_trends(self, keywords: List[str]) -> List[AgentResult]:
        """Fetch technology trends from various sources."""
        # Implementation would aggregate from multiple sources
        return [
            AgentResult(
                id=str(uuid.uuid4()),
                agent_id=self.agent.id,
                execution_id=self.execution_id,
                tenant_id=None,  # Shared agent
                title="AI Breakthrough in Natural Language Processing",
                content=(
                    "Recent developments in large language models show significant "
                    "improvements in understanding context and generating human-like responses."
                ),
                source_name="Tech Trends Weekly",
                source_url="https://techtrends.com/ai-breakthrough",
                published_at=datetime.utcnow(),
                keywords_matched=["artificial intelligence", "machine learning"],
                sentiment="positive",
                created_at=datetime.utcnow(),
            ),
            AgentResult(
                id=str(uuid.uuid4()),
                agent_id=self.agent.id,
                execution_id=self.execution_id,
                tenant_id=None,  # Shared agent
                title="Cloud Computing Market Growth",
                content=(
                    "The cloud computing market continues to expand with hybrid and "
                    "multi-cloud solutions gaining traction."
                ),
                source_name="Cloud Insights",
                source_url="https://cloudinsights.com/market-growth",
                published_at=datetime.utcnow(),
                keywords_matched=["cloud computing"],
                sentiment="positive",
                created_at=datetime.utcnow(),
            ),
        ]


class AgentFactory:
    """Factory for creating agent instances."""

    @staticmethod
    def create_agent(agent: Agent) -> BaseAgent:
        """Create an agent instance based on capabilities."""
        capabilities = set(agent.capabilities)

        if AgentCapability.NEWS_MONITORING in capabilities:
            return NewsMonitoringAgent(agent)
        elif AgentCapability.TECHNOLOGY_TRENDS in capabilities:
            return TechnologyTrendsAgent(agent)
        else:
            raise ValueError(
                f"No agent implementation found for capabilities: {agent.capabilities}"
            )
