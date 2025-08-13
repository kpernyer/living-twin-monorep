"""
Communication distribution engine using Pub/Sub for real-time organizational messaging.
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
    CommunicationType,
    AgentState,
)

logger = logging.getLogger(__name__)


class DistributionChannel(Enum):
    """Distribution channels for communications."""
    REAL_TIME_PUSH = "real_time_push"  # Active app users
    DELEGATION_CHAIN = "delegation_chain"  # Manager to direct reports
    EMAIL_FALLBACK = "email_fallback"  # Offline users
    BROADCAST_ALL = "broadcast_all"  # Organization-wide


class CommunicationDistributor:
    """Handles distribution of communications through various channels."""
    
    def __init__(self, pubsub_adapter, organization_id: str):
        self.pubsub_adapter = pubsub_adapter
        self.organization_id = organization_id
        
        # Track active users (those with app open)
        self.active_users: Set[str] = set()
        
        # Track user presence and last seen
        self.user_presence: Dict[str, datetime] = {}
        
        # Distribution topics
        self.topics = {
            "org_broadcast": f"org-{organization_id}-broadcast",
            "delegation": f"org-{organization_id}-delegation", 
            "direct_messages": f"org-{organization_id}-direct",
            "pulse_updates": f"org-{organization_id}-pulse",
        }
    
    async def distribute_communication(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent],
        sender_agent: SimulationAgent
    ) -> Dict[str, List[str]]:
        """
        Distribute a communication using appropriate channels.
        Returns a dict mapping distribution channels to recipient lists.
        """
        
        distribution_plan = self._create_distribution_plan(
            communication, agents, sender_agent
        )
        
        results = {}
        
        # Execute distribution plan
        for channel, recipients in distribution_plan.items():
            if not recipients:
                continue
                
            try:
                if channel == DistributionChannel.REAL_TIME_PUSH:
                    await self._distribute_real_time_push(communication, recipients)
                    results[channel.value] = recipients
                    
                elif channel == DistributionChannel.DELEGATION_CHAIN:
                    delegated_recipients = await self._distribute_delegation_chain(
                        communication, recipients, agents
                    )
                    results[channel.value] = delegated_recipients
                    
                elif channel == DistributionChannel.EMAIL_FALLBACK:
                    await self._distribute_email_fallback(communication, recipients)
                    results[channel.value] = recipients
                    
                elif channel == DistributionChannel.BROADCAST_ALL:
                    await self._distribute_broadcast_all(communication, agents)
                    results[channel.value] = list(agents.keys())
                    
            except Exception as e:
                logger.error(f"Failed to distribute via {channel.value}: {e}")
        
        # Log distribution summary
        await self._log_distribution_event(communication, results)
        
        return results
    
    def _create_distribution_plan(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent],
        sender_agent: SimulationAgent
    ) -> Dict[DistributionChannel, List[str]]:
        """Create a distribution plan based on communication type and sender role."""
        
        plan = {
            DistributionChannel.REAL_TIME_PUSH: [],
            DistributionChannel.DELEGATION_CHAIN: [],
            DistributionChannel.EMAIL_FALLBACK: [],
            DistributionChannel.BROADCAST_ALL: [],
        }
        
        # CEO/Executive broadcasts go to everyone
        if self._is_executive_broadcast(sender_agent, communication):
            plan[DistributionChannel.BROADCAST_ALL] = list(agents.keys())
            return plan
        
        # Separate recipients by online status
        online_recipients = []
        offline_recipients = []
        
        for recipient_id in communication.recipient_ids:
            if recipient_id in self.active_users:
                online_recipients.append(recipient_id)
            else:
                offline_recipients.append(recipient_id)
        
        # Online users get real-time push
        plan[DistributionChannel.REAL_TIME_PUSH] = online_recipients
        
        # Handle offline users based on communication type
        if communication.type in [CommunicationType.DIRECT_ORDER, CommunicationType.URGENT]:
            # Critical communications use delegation chain for offline users
            plan[DistributionChannel.DELEGATION_CHAIN] = offline_recipients
        else:
            # Non-critical communications use email fallback
            plan[DistributionChannel.EMAIL_FALLBACK] = offline_recipients
        
        return plan
    
    def _is_executive_broadcast(
        self, 
        sender_agent: SimulationAgent, 
        communication: PriorityCommunication
    ) -> bool:
        """Determine if this is an executive broadcast that should go to everyone."""
        
        # CEO or C-level executives
        if any(title in sender_agent.professional.job_title.lower() 
               for title in ["ceo", "chief", "president", "founder"]):
            return True
        
        # High-level department heads with organization-wide communications
        if (sender_agent.professional.seniority_level >= 8 and 
            communication.type in [CommunicationType.ANNOUNCEMENT, CommunicationType.POLICY]):
            return True
        
        # Explicit organization-wide flag
        if hasattr(communication, 'organization_wide') and communication.organization_wide:
            return True
        
        return False
    
    async def _distribute_real_time_push(
        self, 
        communication: PriorityCommunication, 
        recipients: List[str]
    ) -> None:
        """Distribute to users with active app sessions via Pub/Sub."""
        
        message_data = {
            "type": "communication",
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "subject": communication.subject,
            "content": communication.content,
            "priority_level": communication.priority_level,
            "communication_type": communication.type.value,
            "timestamp": datetime.now().isoformat(),
            "recipients": recipients,
        }
        
        # Publish to organization broadcast topic
        await self.pubsub_adapter.publish(
            topic=self.topics["org_broadcast"],
            message=json.dumps(message_data),
            attributes={
                "message_type": "communication",
                "priority": str(communication.priority_level),
                "sender_id": communication.sender_id,
            }
        )
        
        # Also send direct messages to specific recipients
        for recipient_id in recipients:
            await self.pubsub_adapter.publish(
                topic=self.topics["direct_messages"],
                message=json.dumps(message_data),
                attributes={
                    "recipient_id": recipient_id,
                    "message_type": "direct_communication",
                }
            )
        
        logger.info(f"Sent real-time push to {len(recipients)} active users")
    
    async def _distribute_delegation_chain(
        self,
        communication: PriorityCommunication,
        offline_recipients: List[str],
        agents: Dict[str, SimulationAgent]
    ) -> List[str]:
        """Distribute through management delegation chain for offline users."""
        
        delegated_recipients = []
        
        for recipient_id in offline_recipients:
            recipient_agent = agents.get(recipient_id)
            if not recipient_agent:
                continue
            
            # Find the recipient's manager
            manager_id = recipient_agent.professional.manager_id
            if not manager_id or manager_id not in agents:
                continue
            
            manager_agent = agents[manager_id]
            
            # Create delegation message
            delegation_message = {
                "type": "delegation_request",
                "original_communication_id": communication.id,
                "delegate_to": recipient_id,
                "delegate_from": communication.sender_id,
                "manager_id": manager_id,
                "subject": f"DELEGATION: {communication.subject}",
                "content": f"""
