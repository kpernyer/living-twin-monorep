"""
MCP-enhanced AI agent engine for realistic organizational simulation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..domain.models import (
    SimulationAgent,
    PriorityCommunication,
    AgentResponse,
    ResponseType,
    PersonalityTrait,
)

logger = logging.getLogger(__name__)


class MCPAgentEngine:
    """AI-powered agent engine using MCP for intelligent behavior."""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.agent_contexts = {}  # Cache for agent conversation contexts
    
    async def process_communication_with_ai(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> Optional[AgentResponse]:
        """Process communication using AI reasoning instead of rules."""
        
        # Build rich context for the AI agent
        context = await self._build_agent_context(agent, communication, all_agents)
        
        # Use MCP to get AI-powered response
        ai_response = await self._get_ai_response(agent, communication, context)
        
        if not ai_response:
            return None
        
        # Convert AI response to structured format
        structured_response = self._structure_ai_response(agent, communication, ai_response)
        
        # Update agent memory with AI insights
        await self._update_agent_with_ai_insights(agent, communication, structured_response)
        
        return structured_response
    
    async def _build_agent_context(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        all_agents: Dict[str, SimulationAgent]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI reasoning."""
        
        # Get sender information
        sender = all_agents.get(communication.sender_id)
        sender_context = {
            "name": sender.name if sender else "Unknown",
            "role": sender.professional.role if sender else "Unknown",
            "relationship_score": agent.memory.relationship_scores.get(communication.sender_id, 0.5)
        }
        
        # Get recent company knowledge if relevant
        company_context = None
        if hasattr(self.mcp_client, 'search_company_knowledge'):
            try:
                company_context = await self.mcp_client.use_tool("rag_search", {
                    "query": communication.content[:200],  # First 200 chars
                    "tenant_id": agent.organization_id,
                    "limit": 3
                })
            except Exception as e:
                logger.warning(f"Failed to get company context: {e}")
        
        # Build personality description
        personality_desc = self._describe_personality(agent.personality)
        
        # Recent interaction patterns
        recent_interactions = agent.memory.interaction_history[-10:] if agent.memory.interaction_history else []
        
        return {
            "agent": {
                "name": agent.name,
                "role": agent.professional.role,
                "department": agent.professional.department,
                "seniority_level": agent.professional.seniority_level,
                "expertise_areas": agent.professional.expertise_areas,
                "personality": personality_desc,
                "current_state": agent.current_state.value,
                "workload": {
                    "current": agent.professional.current_workload,
                    "capacity": agent.professional.workload_capacity,
                    "utilization": agent.professional.current_workload / agent.professional.workload_capacity
                },
                "stress_level": agent.memory.stress_level
            },
            "communication": {
                "content": communication.content,
                "type": communication.type.value,
                "priority": communication.priority_level,
                "sender": sender_context,
                "timestamp": communication.timestamp.isoformat()
            },
            "company_context": company_context,
            "recent_interactions": recent_interactions,
            "organizational_relationships": {
                "manager": agent.professional.manager_id,
                "direct_reports": agent.professional.direct_reports,
                "key_relationships": {
                    agent_id: score for agent_id, score in agent.memory.relationship_scores.items()
                    if score > 0.7 or score < 0.3  # Only significant relationships
                }
            }
        }
    
    async def _get_ai_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get AI-powered response using MCP reasoning tools."""
        
        # Create a realistic persona prompt
        persona_prompt = self._create_persona_prompt(context["agent"])
        
        # Create the reasoning prompt
        reasoning_prompt = f"""
{persona_prompt}

You've received the following communication:
---
From: {context['communication']['sender']['name']} ({context['communication']['sender']['role']})
Priority: {context['communication']['priority']}/5
Type: {context['communication']['type']}
Content: {context['communication']['content']}
---

Context:
- Your relationship with sender: {context['communication']['sender']['relationship_score']:.1f}/1.0
- Your current workload: {context['agent']['workload']['utilization']:.1f}x capacity
- Your stress level: {context['agent']['stress_level']:.1f}/1.0
- Your current state: {context['agent']['current_state']}

Based on your personality, role, and current situation, how would you respond?

Provide your response in JSON format:
{{
    "response_type": "take_action|ignore|seek_clarification|provide_feedback|escalate|delegate",
    "content": "Your actual response message",
    "reasoning": "Why you chose this response",
    "sentiment": 0.5,  // -1 (negative) to 1 (positive)
    "confidence": 0.8,  // 0 to 1
    "action_taken": true,  // Will you actually do something?
    "estimated_hours": 4  // If action_taken, how many hours to complete?
}}
"""
        
        try:
            # Use MCP chat completion
            ai_response = await self.mcp_client.use_tool("chat_completion", {
                "messages": [
                    {"role": "system", "content": "You are simulating a realistic employee response to workplace communication."},
                    {"role": "user", "content": reasoning_prompt}
                ],
                "model": "gpt-4",
                "temperature": 0.7,  # Some randomness for realistic variation
                "max_tokens": 500
            })
            
            # Parse JSON response
            response_text = ai_response.get("content", "")
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return None
    
    def _create_persona_prompt(self, agent_info: Dict[str, Any]) -> str:
        """Create a detailed persona prompt for the AI."""
        
        return f"""
