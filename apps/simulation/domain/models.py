"""
Domain models for the organizational behavior simulation engine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


class PersonalityTrait(Enum):
    """Core personality traits that influence agent behavior."""
    RISK_TOLERANCE = "risk_tolerance"  # 0.0 (conservative) to 1.0 (risk-taking)
    AUTHORITY_RESPONSE = "authority_response"  # 0.0 (questioning) to 1.0 (compliant)
    COMMUNICATION_STYLE = "communication_style"  # 0.0 (diplomatic) to 1.0 (direct)
    CHANGE_ADAPTABILITY = "change_adaptability"  # 0.0 (resistant) to 1.0 (embracing)
    WORKLOAD_SENSITIVITY = "workload_sensitivity"  # 0.0 (resilient) to 1.0 (overwhelmed)
    COLLABORATION_PREFERENCE = "collaboration_preference"  # 0.0 (individual) to 1.0 (team)


class CommunicationType(Enum):
    """Types of organizational communications."""
    DIRECT_ORDER = "direct_order"
    RECOMMENDATION = "recommendation"
    NUDGE = "nudge"
    CONSULTATION = "consultation"
    FEEDBACK_REQUEST = "feedback_request"


class ResponseType(Enum):
    """Types of agent responses to communications."""
    IGNORE = "ignore"
    TAKE_ACTION = "take_action"
    SEEK_CLARIFICATION = "seek_clarification"
    PROVIDE_FEEDBACK = "provide_feedback"
    ESCALATE = "escalate"
    DELEGATE = "delegate"


class AgentState(Enum):
    """Current state of an agent."""
    AVAILABLE = "available"
    BUSY = "busy"
    OVERWHELMED = "overwhelmed"
    ON_LEAVE = "on_leave"
    IN_MEETING = "in_meeting"


@dataclass
class PersonalityProfile:
    """Personality profile defining agent behavior patterns."""
    traits: Dict[PersonalityTrait, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Ensure all traits have values between 0.0 and 1.0
        for trait in PersonalityTrait:
            if trait not in self.traits:
                self.traits[trait] = 0.5  # Default to neutral
            else:
                self.traits[trait] = max(0.0, min(1.0, self.traits[trait]))
    
    def get_trait(self, trait: PersonalityTrait) -> float:
        """Get a personality trait value."""
        return self.traits.get(trait, 0.5)


@dataclass
class ProfessionalProfile:
    """Professional characteristics and context."""
    department: str
    role: str
    seniority_level: int  # 1 (junior) to 5 (executive)
    expertise_areas: List[str] = field(default_factory=list)
    direct_reports: List[str] = field(default_factory=list)  # Agent IDs
    manager_id: Optional[str] = None
    workload_capacity: float = 1.0  # Base capacity multiplier
    current_workload: float = 0.5  # Current workload as fraction of capacity


@dataclass
class AgentMemory:
    """Agent's memory of past interactions and experiences."""
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    priority_responses: Dict[str, List[str]] = field(default_factory=dict)  # priority_id -> response_ids
    relationship_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> relationship_strength
    stress_level: float = 0.0  # 0.0 (calm) to 1.0 (highly stressed)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SimulationAgent:
    """AI agent representing an organizational member."""
    id: str = field(default_factory=lambda: str(uuid4()))
    email: str = ""
    name: str = ""
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)
    professional: ProfessionalProfile = field(default_factory=ProfessionalProfile)
    memory: AgentMemory = field(default_factory=AgentMemory)
    current_state: AgentState = AgentState.AVAILABLE
    organization_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_response_probability(self, communication: 'PriorityCommunication') -> Dict[ResponseType, float]:
        """Calculate probability of different response types based on personality and context."""
        probabilities = {}
        
        # Base probabilities influenced by personality traits
        authority_response = self.personality.get_trait(PersonalityTrait.AUTHORITY_RESPONSE)
        workload_sensitivity = self.personality.get_trait(PersonalityTrait.WORKLOAD_SENSITIVITY)
        
        # Adjust based on communication type
        if communication.type == CommunicationType.DIRECT_ORDER:
            probabilities[ResponseType.TAKE_ACTION] = 0.7 + (authority_response * 0.25)
            probabilities[ResponseType.SEEK_CLARIFICATION] = 0.2 - (authority_response * 0.1)
            probabilities[ResponseType.IGNORE] = 0.1 - (authority_response * 0.05)
        elif communication.type == CommunicationType.NUDGE:
            probabilities[ResponseType.IGNORE] = 0.4 + (workload_sensitivity * 0.3)
            probabilities[ResponseType.TAKE_ACTION] = 0.3 + (authority_response * 0.2)
            probabilities[ResponseType.SEEK_CLARIFICATION] = 0.3
        else:  # RECOMMENDATION
            probabilities[ResponseType.TAKE_ACTION] = 0.5 + (authority_response * 0.2)
            probabilities[ResponseType.SEEK_CLARIFICATION] = 0.3
            probabilities[ResponseType.IGNORE] = 0.2 + (workload_sensitivity * 0.2)
        
        # Normalize probabilities
        total = sum(probabilities.values())
        return {k: v / total for k, v in probabilities.items()}


