"""Google Cloud Pub/Sub adapter for event publishing and subscribing."""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List, Set
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import DeadLetterPolicy, RetryPolicy, Duration
from concurrent.futures import ThreadPoolExecutor
import asyncio

from ..domain.events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class PubSubBusAdapter:
    """Google Cloud Pub/Sub adapter for tenant-safe event-driven communication."""

    def __init__(self, project_id: str, enable_dlq: bool = True):
        self.project_id = project_id
        self.enable_dlq = enable_dlq
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Track processed messages for idempotency (in production, use Redis/Firestore)
        self._processed_messages: Set[str] = set()
        
        # Topic configuration
        self.topics = {
            'events': 'living-twin-events',
            'document-events': 'living-twin-document-events', 
            'query-events': 'living-twin-query-events',
            'user-events': 'living-twin-user-events',
            'system-events': 'living-twin-system-events'
        }

    def _get_topic_path(self, topic_name: str) -> str:
        """Get the full topic path."""
        return self.publisher.topic_path(self.project_id, topic_name)

    def _get_subscription_path(self, subscription_name: str) -> str:
        """Get the full subscription path."""
        return self.subscriber.subscription_path(self.project_id, subscription_name)

    async def publish_event(
        self, 
        topic_name: str, 
        event_data: Dict[str, Any],
        tenant_id: str,
        event_type: str,
        attributes: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Publish an event to a Pub/Sub topic."""
        try:
            topic_path = self._get_topic_path(topic_name)
            
            # Prepare the message
            message_data = {
                'tenant_id': tenant_id,
                'event_type': event_type,
                'data': event_data,
                'timestamp': str(asyncio.get_event_loop().time())
            }
            
            # Convert to JSON bytes
            message_bytes = json.dumps(message_data).encode('utf-8')
            
            # Prepare attributes
            message_attributes = {
                'tenant_id': tenant_id,
                'event_type': event_type
            }
            if attributes:
                message_attributes.update(attributes)
            
            # Publish the message
            future = self.publisher.publish(
                topic_path, 
                message_bytes, 
                **message_attributes
            )
            
            # Get the message ID
            message_id = future.result()
            logger.info(f"Published event {event_type} to {topic_name}: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error publishing event to {topic_name}: {e}")
            return None

    async def subscribe_to_events(
        self, 
        subscription_name: str, 
        callback: Callable[[Dict[str, Any]], None],
        max_messages: int = 100
    ) -> None:
        """Subscribe to events from a Pub/Sub subscription."""
        try:
            subscription_path = self._get_subscription_path(subscription_name)
            
            def message_callback(message):
                try:
                    # Parse the message
                    message_data = json.loads(message.data.decode('utf-8'))
                    
                    # Extract attributes
                    attributes = dict(message.attributes)
                    
                    # Combine data and attributes
                    event = {
                        'data': message_data,
                        'attributes': attributes,
                        'message_id': message.message_id,
                        'publish_time': message.publish_time
                    }
                    
                    # Call the callback
                    callback(event)
                    
                    # Acknowledge the message
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    message.nack()
            
            # Configure flow control
            flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)
            
            # Start the subscriber
            streaming_pull_future = self.subscriber.subscribe(
                subscription_path, 
                callback=message_callback,
                flow_control=flow_control
            )
            
            logger.info(f"Listening for messages on {subscription_path}")
            
            # Keep the subscriber running
            try:
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()
                logger.info("Subscriber cancelled")
                
        except Exception as e:
            logger.error(f"Error subscribing to {subscription_name}: {e}")

    async def create_topic(self, topic_name: str) -> bool:
        """Create a Pub/Sub topic if it doesn't exist."""
        try:
            topic_path = self._get_topic_path(topic_name)
            
            try:
                self.publisher.create_topic(request={"name": topic_path})
                logger.info(f"Created topic: {topic_path}")
                return True
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Topic already exists: {topic_path}")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creating topic {topic_name}: {e}")
            return False

    async def create_subscription(
        self, 
        topic_name: str, 
        subscription_name: str,
        filter_expression: Optional[str] = None
    ) -> bool:
        """Create a Pub/Sub subscription if it doesn't exist."""
        try:
            topic_path = self._get_topic_path(topic_name)
            subscription_path = self._get_subscription_path(subscription_name)
            
            try:
                request = {
                    "name": subscription_path,
                    "topic": topic_path
                }
                
                if filter_expression:
                    request["filter"] = filter_expression
                
                self.subscriber.create_subscription(request=request)
                logger.info(f"Created subscription: {subscription_path}")
                return True
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Subscription already exists: {subscription_path}")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creating subscription {subscription_name}: {e}")
            return False

    def _generate_idempotency_key(self, event: DomainEvent) -> str:
        """Generate idempotency key for event."""
        key_data = f"{event.event_type.value}:{event.tenant_id}:{event.event_id}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def _is_message_processed(self, idempotency_key: str) -> bool:
        """Check if message has been processed (idempotency check)."""
        # In production, use Redis or Firestore for distributed idempotency
        return idempotency_key in self._processed_messages
    
    def _mark_message_processed(self, idempotency_key: str) -> None:
        """Mark message as processed."""
        # In production, store in Redis with TTL or Firestore
        self._processed_messages.add(idempotency_key)
    
    async def publish_domain_event(self, event: DomainEvent) -> Optional[str]:
        """Publish a domain event with tenant isolation and idempotency."""
        try:
            # Generate idempotency key
            idempotency_key = self._generate_idempotency_key(event)
            
            # Check if already processed
            if self._is_message_processed(idempotency_key):
                logger.info(f"Event {event.event_id} already processed, skipping")
                return None
            
            # Determine topic based on event type
            topic_name = self._get_topic_for_event_type(event.event_type)
            topic_path = self._get_topic_path(topic_name)
            
            # Prepare message data
            message_data = event.to_dict()
            message_bytes = json.dumps(message_data).encode('utf-8')
            
            # Prepare attributes for tenant-safe filtering
            attributes = {
                'tenant_id': event.tenant_id,
                'event_type': event.event_type.value,
                'idempotency_key': idempotency_key,
                'correlation_id': event.correlation_id or '',
                'retry_count': str(event.retry_count)
            }
            
            if event.user_id:
                attributes['user_id'] = event.user_id
            
            # Publish the message
            future = self.publisher.publish(
                topic_path,
                message_bytes,
                **attributes
            )
            
            message_id = future.result()
            
            # Mark as processed
            self._mark_message_processed(idempotency_key)
            
            logger.info(
                f"Published event {event.event_type.value} for tenant {event.tenant_id}: {message_id}"
            )
            return message_id
            
        except Exception as e:
            logger.error(f"Error publishing domain event {event.event_id}: {e}")
            return None
    
    def _get_topic_for_event_type(self, event_type: EventType) -> str:
        """Get topic name for event type."""
        if event_type.value.startswith('document.'):
            return self.topics['document-events']
        elif event_type.value.startswith('query.'):
            return self.topics['query-events']
        elif event_type.value.startswith('user.'):
            return self.topics['user-events']
        elif event_type.value.startswith('system.'):
            return self.topics['system-events']
        else:
            return self.topics['events']
    
    async def create_tenant_subscription(
        self,
        topic_name: str,
        tenant_id: str,
        subscription_suffix: str = "worker",
        enable_dlq: bool = True,
        max_delivery_attempts: int = 5
    ) -> bool:
        """Create a tenant-specific subscription with DLQ support."""
        try:
            topic_path = self._get_topic_path(topic_name)
            subscription_name = f"{topic_name}-{tenant_id}-{subscription_suffix}"
            subscription_path = self._get_subscription_path(subscription_name)
            
            # Create DLQ topic and subscription if enabled
            dlq_topic_path = None
            if enable_dlq and self.enable_dlq:
                dlq_topic_name = f"{topic_name}-{tenant_id}-dlq"
                dlq_topic_path = self._get_topic_path(dlq_topic_name)
                
                # Create DLQ topic
                try:
                    self.publisher.create_topic(request={"name": dlq_topic_path})
                    logger.info(f"Created DLQ topic: {dlq_topic_path}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.error(f"Error creating DLQ topic: {e}")
            
            # Configure subscription with tenant filter
            filter_expression = f'attributes.tenant_id = "{tenant_id}"'
            
            request = {
                "name": subscription_path,
                "topic": topic_path,
                "filter": filter_expression,
                "ack_deadline_seconds": 600,  # 10 minutes
                "message_retention_duration": Duration(seconds=604800),  # 7 days
                "retry_policy": RetryPolicy(
                    minimum_backoff=Duration(seconds=10),
                    maximum_backoff=Duration(seconds=600)
                )
            }
            
            # Add DLQ policy if enabled
            if dlq_topic_path:
                request["dead_letter_policy"] = DeadLetterPolicy(
                    dead_letter_topic=dlq_topic_path,
                    max_delivery_attempts=max_delivery_attempts
                )
            
            try:
                self.subscriber.create_subscription(request=request)
                logger.info(f"Created tenant subscription: {subscription_path}")
                return True
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Subscription already exists: {subscription_path}")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creating tenant subscription: {e}")
            return False
    
    async def subscribe_to_tenant_events(
        self,
        tenant_id: str,
        event_types: List[EventType],
        callback: Callable[[DomainEvent], bool],
        subscription_suffix: str = "worker",
        max_messages: int = 10
    ) -> None:
        """Subscribe to tenant-specific events with idempotency and error handling."""
        try:
            # Create subscriptions for each event type topic
            for event_type in event_types:
                topic_name = self._get_topic_for_event_type(event_type)
                await self.create_tenant_subscription(
                    topic_name=topic_name,
                    tenant_id=tenant_id,
                    subscription_suffix=subscription_suffix
                )
            
            # Subscribe to the main events topic for this tenant
            subscription_name = f"living-twin-events-{tenant_id}-{subscription_suffix}"
            subscription_path = self._get_subscription_path(subscription_name)
            
            def message_callback(message):
                try:
                    # Parse the message
                    message_data = json.loads(message.data.decode('utf-8'))
                    
                    # Create domain event
                    event = DomainEvent.from_dict(message_data)
                    
                    # Check idempotency
                    idempotency_key = message.attributes.get('idempotency_key')
                    if idempotency_key and self._is_message_processed(idempotency_key):
                        logger.info(f"Message {message.message_id} already processed, skipping")
                        message.ack()
                        return
                    
                    # Verify tenant isolation
                    if event.tenant_id != tenant_id:
                        logger.warning(f"Tenant mismatch: expected {tenant_id}, got {event.tenant_id}")
                        message.ack()  # Ack to avoid reprocessing
                        return
                    
                    # Process the event
                    success = callback(event)
                    
                    if success:
                        # Mark as processed and ack
                        if idempotency_key:
                            self._mark_message_processed(idempotency_key)
                        message.ack()
                        logger.info(f"Successfully processed event {event.event_id}")
                    else:
                        # Nack to trigger retry
                        message.nack()
                        logger.warning(f"Failed to process event {event.event_id}, will retry")
                        
                except Exception as e:
                    logger.error(f"Error processing message {message.message_id}: {e}")
                    message.nack()
            
            # Configure flow control
            flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)
            
            # Start the subscriber
            streaming_pull_future = self.subscriber.subscribe(
                subscription_path,
                callback=message_callback,
                flow_control=flow_control
            )
            
            logger.info(f"Listening for tenant {tenant_id} events on {subscription_path}")
            
            # Keep the subscriber running
            try:
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()
                logger.info(f"Subscriber for tenant {tenant_id} cancelled")
                
        except Exception as e:
            logger.error(f"Error subscribing to tenant {tenant_id} events: {e}")
    
    async def setup_topics_and_subscriptions(self) -> bool:
        """Setup all required topics and base subscriptions."""
        try:
            # Create all topics
            for topic_key, topic_name in self.topics.items():
                await self.create_topic(topic_name)
            
            logger.info("All topics and subscriptions setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up topics and subscriptions: {e}")
            return False

    async def publish_document_ingested(self, document_id: str, tenant_id: str) -> Optional[str]:
        """Publish a document ingested event."""
        return await self.publish_event(
            topic_name="document-events",
            event_data={"document_id": document_id},
            tenant_id=tenant_id,
            event_type="document.ingested"
        )

    async def publish_query_executed(self, query_id: str, tenant_id: str, user_id: str) -> Optional[str]:
        """Publish a query executed event."""
        return await self.publish_event(
            topic_name="query-events",
            event_data={"query_id": query_id, "user_id": user_id},
            tenant_id=tenant_id,
            event_type="query.executed"
        )
