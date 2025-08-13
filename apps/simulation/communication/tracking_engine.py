"""
Communication tracking engine with detailed visibility and graph database integration.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum

from ..domain.models import (
    PriorityCommunication,
    SimulationAgent,
    AgentResponse,
    CommunicationType,
    ResponseType,
)

logger = logging.getLogger(__name__)


class DeliveryStatus(Enum):
    """Status of message delivery."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    ACTION_TAKEN = "action_taken"
    FAILED = "failed"


class ActionStatus(Enum):
    """Status of action taken on communication."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DELEGATED = "delegated"
    IGNORED = "ignored"


class CommunicationTracker:
    """Tracks communication delivery, read receipts, and action status with graph database integration."""
    
    def __init__(self, graph_store_adapter, pubsub_adapter, organization_id: str):
        self.graph_store = graph_store_adapter
        self.pubsub_adapter = pubsub_adapter
        self.organization_id = organization_id
        
        # In-memory tracking for real-time updates
        self.delivery_tracking: Dict[str, Dict[str, Dict]] = {}  # comm_id -> recipient_id -> status
        self.action_tracking: Dict[str, Dict[str, Dict]] = {}    # comm_id -> recipient_id -> action_status
        self.read_receipts: Dict[str, Dict[str, datetime]] = {}  # comm_id -> recipient_id -> timestamp
    
    async def track_communication_sent(
        self,
        communication: PriorityCommunication,
        distribution_results: Dict[str, List[str]],
        sender_agent: SimulationAgent
    ) -> str:
        """Track when a communication is sent and create graph relationships."""
        
        tracking_id = f"track_{communication.id}_{datetime.now().timestamp()}"
        
        # Initialize tracking structures
        self.delivery_tracking[communication.id] = {}
        self.action_tracking[communication.id] = {}
        self.read_receipts[communication.id] = {}
        
        # Create graph nodes and relationships
        await self._create_communication_graph_nodes(
            communication, sender_agent, distribution_results, tracking_id
        )
        
        # Track delivery status for each recipient
        all_recipients = set()
        for channel, recipients in distribution_results.items():
            all_recipients.update(recipients)
        
        for recipient_id in all_recipients:
            await self._initialize_recipient_tracking(
                communication.id, recipient_id, distribution_results
            )
        
        # Send tracking update to CEO/sender
        await self._send_tracking_update_to_sender(
            communication, sender_agent, "communication_sent"
        )
        
        logger.info(f"Initialized tracking for communication {communication.id} with {len(all_recipients)} recipients")
        return tracking_id
    
    async def track_delivery_confirmation(
        self,
        communication_id: str,
        recipient_id: str,
        delivery_status: DeliveryStatus,
        metadata: Optional[Dict] = None
    ) -> None:
        """Track delivery confirmation from recipient."""
        
        if communication_id not in self.delivery_tracking:
            logger.warning(f"No tracking found for communication {communication_id}")
            return
        
        # Update delivery tracking
        if recipient_id not in self.delivery_tracking[communication_id]:
            self.delivery_tracking[communication_id][recipient_id] = {}
        
        self.delivery_tracking[communication_id][recipient_id].update({
            "status": delivery_status.value,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        })
        
        # Update graph database
        await self._update_delivery_status_in_graph(
            communication_id, recipient_id, delivery_status, metadata
        )
        
        # Send real-time update to sender
        await self._send_delivery_update_to_sender(
            communication_id, recipient_id, delivery_status
        )
        
        logger.info(f"Tracked delivery: {communication_id} -> {recipient_id} = {delivery_status.value}")
    
    async def track_read_receipt(
        self,
        communication_id: str,
        recipient_id: str,
        read_timestamp: Optional[datetime] = None
    ) -> None:
        """Track when a recipient reads the communication."""
        
        read_time = read_timestamp or datetime.now()
        
        # Update read receipts
        if communication_id not in self.read_receipts:
            self.read_receipts[communication_id] = {}
        
        self.read_receipts[communication_id][recipient_id] = read_time
        
        # Update delivery status to read
        await self.track_delivery_confirmation(
            communication_id, recipient_id, DeliveryStatus.READ,
            {"read_timestamp": read_time.isoformat()}
        )
        
        # Update graph database with read relationship
        await self._create_read_relationship_in_graph(
            communication_id, recipient_id, read_time
        )
        
        logger.info(f"Tracked read receipt: {communication_id} -> {recipient_id}")
    
    async def track_action_status(
        self,
        communication_id: str,
        recipient_id: str,
        action_status: ActionStatus,
        action_details: Optional[Dict] = None
    ) -> None:
        """Track action taken by recipient."""
        
        if communication_id not in self.action_tracking:
            self.action_tracking[communication_id] = {}
        
        if recipient_id not in self.action_tracking[communication_id]:
            self.action_tracking[communication_id][recipient_id] = {}
        
        # Update action tracking
        self.action_tracking[communication_id][recipient_id].update({
            "status": action_status.value,
            "timestamp": datetime.now(),
            "details": action_details or {},
            "history": self.action_tracking[communication_id][recipient_id].get("history", [])
        })
        
        # Add to history
        self.action_tracking[communication_id][recipient_id]["history"].append({
            "status": action_status.value,
            "timestamp": datetime.now().isoformat(),
            "details": action_details or {}
        })
        
        # Update graph database
        await self._update_action_status_in_graph(
            communication_id, recipient_id, action_status, action_details
        )
        
        # Send real-time update to sender
        await self._send_action_update_to_sender(
            communication_id, recipient_id, action_status, action_details
        )
        
        logger.info(f"Tracked action: {communication_id} -> {recipient_id} = {action_status.value}")
    
    async def get_communication_dashboard(
        self,
        communication_id: str,
        requester_id: str
    ) -> Dict:
        """Get comprehensive dashboard view for a communication (CEO view)."""
        
        # Get communication details from graph
        communication_data = await self._get_communication_from_graph(communication_id)
        
        if not communication_data:
            return {"error": "Communication not found"}
        
        # Check if requester has permission to view (sender or senior executive)
        if not await self._has_tracking_permission(requester_id, communication_data):
            return {"error": "Insufficient permissions"}
        
        # Compile comprehensive tracking data
        dashboard = {
            "communication_id": communication_id,
            "subject": communication_data.get("subject"),
            "sent_timestamp": communication_data.get("sent_timestamp"),
            "sender": communication_data.get("sender_name"),
            "priority_level": communication_data.get("priority_level"),
            "communication_type": communication_data.get("communication_type"),
            
            # Delivery statistics
            "delivery_summary": await self._get_delivery_summary(communication_id),
            
            # Action statistics  
            "action_summary": await self._get_action_summary(communication_id),
            
            # Detailed recipient status
            "recipient_details": await self._get_detailed_recipient_status(communication_id),
            
            # Timeline of events
            "timeline": await self._get_communication_timeline(communication_id),
            
            # Escalation information
            "escalation_info": await self._get_escalation_info(communication_id),
            
            # Real-time metrics
            "real_time_metrics": self._calculate_real_time_metrics(communication_id),
        }
        
        return dashboard
    
    async def _create_communication_graph_nodes(
        self,
        communication: PriorityCommunication,
        sender_agent: SimulationAgent,
        distribution_results: Dict[str, List[str]],
        tracking_id: str
    ) -> None:
        """Create communication nodes and relationships in graph database."""
        
        # Create communication node
        comm_node = {
            "id": communication.id,
            "type": "Communication",
            "subject": communication.subject,
            "content": communication.content,
            "communication_type": communication.type.value,
            "priority_level": communication.priority_level,
            "sent_timestamp": datetime.now().isoformat(),
            "organization_id": self.organization_id,
            "tracking_id": tracking_id,
        }
        
        await self.graph_store.create_node("Communication", comm_node)
        
        # Create SENT relationship from sender to communication
        await self.graph_store.create_relationship(
            sender_agent.id, "Agent",
            communication.id, "Communication",
            "SENT",
            {
                "timestamp": datetime.now().isoformat(),
                "distribution_channels": list(distribution_results.keys()),
                "total_recipients": sum(len(recipients) for recipients in distribution_results.values())
            }
        )
        
        # Create TARGETED relationships to all recipients
        all_recipients = set()
        for channel, recipients in distribution_results.items():
            all_recipients.update(recipients)
        
        for recipient_id in all_recipients:
            # Determine distribution channel for this recipient
            recipient_channel = None
            for channel, recipients in distribution_results.items():
                if recipient_id in recipients:
                    recipient_channel = channel
                    break
            
            await self.graph_store.create_relationship(
                communication.id, "Communication",
                recipient_id, "Agent",
                "TARGETED",
                {
                    "timestamp": datetime.now().isoformat(),
                    "distribution_channel": recipient_channel,
                    "delivery_status": DeliveryStatus.SENT.value,
                    "action_status": ActionStatus.PENDING.value,
                }
            )
    
    async def _initialize_recipient_tracking(
        self,
        communication_id: str,
        recipient_id: str,
        distribution_results: Dict[str, List[str]]
    ) -> None:
        """Initialize tracking for a specific recipient."""
        
        # Determine distribution channel
        distribution_channel = None
        for channel, recipients in distribution_results.items():
            if recipient_id in recipients:
                distribution_channel = channel
                break
        
        # Initialize delivery tracking
        self.delivery_tracking[communication_id][recipient_id] = {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.now(),
            "distribution_channel": distribution_channel,
            "metadata": {}
        }
        
        # Initialize action tracking
        self.action_tracking[communication_id][recipient_id] = {
            "status": ActionStatus.PENDING.value,
            "timestamp": datetime.now(),
            "details": {},
            "history": [{
                "status": ActionStatus.PENDING.value,
                "timestamp": datetime.now().isoformat(),
                "details": {"initial_status": True}
            }]
        }
    
    async def _update_delivery_status_in_graph(
        self,
        communication_id: str,
        recipient_id: str,
        delivery_status: DeliveryStatus,
        metadata: Optional[Dict]
    ) -> None:
        """Update delivery status in graph database."""
        
        # Update TARGETED relationship properties
        await self.graph_store.update_relationship_properties(
            communication_id, "Communication",
            recipient_id, "Agent",
            "TARGETED",
            {
                "delivery_status": delivery_status.value,
                "delivery_timestamp": datetime.now().isoformat(),
                "delivery_metadata": json.dumps(metadata or {})
            }
        )
        
        # Create specific delivery event node for detailed tracking
        delivery_event = {
            "id": f"delivery_{communication_id}_{recipient_id}_{datetime.now().timestamp()}",
            "type": "DeliveryEvent",
            "communication_id": communication_id,
            "recipient_id": recipient_id,
            "status": delivery_status.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": json.dumps(metadata or {})
        }
        
        await self.graph_store.create_node("DeliveryEvent", delivery_event)
        
        # Link delivery event to communication and recipient
        await self.graph_store.create_relationship(
            communication_id, "Communication",
            delivery_event["id"], "DeliveryEvent",
            "HAS_DELIVERY_EVENT",
            {"timestamp": datetime.now().isoformat()}
        )
        
        await self.graph_store.create_relationship(
            recipient_id, "Agent",
            delivery_event["id"], "DeliveryEvent",
            "RECEIVED_DELIVERY",
            {"timestamp": datetime.now().isoformat()}
        )
    
    async def _create_read_relationship_in_graph(
        self,
        communication_id: str,
        recipient_id: str,
        read_timestamp: datetime
    ) -> None:
        """Create READ relationship in graph database."""
        
        await self.graph_store.create_relationship(
            recipient_id, "Agent",
            communication_id, "Communication",
            "READ",
            {
                "timestamp": read_timestamp.isoformat(),
                "read_duration": "0",  # Could calculate time between delivery and read
            }
        )
    
    async def _update_action_status_in_graph(
        self,
        communication_id: str,
        recipient_id: str,
        action_status: ActionStatus,
        action_details: Optional[Dict]
    ) -> None:
        """Update action status in graph database."""
        
        # Update TARGETED relationship
        await self.graph_store.update_relationship_properties(
            communication_id, "Communication",
            recipient_id, "Agent",
            "TARGETED",
            {
                "action_status": action_status.value,
                "action_timestamp": datetime.now().isoformat(),
                "action_details": json.dumps(action_details or {})
            }
        )
        
        # Create action event node
        action_event = {
            "id": f"action_{communication_id}_{recipient_id}_{datetime.now().timestamp()}",
            "type": "ActionEvent",
            "communication_id": communication_id,
            "recipient_id": recipient_id,
            "action_status": action_status.value,
            "timestamp": datetime.now().isoformat(),
            "details": json.dumps(action_details or {})
        }
        
        await self.graph_store.create_node("ActionEvent", action_event)
        
        # Link action event
        await self.graph_store.create_relationship(
            communication_id, "Communication",
            action_event["id"], "ActionEvent",
            "HAS_ACTION_EVENT",
            {"timestamp": datetime.now().isoformat()}
        )
        
        await self.graph_store.create_relationship(
            recipient_id, "Agent",
            action_event["id"], "ActionEvent",
            "PERFORMED_ACTION",
            {"timestamp": datetime.now().isoformat()}
        )
        
        # If action is completed, create COMPLETED relationship
        if action_status == ActionStatus.COMPLETED:
            await self.graph_store.create_relationship(
                recipient_id, "Agent",
                communication_id, "Communication",
                "COMPLETED",
                {
                    "timestamp": datetime.now().isoformat(),
                    "completion_details": json.dumps(action_details or {})
                }
            )
    
    async def _send_tracking_update_to_sender(
        self,
        communication: PriorityCommunication,
        sender_agent: SimulationAgent,
        event_type: str
    ) -> None:
        """Send real-time tracking update to the communication sender."""
        
        tracking_update = {
            "type": "tracking_update",
            "event_type": event_type,
            "communication_id": communication.id,
            "sender_id": sender_agent.id,
            "timestamp": datetime.now().isoformat(),
            "summary": await self._get_delivery_summary(communication.id),
        }
        
        await self.pubsub_adapter.publish(
            topic=f"tracking-updates-{sender_agent.id}",
            message=json.dumps(tracking_update),
            attributes={
                "message_type": "tracking_update",
                "sender_id": sender_agent.id,
                "communication_id": communication.id,
            }
        )
    
    async def _send_delivery_update_to_sender(
        self,
        communication_id: str,
        recipient_id: str,
        delivery_status: DeliveryStatus
    ) -> None:
        """Send delivery status update to sender."""
        
        # Get communication details to find sender
        communication_data = await self._get_communication_from_graph(communication_id)
        if not communication_data:
            return
        
        sender_id = communication_data.get("sender_id")
        if not sender_id:
            return
        
        delivery_update = {
            "type": "delivery_update",
            "communication_id": communication_id,
            "recipient_id": recipient_id,
            "recipient_name": await self._get_agent_name(recipient_id),
            "delivery_status": delivery_status.value,
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.pubsub_adapter.publish(
            topic=f"tracking-updates-{sender_id}",
            message=json.dumps(delivery_update),
            attributes={
                "message_type": "delivery_update",
                "sender_id": sender_id,
                "recipient_id": recipient_id,
            }
        )
    
    async def _send_action_update_to_sender(
        self,
        communication_id: str,
        recipient_id: str,
        action_status: ActionStatus,
        action_details: Optional[Dict]
    ) -> None:
        """Send action status update to sender."""
        
        # Get communication details to find sender
        communication_data = await self._get_communication_from_graph(communication_id)
        if not communication_data:
            return
        
        sender_id = communication_data.get("sender_id")
        if not sender_id:
            return
        
        action_update = {
            "type": "action_update",
            "communication_id": communication_id,
            "recipient_id": recipient_id,
            "recipient_name": await self._get_agent_name(recipient_id),
            "action_status": action_status.value,
            "action_details": action_details or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.pubsub_adapter.publish(
            topic=f"tracking-updates-{sender_id}",
            message=json.dumps(action_update),
            attributes={
                "message_type": "action_update",
                "sender_id": sender_id,
                "recipient_id": recipient_id,
            }
        )
    
    async def _get_delivery_summary(self, communication_id: str) -> Dict:
        """Get delivery summary statistics."""
        
        if communication_id not in self.delivery_tracking:
            return {"total": 0, "delivered": 0, "read": 0, "failed": 0}
        
        tracking_data = self.delivery_tracking[communication_id]
        
        total = len(tracking_data)
        delivered = sum(1 for status in tracking_data.values() 
                       if status["status"] in [DeliveryStatus.DELIVERED.value, DeliveryStatus.READ.value])
        read = sum(1 for status in tracking_data.values() 
                  if status["status"] == DeliveryStatus.READ.value)
        failed = sum(1 for status in tracking_data.values() 
                    if status["status"] == DeliveryStatus.FAILED.value)
        
        return {
            "total": total,
            "delivered": delivered,
            "read": read,
            "failed": failed,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "read_rate": (read / total * 100) if total > 0 else 0,
        }
    
    async def _get_action_summary(self, communication_id: str) -> Dict:
        """Get action summary statistics."""
        
        if communication_id not in self.action_tracking:
            return {"total": 0, "completed": 0, "in_progress": 0, "pending": 0, "ignored": 0}
        
        tracking_data = self.action_tracking[communication_id]
        
        total = len(tracking_data)
        completed = sum(1 for status in tracking_data.values() 
                       if status["status"] == ActionStatus.COMPLETED.value)
        in_progress = sum(1 for status in tracking_data.values() 
                         if status["status"] == ActionStatus.IN_PROGRESS.value)
        pending = sum(1 for status in tracking_data.values() 
                     if status["status"] == ActionStatus.PENDING.value)
        ignored = sum(1 for status in tracking_data.values() 
                     if status["status"] == ActionStatus.IGNORED.value)
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "ignored": ignored,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "compliance_rate": ((completed + in_progress) / total * 100) if total > 0 else 0,
        }
    
    async def _get_detailed_recipient_status(self, communication_id: str) -> List[Dict]:
        """Get detailed status for each recipient."""
        
        recipients = []
        
        if communication_id in self.delivery_tracking:
            for recipient_id, delivery_data in self.delivery_tracking[communication_id].items():
                action_data = self.action_tracking.get(communication_id, {}).get(recipient_id, {})
                read_time = self.read_receipts.get(communication_id, {}).get(recipient_id)
                
                recipient_info = {
                    "recipient_id": recipient_id,
                    "recipient_name": await self._get_agent_name(recipient_id),
                    "delivery_status": delivery_data["status"],
                    "delivery_timestamp": delivery_data["timestamp"].isoformat(),
                    "distribution_channel": delivery_data.get("distribution_channel"),
                    "action_status": action_data.get("status", ActionStatus.PENDING.value),
                    "action_timestamp": action_data.get("timestamp", datetime.now()).isoformat() if action_data.get("timestamp") else None,
                    "read_timestamp": read_time.isoformat() if read_time else None,
                    "action_details": action_data.get("details", {}),
                }
                
                recipients.append(recipient_info)
        
        return recipients
    
    async def _get_communication_timeline(self, communication_id: str) -> List[Dict]:
        """Get chronological timeline of all events for this communication."""
        
        # This would query the graph database for all events related to the communication
        # For now, return a simplified version based on in-memory data
        
        timeline = []
        
        # Add delivery events
        if communication_id in self.delivery_tracking:
            for recipient_id, delivery_data in self.delivery_tracking[communication_id].items():
                timeline.append({
                    "timestamp": delivery_data["timestamp"].isoformat(),
                    "event_type": "delivery",
                    "recipient_id": recipient_id,
                    "recipient_name": await self._get_agent_name(recipient_id),
                    "status": delivery_data["status"],
                    "details": delivery_data.get("metadata", {})
                })
        
        # Add action events
        if communication_id in self.action_tracking:
            for recipient_id, action_data in self.action_tracking[communication_id].items():
                for history_item in action_data.get("history", []):
                    timeline.append({
                        "timestamp": history_item["timestamp"],
                        "event_type": "action",
                        "recipient_id": recipient_id,
                        "recipient_name": await self._get_agent_name(recipient_id),
                        "status": history_item["status"],
                        "details": history_item.get("details", {})
                    })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return timeline
    
    async def _get_escalation_info(self, communication_id: str) -> Dict:
        """Get escalation information for this communication."""
        
        # Query graph database for escalation relationships
        # This is a placeholder - would need actual graph queries
        
        return {
            "has_escalations": False,
            "escalation_count": 0,
            "escalated_to": [],
            "escalation_reason": None,
        }
    
    def _calculate_real_time_metrics(self, communication_id: str) -> Dict:
        """Calculate real-time metrics for the communication."""
        
        delivery_summary = asyncio.create_task(self._get_delivery_summary(communication_id))
        action_summary = asyncio.create_task(self._get_action_summary(communication_id))
        
        # Calculate time-based metrics
        sent_time = None  # Would get from graph database
        current_time = datetime.now()
        
        return {
            "time_since_sent": "0 minutes",  # Placeholder
            "average_read_time": "5 minutes",  # Placeholder
            "fastest_responder": None,  # Placeholder
            "slowest_responder": None,  # Placeholder
            "response_velocity": "2.5 responses/hour",  # Placeholder
        }
    
    async def _get_communication_from_graph(self, communication_id: str) -> Optional[Dict]:
        """Get communication details from graph database."""
        
        # This would query the graph database
        # For now, return a placeholder
        
        return {
            "id": communication_id,
            "subject": "Sample Communication",
            "sender_id": "sender_123",
            "sender_name": "John Doe",
            "sent_timestamp": datetime.now().isoformat(),
            "priority_level": 3,
            "communication_type": "nudge",
        }
    
    async def _has_tracking_permission(self, requester_id: str, communication_data: Dict) -> bool:
        """Check if requester has permission to view tracking data."""
        
        # Sender can always view
        if requester_id == communication_data.get("sender_id"):
            return True
        
        # Senior executives can view organization-wide communications
        # This would check the requester's role in the graph database
        
        return True  # Placeholder - implement proper permission checking
    
    async def _get_agent_name(self, agent_id: str) -> str:
        """Get agent name from graph database."""
        
        # This would query the graph database for agent details
        return f"Agent {agent_id}"  # Placeholder