You are receiving this because {recipient_agent.name} is currently offline.

ORIGINAL MESSAGE:
{communication.content}

ACTION REQUIRED:
Please ensure {recipient_agent.name} receives this message and takes appropriate action.
You may delegate this further to other team members if appropriate.

Original sender: {communication.sender_id}
Priority: {communication.priority_level}/5
                """.strip(),
                "priority_level": min(5, communication.priority_level + 1),  # Increase priority
                "timestamp": datetime.now().isoformat(),
            }
            
            # Send delegation to manager
            if manager_id in self.active_users:
                # Manager is online - send real-time
                await self.pubsub_adapter.publish(
                    topic=self.topics["delegation"],
                    message=json.dumps(delegation_message),
                    attributes={
                        "recipient_id": manager_id,
                        "message_type": "delegation",
                        "original_recipient": recipient_id,
                    }
                )
            else:
                # Manager is also offline - escalate further up the chain
                await self._escalate_delegation_chain(
                    delegation_message, manager_agent, agents
                )
            
            delegated_recipients.append(manager_id)
        
        logger.info(f"Delegated {len(offline_recipients)} messages through management chain")
        return delegated_recipients
    
    async def _escalate_delegation_chain(
        self,
        delegation_message: Dict,
        manager_agent: SimulationAgent,
        agents: Dict[str, SimulationAgent]
    ) -> None:
        """Escalate delegation up the management chain."""
        
        # Find manager's manager
        senior_manager_id = manager_agent.professional.manager_id
        if not senior_manager_id or senior_manager_id not in agents:
            # No higher manager - send email fallback
            await self._distribute_email_fallback(
                type('obj', (object,), delegation_message)(), 
                [manager_agent.id]
            )
            return
        
        # Update delegation message for senior manager
        delegation_message["escalated"] = True
        delegation_message["escalation_level"] = delegation_message.get("escalation_level", 0) + 1
        delegation_message["manager_id"] = senior_manager_id
        
        if senior_manager_id in self.active_users:
            await self.pubsub_adapter.publish(
                topic=self.topics["delegation"],
                message=json.dumps(delegation_message),
                attributes={
                    "recipient_id": senior_manager_id,
                    "message_type": "escalated_delegation",
                    "escalation_level": str(delegation_message["escalation_level"]),
                }
            )
        else:
            # Continue escalating
            senior_manager = agents[senior_manager_id]
            await self._escalate_delegation_chain(delegation_message, senior_manager, agents)
    
    async def _distribute_email_fallback(
        self, 
        communication: PriorityCommunication, 
        recipients: List[str]
    ) -> None:
        """Send email notifications for offline users (fallback)."""
        
        email_message = {
            "type": "email_notification",
            "communication_id": communication.id,
            "subject": f"[Living Twin] {communication.subject}",
            "content": communication.content,
            "recipients": recipients,
            "priority": communication.priority_level,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Publish to email notification topic
        await self.pubsub_adapter.publish(
            topic="email-notifications",  # External email service topic
            message=json.dumps(email_message),
            attributes={
                "message_type": "email_fallback",
                "organization_id": self.organization_id,
            }
        )
        
        logger.info(f"Sent email fallback to {len(recipients)} offline users")
    
    async def _distribute_broadcast_all(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> None:
        """Broadcast to entire organization (CEO/executive announcements)."""
        
        broadcast_message = {
            "type": "organization_broadcast",
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "subject": communication.subject,
            "content": communication.content,
            "priority_level": communication.priority_level,
            "communication_type": communication.type.value,
            "timestamp": datetime.now().isoformat(),
            "organization_wide": True,
        }
        
        # Send to organization broadcast topic (all active users)
        await self.pubsub_adapter.publish(
            topic=self.topics["org_broadcast"],
            message=json.dumps(broadcast_message),
            attributes={
                "message_type": "organization_broadcast",
                "priority": str(communication.priority_level),
                "sender_id": communication.sender_id,
                "organization_id": self.organization_id,
            }
        )
        
        # Also trigger pulse updates for all users
        pulse_update = {
            "type": "pulse_update",
            "event": "organization_communication",
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "priority": communication.priority_level,
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.pubsub_adapter.publish(
            topic=self.topics["pulse_updates"],
            message=json.dumps(pulse_update),
            attributes={
                "message_type": "pulse_update",
                "organization_id": self.organization_id,
            }
        )
        
        # For offline users, send delegation to their managers
        offline_users = [
            agent_id for agent_id in agents.keys() 
            if agent_id not in self.active_users
        ]
        
        if offline_users:
            await self._distribute_delegation_chain(communication, offline_users, agents)
        
        logger.info(f"Broadcast to entire organization ({len(agents)} employees)")
    
    async def _log_distribution_event(
        self,
        communication: PriorityCommunication,
        results: Dict[str, List[str]]
    ) -> None:
        """Log distribution event for analytics."""
        
        distribution_log = {
            "type": "communication_distribution",
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "organization_id": self.organization_id,
            "distribution_channels": results,
            "total_recipients": sum(len(recipients) for recipients in results.values()),
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.pubsub_adapter.publish(
            topic="analytics-events",
            message=json.dumps(distribution_log),
            attributes={
                "event_type": "communication_distribution",
                "organization_id": self.organization_id,
            }
        )
    
    # User presence management
    
    async def update_user_presence(self, user_id: str, is_active: bool) -> None:
        """Update user presence status."""
        
        if is_active:
            self.active_users.add(user_id)
        else:
            self.active_users.discard(user_id)
        
        self.user_presence[user_id] = datetime.now()
        
        # Publish presence update
        presence_update = {
            "type": "presence_update",
            "user_id": user_id,
            "is_active": is_active,
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.pubsub_adapter.publish(
            topic=self.topics["pulse_updates"],
            message=json.dumps(presence_update),
            attributes={
                "message_type": "presence_update",
                "user_id": user_id,
            }
        )
    
    def get_active_users(self) -> Set[str]:
        """Get currently active users."""
        return self.active_users.copy()
    
    def get_user_presence_info(self) -> Dict[str, Dict]:
        """Get presence information for all users."""
        
        return {
            user_id: {
                "is_active": user_id in self.active_users,
                "last_seen": last_seen.isoformat(),
            }
            for user_id, last_seen in self.user_presence.items()
        }
    
    async def cleanup_stale_presence(self, max_age_minutes: int = 30) -> None:
        """Clean up stale presence data."""
        
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        stale_users = [
            user_id for user_id, last_seen in self.user_presence.items()
            if last_seen < cutoff_time
        ]
        
        for user_id in stale_users:
            self.active_users.discard(user_id)
            del self.user_presence[user_id]
        
        if stale_users:
            logger.info(f"Cleaned up {len(stale_users)} stale user presence records")
