"""Configuration settings for the AI Agent system."""

import os
from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """AI Agent specific settings."""

    # Agent System Settings
    agent_scheduler_enabled: bool = os.getenv("AGENT_SCHEDULER_ENABLED", "true").lower() == "true"
    agent_scheduler_interval_seconds: int = int(os.getenv("AGENT_SCHEDULER_INTERVAL_SECONDS", "60"))
    agent_max_concurrent_executions: int = int(os.getenv("AGENT_MAX_CONCURRENT_EXECUTIONS", "10"))
    agent_execution_timeout_seconds: int = int(os.getenv("AGENT_EXECUTION_TIMEOUT_SECONDS", "300"))

    # Isolation Mode Settings
    agent_isolation_enabled: bool = os.getenv("AGENT_ISOLATION_ENABLED", "true").lower() == "true"
    agent_isolation_worker_timeout: int = int(os.getenv("AGENT_ISOLATION_WORKER_TIMEOUT", "600"))

    # News API Configuration
    newsapi_api_key: str = os.getenv("NEWSAPI_API_KEY", "")
    newsapi_base_url: str = os.getenv("NEWSAPI_BASE_URL", "https://newsapi.org/v2")
    newsapi_rate_limit_per_day: int = int(os.getenv("NEWSAPI_RATE_LIMIT_PER_DAY", "1000"))

    # RSS Feed Configuration
    rss_fetch_timeout: int = int(os.getenv("RSS_FETCH_TIMEOUT", "30"))
    rss_max_feeds_per_agent: int = int(os.getenv("RSS_MAX_FEEDS_PER_AGENT", "20"))

    # Result Storage
    agent_results_retention_days: int = int(os.getenv("AGENT_RESULTS_RETENTION_DAYS", "30"))
    agent_execution_history_retention_days: int = int(
        os.getenv("AGENT_EXECUTION_HISTORY_retention_days", "90")
    )

    # Health Monitoring
    agent_health_check_interval_minutes: int = int(
        os.getenv("AGENT_HEALTH_CHECK_INTERVAL_MINUTES", "15")
    )
    agent_health_success_rate_threshold: float = float(
        os.getenv("AGENT_HEALTH_SUCCESS_RATE_THRESHOLD", "0.8")
    )
    agent_health_max_error_count: int = int(os.getenv("AGENT_HEALTH_MAX_ERROR_COUNT", "3"))

    # Default Agent Configurations
    default_tenant_agent_config: Dict[str, Any] = {
        "update_frequency_minutes": 60,
        "max_results_per_update": 20,
        "isolation_mode": False,
        "keywords": [],
        "sources": [],
    }

    default_shared_agent_config: Dict[str, Any] = {
        "update_frequency_minutes": 120,
        "max_results_per_update": 50,
        "isolation_mode": True,
        "keywords": [],
        "sources": [],
    }

    # Free News Sources (no API key required)
    free_news_sources: List[str] = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.theguardian.com/world/rss",
        "https://feeds.npr.org/1001/rss.xml",
    ]

    # Technology News Sources
    tech_news_sources: List[str] = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
    ]

    # Agent Capability Mappings
    capability_implementations: Dict[str, str] = {
        "news_monitoring": "NewsMonitoringAgent",
        "technology_trends": "TechnologyTrendsAgent",
        "trend_analysis": "TechnologyTrendsAgent",
        "competitor_tracking": "NewsMonitoringAgent",
        "market_analysis": "NewsMonitoringAgent",
        "custom_keyword_monitoring": "NewsMonitoringAgent",
    }

    # Worker Configuration
    agent_worker_memory_mb: int = int(os.getenv("AGENT_WORKER_MEMORY_MB", "512"))
    agent_worker_cpu_cores: float = float(os.getenv("AGENT_WORKER_CPU_CORES", "0.5"))
    agent_worker_timeout_seconds: int = int(os.getenv("AGENT_WORKER_TIMEOUT_SECONDS", "600"))

    # Monitoring and Logging
    agent_metrics_enabled: bool = os.getenv("AGENT_METRICS_ENABLED", "true").lower() == "true"
    agent_log_level: str = os.getenv("AGENT_LOG_LEVEL", "INFO")
    agent_audit_log_enabled: bool = os.getenv("AGENT_AUDIT_LOG_ENABLED", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global agent settings instance
agent_settings = AgentSettings()


@dataclass
class AgentWorkerConfig:
    """Configuration for agent workers."""

    memory_mb: int
    cpu_cores: float
    timeout_seconds: int
    isolation_mode: bool = True


@dataclass
class AgentSchedulerConfig:
    """Configuration for agent scheduler."""

    enabled: bool
    interval_seconds: int
    max_concurrent: int
    timeout_seconds: int


def get_agent_worker_config() -> AgentWorkerConfig:
    """Get agent worker configuration."""
    return AgentWorkerConfig(
        memory_mb=agent_settings.agent_worker_memory_mb,
        cpu_cores=agent_settings.agent_worker_cpu_cores,
        timeout_seconds=agent_settings.agent_worker_timeout_seconds,
        isolation_mode=agent_settings.agent_isolation_enabled,
    )


def get_agent_scheduler_config() -> AgentSchedulerConfig:
    """Get agent scheduler configuration."""
    return AgentSchedulerConfig(
        enabled=agent_settings.agent_scheduler_enabled,
        interval_seconds=agent_settings.agent_scheduler_interval_seconds,
        max_concurrent=agent_settings.agent_max_concurrent_executions,
        timeout_seconds=agent_settings.agent_execution_timeout_seconds,
    )
