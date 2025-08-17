"""Strategic intelligence service for processing market intelligence into organizational insights and strategic truths."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import time

from .intelligence_models import (
    OrganizationalTruth, CompiledReport, CommunicationQueue,
    PromptTemplate, IntelligenceRequest, IntelligenceResponse,
    TruthQuery, CommunicationQuery, EscalationRule,
    TruthCategory, ImpactLevel, AnalysisDepth, PriorityLevel,
    CommunicationType, StrategicAlignmentScorecard, StrategicAlignmentKPI,
    StrategicAlignmentZone, StrategicAlignmentQuery
)
from .agent_models import AgentResult, AgentResultQuery
from .agent_service import AgentService

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Service for generating strategic intelligence from market intelligence data."""
    
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service
        self.templates: Dict[str, PromptTemplate] = {}
        self.truths_cache: Dict[str, OrganizationalTruth] = {}
        self.communication_queue: List[CommunicationQueue] = []
        self.escalation_rules: List[EscalationRule] = []
        self.alignment_scorecards: Dict[str, StrategicAlignmentScorecard] = {}
        self.alignment_kpis: Dict[str, StrategicAlignmentKPI] = {}
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates."""
        default_templates = [
            PromptTemplate(
                id="ceo_strategic_truths",
                name="Strategic Truths for CEO",
                description="Extract fundamental strategic truths from agent results",
                role="ceo",
                category="strategic",
                template="""Analyze the following agent results and extract 3-5 fundamental truths that impact our strategic position:

{agent_results}

Focus on:
- Market trends and competitive movements
- Technology adoption patterns
- Regulatory or social changes
- Financial or operational implications

Format each truth as a clear, actionable statement with confidence level and evidence count.""",
                variables=["agent_results", "industry", "company_size"],
                analysis_depth="weekly",
                output_format="truth"
            ),
            PromptTemplate(
                id="cto_technology_trends",
                name="Technology Trends for CTO",
                description="Identify technology trends and their implications",
                role="cto",
                category="technology",
                template="""From the following agent results, identify emerging technology trends relevant to our industry:

{agent_results}

Analyze:
- Early adopters and their use cases
- Technology maturity and adoption readiness
- Potential impact on our technology stack
- Security and scalability considerations

Provide specific insights and recommendations.""",
                variables=["agent_results", "industry"],
                analysis_depth="weekly",
                output_format="report"
            ),
            PromptTemplate(
                id="daily_critical_alerts",
                name="Daily Critical Alerts",
                description="Identify urgent issues requiring immediate attention",
                role="all",
                category="operational",
                template="""Review the following agent results for critical issues requiring immediate attention:

{agent_results}

Identify:
- Breaking news affecting our business
- Competitive threats or opportunities
- Regulatory changes with immediate impact
- Market disruptions or opportunities

Focus only on high-priority items that need action today.""",
                variables=["agent_results"],
                analysis_depth="daily",
                output_format="insight"
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
    
    async def generate_intelligence(self, request: IntelligenceRequest) -> IntelligenceResponse:
        """Generate strategic intelligence from market intelligence data using specified template."""
        start_time = time.time()
        
        try:
            # Get agent results
            agent_results = await self._get_agent_results(request.agent_ids, request.tenant_id)
            
            # Get template
            template = self.templates.get(request.template_id)
            if not template:
                raise ValueError(f"Template {request.template_id} not found")
            
            # Generate prompt
            prompt = self._build_prompt(template, agent_results, request.variables)
            
            # Process with LLM (simulated for now)
            llm_response = await self._process_with_llm(prompt, template.output_format, request.analysis_depth)
            
            # Extract truths and reports
            truths = await self._extract_truths(llm_response, request.tenant_id, template.category)
            reports = await self._extract_reports(llm_response, request.tenant_id, template)
            
            # Generate communications
            communications = await self._generate_communications(
                truths, reports, request.tenant_id, template.role
            )
            
            # Store results
            await self._store_intelligence(truths, reports, communications)
            
            processing_time = time.time() - start_time
            
            return IntelligenceResponse(
                request_id=request.id,
                truths=truths,
                reports=reports,
                communications=communications,
                processing_time_seconds=processing_time,
                token_count=len(prompt.split())  # Simplified token counting
            )
            
        except Exception as e:
            logger.error(f"Error generating intelligence: {e}")
            raise
    
    async def _get_agent_results(self, agent_ids: List[str], tenant_id: str) -> List[AgentResult]:
        """Get market intelligence data for analysis."""
        all_results = []
        
        for agent_id in agent_ids:
            # Get results from agent service
            results = await self.agent_service.get_agent_results(
                query=AgentResultQuery(
                    agent_id=agent_id,
                    tenant_id=tenant_id,
                    limit=50
                )
            )
            all_results.extend(results)
        
        return all_results
    
    def _build_prompt(self, template: PromptTemplate, agent_results: List[AgentResult], variables: Dict[str, Any]) -> str:
        """Build prompt from template and agent results."""
        # Convert agent results to text
        results_text = self._format_agent_results(agent_results)
        
        # Replace variables in template
        prompt = template.template
        prompt = prompt.replace("{agent_results}", results_text)
        
        for var_name, var_value in variables.items():
            prompt = prompt.replace(f"{{{var_name}}}", str(var_value))
        
        return prompt
    
    def _format_agent_results(self, results: List[AgentResult]) -> str:
        """Format market intelligence data for prompt inclusion."""
        formatted = []
        
        for result in results:
            formatted.append(f"""
