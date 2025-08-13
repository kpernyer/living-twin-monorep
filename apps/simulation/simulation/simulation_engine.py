"""
Main simulation engine that orchestrates the organizational behavior simulation.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

from ..domain.models import (
    SimulationState,
    SimulationAgent,
    PriorityCommunication,
    AgentResponse,
    ConsultationRequest,
    ConsultationFeedback,
    SimulationEvent,
    OrganizationalMetrics,
    CommunicationType,
    ResponseType,
    PersonalityTrait,
    AgentState,
)
from ..agents.agent_factory import AgentFactory
from ..agents.behavior_engine import BehaviorEngine
from .time_engine import TimeEngine, SimulationScheduler
from .escalation_manager import EscalationManager
from ..communication import CommunicationDistributor, CommunicationTracker

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Main engine that orchestrates the organizational behavior simulation."""
    
    def __init__(self, organization_id: str, time_acceleration_factor: int = 144):
        self.organization_id = organization_id
        self.time_engine = TimeEngine(time_acceleration_factor)
        self.scheduler = SimulationScheduler(self.time_engine)
        self.behavior_engine = BehaviorEngine()
        self.escalation_manager = EscalationManager()
        
        # Simulation state
        self.state = SimulationState(
            organization_id=organization_id,
            time_acceleration_factor=time_acceleration_factor
        )
        
        # Event callbacks
        self.event_callbacks: List[Callable[[SimulationEvent], None]] = []
        
        # Setup time callbacks
        self.time_engine.add_tick_callback(self._on_time_tick)
        
        # Schedule regular maintenance tasks
        self.scheduler.schedule_daily_event(9, 0, self._daily_maintenance)  # 9 AM daily
        self.scheduler.schedule_daily_event(17, 0, self._end_of_day_processing)  # 5 PM daily
    
    async def start_simulation(self, employee_data: Dict) -> None:
        """Start the simulation with employee data."""
        
        logger.info(f"Starting simulation for organization {self.organization_id}")
        
        # Create agents from employee data
        self.state.agents = AgentFactory.create_agents_from_organization(
            {"employees": employee_data}, 
            self.organization_id
        )
        
        logger.info(f"Created {len(self.state.agents)} agents")
        
        # Start the time engine
        self.time_engine.start()
        self.state.is_running = True
        self.state.real_start_time = datetime.now()
        self.state.simulation_time = self.time_engine.get_current_simulation_time()
        
        # Log simulation start event
        await self._log_event("simulation_started", {
            "agent_count": len(self.state.agents),
            "time_acceleration": self.state.time_acceleration_factor,
        })
        
        logger.info("Simulation started successfully")
    
    async def stop_simulation(self) -> None:
        """Stop the simulation."""
        
        logger.info("Stopping simulation")
        
        await self.time_engine.stop()
        self.state.is_running = False
        
        # Log simulation stop event
        await self._log_event("simulation_stopped", {
            "duration_real_seconds": (datetime.now() - self.state.real_start_time).total_seconds(),
            "final_metrics": self.calculate_organizational_metrics(),
        })
        
        logger.info("Simulation stopped")
    
    async def send_communication(
        self,
        sender_id: str,
        recipient_ids: List[str],
        communication_type: CommunicationType,
        subject: str,
        content: str,
        priority_level: int = 3,
        deadline: Optional[datetime] = None
    ) -> PriorityCommunication:
        """Send a communication in the simulation."""
        
        communication = PriorityCommunication(
            type=communication_type,
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            subject=subject,
            content=content,
            priority_level=priority_level,
            deadline=deadline,
            organization_id=self.organization_id,
        )
        
        self.state.active_communications.append(communication)
        self.state.total_communications_sent += 1
        
        # Schedule response processing
        self.scheduler.schedule_delay(
            delay_seconds=random.uniform(300, 3600),  # 5 minutes to 1 hour
            callback=lambda: asyncio.create_task(self._process_communication_responses(communication))
        )
        
        # Log communication event
        await self._log_event("communication_sent", {
            "communication_id": communication.id,
            "type": communication_type.value,
            "sender_id": sender_id,
            "recipient_count": len(recipient_ids),
            "priority": priority_level,
        })
        
        logger.info(f"Communication sent: {subject} ({communication_type.value}) to {len(recipient_ids)} recipients")
        
        return communication
    
    async def create_consultation(
        self,
        requester_id: str,
        title: str,
        description: str,
        proposed_change: str,
        target_audience: List[str],
        deadline: datetime
    ) -> ConsultationRequest:
        """Create a consultation request for crowd wisdom."""
        
        consultation = ConsultationRequest(
            requester_id=requester_id,
            title=title,
            description=description,
            proposed_change=proposed_change,
            target_audience=target_audience,
            deadline=deadline,
            organization_id=self.organization_id,
        )
        
        self.state.active_consultations.append(consultation)
        
        # Schedule consultation processing
        self.scheduler.schedule_delay(
            delay_seconds=random.uniform(1800, 7200),  # 30 minutes to 2 hours
            callback=lambda: asyncio.create_task(self._process_consultation_responses(consultation))
        )
        
        # Log consultation event
        await self._log_event("consultation_created", {
            "consultation_id": consultation.id,
            "requester_id": requester_id,
            "target_audience_size": len(target_audience),
        })
        
        logger.info(f"Consultation created: {title}")
        
        return consultation
    
    async def _process_communication_responses(self, communication: PriorityCommunication) -> None:
        """Process agent responses to a communication."""
        
        responses = []
        
        for recipient_id in communication.recipient_ids:
            agent = self.state.agents.get(recipient_id)
            if not agent:
                continue
            
            # Generate response using behavior engine
            response = self.behavior_engine.process_communication(
                agent, communication, self.state.agents
            )
            
            if response:
                responses.append(response)
                communication.responses.append(response)
                self.state.total_responses_received += 1
                
                # Log response event
                await self._log_event("agent_response", {
                    "communication_id": communication.id,
                    "agent_id": agent.id,
                    "response_type": response.response_type.value,
                    "sentiment": response.sentiment,
                }, agent_id=agent.id)
        
        # Check for escalation opportunities
        if communication.type in [CommunicationType.NUDGE, CommunicationType.RECOMMENDATION]:
            escalated_communications = self.escalation_manager.check_for_escalations(
                [communication], self.state.agents
            )
            
            for escalated_comm in escalated_communications:
                self.state.active_communications.append(escalated_comm)
                self.state.escalations_triggered += 1
                
                # Schedule processing for escalated communication
                self.scheduler.schedule_delay(
                    delay_seconds=random.uniform(600, 1800),  # 10-30 minutes
                    callback=lambda: asyncio.create_task(self._process_communication_responses(escalated_comm))
                )
                
                await self._log_event("communication_escalated", {
                    "original_id": communication.id,
                    "escalated_id": escalated_comm.id,
                    "nudge_count": communication.nudge_count,
                })
        
        logger.info(f"Processed {len(responses)} responses to communication: {communication.subject}")
    
    async def _process_consultation_responses(self, consultation: ConsultationRequest) -> None:
        """Process agent responses to a consultation request."""
        
        responses = []
        
        for agent_id in consultation.target_audience:
            agent = self.state.agents.get(agent_id)
            if not agent:
                continue
            
            # Determine if agent will provide feedback
            if random.random() < 0.7:  # 70% participation rate
                feedback = self._generate_consultation_feedback(agent, consultation)
                responses.append(feedback)
                consultation.feedback_responses.append(feedback)
                
                await self._log_event("consultation_feedback", {
                    "consultation_id": consultation.id,
                    "agent_id": agent.id,
                    "sentiment": feedback.sentiment,
                }, agent_id=agent.id)
        
        logger.info(f"Processed {len(responses)} feedback responses to consultation: {consultation.title}")
    
    def _generate_consultation_feedback(
        self, 
        agent: SimulationAgent, 
        consultation: ConsultationRequest
    ) -> ConsultationFeedback:
        """Generate feedback for a consultation request."""
        
        # Generate feedback based on agent's expertise and personality
        expertise_areas = agent.professional.expertise_areas
        relevant_expertise = [area for area in expertise_areas if area in consultation.proposed_change.lower()]
        
        if relevant_expertise:
            confidence = random.uniform(0.6, 0.9)
            sentiment = random.uniform(0.2, 0.8)
            feedback = f"Based on my {relevant_expertise[0].replace('_', ' ')} experience, I think this change could..."
        else:
            confidence = random.uniform(0.3, 0.6)
            sentiment = random.uniform(0.0, 0.6)
            feedback = "From my perspective, this proposed change might..."
        
        concerns = []
        suggestions = []
        
        # Generate concerns based on personality
        risk_tolerance = agent.personality.get_trait(PersonalityTrait.RISK_TOLERANCE)
        if risk_tolerance < 0.4:
            concerns.append("Potential risks to current operations")
            concerns.append("Need for thorough testing before implementation")
        
        # Generate suggestions based on expertise
        if "engineering" in agent.professional.department.lower():
            suggestions.append("Consider technical implementation challenges")
            suggestions.append("Ensure proper testing and rollback procedures")
        elif "sales" in agent.professional.department.lower():
            suggestions.append("Assess customer impact and communication strategy")
            suggestions.append("Consider timing with sales cycles")
        
        return ConsultationFeedback(
            consultation_id=consultation.id,
            agent_id=agent.id,
            feedback=feedback,
            sentiment=sentiment,
            confidence=confidence,
            concerns=concerns,
            suggestions=suggestions,
        )
    
    def _on_time_tick(self, current_time: datetime) -> None:
        """Called on each time tick to update simulation state."""
        
        self.state.simulation_time = current_time
        
        # Update agent states periodically
        if random.random() < 0.1:  # 10% chance per tick
            self._update_agent_states()
        
        # Calculate organizational metrics periodically
        if random.random() < 0.05:  # 5% chance per tick
            self.state.organizational_friction_score = self._calculate_friction_score()
    
    def _update_agent_states(self) -> None:
        """Update agent states based on workload and stress."""
        
        for agent in self.state.agents.values():
            # Gradually reduce stress over time
            agent.memory.stress_level = max(0.0, agent.memory.stress_level - 0.01)
            
            # Gradually reduce workload over time (work gets completed)
            agent.professional.current_workload = max(0.1, agent.professional.current_workload - 0.05)
            
            # Update agent state based on current workload
            workload_ratio = agent.professional.current_workload / agent.professional.workload_capacity
            if workload_ratio > 1.1:
                agent.current_state = AgentState.OVERWHELMED
            elif workload_ratio > 0.8:
                agent.current_state = AgentState.BUSY
            else:
                agent.current_state = AgentState.AVAILABLE
    
    def _calculate_friction_score(self) -> float:
        """Calculate organizational friction score."""
        
        if not self.state.agents:
            return 0.0
        
        # Factors that contribute to friction
        total_stress = sum(agent.memory.stress_level for agent in self.state.agents.values())
        avg_stress = total_stress / len(self.state.agents)
        
        # Escalation rate
        escalation_rate = (
            self.state.escalations_triggered / max(1, self.state.total_communications_sent)
        )
        
        # Non-response rate
        response_rate = (
            self.state.total_responses_received / max(1, self.state.total_communications_sent)
        )
        non_response_rate = 1.0 - response_rate
        
        # Combine factors
        friction_score = (avg_stress * 0.4) + (escalation_rate * 0.4) + (non_response_rate * 0.2)
        
        return min(1.0, friction_score)
    
    def _daily_maintenance(self) -> None:
        """Daily maintenance tasks."""
        
        logger.info("Running daily maintenance")
        
        # Clean up old communications
        cutoff_time = self.state.simulation_time - timedelta(days=7)
        self.state.active_communications = [
            comm for comm in self.state.active_communications
            if comm.created_at > cutoff_time
        ]
        
        # Clean up old consultations
        self.state.active_consultations = [
            cons for cons in self.state.active_consultations
            if cons.created_at > cutoff_time and not cons.is_closed
        ]
    
    def _end_of_day_processing(self) -> None:
        """End of day processing."""
        
        logger.info("Running end of day processing")
        
        # Update average response time
        # (This would require tracking response times)
        
        # Generate daily metrics
        daily_metrics = self.calculate_organizational_metrics()
        
        # Log daily summary
        asyncio.create_task(self._log_event("daily_summary", {
            "metrics": daily_metrics,
            "active_communications": len(self.state.active_communications),
            "active_consultations": len(self.state.active_consultations),
        }))
    
    async def _log_event(
        self, 
        event_type: str, 
        data: Dict, 
        agent_id: Optional[str] = None,
        description: str = ""
    ) -> None:
        """Log a simulation event."""
        
        event = SimulationEvent(
            simulation_id=self.state.id,
            event_type=event_type,
            simulation_timestamp=self.state.simulation_time,
            agent_id=agent_id,
            data=data,
            description=description,
        )
        
        # Call event callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def add_event_callback(self, callback: Callable[[SimulationEvent], None]) -> None:
        """Add an event callback."""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[SimulationEvent], None]) -> None:
        """Remove an event callback."""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def calculate_organizational_metrics(self) -> OrganizationalMetrics:
        """Calculate current organizational metrics."""
        
        if not self.state.agents:
            return OrganizationalMetrics(
                organization_id=self.organization_id,
                simulation_id=self.state.id,
            )
        
        # Calculate response rate
        response_rate = (
            self.state.total_responses_received / max(1, self.state.total_communications_sent) * 100
        )
        
        # Calculate escalation rate
        escalation_rate = (
            self.state.escalations_triggered / max(1, self.state.total_communications_sent) * 100
        )
        
        # Calculate average stress level
        total_stress = sum(agent.memory.stress_level for agent in self.state.agents.values())
        avg_stress = total_stress / len(self.state.agents)
        
        # Calculate compliance rate (simplified)
        compliance_rate = max(0, 100 - escalation_rate)  # Inverse of escalation rate
        
        # Calculate collaboration score (based on cross-department interactions)
        collaboration_score = random.uniform(0.6, 0.9) * 100  # Placeholder
        
        return OrganizationalMetrics(
            organization_id=self.organization_id,
            simulation_id=self.state.id,
            time_period_start=self.state.real_start_time,
            time_period_end=datetime.now(),
            total_communications=self.state.total_communications_sent,
            response_rate=response_rate,
            escalation_rate=escalation_rate,
            compliance_rate=compliance_rate,
            collaboration_score=collaboration_score,
            stress_level_average=avg_stress,
        )
    
    def get_simulation_status(self) -> Dict:
        """Get current simulation status."""
        
        return {
            "is_running": self.state.is_running,
            "organization_id": self.organization_id,
            "agent_count": len(self.state.agents),
            "active_communications": len(self.state.active_communications),
            "active_consultations": len(self.state.active_consultations),
            "total_communications_sent": self.state.total_communications_sent,
            "total_responses_received": self.state.total_responses_received,
            "escalations_triggered": self.state.escalations_triggered,
            "organizational_friction_score": self.state.organizational_friction_score,
            "time_info": self.time_engine.get_time_info(),
            "scheduled_events": self.scheduler.get_scheduled_events_info(),
        }