@dataclass
class PriorityCommunication:
    """A communication about organizational priorities."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: CommunicationType = CommunicationType.NUDGE
    sender_id: str = ""
    recipient_ids: List[str] = field(default_factory=list)
    subject: str = ""
    content: str = ""
    priority_level: int = 1  # 1 (low) to 5 (critical)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    organization_id: str = ""
    
    # Tracking fields
    nudge_count: int = 0  # How many times this has been sent as a nudge
    escalation_threshold: int = 5  # Nudges before auto-escalation
    responses: List['AgentResponse'] = field(default_factory=list)


@dataclass
class AgentResponse:
    """An agent's response to a priority communication."""
    id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    communication_id: str = ""
    response_type: ResponseType = ResponseType.IGNORE
    content: str = ""  # Response message/reasoning
    sentiment: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    confidence: float = 0.5  # Agent's confidence in their response
    created_at: datetime = field(default_factory=datetime.now)
    
    # Action tracking
    action_taken: bool = False
    estimated_completion_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None


@dataclass
class ConsultationRequest:
    """Request for crowd wisdom/feedback on a proposed change."""
    id: str = field(default_factory=lambda: str(uuid4()))
    requester_id: str = ""
    title: str = ""
    description: str = ""
    proposed_change: str = ""
    target_audience: List[str] = field(default_factory=list)  # Agent IDs or department names
    deadline: datetime = field(default_factory=lambda: datetime.now())
    organization_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Responses
    feedback_responses: List['ConsultationFeedback'] = field(default_factory=list)
    is_closed: bool = False


@dataclass
class ConsultationFeedback:
    """Feedback provided by an agent on a consultation request."""
    id: str = field(default_factory=lambda: str(uuid4()))
    consultation_id: str = ""
    agent_id: str = ""
    feedback: str = ""
    sentiment: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    confidence: float = 0.5
    concerns: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SimulationState:
    """Current state of the organizational simulation."""
    id: str = field(default_factory=lambda: str(uuid4()))
    organization_id: str = ""
    simulation_time: datetime = field(default_factory=datetime.now)
    real_start_time: datetime = field(default_factory=datetime.now)
    time_acceleration_factor: int = 144  # 10 seconds = 1 day (86400/600)
    is_running: bool = False
    
    # Active elements
    active_communications: List[PriorityCommunication] = field(default_factory=list)
    active_consultations: List[ConsultationRequest] = field(default_factory=list)
    agents: Dict[str, SimulationAgent] = field(default_factory=dict)
    
    # Metrics
    total_communications_sent: int = 0
    total_responses_received: int = 0
    escalations_triggered: int = 0
    average_response_time: float = 0.0
    organizational_friction_score: float = 0.0  # 0.0 (smooth) to 1.0 (high friction)


@dataclass
class SimulationEvent:
    """An event that occurred during simulation."""
    id: str = field(default_factory=lambda: str(uuid4()))
    simulation_id: str = ""
    event_type: str = ""  # "communication_sent", "response_received", "escalation", etc.
    timestamp: datetime = field(default_factory=datetime.now)
    simulation_timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class OrganizationalMetrics:
    """Metrics calculated from simulation data."""
    organization_id: str = ""
    simulation_id: str = ""
    time_period_start: datetime = field(default_factory=datetime.now)
    time_period_end: datetime = field(default_factory=datetime.now)
    
    # Communication metrics
    total_communications: int = 0
    response_rate: float = 0.0  # Percentage of communications that received responses
    average_response_time_hours: float = 0.0
    escalation_rate: float = 0.0  # Percentage of nudges that escalated to orders
    
    # Behavioral metrics
    compliance_rate: float = 0.0  # Percentage of direct orders followed
    collaboration_score: float = 0.0  # How much cross-department interaction
    stress_level_average: float = 0.0  # Average stress across all agents
    
    # Department-specific metrics
    department_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Friction points
    high_friction_communications: List[str] = field(default_factory=list)  # Communication IDs
    bottleneck_agents: List[str] = field(default_factory=list)  # Agent IDs causing delays
