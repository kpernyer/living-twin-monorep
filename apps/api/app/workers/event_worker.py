"""Cloud Run job worker for processing Pub/Sub events."""

import asyncio
import logging
import os
import signal
import sys

from ..adapters.firestore_repo import FirestoreRepository
from ..adapters.neo4j_store import Neo4jVectorStore
from ..adapters.pubsub_bus import PubSubBusAdapter
from ..config import get_settings
from ..domain.events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class EventWorker:
    """Worker for processing domain events from Pub/Sub."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.settings = get_settings()
        self.running = False

        # Initialize adapters
        self.pubsub = PubSubBusAdapter(project_id=self.settings.gcp_project_id, enable_dlq=True)

        # Initialize other services as needed
        self.vector_store = None
        self.firestore_repo = None

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
            # Initialize vector store if needed
            if self.settings.neo4j_uri:
                self.vector_store = Neo4jVectorStore(
                    uri=self.settings.neo4j_uri,
                    user=self.settings.neo4j_user,
                    password=self.settings.neo4j_password,
                    database=self.settings.neo4j_db,
                )

            # Initialize Firestore if needed
            if not self.settings.use_local_mock:
                self.firestore_repo = FirestoreRepository()

            # Setup Pub/Sub topics and subscriptions
            await self.pubsub.setup_topics_and_subscriptions()

            logger.info(f"Worker initialized for tenant {self.tenant_id}")

        except Exception as e:
            logger.error(f"Error initializing worker: {e}")
            raise

    async def process_document_event(self, event: DomainEvent) -> bool:
        """Process document-related events."""
        try:
            logger.info(
                f"Processing document event {event.event_type.value} for tenant {event.tenant_id}"
            )

            if event.event_type == EventType.DOCUMENT_INGESTED:
                # Handle document ingestion completion
                document_id = event.data.get("document_id")
                document_title = event.data.get("document_title", "Unknown")

                logger.info(
                    f"Document {document_id} ({document_title}) ingested for "
                    f"tenant {event.tenant_id}"
                )

                # Here you could trigger additional processing:
                # - Update search indexes
                # - Send notifications
                # - Update analytics
                # - Trigger ML pipelines

                return True

            elif event.event_type == EventType.DOCUMENT_UPDATED:
                # Handle document updates
                document_id = event.data.get("document_id")
                logger.info(f"Document {document_id} updated for tenant {event.tenant_id}")
                return True

            elif event.event_type == EventType.DOCUMENT_DELETED:
                # Handle document deletion
                document_id = event.data.get("document_id")
                logger.info(f"Document {document_id} deleted for tenant {event.tenant_id}")
                return True

            return True

        except Exception as e:
            logger.error(f"Error processing document event {event.event_id}: {e}")
            return False

    async def process_query_event(self, event: DomainEvent) -> bool:
        """Process query-related events."""
        try:
            logger.info(
                f"Processing query event {event.event_type.value} for tenant {event.tenant_id}"
            )

            if event.event_type == EventType.QUERY_EXECUTED:
                # Handle query execution
                query_id = event.data.get("query_id")
                user_id = event.user_id
                response_time_ms = event.data.get("response_time_ms", 0)

                logger.info(
                    f"Query {query_id} executed by user {user_id} "
                    f"for tenant {event.tenant_id} in {response_time_ms}ms"
                )

                # Here you could:
                # - Update usage analytics
                # - Track user behavior
                # - Update recommendation systems
                # - Monitor performance metrics

                return True

            elif event.event_type == EventType.QUERY_FAILED:
                # Handle query failures
                query_id = event.data.get("query_id")
                error_message = event.data.get("error_message", "Unknown error")

                logger.warning(
                    f"Query {query_id} failed for tenant {event.tenant_id}: {error_message}"
                )

                # Here you could:
                # - Log errors for analysis
                # - Send alerts
                # - Update error metrics

                return True

            return True

        except Exception as e:
            logger.error(f"Error processing query event {event.event_id}: {e}")
            return False

    async def process_user_event(self, event: DomainEvent) -> bool:
        """Process user-related events."""
        try:
            logger.info(
                f"Processing user event {event.event_type.value} for tenant {event.tenant_id}"
            )

            if event.event_type == EventType.USER_REGISTERED:
                # Handle user registration
                user_id = event.data.get("user_id")
                email = event.data.get("email")

                logger.info(f"User {user_id} ({email}) registered for tenant {event.tenant_id}")

                # Here you could:
                # - Send welcome emails
                # - Setup user preferences
                # - Initialize user data
                # - Update organization metrics

                return True

            elif event.event_type == EventType.USER_LOGIN:
                # Handle user login
                user_id = event.data.get("user_id")
                logger.info(f"User {user_id} logged in for tenant {event.tenant_id}")

                # Here you could:
                # - Update last login time
                # - Track user activity
                # - Update session metrics

                return True

            return True

        except Exception as e:
            logger.error(f"Error processing user event {event.event_id}: {e}")
            return False

    async def process_system_event(self, event: DomainEvent) -> bool:
        """Process system-related events."""
        try:
            logger.info(
                f"Processing system event {event.event_type.value} for tenant {event.tenant_id}"
            )

            if event.event_type == EventType.SYSTEM_ERROR:
                # Handle system errors
                error_type = event.data.get("error_type", "Unknown")
                error_message = event.data.get("error_message", "Unknown error")

                logger.error(
                    f"System error for tenant {event.tenant_id}: {error_type} - {error_message}"
                )

                # Here you could:
                # - Send alerts
                # - Update error dashboards
                # - Trigger incident response

                return True

            elif event.event_type == EventType.SYSTEM_HEALTH_CHECK:
                # Handle health checks
                status = event.data.get("status", "unknown")
                logger.info(f"Health check for tenant {event.tenant_id}: {status}")
                return True

            return True

        except Exception as e:
            logger.error(f"Error processing system event {event.event_id}: {e}")
            return False

    async def process_event(self, event: DomainEvent) -> bool:
        """Process a domain event based on its type."""
        try:
            # Route event to appropriate handler
            if event.event_type.value.startswith("document."):
                return await self.process_document_event(event)
            elif event.event_type.value.startswith("query."):
                return await self.process_query_event(event)
            elif event.event_type.value.startswith("user."):
                return await self.process_user_event(event)
            elif event.event_type.value.startswith("system."):
                return await self.process_system_event(event)
            else:
                logger.warning(f"Unknown event type: {event.event_type.value}")
                return True  # Ack unknown events to avoid infinite retries

        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            return False

    async def start(self):
        """Start the event worker."""
        try:
            await self.initialize()

            self.running = True
            logger.info(f"Starting event worker for tenant {self.tenant_id}")

            # Define which event types this worker should handle
            event_types = [
                EventType.DOCUMENT_INGESTED,
                EventType.DOCUMENT_UPDATED,
                EventType.DOCUMENT_DELETED,
                EventType.QUERY_EXECUTED,
                EventType.QUERY_FAILED,
                EventType.USER_REGISTERED,
                EventType.USER_LOGIN,
                EventType.SYSTEM_ERROR,
                EventType.SYSTEM_HEALTH_CHECK,
            ]

            # Start subscribing to tenant events
            await self.pubsub.subscribe_to_tenant_events(
                tenant_id=self.tenant_id,
                event_types=event_types,
                callback=self.process_event,
                subscription_suffix="worker",
                max_messages=5,  # Process 5 messages concurrently
            )

        except Exception as e:
            logger.error(f"Error starting worker: {e}")
            raise

    async def stop(self):
        """Stop the event worker."""
        logger.info(f"Stopping event worker for tenant {self.tenant_id}")
        self.running = False


async def main():
    """Main entry point for the Cloud Run job."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Get tenant ID from environment variable
    tenant_id = os.getenv("TENANT_ID")
    if not tenant_id:
        logger.error("TENANT_ID environment variable is required")
        sys.exit(1)

    # Create and start worker
    worker = EventWorker(tenant_id=tenant_id)

    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        sys.exit(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
