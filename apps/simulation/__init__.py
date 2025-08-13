"""
Organizational behavior simulation engine.

This package provides a comprehensive simulation system for modeling organizational
behavior, including AI agents that represent employees, communication patterns,
escalation dynamics, and crowd wisdom mechanisms.

Key Components:
- Domain models for agents, communications, and organizational metrics
- Agent factory for creating AI agents from employee data
- Behavior engine for realistic agent decision-making
- Time acceleration engine for fast simulation
- Escalation manager for nudge-to-order dynamics
- Main simulation engine that orchestrates everything

Usage:
    from apps.simulation import SimulationEngine, AgentFactory
    
    # Create and start a simulation
    engine = SimulationEngine("org_123")
    # await engine.start_simulation(employee_data)
    
    # Send communications and observe behavior
    # await engine.send_communication(
    #     sender_id="manager_1",
    #     recipient_ids=["emp_1", "emp_2"],
    #     communication_type=CommunicationType.NUDGE,
    #     subject="Please update your status",
    #     content="We need everyone to update their project status by EOD."
    # )
"""

from .domain import *
from .agents import AgentFactory
from .simulation import SimulationEngine, TimeEngine, SimulationScheduler, EscalationManager
from .communication import CommunicationDistributor, CommunicationTracker, DeliveryStatus, ActionStatus

__all__ = [
    # Domain models
    "PersonalityTrait",
    "CommunicationType", 
    "ResponseType",
    "AgentState",
    "PersonalityProfile",
    "ProfessionalProfile",
    "AgentMemory",
    "SimulationAgent",
    "PriorityCommunication",
    "AgentResponse",
    "ConsultationRequest",
    "ConsultationFeedback",
    "SimulationState",
    "SimulationEvent",
    "OrganizationalMetrics",
    
    # Agent system
    "AgentFactory",
    
    # Simulation engine
    "SimulationEngine",
    "TimeEngine",
    "SimulationScheduler", 
    "EscalationManager",
]

__version__ = "0.1.0"
