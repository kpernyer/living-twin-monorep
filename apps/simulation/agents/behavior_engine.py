"""
Behavior engine for AI agents in the organizational simulation.
"""

import random
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..domain.models import (
    SimulationAgent,
    PriorityCommunication,
    AgentResponse,
    ResponseType,
    CommunicationType,
    PersonalityTrait,
    AgentState,
)

logger = logging.getLogger(__name__)


class BehaviorEngine:
    """Engine that determines how agents behave and respond to communications."""
    
    def __init__(self):
        self.response_generators = {
            ResponseType.IGNORE: self._generate_ignore_response,
            ResponseType.TAKE_ACTION: self._generate_action_response,
            ResponseType.SEEK_CLARIFICATION: self._generate_clarification_response,
            ResponseType.PROVIDE_FEEDBACK: self._generate_feedback_response,
            ResponseType.ESCALATE: self._generate_escalation_response,
            ResponseType.DELEGATE: self._generate_delegation_response,
        }
    
    def process_communication(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> Optional[AgentResponse]:
        """Process a communication and generate an agent's response."""
        
        # Check if agent should respond based on their current state
        if not self._should_respond(agent, communication):
            return None
        
        # Calculate response probabilities based on personality and context
        response_probabilities = agent.calculate_response_probability(communication)
        
        # Adjust probabilities based on current context
        response_probabilities = self._adjust_probabilities_for_context(
            agent, communication, response_probabilities, all_agents
        )
        
        # Select response type based on probabilities
        response_type = self._select_response_type(response_probabilities)
        
        # Generate the actual response
        response = self._generate_response(agent, communication, response_type, all_agents)
        
        # Update agent's memory and state
        self._update_agent_after_response(agent, communication, response)
        
        logger.info(f"Agent {agent.name} responded to communication with {response_type.value}")
        return response
    
    def _should_respond(self, agent: SimulationAgent, communication: PriorityCommunication) -> bool:
        """Determine if an agent should respond to a communication."""
        
        # Agents on leave don't respond
        if agent.current_state == AgentState.ON_LEAVE:
            return False
        
        # Overwhelmed agents have reduced response rate
        if agent.current_state == AgentState.OVERWHELMED:
            return random.random() < 0.3
        
        # Busy agents have reduced response rate for non-urgent communications
        if agent.current_state == AgentState.BUSY and communication.priority_level < 4:
            return random.random() < 0.6
        
        # Direct orders almost always get responses
        if communication.type == CommunicationType.DIRECT_ORDER:
            return random.random() < 0.95
        
        # Base response rate varies by personality
        authority_response = agent.personality.get_trait(PersonalityTrait.AUTHORITY_RESPONSE)
        base_response_rate = 0.5 + (authority_response * 0.3)
        
        return random.random() < base_response_rate
    
    def _adjust_probabilities_for_context(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        base_probabilities: Dict[ResponseType, float],
        all_agents: Dict[str, SimulationAgent]
    ) -> Dict[ResponseType, float]:
        """Adjust response probabilities based on current context."""
        
        adjusted = base_probabilities.copy()
        
        # Relationship with sender affects response
        sender_relationship = agent.memory.relationship_scores.get(communication.sender_id, 0.5)
        
        if sender_relationship > 0.7:  # Good relationship
            adjusted[ResponseType.TAKE_ACTION] *= 1.3
            adjusted[ResponseType.IGNORE] *= 0.7
        elif sender_relationship < 0.3:  # Poor relationship
            adjusted[ResponseType.IGNORE] *= 1.4
            adjusted[ResponseType.TAKE_ACTION] *= 0.8
        
        # High stress reduces compliance
        if agent.memory.stress_level > 0.7:
            adjusted[ResponseType.IGNORE] *= 1.2
            adjusted[ResponseType.SEEK_CLARIFICATION] *= 1.1
        
        # High workload affects response
        workload_ratio = agent.professional.current_workload / agent.professional.workload_capacity
        if workload_ratio > 0.8:
            adjusted[ResponseType.IGNORE] *= 1.3
            adjusted[ResponseType.DELEGATE] *= 1.2
        
        # Priority level affects response
        priority_multiplier = 1.0 + (communication.priority_level - 3) * 0.2
        adjusted[ResponseType.TAKE_ACTION] *= priority_multiplier
        
        # Normalize probabilities
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}
    
    def _select_response_type(self, probabilities: Dict[ResponseType, float]) -> ResponseType:
        """Select a response type based on probabilities."""
        rand = random.random()
        cumulative = 0.0
        
        for response_type, probability in probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                return response_type
        
        # Fallback
        return ResponseType.IGNORE
    
    def _generate_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        response_type: ResponseType,
        all_agents: Dict[str, SimulationAgent]
    ) -> AgentResponse:
        """Generate the actual response content."""
        
        generator = self.response_generators.get(response_type, self._generate_ignore_response)
        content, sentiment, confidence = generator(agent, communication, all_agents)
        
        # Determine if action will be taken
        action_taken = response_type in [ResponseType.TAKE_ACTION, ResponseType.DELEGATE]
        
        # Estimate completion time if action is taken
        completion_time = None
        if action_taken:
            completion_time = self._estimate_completion_time(agent, communication)
        
        return AgentResponse(
            agent_id=agent.id,
            communication_id=communication.id,
            response_type=response_type,
            content=content,
            sentiment=sentiment,
            confidence=confidence,
            action_taken=action_taken,
            estimated_completion_time=completion_time,
        )
    
    def _generate_ignore_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate an ignore response (no actual response sent)."""
        
        reasons = [
            "Too busy with current priorities",
            "Unclear on the relevance to my role",
            "Waiting for more information",
            "Focusing on higher priority tasks",
            "Need to discuss with team first",
        ]
        
        reason = random.choice(reasons)
        return f"[Internal: {reason}]", 0.0, 0.3
    
    def _generate_action_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate a positive action response."""
        
        communication_style = agent.personality.get_trait(PersonalityTrait.COMMUNICATION_STYLE)
        
        if communication_style > 0.7:  # Direct style
            responses = [
                "Will handle this immediately.",
                "On it. Expected completion by end of day.",
                "Understood. Taking action now.",
                "Got it. Will prioritize this.",
            ]
        else:  # Diplomatic style
            responses = [
                "Thank you for bringing this to my attention. I'll address this promptly.",
                "I appreciate the guidance. I'll work on this right away.",
                "This aligns well with our objectives. I'll get started on this.",
                "I understand the importance of this. Will make it a priority.",
            ]
        
        response = random.choice(responses)
        sentiment = random.uniform(0.3, 0.8)
        confidence = random.uniform(0.6, 0.9)
        
        return response, sentiment, confidence
    
    def _generate_clarification_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate a clarification-seeking response."""
        
        questions = [
            "Could you provide more details on the expected timeline?",
            "What resources will be available for this initiative?",
            "How does this align with our current quarterly objectives?",
            "Should this take priority over existing commitments?",
            "What would success look like for this project?",
            "Are there specific stakeholders I should coordinate with?",
        ]
        
        question = random.choice(questions)
        sentiment = random.uniform(0.1, 0.5)
        confidence = random.uniform(0.4, 0.7)
        
        return question, sentiment, confidence
    
    def _generate_feedback_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate a feedback response."""
        
        expertise_areas = agent.professional.expertise_areas
        
        feedback_types = [
            "Based on my experience with {expertise}, I think we should consider...",
            "From a {expertise} perspective, this could impact...",
            "I've seen similar initiatives succeed when we focus on...",
            "One potential challenge I foresee is...",
            "This reminds me of a successful project where we...",
        ]
        
        expertise = random.choice(expertise_areas) if expertise_areas else "general business"
        feedback_template = random.choice(feedback_types)
        feedback = feedback_template.format(expertise=expertise.replace("_", " "))
        
        sentiment = random.uniform(0.2, 0.7)
        confidence = random.uniform(0.5, 0.8)
        
        return feedback, sentiment, confidence
    
    def _generate_escalation_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate an escalation response."""
        
        escalation_reasons = [
            "This requires approval from my manager before proceeding.",
            "I need to coordinate with other departments on this.",
            "This impacts our budget and needs finance review.",
            "The scope is beyond my current authority level.",
            "This conflicts with other strategic priorities.",
        ]
        
        reason = random.choice(escalation_reasons)
        sentiment = random.uniform(-0.2, 0.3)
        confidence = random.uniform(0.6, 0.8)
        
        return reason, sentiment, confidence
    
    def _generate_delegation_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> tuple[str, float, float]:
        """Generate a delegation response."""
        
        if not agent.professional.direct_reports:
            # Can't delegate, fall back to action
            return self._generate_action_response(agent, communication, all_agents)
        
        delegation_messages = [
            "I'll assign this to my team and ensure proper oversight.",
            "This is a great opportunity for my team to take ownership.",
            "I'll delegate this to the appropriate team member.",
            "My team has the right expertise to handle this effectively.",
        ]
        
        message = random.choice(delegation_messages)
        sentiment = random.uniform(0.3, 0.6)
        confidence = random.uniform(0.7, 0.9)
        
        return message, sentiment, confidence
    
    def _estimate_completion_time(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication
    ) -> datetime:
        """Estimate when the agent will complete the requested action."""
        
        # Base completion time based on priority and complexity
        base_hours = {
            1: random.uniform(24, 72),    # Low priority: 1-3 days
            2: random.uniform(12, 48),    # Medium-low: 0.5-2 days
            3: random.uniform(8, 24),     # Medium: 8-24 hours
            4: random.uniform(4, 12),     # High: 4-12 hours
            5: random.uniform(1, 6),      # Critical: 1-6 hours
        }
        
        hours = base_hours.get(communication.priority_level, 24)
        
        # Adjust based on agent's workload
        workload_ratio = agent.professional.current_workload / agent.professional.workload_capacity
        hours *= (1 + workload_ratio)
        
        # Adjust based on agent's seniority (higher seniority = more resources)
        seniority_factor = 1.0 - (agent.professional.seniority_level - 1) * 0.1
        hours *= seniority_factor
        
        return datetime.now() + timedelta(hours=hours)
    
    def _update_agent_after_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        response: AgentResponse
    ) -> None:
        """Update agent's state and memory after responding."""
        
        # Update interaction history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "response_type": response.response_type.value,
            "sentiment": response.sentiment,
        }
        agent.memory.interaction_history.append(interaction)
        
        # Update stress level based on response type and workload
        if response.response_type == ResponseType.IGNORE:
            agent.memory.stress_level += 0.05  # Ignoring creates some stress
        elif response.response_type == ResponseType.TAKE_ACTION:
            agent.memory.stress_level += 0.1   # Taking action increases workload stress
            agent.professional.current_workload += 0.1
        elif response.response_type == ResponseType.SEEK_CLARIFICATION:
            agent.memory.stress_level += 0.02  # Minimal stress from asking questions
        
        # Cap stress level
        agent.memory.stress_level = min(1.0, agent.memory.stress_level)
        
        # Cap workload
        agent.professional.current_workload = min(
            agent.professional.workload_capacity * 1.2,  # Can go 20% over capacity
            agent.professional.current_workload
        )
        
        # Update relationship with sender based on response
        sender_id = communication.sender_id
        current_relationship = agent.memory.relationship_scores.get(sender_id, 0.5)
        
        if response.response_type == ResponseType.TAKE_ACTION:
            agent.memory.relationship_scores[sender_id] = min(1.0, current_relationship + 0.05)
        elif response.response_type == ResponseType.IGNORE:
            agent.memory.relationship_scores[sender_id] = max(0.0, current_relationship - 0.1)
        
        # Update agent state based on workload
        workload_ratio = agent.professional.current_workload / agent.professional.workload_capacity
        if workload_ratio > 1.1:
            agent.current_state = AgentState.OVERWHELMED
        elif workload_ratio > 0.8:
            agent.current_state = AgentState.BUSY
        else:
            agent.current_state = AgentState.AVAILABLE
        
        agent.memory.last_updated = datetime.now()
