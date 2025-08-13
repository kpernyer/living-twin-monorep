"""
Escalation manager for handling nudge-to-order escalation logic.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..domain.models import (
    PriorityCommunication,
    SimulationAgent,
    AgentResponse,
    CommunicationType,
    ResponseType,
    SimulationEvent,
)

logger = logging.getLogger(__name__)


class EscalationManager:
    """Manages the escalation of nudges to direct orders."""
    
    def __init__(self, default_escalation_threshold: int = 5):
        self.default_escalation_threshold = default_escalation_threshold
        self.escalation_history: List[Dict] = []
    
    def check_for_escalations(
        self,
        communications: List[PriorityCommunication],
        agents: Dict[str, SimulationAgent]
    ) -> List[PriorityCommunication]:
        """Check communications for escalation opportunities and create escalated versions."""
        
        escalated_communications = []
        
        for communication in communications:
            if self._should_escalate(communication, agents):
                escalated_comm = self._create_escalated_communication(communication, agents)
                escalated_communications.append(escalated_comm)
                
                # Log the escalation
                self._log_escalation(communication, escalated_comm, agents)
        
        return escalated_communications
    
    def _should_escalate(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> bool:
        """Determine if a communication should be escalated."""
        
        # Only escalate nudges and recommendations
        if communication.type not in [CommunicationType.NUDGE, CommunicationType.RECOMMENDATION]:
            return False
        
        # Check if we've reached the escalation threshold
        if communication.nudge_count < communication.escalation_threshold:
            return False
        
        # Check if there are non-responsive recipients
        non_responsive_recipients = self._find_non_responsive_recipients(communication, agents)
        
        return len(non_responsive_recipients) > 0
    
    def _find_non_responsive_recipients(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> List[str]:
        """Find recipients who haven't responded appropriately to the communication."""
        
        non_responsive = []
        
        # Get all responses to this communication
        responses_by_agent = {}
        for response in communication.responses:
            responses_by_agent[response.agent_id] = response
        
        for recipient_id in communication.recipient_ids:
            if recipient_id not in responses_by_agent:
                # No response at all
                non_responsive.append(recipient_id)
            else:
                response = responses_by_agent[recipient_id]
                # Check if the response was non-compliant
                if response.response_type in [ResponseType.IGNORE, ResponseType.ESCALATE]:
                    non_responsive.append(recipient_id)
                elif response.response_type == ResponseType.TAKE_ACTION and not response.action_taken:
                    # Said they'd take action but didn't
                    non_responsive.append(recipient_id)
        
        return non_responsive
    
    def _create_escalated_communication(
        self,
        original_communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> PriorityCommunication:
        """Create an escalated version of the communication."""
        
        # Find non-responsive recipients
        non_responsive_recipients = self._find_non_responsive_recipients(original_communication, agents)
        
        # Create escalated communication
        escalated_comm = PriorityCommunication(
            type=CommunicationType.DIRECT_ORDER,
            sender_id=original_communication.sender_id,
            recipient_ids=non_responsive_recipients,
            subject=f"URGENT: {original_communication.subject}",
            content=self._generate_escalated_content(original_communication, agents),
            priority_level=min(5, original_communication.priority_level + 1),  # Increase priority
            deadline=original_communication.deadline,
            organization_id=original_communication.organization_id,
            nudge_count=0,  # Reset nudge count for the new communication
            escalation_threshold=self.default_escalation_threshold,
        )
        
        return escalated_comm
    
    def _generate_escalated_content(
        self,
        original_communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> str:
        """Generate content for the escalated communication."""
        
        sender = agents.get(original_communication.sender_id)
        sender_name = sender.name if sender else "Management"
        
        escalated_content = f"""
This is a direct order following {original_communication.nudge_count} previous communications on this matter.

ORIGINAL REQUEST:
{original_communication.content}

IMMEDIATE ACTION REQUIRED:
This directive requires immediate attention and compliance. Previous communications on this matter have not received adequate response.

Please confirm receipt and provide a detailed action plan within 2 hours.

Failure to respond will result in further escalation to senior management.

- {sender_name}
        """.strip()
        
        return escalated_content
    
    def _log_escalation(
        self,
        original_communication: PriorityCommunication,
        escalated_communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> None:
        """Log the escalation event."""
        
        sender = agents.get(original_communication.sender_id)
        non_responsive_agents = [
            agents.get(agent_id, {}).get('name', agent_id) 
            for agent_id in escalated_communication.recipient_ids
        ]
        
        escalation_record = {
            "timestamp": datetime.now().isoformat(),
            "original_communication_id": original_communication.id,
            "escalated_communication_id": escalated_communication.id,
            "sender_name": sender.name if sender else "Unknown",
            "sender_id": original_communication.sender_id,
            "non_responsive_recipients": non_responsive_agents,
            "nudge_count": original_communication.nudge_count,
            "escalation_threshold": original_communication.escalation_threshold,
            "original_type": original_communication.type.value,
            "escalated_type": escalated_communication.type.value,
            "priority_increase": escalated_communication.priority_level - original_communication.priority_level,
        }
        
        self.escalation_history.append(escalation_record)
        
        logger.warning(
            f"ESCALATION: {sender.name if sender else 'Unknown'} escalated communication "
            f"'{original_communication.subject}' to direct order after {original_communication.nudge_count} nudges. "
            f"Non-responsive: {', '.join(non_responsive_agents)}"
        )
    
    def update_nudge_count(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> bool:
        """Update the nudge count for a communication and check if it should be escalated."""
        
        if communication.type == CommunicationType.NUDGE:
            communication.nudge_count += 1
            
            logger.info(
                f"Nudge count updated to {communication.nudge_count} for communication "
                f"'{communication.subject}' (threshold: {communication.escalation_threshold})"
            )
            
            return communication.nudge_count >= communication.escalation_threshold
        
        return False
    
    def get_escalation_metrics(self, organization_id: str) -> Dict:
        """Get escalation metrics for an organization."""
        
        org_escalations = [
            record for record in self.escalation_history
            if record.get("organization_id") == organization_id
        ]
        
        if not org_escalations:
            return {
                "total_escalations": 0,
                "average_nudges_before_escalation": 0,
                "most_escalated_senders": [],
                "most_non_responsive_recipients": [],
                "escalation_rate": 0.0,
            }
        
        # Calculate metrics
        total_escalations = len(org_escalations)
        total_nudges = sum(record["nudge_count"] for record in org_escalations)
        average_nudges = total_nudges / total_escalations if total_escalations > 0 else 0
        
        # Count senders and recipients
        sender_counts = {}
        recipient_counts = {}
        
        for record in org_escalations:
            sender = record["sender_name"]
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            for recipient in record["non_responsive_recipients"]:
                recipient_counts[recipient] = recipient_counts.get(recipient, 0) + 1
        
        # Sort by frequency
        most_escalated_senders = sorted(
            sender_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        most_non_responsive = sorted(
            recipient_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "total_escalations": total_escalations,
            "average_nudges_before_escalation": round(average_nudges, 2),
            "most_escalated_senders": most_escalated_senders,
            "most_non_responsive_recipients": most_non_responsive,
            "escalation_rate": round(total_escalations / max(1, total_nudges) * 100, 2),
        }
    
    def get_agent_escalation_profile(self, agent_id: str) -> Dict:
        """Get escalation profile for a specific agent."""
        
        # Count escalations sent by this agent
        escalations_sent = [
            record for record in self.escalation_history
            if record["sender_id"] == agent_id
        ]
        
        # Count times this agent was non-responsive
        times_non_responsive = 0
        for record in self.escalation_history:
            if agent_id in [r.get("id") for r in record.get("non_responsive_recipients", [])]:
                times_non_responsive += 1
        
        return {
            "escalations_sent": len(escalations_sent),
            "times_non_responsive": times_non_responsive,
            "average_nudges_before_escalating": (
                sum(r["nudge_count"] for r in escalations_sent) / len(escalations_sent)
                if escalations_sent else 0
            ),
            "escalation_tendency": "high" if len(escalations_sent) > 3 else "low",
            "responsiveness": "low" if times_non_responsive > 2 else "high",
        }
    
    def predict_escalation_risk(
        self,
        communication: PriorityCommunication,
        agents: Dict[str, SimulationAgent]
    ) -> Dict:
        """Predict the risk of escalation for a communication."""
        
        if communication.type not in [CommunicationType.NUDGE, CommunicationType.RECOMMENDATION]:
            return {"risk_level": "none", "risk_score": 0.0, "factors": []}
        
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Current nudge count vs threshold
        nudge_progress = communication.nudge_count / communication.escalation_threshold
        if nudge_progress > 0.6:
            risk_factors.append(f"High nudge count ({communication.nudge_count}/{communication.escalation_threshold})")
            risk_score += 0.3
        
        # Factor 2: Non-responsive recipients
        non_responsive = self._find_non_responsive_recipients(communication, agents)
        if non_responsive:
            risk_factors.append(f"{len(non_responsive)} non-responsive recipients")
            risk_score += 0.2 * len(non_responsive) / len(communication.recipient_ids)
        
        # Factor 3: Sender's escalation history
        sender_profile = self.get_agent_escalation_profile(communication.sender_id)
        if sender_profile["escalation_tendency"] == "high":
            risk_factors.append("Sender has high escalation tendency")
            risk_score += 0.2
        
        # Factor 4: Priority level
        if communication.priority_level >= 4:
            risk_factors.append("High priority communication")
            risk_score += 0.1
        
        # Factor 5: Time since last communication
        # (This would require tracking communication timestamps)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        elif risk_score >= 0.2:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "factors": risk_factors,
            "nudge_progress": round(nudge_progress, 2),
            "non_responsive_count": len(non_responsive),
        }
