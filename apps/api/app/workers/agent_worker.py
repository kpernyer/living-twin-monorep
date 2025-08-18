"""Cloud Run job worker for running AI agents in isolation."""

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

from ..config import get_settings
from ..domain.agent_models import AgentExecutionRequest
from ..domain.agent_service import AgentService

logger = logging.getLogger(__name__)


class AgentWorker:
    """Worker for running AI agents in isolation mode."""

    def __init__(self, agent_id: str, tenant_id: Optional[str] = None):
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.settings = get_settings()
        self.running = False
        self.agent_service = AgentService()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def initialize(self):
        """Initialize worker dependencies."""
        try:
            # Start the agent service
            await self.agent_service.start()

            logger.info(f"Agent worker initialized for agent {self.agent_id}")

        except Exception as e:
            logger.error(f"Error initializing agent worker: {e}")
            raise

    async def run_agent(self, isolation_mode: bool = True) -> bool:
        """Run the specified agent in isolation mode."""
        try:
            logger.info(f"Starting agent execution for agent {self.agent_id}")

            # Create execution request
            request = AgentExecutionRequest(
                agent_id=self.agent_id,
                tenant_id=self.tenant_id,
                force_run=True,  # Force run in worker mode
                isolation_mode=isolation_mode,
            )

            # Execute the agent
            execution = await self.agent_service.execute_agent(request)

            if execution.status == "completed":
                logger.info(
                    f"Agent {self.agent_id} executed successfully with "
                    f"{execution.results_count} results"
                )
                return True
            else:
                logger.error(f"Agent {self.agent_id} execution failed: {execution.error_message}")
                return False

        except Exception as e:
            logger.error(f"Error running agent {self.agent_id}: {e}")
            return False

    async def run(self):
        """Main worker run loop."""
        try:
            await self.initialize()
            self.running = True

            # Run the agent once
            success = await self.run_agent(isolation_mode=True)

            if success:
                logger.info(f"Agent {self.agent_id} completed successfully")
                return 0
            else:
                logger.error(f"Agent {self.agent_id} failed")
                return 1

        except Exception as e:
            logger.error(f"Worker error: {e}")
            return 1
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup worker resources."""
        try:
            await self.agent_service.stop()
            logger.info("Agent worker cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main entry point for the agent worker."""
    # Get agent ID from environment
    agent_id = os.getenv("AGENT_ID")
    tenant_id = os.getenv("TENANT_ID")

    if not agent_id:
        logger.error("AGENT_ID environment variable is required")
        sys.exit(1)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create and run worker
    worker = AgentWorker(agent_id=agent_id, tenant_id=tenant_id)
    exit_code = await worker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