Source: {result.source_name}
Title: {result.title}
Content: {result.content}
Keywords: {', '.join(result.keywords_matched)}
Sentiment: {result.sentiment}
Published: {result.published_at}
""")
        
        return "\n".join(formatted)
    
    async def _process_with_llm(self, prompt: str, output_format: str, analysis_depth: AnalysisDepth) -> str:
        """Process prompt with LLM (simulated for now)."""
        # This would integrate with OpenAI or other LLM service
        # For now, return simulated response
        
        if output_format == "truth":
            return """
TRUTHS:
1. AI adoption accelerating in finance sector (confidence: 0.85, evidence: 12)
2. Cloud costs rising 15% year-over-year (confidence: 0.78, evidence: 8)
3. Competitor X struggling with legacy system migration (confidence: 0.92, evidence: 5)
"""
        elif output_format == "report":
            return """
REPORT: Technology Trends Analysis
SUMMARY: Emerging AI and cloud technologies are reshaping the financial sector.

INSIGHTS:
- Early adopters seeing 30% efficiency gains
- Security concerns remain primary barrier
- Integration complexity underestimated

RECOMMENDATIONS:
- Accelerate AI pilot programs
- Strengthen cloud security posture
- Invest in integration expertise
"""
        else:
            return """
CRITICAL ALERTS:
- Major competitor launching AI-powered product next month
- Regulatory changes affecting data privacy requirements
- Market volatility impacting customer spending patterns
"""
    
    async def _extract_truths(self, llm_response: str, tenant_id: str, category: str) -> List[OrganizationalTruth]:
        """Extract strategic insights from LLM response."""
        truths = []
        
        # Parse LLM response for truths (simplified parsing)
        if "TRUTHS:" in llm_response:
            truths_section = llm_response.split("TRUTHS:")[1].split("\n")
            
            for line in truths_section:
                if line.strip() and line[0].isdigit():
                    # Parse truth statement
                    parts = line.split("(confidence:")
                    if len(parts) == 2:
                        statement = parts[0].split(". ", 1)[1].strip()
                        confidence_part = parts[1].split(")")[0]
                        confidence = float(confidence_part.split(":")[1].strip())
                        evidence = int(confidence_part.split("evidence:")[1].strip())
                        
                        truth = OrganizationalTruth(
                            statement=statement,
                            confidence=confidence,
                            evidence_count=evidence,
                            category=TruthCategory(category),
                            impact_level=self._assess_impact_level(confidence, evidence),
                            tenant_id=tenant_id
                        )
                        truths.append(truth)
        
        return truths
    
    async def _extract_reports(self, llm_response: str, tenant_id: str, template: PromptTemplate) -> List[CompiledReport]:
        """Extract strategic analysis reports from LLM response."""
        reports = []
        
        if "REPORT:" in llm_response:
            # Parse report structure
            report_section = llm_response.split("REPORT:")[1]
            
            # Extract title and summary
            lines = report_section.split("\n")
            title = lines[0].strip()
            summary = ""
            
            for line in lines[1:]:
                if line.startswith("SUMMARY:"):
                    summary = line.split("SUMMARY:")[1].strip()
                    break
            
            # Extract insights and recommendations
            insights = []
            recommendations = []
            
            in_insights = False
            in_recommendations = False
            
            for line in lines:
                if line.startswith("INSIGHTS:"):
                    in_insights = True
                    in_recommendations = False
                    continue
                elif line.startswith("RECOMMENDATIONS:"):
                    in_insights = False
                    in_recommendations = True
                    continue
                elif line.strip() and (in_insights or in_recommendations):
                    if in_insights:
                        insights.append(line.strip())
                    elif in_recommendations:
                        recommendations.append(line.strip())
            
            report = CompiledReport(
                title=title,
                summary=summary,
                insights=insights,
                recommendations=recommendations,
                analysis_depth=AnalysisDepth(template.analysis_depth),
                tenant_id=tenant_id,
                priority=self._assess_report_priority(insights, recommendations)
            )
            reports.append(report)
        
        return reports
    
    async def _generate_communications(
        self, 
        truths: List[OrganizationalTruth], 
        reports: List[CompiledReport], 
        tenant_id: str, 
        target_role: str
    ) -> List[CommunicationQueue]:
        """Generate priority communications for relevant users."""
        communications = []
        
        # Get users with target role
        users = await self._get_users_by_role(tenant_id, target_role)
        
        for user in users:
            # Generate communication based on truths and reports
            for truth in truths:
                if truth.impact_level in [ImpactLevel.HIGH, ImpactLevel.CRITICAL]:
                    communication = CommunicationQueue(
                        user_id=user.id,
                        tenant_id=tenant_id,
                        topic=f"Strategic Truth: {truth.statement[:50]}...",
                        content=f"New strategic insight: {truth.statement}\nConfidence: {truth.confidence:.1%}\nEvidence: {truth.evidence_count} sources",
                        type=CommunicationType.NUDGE,
                        priority=self._calculate_priority(truth.impact_level),
                        related_truths=[truth.id],
                        scheduled_for=datetime.utcnow() + timedelta(hours=1)
                    )
                    communications.append(communication)
            
            for report in reports:
                if report.priority in [PriorityLevel.HIGH, PriorityLevel.URGENT]:
                    communication = CommunicationQueue(
                        user_id=user.id,
                        tenant_id=tenant_id,
                        topic=f"Report: {report.title}",
                        content=f"New analysis report: {report.summary}\nKey insights: {len(report.insights)} items\nRecommendations: {len(report.recommendations)} actions",
                        type=CommunicationType.RECOMMENDATION,
                        priority=self._calculate_priority(report.priority),
                        source_report=report.id,
                        scheduled_for=datetime.utcnow() + timedelta(hours=2)
                    )
                    communications.append(communication)
        
        return communications
    
    async def _store_intelligence(
        self, 
        truths: List[OrganizationalTruth], 
        reports: List[CompiledReport], 
        communications: List[CommunicationQueue]
    ):
        """Store strategic intelligence results."""
        # Store truths
        for truth in truths:
            self.truths_cache[truth.id] = truth
        
        # Store communications in queue
        self.communication_queue.extend(communications)
        
        # Sort queue by priority and scheduled time
        self.communication_queue.sort(key=lambda x: (x.priority, x.scheduled_for), reverse=True)
        
        logger.info(f"Stored {len(truths)} strategic insights, {len(reports)} reports, {len(communications)} priority communications")
    
    def _assess_impact_level(self, confidence: float, evidence: int) -> ImpactLevel:
        """Assess impact level based on confidence and evidence."""
        if confidence >= 0.9 and evidence >= 10:
            return ImpactLevel.CRITICAL
        elif confidence >= 0.8 and evidence >= 5:
            return ImpactLevel.HIGH
        elif confidence >= 0.6 and evidence >= 3:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _assess_report_priority(self, insights: List[str], recommendations: List[str]) -> PriorityLevel:
        """Assess report priority based on content."""
        total_items = len(insights) + len(recommendations)
        
        if total_items >= 8:
            return PriorityLevel.URGENT
        elif total_items >= 5:
            return PriorityLevel.HIGH
        elif total_items >= 3:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
    
    def _calculate_priority(self, impact_level: ImpactLevel) -> int:
        """Calculate numeric priority from impact level."""
        priority_map = {
            ImpactLevel.CRITICAL: 10,
            ImpactLevel.HIGH: 8,
            ImpactLevel.MEDIUM: 5,
            ImpactLevel.LOW: 3
        }
        return priority_map.get(impact_level, 5)
    
    async def _get_users_by_role(self, tenant_id: str, role: str) -> List[Any]:
        """Get users by role (simplified for now)."""
        # This would query the user database
        # For now, return mock users
        return [
            {"id": f"user_{role}_1", "role": role},
            {"id": f"user_{role}_2", "role": role}
        ]
    
    async def get_truths(self, query: TruthQuery) -> List[OrganizationalTruth]:
        """Get strategic insights based on query criteria."""
        truths = list(self.truths_cache.values())
        
        # Apply filters
        if query.categories:
            truths = [t for t in truths if t.category in query.categories]
        
        if query.impact_levels:
            truths = [t for t in truths if t.impact_level in query.impact_levels]
        
        if query.confidence_min:
            truths = [t for t in truths if t.confidence >= query.confidence_min]
        
        if query.date_from:
            truths = [t for t in truths if t.created_at >= query.date_from]
        
        if query.date_to:
            truths = [t for t in truths if t.created_at <= query.date_to]
        
        # Sort by confidence and limit
        truths.sort(key=lambda x: x.confidence, reverse=True)
        return truths[query.offset:query.offset + query.limit]
    
    async def get_communications(self, query: CommunicationQuery) -> List[CommunicationQueue]:
        """Get priority communications for a user."""
        user_communications = [
            c for c in self.communication_queue 
            if c.user_id == query.user_id and c.tenant_id == query.tenant_id
        ]
        
        # Apply filters
        if query.types:
            user_communications = [c for c in user_communications if c.type in query.types]
        
        if query.priority_min:
            user_communications = [c for c in user_communications if c.priority >= query.priority_min]
        
        if query.delivered is not None:
            user_communications = [c for c in user_communications if c.delivered == query.delivered]
        
        if query.acknowledged is not None:
            user_communications = [c for c in user_communications if c.acknowledged == query.acknowledged]
        
        # Sort by priority and scheduled time
        user_communications.sort(key=lambda x: (x.priority, x.scheduled_for), reverse=True)
        return user_communications[query.offset:query.offset + query.limit]
    
    async def acknowledge_communication(self, communication_id: str, user_id: str) -> bool:
        """Mark a priority communication as acknowledged."""
        for comm in self.communication_queue:
            if comm.id == communication_id and comm.user_id == user_id:
                comm.acknowledged = True
                comm.acknowledged_at = datetime.utcnow()
                return True
        return False
    
    async def process_escalations(self):
        """Process escalation rules for communications."""
        for comm in self.communication_queue:
            if not comm.acknowledged and comm.attempts >= 4:
                # Apply escalation rules
                if comm.type == CommunicationType.NUDGE:
                    comm.type = CommunicationType.RECOMMENDATION
                    comm.escalation_level = 1
                    comm.priority = min(10, comm.priority + 2)
                elif comm.type == CommunicationType.RECOMMENDATION and comm.attempts >= 6:
                    comm.type = CommunicationType.ORDER
                    comm.escalation_level = 2
                    comm.priority = 10
        
        logger.info("Processed escalations for priority communications")

    async def calculate_strategic_alignment_scorecard(self, tenant_id: str) -> StrategicAlignmentScorecard:
        """Calculate comprehensive strategic alignment scorecard for an organization."""
        
        # Calculate individual KPIs
        alignment_kpis = await self._calculate_alignment_kpis(tenant_id)
        execution_kpis = await self._calculate_execution_kpis(tenant_id)
        
        # Calculate overall scores
        alignment_score = sum(kpi.current_value for kpi in alignment_kpis) / len(alignment_kpis)
        execution_score = sum(kpi.current_value for kpi in execution_kpis) / len(execution_kpis)
        overall_score = (alignment_score + execution_score) / 2
        
        # Determine alignment zone
        if overall_score >= 80:
            alignment_zone = StrategicAlignmentZone.GREEN
        elif overall_score >= 60:
            alignment_zone = StrategicAlignmentZone.YELLOW
        else:
            alignment_zone = StrategicAlignmentZone.RED
        
        # Calculate strategic velocity (speed of strategic execution)
        strategic_velocity = await self._calculate_strategic_velocity(tenant_id)
        
        # Generate risk indicators and priority interventions
        risk_indicators = await self._identify_risk_indicators(tenant_id, alignment_kpis, execution_kpis)
        priority_interventions = await self._generate_priority_interventions(tenant_id, risk_indicators)
        
        # Create scorecard
        scorecard = StrategicAlignmentScorecard(
            tenant_id=tenant_id,
            measurement_date=datetime.utcnow(),
            strategic_initiative_velocity=alignment_kpis[0].current_value if alignment_kpis else 0.0,
            goal_cascade_alignment=alignment_kpis[1].current_value if len(alignment_kpis) > 1 else 0.0,
            decision_strategy_consistency=alignment_kpis[2].current_value if len(alignment_kpis) > 2 else 0.0,
            resource_allocation_efficiency=alignment_kpis[3].current_value if len(alignment_kpis) > 3 else 0.0,
            strategic_response_time=execution_kpis[0].current_value if execution_kpis else 0.0,
            cross_functional_alignment=execution_kpis[1].current_value if len(execution_kpis) > 1 else 0.0,
            strategic_communication_effectiveness=execution_kpis[2].current_value if len(execution_kpis) > 2 else 0.0,
            adaptation_speed=execution_kpis[3].current_value if len(execution_kpis) > 3 else 0.0,
            overall_alignment_score=overall_score,
            alignment_zone=alignment_zone,
            strategic_velocity=strategic_velocity,
            risk_indicators=risk_indicators,
            priority_interventions=priority_interventions
        )
        
        # Store scorecard
        self.alignment_scorecards[scorecard.id] = scorecard
        
        logger.info(f"Calculated strategic alignment scorecard for tenant {tenant_id}: {overall_score:.1f}% ({alignment_zone.value})")
        return scorecard

    async def _calculate_alignment_kpis(self, tenant_id: str) -> List[StrategicAlignmentKPI]:
        """Calculate alignment KPIs based on organizational data."""
        kpis = []
        
        # 1. Strategic Initiative Velocity
        initiative_velocity = await self._calculate_initiative_velocity(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Strategic Initiative Velocity",
            kpi_category="alignment",
            current_value=initiative_velocity,
            calculation_method="Percentage of strategic projects on track"
        ))
        
        # 2. Goal Cascade Alignment
        goal_alignment = await self._calculate_goal_cascade_alignment(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Goal Cascade Alignment",
            kpi_category="alignment",
            current_value=goal_alignment,
            calculation_method="Percentage of team goals linked to strategic objectives"
        ))
        
        # 3. Decision-Strategy Consistency
        decision_consistency = await self._calculate_decision_consistency(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Decision-Strategy Consistency",
            kpi_category="alignment",
            current_value=decision_consistency,
            calculation_method="Percentage of major decisions aligned with strategy"
        ))
        
        # 4. Resource Allocation Efficiency
        resource_efficiency = await self._calculate_resource_efficiency(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Resource Allocation Efficiency",
            kpi_category="alignment",
            current_value=resource_efficiency,
            calculation_method="Percentage of budget spent on strategic priorities"
        ))
        
        return kpis

    async def _calculate_execution_kpis(self, tenant_id: str) -> List[StrategicAlignmentKPI]:
        """Calculate execution KPIs based on organizational data."""
        kpis = []
        
        # 1. Strategic Response Time
        response_time = await self._calculate_strategic_response_time(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Strategic Response Time",
            kpi_category="execution",
            current_value=response_time,
            calculation_method="Days to respond to strategic opportunities"
        ))
        
        # 2. Cross-Functional Alignment
        cross_functional = await self._calculate_cross_functional_alignment(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Cross-Functional Alignment",
            kpi_category="execution",
            current_value=cross_functional,
            calculation_method="Percentage of departments working toward same goals"
        ))
        
        # 3. Strategic Communication Effectiveness
        communication_effectiveness = await self._calculate_communication_effectiveness(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Strategic Communication Effectiveness",
            kpi_category="execution",
            current_value=communication_effectiveness,
            calculation_method="Percentage of strategic messages understood"
        ))
        
        # 4. Adaptation Speed
        adaptation_speed = await self._calculate_adaptation_speed(tenant_id)
        kpis.append(StrategicAlignmentKPI(
            tenant_id=tenant_id,
            kpi_name="Adaptation Speed",
            kpi_category="execution",
            current_value=adaptation_speed,
            calculation_method="Time to pivot strategy based on market changes"
        ))
        
        return kpis

    async def _calculate_initiative_velocity(self, tenant_id: str) -> float:
        """Calculate strategic initiative velocity (simulated)."""
        # This would analyze project management data
        # For now, return a simulated value
        return 75.0  # 75% of strategic projects on track

    async def _calculate_goal_cascade_alignment(self, tenant_id: str) -> float:
        """Calculate goal cascade alignment (simulated)."""
        # This would analyze goal-setting and tracking data
        return 68.0  # 68% of team goals linked to strategic objectives

    async def _calculate_decision_consistency(self, tenant_id: str) -> float:
        """Calculate decision-strategy consistency (simulated)."""
        # This would analyze decision-making patterns
        return 82.0  # 82% of major decisions aligned with strategy

    async def _calculate_resource_efficiency(self, tenant_id: str) -> float:
        """Calculate resource allocation efficiency (simulated)."""
        # This would analyze budget allocation data
        return 71.0  # 71% of budget spent on strategic priorities

    async def _calculate_strategic_response_time(self, tenant_id: str) -> float:
        """Calculate strategic response time (simulated)."""
        # This would analyze response times to strategic opportunities
        # Convert days to a 0-100 scale (lower days = higher score)
        avg_days = 3.5  # Average 3.5 days to respond
        return max(0, 100 - (avg_days * 10))  # 65% score

    async def _calculate_cross_functional_alignment(self, tenant_id: str) -> float:
        """Calculate cross-functional alignment (simulated)."""
        # This would analyze inter-departmental collaboration
        return 73.0  # 73% of departments working toward same goals

    async def _calculate_communication_effectiveness(self, tenant_id: str) -> float:
        """Calculate strategic communication effectiveness (simulated)."""
        # This would analyze communication tracking data
        return 79.0  # 79% of strategic messages understood

    async def _calculate_adaptation_speed(self, tenant_id: str) -> float:
        """Calculate adaptation speed (simulated)."""
        # This would analyze time to implement strategic changes
        avg_weeks = 4.2  # Average 4.2 weeks to adapt
        return max(0, 100 - (avg_weeks * 5))  # 79% score

    async def _calculate_strategic_velocity(self, tenant_id: str) -> float:
        """Calculate strategic velocity (speed of strategic execution)."""
        # This would analyze the speed of strategic execution
        return 76.0  # 76% strategic velocity

    async def _identify_risk_indicators(self, tenant_id: str, alignment_kpis: List[StrategicAlignmentKPI], execution_kpis: List[StrategicAlignmentKPI]) -> List[str]:
        """Identify risk indicators based on KPI analysis."""
        risks = []
        
        for kpi in alignment_kpis + execution_kpis:
            if kpi.current_value < 60:
                risks.append(f"Low {kpi.kpi_name}: {kpi.current_value:.1f}%")
            elif kpi.current_value < 70:
                risks.append(f"Moderate {kpi.kpi_name}: {kpi.current_value:.1f}%")
        
        return risks

    async def _generate_priority_interventions(self, tenant_id: str, risk_indicators: List[str]) -> List[str]:
        """Generate priority interventions based on risk indicators."""
        interventions = []
        
        if any("Strategic Initiative Velocity" in risk for risk in risk_indicators):
            interventions.append("Review and accelerate strategic project timelines")
        
        if any("Goal Cascade Alignment" in risk for risk in risk_indicators):
            interventions.append("Strengthen goal-setting process and alignment")
        
        if any("Cross-Functional Alignment" in risk for risk in risk_indicators):
            interventions.append("Improve inter-departmental collaboration and communication")
        
        if any("Strategic Communication Effectiveness" in risk for risk in risk_indicators):
            interventions.append("Enhance strategic messaging and communication channels")
        
        return interventions

    async def get_strategic_alignment_scorecard(self, query: StrategicAlignmentQuery) -> StrategicAlignmentScorecard:
        """Get strategic alignment scorecard for a tenant."""
        # For now, calculate a new scorecard
        # In production, this would retrieve from database with caching
        return await self.calculate_strategic_alignment_scorecard(query.tenant_id)

    async def get_strategic_alignment_history(self, query: StrategicAlignmentQuery) -> List[StrategicAlignmentScorecard]:
        """Get historical strategic alignment data."""
        # This would query historical scorecard data
        # For now, return current scorecard
        current_scorecard = await self.calculate_strategic_alignment_scorecard(query.tenant_id)
        return [current_scorecard]
