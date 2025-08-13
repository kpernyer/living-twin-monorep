"""
Agent factory for creating AI agents from employee data.
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

from ..domain.models import (
    SimulationAgent,
    PersonalityProfile,
    ProfessionalProfile,
    AgentMemory,
    PersonalityTrait,
    AgentState,
)


class AgentFactory:
    """Factory for creating simulation agents from employee data."""
    
    # Personality archetypes based on role and department
    PERSONALITY_ARCHETYPES = {
        "CEO": {
            PersonalityTrait.RISK_TOLERANCE: 0.8,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.3,  # Questions authority
            PersonalityTrait.COMMUNICATION_STYLE: 0.9,  # Very direct
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.9,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.2,  # High resilience
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.7,
        },
        "VP": {
            PersonalityTrait.RISK_TOLERANCE: 0.7,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.6,
            PersonalityTrait.COMMUNICATION_STYLE: 0.8,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.8,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.3,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.8,
        },
        "Director": {
            PersonalityTrait.RISK_TOLERANCE: 0.6,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.7,
            PersonalityTrait.COMMUNICATION_STYLE: 0.7,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.7,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.4,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.8,
        },
        "Manager": {
            PersonalityTrait.RISK_TOLERANCE: 0.5,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.8,
            PersonalityTrait.COMMUNICATION_STYLE: 0.6,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.6,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.5,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.7,
        },
        "Engineer": {
            PersonalityTrait.RISK_TOLERANCE: 0.4,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.6,
            PersonalityTrait.COMMUNICATION_STYLE: 0.4,  # More diplomatic
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.7,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.6,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.6,
        },
        "Sales": {
            PersonalityTrait.RISK_TOLERANCE: 0.7,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.7,
            PersonalityTrait.COMMUNICATION_STYLE: 0.8,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.8,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.4,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.9,
        },
        "HR": {
            PersonalityTrait.RISK_TOLERANCE: 0.3,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.8,
            PersonalityTrait.COMMUNICATION_STYLE: 0.3,  # Very diplomatic
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.6,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.5,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.9,
        },
        "Operations": {
            PersonalityTrait.RISK_TOLERANCE: 0.2,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.9,
            PersonalityTrait.COMMUNICATION_STYLE: 0.5,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.4,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.6,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.6,
        },
        "Marketing": {
            PersonalityTrait.RISK_TOLERANCE: 0.6,
            PersonalityTrait.AUTHORITY_RESPONSE: 0.7,
            PersonalityTrait.COMMUNICATION_STYLE: 0.7,
            PersonalityTrait.CHANGE_ADAPTABILITY: 0.8,
            PersonalityTrait.WORKLOAD_SENSITIVITY: 0.5,
            PersonalityTrait.COLLABORATION_PREFERENCE: 0.8,
        },
    }
    
    # Department-specific expertise areas
    DEPARTMENT_EXPERTISE = {
        "Engineering": ["software_development", "system_architecture", "technical_design", "code_review"],
        "Sales": ["customer_relations", "negotiation", "market_analysis", "revenue_optimization"],
        "Marketing": ["brand_management", "content_creation", "market_research", "campaign_management"],
        "HR": ["talent_acquisition", "employee_relations", "policy_development", "performance_management"],
        "Operations": ["process_optimization", "resource_management", "quality_assurance", "logistics"],
        "IT": ["infrastructure", "security", "data_management", "technical_support"],
        "Finance": ["financial_analysis", "budgeting", "risk_assessment", "compliance"],
    }
    
    @classmethod
    def create_agent_from_employee(
        cls,
        employee_data: Dict,
        organization_id: str,
        manager_id: Optional[str] = None,
        direct_reports: Optional[List[str]] = None
    ) -> SimulationAgent:
        """Create a simulation agent from employee data."""
        
        # Extract basic info
        email = employee_data.get("email", "")
        name = cls._extract_name_from_email(email)
        department = employee_data.get("department", "General")
        role = employee_data.get("role", "Employee")
        
        # Determine seniority level
        seniority = cls._determine_seniority_level(role)
        
        # Create personality profile
        personality = cls._create_personality_profile(role, department)
        
        # Create professional profile
        professional = ProfessionalProfile(
            department=department,
            role=role,
            seniority_level=seniority,
            expertise_areas=cls._get_expertise_areas(department, role),
            direct_reports=direct_reports or [],
            manager_id=manager_id,
            workload_capacity=cls._calculate_workload_capacity(seniority),
            current_workload=random.uniform(0.3, 0.8)  # Random initial workload
        )
        
        # Create agent memory with some initial relationship scores
        memory = AgentMemory(
            relationship_scores={},
            stress_level=random.uniform(0.1, 0.4),  # Low to moderate initial stress
        )
        
        # Determine initial state
        initial_state = cls._determine_initial_state()
        
        return SimulationAgent(
            email=email,
            name=name,
            personality=personality,
            professional=professional,
            memory=memory,
            current_state=initial_state,
            organization_id=organization_id,
        )
    
    @classmethod
    def create_agents_from_organization(
        cls,
        organization_data: Dict,
        organization_id: str
    ) -> Dict[str, SimulationAgent]:
        """Create all agents for an organization from employee data."""
        
        agents = {}
        employee_data = organization_data.get("employees", {})
        
        # First pass: create all agents
        for email, employee_info in employee_data.items():
            agent = cls.create_agent_from_employee(
                {**employee_info, "email": email},
                organization_id
            )
            agents[agent.id] = agent
        
        # Second pass: establish reporting relationships
        email_to_agent_id = {agent.email: agent.id for agent in agents.values()}
        
        for agent in agents.values():
            # Find manager
            manager_email = cls._find_manager_email(agent.email, employee_data)
            if manager_email and manager_email in email_to_agent_id:
                agent.professional.manager_id = email_to_agent_id[manager_email]
            
            # Find direct reports
            direct_report_emails = cls._find_direct_reports(agent.email, employee_data)
            agent.professional.direct_reports = [
                email_to_agent_id[email] for email in direct_report_emails
                if email in email_to_agent_id
            ]
            
            # Initialize relationship scores with colleagues
            cls._initialize_relationship_scores(agent, agents)
        
        return agents
    
    @classmethod
    def _extract_name_from_email(cls, email: str) -> str:
        """Extract a display name from email address."""
        if not email:
            return "Unknown"
        
        local_part = email.split("@")[0]
        # Convert john.doe or john_doe to John Doe
        name_parts = local_part.replace(".", " ").replace("_", " ").split()
        return " ".join(part.capitalize() for part in name_parts)
    
    @classmethod
    def _determine_seniority_level(cls, role: str) -> int:
        """Determine seniority level from role title."""
        role_lower = role.lower()
        
        if any(title in role_lower for title in ["ceo", "chief", "president"]):
            return 5
        elif any(title in role_lower for title in ["vp", "vice president"]):
            return 4
        elif any(title in role_lower for title in ["director", "head of"]):
            return 3
        elif any(title in role_lower for title in ["manager", "lead", "senior manager"]):
            return 2
        else:
            return 1
    
    @classmethod
    def _create_personality_profile(cls, role: str, department: str) -> PersonalityProfile:
        """Create a personality profile based on role and department."""
        
        # Start with role-based archetype
        base_traits = {}
        for archetype, traits in cls.PERSONALITY_ARCHETYPES.items():
            if archetype.lower() in role.lower():
                base_traits = traits.copy()
                break
        
        # If no role match, use department-based traits
        if not base_traits:
            for archetype, traits in cls.PERSONALITY_ARCHETYPES.items():
                if archetype.lower() in department.lower():
                    base_traits = traits.copy()
                    break
        
        # Default to balanced traits if no match
        if not base_traits:
            base_traits = {trait: 0.5 for trait in PersonalityTrait}
        
        # Add some individual variation (±0.2)
        varied_traits = {}
        for trait, base_value in base_traits.items():
            variation = random.uniform(-0.2, 0.2)
            varied_traits[trait] = max(0.0, min(1.0, base_value + variation))
        
        return PersonalityProfile(traits=varied_traits)
    
    @classmethod
    def _get_expertise_areas(cls, department: str, role: str) -> List[str]:
        """Get expertise areas based on department and role."""
        base_expertise = cls.DEPARTMENT_EXPERTISE.get(department, ["general_business"])
        
        # Add role-specific expertise
        role_lower = role.lower()
        if "senior" in role_lower or "lead" in role_lower:
            base_expertise.append("mentoring")
        if "manager" in role_lower or "director" in role_lower:
            base_expertise.extend(["team_management", "strategic_planning"])
        if any(title in role_lower for title in ["vp", "chief", "ceo"]):
            base_expertise.extend(["executive_leadership", "organizational_strategy"])
        
        return base_expertise
    
    @classmethod
    def _calculate_workload_capacity(cls, seniority_level: int) -> float:
        """Calculate workload capacity based on seniority."""
        # Higher seniority = higher capacity (more resources, delegation ability)
        base_capacity = 0.8 + (seniority_level * 0.1)
        return min(1.5, base_capacity)  # Cap at 1.5x normal capacity
    
    @classmethod
    def _determine_initial_state(cls) -> AgentState:
        """Determine initial agent state with realistic distribution."""
        states = [
            (AgentState.AVAILABLE, 0.6),
            (AgentState.BUSY, 0.3),
            (AgentState.IN_MEETING, 0.08),
            (AgentState.OVERWHELMED, 0.02),
        ]
        
        rand = random.random()
        cumulative = 0.0
        for state, probability in states:
            cumulative += probability
            if rand <= cumulative:
                return state
        
        return AgentState.AVAILABLE
    
    @classmethod
    def _find_manager_email(cls, employee_email: str, employee_data: Dict) -> Optional[str]:
        """Find the manager's email for an employee."""
        # This is a simplified approach - in real data, you'd have explicit manager relationships
        employee_info = employee_data.get(employee_email, {})
        department = employee_info.get("department", "")
        role = employee_info.get("role", "")
        
        # Look for managers in the same department
        for email, info in employee_data.items():
            if email == employee_email:
                continue
            
            other_role = info.get("role", "").lower()
            other_dept = info.get("department", "")
            
            # Same department and manager role
            if (other_dept == department and 
                any(title in other_role for title in ["manager", "director", "vp", "head"])):
                return email
        
        return None
    
    @classmethod
    def _find_direct_reports(cls, manager_email: str, employee_data: Dict) -> List[str]:
        """Find direct reports for a manager."""
        manager_info = employee_data.get(manager_email, {})
        manager_dept = manager_info.get("department", "")
        manager_role = manager_info.get("role", "").lower()
        
        # Only managers have direct reports
        if not any(title in manager_role for title in ["manager", "director", "vp", "ceo", "head"]):
            return []
        
        direct_reports = []
        for email, info in employee_data.items():
            if email == manager_email:
                continue
            
            employee_dept = info.get("department", "")
            employee_role = info.get("role", "").lower()
            
            # Same department, non-manager role (simplified logic)
            if (employee_dept == manager_dept and 
                not any(title in employee_role for title in ["manager", "director", "vp", "ceo"])):
                direct_reports.append(email)
        
        return direct_reports
    
    @classmethod
    def _initialize_relationship_scores(cls, agent: SimulationAgent, all_agents: Dict[str, SimulationAgent]) -> None:
        """Initialize relationship scores with other agents."""
        for other_agent_id, other_agent in all_agents.items():
            if other_agent_id == agent.id:
                continue
            
            # Base relationship score
            base_score = 0.5
            
            # Same department bonus
            if other_agent.professional.department == agent.professional.department:
                base_score += 0.2
            
            # Manager/direct report relationships
            if other_agent_id == agent.professional.manager_id:
                base_score += 0.3  # Good relationship with manager
            elif other_agent_id in agent.professional.direct_reports:
                base_score += 0.2  # Good relationship with direct reports
            
            # Similar seniority levels work well together
            seniority_diff = abs(agent.professional.seniority_level - other_agent.professional.seniority_level)
            if seniority_diff <= 1:
                base_score += 0.1
            
            # Add some random variation
            variation = random.uniform(-0.2, 0.2)
            final_score = max(0.0, min(1.0, base_score + variation))
            
            agent.memory.relationship_scores[other_agent_id] = final_score