You are {agent_info['name']}, a {agent_info['role']} in the {agent_info['department']} department.

Your personality:
{agent_info['personality']}

Your professional context:
- Seniority level: {agent_info['seniority_level']}/5
- Expertise: {', '.join(agent_info['expertise_areas'])}
- Current workload: {agent_info['workload']['utilization']:.1f}x your normal capacity
- Stress level: {agent_info['stress_level']:.1f}/1.0 (where 1.0 is maximum stress)

You should respond authentically as this person would, considering:
- Your personality traits and communication style
- Your current workload and stress level
- Your role and responsibilities
- Your relationship with the person contacting you
- The priority and type of communication
"""
    
    def _describe_personality(self, personality) -> str:
        """Convert personality traits to natural language description."""
        
        traits = []
        
        risk_tolerance = personality.get_trait(PersonalityTrait.RISK_TOLERANCE)
        if risk_tolerance > 0.7:
            traits.append("You're comfortable taking risks and trying new approaches")
        elif risk_tolerance < 0.3:
            traits.append("You prefer proven methods and are cautious about risks")
        
        authority_response = personality.get_trait(PersonalityTrait.AUTHORITY_RESPONSE)
        if authority_response > 0.7:
            traits.append("You generally follow directions from leadership")
        elif authority_response < 0.3:
            traits.append("You tend to question authority and think independently")
        
        communication_style = personality.get_trait(PersonalityTrait.COMMUNICATION_STYLE)
        if communication_style > 0.7:
            traits.append("You communicate directly and assertively")
        elif communication_style < 0.3:
            traits.append("You prefer diplomatic and tactful communication")
        
        change_adaptability = personality.get_trait(PersonalityTrait.CHANGE_ADAPTABILITY)
        if change_adaptability > 0.7:
            traits.append("You adapt quickly to changes and new situations")
        elif change_adaptability < 0.3:
            traits.append("You prefer stability and are resistant to change")
        
        workload_sensitivity = personality.get_trait(PersonalityTrait.WORKLOAD_SENSITIVITY)
        if workload_sensitivity > 0.7:
            traits.append("You become stressed easily when workload increases")
        elif workload_sensitivity < 0.3:
            traits.append("You handle high workloads well without much stress")
        
        collaboration_preference = personality.get_trait(PersonalityTrait.COLLABORATION_PREFERENCE)
        if collaboration_preference > 0.7:
            traits.append("You enjoy working with others and value teamwork")
        elif collaboration_preference < 0.3:
            traits.append("You prefer working independently")
        
        return "- " + "\n- ".join(traits)
    
    def _structure_ai_response(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        ai_response: Dict[str, Any]
    ) -> AgentResponse:
        """Convert AI response to structured AgentResponse."""
        
        # Map response type string to enum
        response_type_map = {
            "take_action": ResponseType.TAKE_ACTION,
            "ignore": ResponseType.IGNORE,
            "seek_clarification": ResponseType.SEEK_CLARIFICATION,
            "provide_feedback": ResponseType.PROVIDE_FEEDBACK,
            "escalate": ResponseType.ESCALATE,
            "delegate": ResponseType.DELEGATE,
        }
        
        response_type = response_type_map.get(
            ai_response.get("response_type", "ignore"),
            ResponseType.IGNORE
        )
        
        # Calculate completion time if action is taken
        completion_time = None
        if ai_response.get("action_taken", False) and ai_response.get("estimated_hours"):
            from datetime import timedelta
            completion_time = datetime.now() + timedelta(hours=ai_response["estimated_hours"])
        
        return AgentResponse(
            agent_id=agent.id,
            communication_id=communication.id,
            response_type=response_type,
            content=ai_response.get("content", ""),
            sentiment=float(ai_response.get("sentiment", 0.0)),
            confidence=float(ai_response.get("confidence", 0.5)),
            action_taken=ai_response.get("action_taken", False),
            estimated_completion_time=completion_time,
            metadata={
                "ai_reasoning": ai_response.get("reasoning", ""),
                "ai_generated": True,
                "model_used": "gpt-4"
            }
        )
    
    async def _update_agent_with_ai_insights(
        self,
        agent: SimulationAgent,
        communication: PriorityCommunication,
        response: AgentResponse
    ) -> None:
        """Update agent state with AI-generated insights."""
        
        # Standard updates (same as rule-based system)
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "communication_id": communication.id,
            "sender_id": communication.sender_id,
            "response_type": response.response_type.value,
            "sentiment": response.sentiment,
            "ai_generated": True,
            "reasoning": response.metadata.get("ai_reasoning", "")
        }
        agent.memory.interaction_history.append(interaction)
        
        # AI-enhanced updates
        if response.response_type == ResponseType.TAKE_ACTION:
            # AI can provide more nuanced workload estimates
            estimated_hours = response.metadata.get("estimated_hours", 4)
            workload_increase = estimated_hours / 40  # Convert hours to workload units
            agent.professional.current_workload += workload_increase
        
        # Use AI to assess stress impact more realistically
        try:
            stress_assessment = await self.mcp_client.use_tool("chat_completion", {
                "messages": [{
                    "role": "user",
                    "content": f"""
                    An employee with stress level {agent.memory.stress_level:.2f} just {response.response_type.value} 
                    to a priority {communication.priority_level} communication. 
                    How should their stress level change? Respond with just a number between -0.1 and 0.2.
                    """
                }],
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 10
            })
            
            stress_change = float(stress_assessment.get("content", "0.05"))
            agent.memory.stress_level = max(0.0, min(1.0, agent.memory.stress_level + stress_change))
            
        except Exception as e:
            logger.warning(f"AI stress assessment failed, using default: {e}")
            # Fallback to rule-based stress update
            if response.response_type == ResponseType.TAKE_ACTION:
                agent.memory.stress_level += 0.1
        
        agent.memory.last_updated = datetime.now()
    
    async def generate_proactive_communication(
        self,
        agent: SimulationAgent,
        all_agents: Dict[str, SimulationAgent]
    ) -> Optional[PriorityCommunication]:
        """Use AI to generate proactive communications from agents."""
        
        context = {
            "agent": agent.to_dict(),
            "recent_interactions": agent.memory.interaction_history[-5:],
            "stress_level": agent.memory.stress_level,
            "workload_utilization": agent.professional.current_workload / agent.professional.workload_capacity
        }
        
        prompt = f"""
        You are {agent.name}, a {agent.professional.role}. Based on your recent interactions and current state,
        would you proactively reach out to anyone in your organization today?
        
        Consider:
        - Your current stress level: {agent.memory.stress_level:.2f}/1.0
        - Your workload: {context['workload_utilization']:.1f}x capacity
        - Recent interactions: {len(agent.memory.interaction_history)} total
        
        If yes, respond with JSON:
        {{
            "should_communicate": true,
            "recipient_role": "manager|peer|direct_report",
            "communication_type": "status_update|request_help|provide_update|escalate_issue",
            "content": "Your message",
            "priority": 1-5,
            "reasoning": "Why you're reaching out"
        }}
        
        If no, respond with: {{"should_communicate": false}}
        """
        
        try:
            ai_response = await self.mcp_client.use_tool("chat_completion", {
                "messages": [{"role": "user", "content": prompt}],
                "model": "gpt-3.5-turbo",
                "temperature": 0.8,
                "max_tokens": 300
            })
            
            response_data = json.loads(ai_response.get("content", "{}"))
            
            if not response_data.get("should_communicate", False):
                return None
            
            # Find appropriate recipient
            recipient_id = self._find_recipient(agent, response_data["recipient_role"], all_agents)
            if not recipient_id:
                return None
            
            # Create proactive communication
            from ..domain.models import CommunicationType
            comm_type_map = {
                "status_update": CommunicationType.STATUS_UPDATE,
                "request_help": CommunicationType.REQUEST,
                "provide_update": CommunicationType.INFORMATION_SHARING,
                "escalate_issue": CommunicationType.ESCALATION
            }
            
            return PriorityCommunication(
                sender_id=agent.id,
                recipient_id=recipient_id,
                content=response_data["content"],
                type=comm_type_map.get(response_data["communication_type"], CommunicationType.INFORMATION_SHARING),
                priority_level=response_data.get("priority", 3),
                timestamp=datetime.now(),
                metadata={
                    "ai_generated": True,
                    "proactive": True,
                    "reasoning": response_data.get("reasoning", "")
                }
            )
            
        except Exception as e:
            logger.error(f"Proactive communication generation failed: {e}")
            return None
    
    def _find_recipient(
        self,
        agent: SimulationAgent,
        recipient_role: str,
        all_agents: Dict[str, SimulationAgent]
    ) -> Optional[str]:
        """Find appropriate recipient based on role relationship."""
        
        if recipient_role == "manager" and agent.professional.manager_id:
            return agent.professional.manager_id
        elif recipient_role == "direct_report" and agent.professional.direct_reports:
            import random
            return random.choice(agent.professional.direct_reports)
        elif recipient_role == "peer":
            # Find peer in same department
            peers = [
                other_agent.id for other_agent in all_agents.values()
                if (other_agent.professional.department == agent.professional.department and
                    other_agent.id != agent.id and
                    other_agent.professional.seniority_level == agent.professional.seniority_level)
            ]
            if peers:
                import random
                return random.choice(peers)
        
        return None
