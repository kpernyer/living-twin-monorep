"""AI Agent service for managing agent lifecycle and execution."""

import asyncio
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .agent_models import (
    Agent,
    AgentExecution,
    AgentExecutionRequest,
    AgentHealthCheck,
    AgentRequest,
    AgentResult,
    AgentResultQuery,
    AgentStatus,
    AgentType,
)
from .agents import AgentFactory, BaseAgent

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing AI agents."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.agent_instances: Dict[str, BaseAgent] = {}
        self.execution_history: Dict[str, List[AgentExecution]] = defaultdict(list)
        self.results_cache: Dict[str, List[AgentResult]] = defaultdict(list)
        self.scheduler_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def start(self):
        """Start the agent service."""
        if self.is_running:
            return

        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Agent service started")

    async def stop(self):
        """Stop the agent service."""
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent service stopped")

    async def create_agent(self, request: AgentRequest) -> Agent:
        """Create a new agent."""
        agent_id = str(uuid.uuid4())

        # Create agent instance
        agent = Agent(
            id=agent_id,
            name=request.name,
            description=request.description,
            agent_type=request.agent_type,
            capabilities=request.capabilities,
            config=request.config,
            tenant_id=request.tenant_id,
            created_at=datetime.utcnow(),
        )

        # Validate configuration
        agent_instance = AgentFactory.create_agent(agent)
        if not agent_instance.validate_config(agent.config):
            raise ValueError("Invalid agent configuration")

        # Store agent
        self.agents[agent_id] = agent
        self.agent_instances[agent_id] = agent_instance

        logger.info(f"Created agent {agent_id} ({agent.name}) for tenant {agent.tenant_id}")
        return agent

    async def update_agent(self, agent_id: str, request: AgentRequest) -> Agent:
        """Update an existing agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]

        # Update fields
        agent.name = request.name
        agent.description = request.description
        agent.agent_type = request.agent_type
        agent.capabilities = request.capabilities
        agent.config = request.config
        agent.tenant_id = request.tenant_id
        agent.updated_at = datetime.utcnow()

        # Recreate agent instance
        agent_instance = AgentFactory.create_agent(agent)
        if not agent_instance.validate_config(agent.config):
            raise ValueError("Invalid agent configuration")

        self.agent_instances[agent_id] = agent_instance

        logger.info(f"Updated agent {agent_id} ({agent.name})")
        return agent

    async def delete_agent(self, agent_id: str):
        """Delete an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        # Stop agent if running
        agent = self.agents[agent_id]
        if agent.status == AgentStatus.RUNNING:
            agent.status = AgentStatus.INACTIVE

        # Remove from storage
        del self.agents[agent_id]
        if agent_id in self.agent_instances:
            del self.agent_instances[agent_id]

        logger.info(f"Deleted agent {agent_id}")

    async def activate_agent(self, agent_id: str):
        """Activate an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]
        agent.status = AgentStatus.ACTIVE
        agent.updated_at = datetime.utcnow()

        logger.info(f"Activated agent {agent_id}")

    async def deactivate_agent(self, agent_id: str):
        """Deactivate an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]
        agent.status = AgentStatus.INACTIVE
        agent.updated_at = datetime.utcnow()

        logger.info(f"Deactivated agent {agent_id}")

    async def execute_agent(self, request: AgentExecutionRequest) -> AgentExecution:
        """Execute an agent manually."""
        if request.agent_id not in self.agents:
            raise ValueError(f"Agent {request.agent_id} not found")

        agent = self.agents[request.agent_id]
        agent_instance = self.agent_instances[request.agent_id]

        # Check if agent is active (unless forced)
        if not request.force_run and agent.status != AgentStatus.ACTIVE:
            raise ValueError(f"Agent {request.agent_id} is not active")

        # Determine isolation mode
        isolation_mode = request.isolation_mode
        if isolation_mode is None:
            isolation_mode = agent.config.isolation_mode

        # Execute agent
        execution = await agent_instance.run(isolation_mode=isolation_mode)

        # Store execution history
        self.execution_history[request.agent_id].append(execution)

        # Update agent last run time
        if execution.status == "completed":
            agent.last_run = execution.completed_at
            agent.next_run = agent_instance.get_next_run_time()

        logger.info(f"Executed agent {request.agent_id}, status: {execution.status}")
        return execution

    async def get_agent_results(self, query: AgentResultQuery) -> List[AgentResult]:
        """Get agent results based on query."""
        results = []

        for agent_id, agent_results in self.results_cache.items():
            agent = self.agents.get(agent_id)
            if not agent:
                continue

            # Apply filters
            if query.agent_id and agent_id != query.agent_id:
                continue

            if query.tenant_id and agent.tenant_id != query.tenant_id:
                continue

            if query.agent_type and agent.agent_type != query.agent_type:
                continue

            # Filter by date range
            filtered_results = []
            for result in agent_results:
                if query.date_from and result.created_at < query.date_from:
                    continue
                if query.date_to and result.created_at > query.date_to:
                    continue
                if query.keywords and not any(
                    kw in result.keywords_matched for kw in query.keywords
                ):
                    continue
                filtered_results.append(result)

            results.extend(filtered_results)

        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start = query.offset
        end = start + query.limit
        return results[start:end]

    async def get_agent_health(self, agent_id: str) -> AgentHealthCheck:
        """Get health status for an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]
        executions = self.execution_history.get(agent_id, [])

        # Calculate health metrics
        recent_executions = [
            e
            for e in executions
            if e.completed_at and e.completed_at > datetime.utcnow() - timedelta(days=7)
        ]

        success_count = len([e for e in recent_executions if e.status == "completed"])
        error_count = len([e for e in recent_executions if e.status == "failed"])
        total_count = len(recent_executions)

        success_rate = success_count / total_count if total_count > 0 else 0.0

        avg_execution_time = None
        if recent_executions:
            completed_times = [
                e.execution_time_seconds for e in recent_executions if e.execution_time_seconds
            ]
            if completed_times:
                avg_execution_time = sum(completed_times) / len(completed_times)

        # Determine if healthy
        is_healthy = agent.status == AgentStatus.ACTIVE and success_rate >= 0.8 and error_count < 3

        # Collect issues
        issues = []
        if agent.status != AgentStatus.ACTIVE:
            issues.append(f"Agent is {agent.status.value}")
        if success_rate < 0.8:
            issues.append(f"Low success rate: {success_rate:.1%}")
        if error_count >= 3:
            issues.append(f"High error count: {error_count}")

        return AgentHealthCheck(
            agent_id=agent_id,
            status=agent.status,
            last_run=agent.last_run,
            next_run=agent.next_run,
            error_count=error_count,
            success_rate=success_rate,
            average_execution_time=avg_execution_time,
            is_healthy=is_healthy,
            issues=issues,
        )

    async def _scheduler_loop(self):
        """Main scheduler loop for running agents on schedule."""
        while self.is_running:
            try:
                # Check all agents for scheduled runs
                for agent_id, agent in self.agents.items():
                    if agent.status != AgentStatus.ACTIVE:
                        continue

                    agent_instance = self.agent_instances[agent_id]
                    if agent_instance.should_run():
                        # Execute agent asynchronously
                        asyncio.create_task(self._execute_scheduled_agent(agent_id))

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)

    async def _execute_scheduled_agent(self, agent_id: str):
        """Execute a scheduled agent run."""
        try:
            agent = self.agents[agent_id]
            agent.status = AgentStatus.RUNNING

            request = AgentExecutionRequest(
                agent_id=agent_id,
                tenant_id=agent.tenant_id,
                force_run=False,
                isolation_mode=agent.config.isolation_mode,
            )

            execution = await self.execute_agent(request)

            # Update agent status
            if execution.status == "completed":
                agent.status = AgentStatus.ACTIVE
            else:
                agent.status = AgentStatus.ERROR

        except Exception as e:
            logger.error(f"Error executing scheduled agent {agent_id}: {e}")
            agent = self.agents[agent_id]
            agent.status = AgentStatus.ERROR

    def get_agents_by_tenant(self, tenant_id: str) -> List[Agent]:
        """Get all agents for a specific tenant."""
        return [agent for agent in self.agents.values() if agent.tenant_id == tenant_id]

    def get_shared_agents(self) -> List[Agent]:
        """Get all shared agents."""
        return [agent for agent in self.agents.values() if agent.agent_type == AgentType.SHARED]
