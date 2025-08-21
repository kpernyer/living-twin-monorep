"""
GraphQL resolvers for Living Twin Strategic Intelligence Platform.

These resolvers act as a facade over the existing domain services,
providing GraphQL access to the same functionality as the REST API.
"""
import strawberry
from datetime import datetime
from typing import List, Optional

from ..domain.intelligence_service import IntelligenceService
from ..domain.agent_service import AgentService
from ..domain.intelligence_models import TruthQuery, CommunicationQuery, IntelligenceRequest
from ..adapters.firebase_auth import get_current_user, get_current_tenant
from ..routers.health import health_checker
from .. import di

from .types import (
    OrganizationalTruth,
    CommunicationQueue,
    CompiledReport,
    StrategicAlignmentScorecard,
    DocumentInfo,
    QueryResult,
    SystemHealth,
    StrategicIntelligenceDashboard,
    TruthsFilter,
    CommunicationsFilter,
    DocumentQueryInput,
    IntelligenceGenerationInput,
    IntelligenceGenerationResponse,
    TruthCategory,
    ImpactLevel,
    CommunicationType,
    AnalysisDepth,
    StrategicAlignmentZone,
)


def _convert_domain_truth_to_graphql(domain_truth) -> OrganizationalTruth:
    """Convert domain OrganizationalTruth to GraphQL type."""
    return OrganizationalTruth(
        id=domain_truth.id,
        statement=domain_truth.statement,
        confidence=domain_truth.confidence,
        evidence_count=domain_truth.evidence_count,
        last_updated=domain_truth.last_updated,
        version=domain_truth.version,
        category=TruthCategory(domain_truth.category.value),
        impact_level=ImpactLevel(domain_truth.impact_level.value),
        tenant_id=domain_truth.tenant_id,
        created_at=domain_truth.created_at,
        strategic_goals=domain_truth.strategic_goals,
        related_truths=domain_truth.related_truths,
        metadata=domain_truth.metadata,
    )


def _convert_domain_communication_to_graphql(domain_comm) -> CommunicationQueue:
    """Convert domain CommunicationQueue to GraphQL type."""
    return CommunicationQueue(
        id=domain_comm.id,
        user_id=domain_comm.user_id,
        tenant_id=domain_comm.tenant_id,
        topic=domain_comm.topic,
        content=domain_comm.content,
        type=CommunicationType(domain_comm.type.value),
        priority=domain_comm.priority,
        created_at=domain_comm.created_at,
        scheduled_for=domain_comm.scheduled_for,
        attempts=domain_comm.attempts,
        escalation_level=domain_comm.escalation_level,
        related_truths=domain_comm.related_truths,
        related_goals=domain_comm.related_goals,
        source_report=domain_comm.source_report,
        delivered=domain_comm.delivered,
        acknowledged=domain_comm.acknowledged,
        acknowledged_at=domain_comm.acknowledged_at,
        metadata=domain_comm.metadata,
    )


def _convert_domain_report_to_graphql(domain_report) -> CompiledReport:
    """Convert domain CompiledReport to GraphQL type."""
    return CompiledReport(
        id=domain_report.id,
        title=domain_report.title,
        summary=domain_report.summary,
        insights=domain_report.insights,
        recommendations=domain_report.recommendations,
        data_sources=domain_report.data_sources,
        analysis_depth=AnalysisDepth(domain_report.analysis_depth.value),
        tenant_id=domain_report.tenant_id,
        created_at=domain_report.created_at,
        expires_at=domain_report.expires_at,
        priority=domain_report.priority,
        related_truths=domain_report.related_truths,
        agent_results=domain_report.agent_results,
        metadata=domain_report.metadata,
    )


def _convert_domain_scorecard_to_graphql(domain_scorecard) -> StrategicAlignmentScorecard:
    """Convert domain StrategicAlignmentScorecard to GraphQL type."""
    return StrategicAlignmentScorecard(
        id=domain_scorecard.id,
        tenant_id=domain_scorecard.tenant_id,
        measurement_date=domain_scorecard.measurement_date,
        strategic_initiative_velocity=domain_scorecard.strategic_initiative_velocity,
        goal_cascade_alignment=domain_scorecard.goal_cascade_alignment,
        decision_strategy_consistency=domain_scorecard.decision_strategy_consistency,
        resource_allocation_efficiency=domain_scorecard.resource_allocation_efficiency,
        strategic_response_time=domain_scorecard.strategic_response_time,
        cross_functional_alignment=domain_scorecard.cross_functional_alignment,
        strategic_communication_effectiveness=domain_scorecard.strategic_communication_effectiveness,
        adaptation_speed=domain_scorecard.adaptation_speed,
        overall_alignment_score=domain_scorecard.overall_alignment_score,
        alignment_zone=StrategicAlignmentZone(domain_scorecard.alignment_zone.value),
        strategic_velocity=domain_scorecard.strategic_velocity,
        trend_30_days=domain_scorecard.trend_30_days,
        trend_60_days=domain_scorecard.trend_60_days,
        trend_90_days=domain_scorecard.trend_90_days,
        risk_indicators=domain_scorecard.risk_indicators,
        priority_interventions=domain_scorecard.priority_interventions,
        metadata=domain_scorecard.metadata,
    )


def get_intelligence_service() -> IntelligenceService:
    """Get intelligence service instance."""
    agent_service = AgentService()
    return IntelligenceService(agent_service)


@strawberry.type
class Query:
    """GraphQL Query root."""

    @strawberry.field
    async def truths(
        self,
        info: strawberry.Info,
        filter: Optional[TruthsFilter] = None
    ) -> List[OrganizationalTruth]:
        """Get organizational truths with optional filtering."""
        # Get current tenant from context (you'll need to set this up in context)
        tenant_id = info.context.get("tenant_id", "demo")
        
        intelligence_service = get_intelligence_service()
        
        # Convert GraphQL filter to domain query
        domain_categories = None
        if filter and filter.categories:
            from ..domain.intelligence_models import TruthCategory as DomainTruthCategory
            domain_categories = [DomainTruthCategory(cat.value) for cat in filter.categories]
        
        domain_impact_levels = None
        if filter and filter.impact_levels:
            from ..domain.intelligence_models import ImpactLevel as DomainImpactLevel
            domain_impact_levels = [DomainImpactLevel(level.value) for level in filter.impact_levels]
        
        query = TruthQuery(
            tenant_id=tenant_id,
            categories=domain_categories,
            impact_levels=domain_impact_levels,
            confidence_min=filter.confidence_min if filter else None,
            date_from=filter.date_from if filter else None,
            date_to=filter.date_to if filter else None,
            limit=filter.limit if filter else 50,
            offset=filter.offset if filter else 0,
        )
        
        domain_truths = await intelligence_service.get_truths(query)
        return [_convert_domain_truth_to_graphql(truth) for truth in domain_truths]

    @strawberry.field
    async def communications(
        self,
        info: strawberry.Info,
        filter: Optional[CommunicationsFilter] = None
    ) -> List[CommunicationQueue]:
        """Get priority communications with optional filtering."""
        tenant_id = info.context.get("tenant_id", "demo")
        user_id = info.context.get("user_id", "dev")
        
        intelligence_service = get_intelligence_service()
        
        # Convert GraphQL filter to domain query
        domain_types = None
        if filter and filter.types:
            from ..domain.intelligence_models import CommunicationType as DomainCommunicationType
            domain_types = [DomainCommunicationType(t.value) for t in filter.types]
        
        query = CommunicationQuery(
            user_id=user_id,
            tenant_id=tenant_id,
            types=domain_types,
            priority_min=filter.priority_min if filter else None,
            delivered=filter.delivered if filter else None,
            acknowledged=filter.acknowledged if filter else None,
            limit=filter.limit if filter else 20,
            offset=filter.offset if filter else 0,
        )
        
        domain_comms = await intelligence_service.get_communications(query)
        return [_convert_domain_communication_to_graphql(comm) for comm in domain_comms]

    @strawberry.field
    async def strategic_alignment_scorecard(
        self,
        info: strawberry.Info,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        include_details: bool = False
    ) -> Optional[StrategicAlignmentScorecard]:
        """Get strategic alignment scorecard."""
        tenant_id = info.context.get("tenant_id", "demo")
        
        intelligence_service = get_intelligence_service()
        
        from ..domain.intelligence_models import StrategicAlignmentQuery
        query = StrategicAlignmentQuery(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            include_details=include_details,
        )
        
        domain_scorecard = await intelligence_service.get_strategic_alignment_scorecard(query)
        if domain_scorecard:
            return _convert_domain_scorecard_to_graphql(domain_scorecard)
        return None

    @strawberry.field
    async def query_documents(
        self,
        info: strawberry.Info,
        input: DocumentQueryInput
    ) -> QueryResult:
        """Query documents using RAG."""
        tenant_id = input.tenant_id or info.context.get("tenant_id", "demo")
        user_id = info.context.get("user_id", "dev")
        
        # Use the RAG service directly
        from ..domain.models import QueryRequest
        domain_request = QueryRequest(
            query=input.question,
            tenant_id=tenant_id,
            user_id=user_id,
            context_limit=input.k
        )
        
        response = di.container.rag.query_documents(domain_request)
        
        return QueryResult(
            answer=response.answer,
            sources=[
                {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "score": doc.metadata.get("score", 0.0),
                }
                for doc in response.sources
            ],
            confidence=response.confidence,
            query_id=response.query_id,
        )

    @strawberry.field
    async def recent_documents(
        self,
        info: strawberry.Info,
        limit: int = 20
    ) -> List[DocumentInfo]:
        """Get recently ingested documents."""
        tenant_id = info.context.get("tenant_id", "demo")
        
        documents = di.container.rag.get_recent_documents(tenant_id=tenant_id, limit=limit)
        
        return [
            DocumentInfo(
                id=doc["id"],
                title=doc["title"],
                type=doc.get("type", "text"),
                created_at=datetime.fromisoformat(doc.get("created_at", datetime.now().isoformat())),
                chunks=doc.get("chunk_count", 0),
            )
            for doc in documents
        ]

    @strawberry.field
    async def system_health(self, info: strawberry.Info) -> SystemHealth:
        """Get system health information."""
        # Get health information
        services = await health_checker.check_all_services(di.container)
        system_metrics = health_checker.get_system_metrics()
        
        return SystemHealth(
            status=health_checker.determine_overall_status(services),
            timestamp=datetime.utcnow(),
            version=health_checker.version,
            uptime_seconds=health_checker.get_uptime(),
            services=[
                {
                    "name": service.name,
                    "status": service.status,
                    "latency_ms": service.latency_ms,
                    "error": service.error,
                    "metadata": service.metadata,
                }
                for service in services
            ],
            system_metrics={
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_used_mb": system_metrics.memory_used_mb,
                "memory_available_mb": system_metrics.memory_available_mb,
                "disk_percent": system_metrics.disk_percent,
                "disk_used_gb": system_metrics.disk_used_gb,
                "disk_free_gb": system_metrics.disk_free_gb,
                "active_connections": system_metrics.active_connections,
                "process_count": system_metrics.process_count,
            },
        )

    @strawberry.field
    async def strategic_intelligence_dashboard(
        self,
        info: strawberry.Info
    ) -> StrategicIntelligenceDashboard:
        """Get comprehensive strategic intelligence dashboard."""
        tenant_id = info.context.get("tenant_id", "demo")
        user_id = info.context.get("user_id", "dev")
        
        intelligence_service = get_intelligence_service()
        
        # Get dashboard components
        recent_truths = await intelligence_service.get_truths(
            TruthQuery(tenant_id=tenant_id, limit=10)
        )
        
        pending_communications = await intelligence_service.get_communications(
            CommunicationQuery(
                user_id=user_id,
                tenant_id=tenant_id,
                acknowledged=False,
                limit=10
            )
        )
        
        from ..domain.intelligence_models import ImpactLevel as DomainImpactLevel
        high_impact_truths = await intelligence_service.get_truths(
            TruthQuery(
                tenant_id=tenant_id,
                impact_levels=[DomainImpactLevel.HIGH, DomainImpactLevel.CRITICAL],
                limit=5
            )
        )
        
        # Get alignment scorecard
        from ..domain.intelligence_models import StrategicAlignmentQuery
        alignment_scorecard = await intelligence_service.get_strategic_alignment_scorecard(
            StrategicAlignmentQuery(tenant_id=tenant_id)
        )
        
        # Get system health
        services = await health_checker.check_all_services(di.container)
        system_metrics = health_checker.get_system_metrics()
        
        system_health = SystemHealth(
            status=health_checker.determine_overall_status(services),
            timestamp=datetime.utcnow(),
            version=health_checker.version,
            uptime_seconds=health_checker.get_uptime(),
            services=[
                {
                    "name": service.name,
                    "status": service.status,
                    "latency_ms": service.latency_ms,
                    "error": service.error,
                    "metadata": service.metadata,
                }
                for service in services
            ],
            system_metrics={
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_used_mb": system_metrics.memory_used_mb,
                "memory_available_mb": system_metrics.memory_available_mb,
                "disk_percent": system_metrics.disk_percent,
                "disk_used_gb": system_metrics.disk_used_gb,
                "disk_free_gb": system_metrics.disk_free_gb,
                "active_connections": system_metrics.active_connections,
                "process_count": system_metrics.process_count,
            },
        )
        
        return StrategicIntelligenceDashboard(
            recent_truths=[_convert_domain_truth_to_graphql(truth) for truth in recent_truths],
            pending_communications=[_convert_domain_communication_to_graphql(comm) for comm in pending_communications],
            high_impact_truths=[_convert_domain_truth_to_graphql(truth) for truth in high_impact_truths],
            recent_reports=[],  # This would need to be implemented in the intelligence service
            alignment_scorecard=_convert_domain_scorecard_to_graphql(alignment_scorecard) if alignment_scorecard else None,
            total_truths=len(intelligence_service.truths_cache) if hasattr(intelligence_service, 'truths_cache') else 0,
            queue_length=len(intelligence_service.communication_queue) if hasattr(intelligence_service, 'communication_queue') else 0,
            system_health=system_health,
        )


@strawberry.type
class Mutation:
    """GraphQL Mutation root."""

    @strawberry.mutation
    async def generate_strategic_intelligence(
        self,
        info: strawberry.Info,
        input: IntelligenceGenerationInput
    ) -> IntelligenceGenerationResponse:
        """Generate strategic intelligence from agent data."""
        tenant_id = info.context.get("tenant_id", "demo")
        user_id = info.context.get("user_id", "dev")
        
        intelligence_service = get_intelligence_service()
        
        # Convert GraphQL input to domain request
        from ..domain.intelligence_models import AnalysisDepth as DomainAnalysisDepth
        analysis_depth = None
        if input.analysis_depth:
            analysis_depth = DomainAnalysisDepth(input.analysis_depth.value)
        
        domain_request = IntelligenceRequest(
            agent_ids=input.agent_ids,
            template_id=input.template_id,
            analysis_depth=analysis_depth,
            variables=input.variables,
            tenant_id=tenant_id,
            user_id=user_id,
            priority=input.priority,
        )
        
        response = await intelligence_service.generate_intelligence(domain_request)
        
        return IntelligenceGenerationResponse(
            id=response.id,
            request_id=response.request_id,
            truths=[_convert_domain_truth_to_graphql(truth) for truth in response.truths],
            reports=[_convert_domain_report_to_graphql(report) for report in response.reports],
            communications=[_convert_domain_communication_to_graphql(comm) for comm in response.communications],
            generated_at=response.generated_at,
            processing_time_seconds=response.processing_time_seconds,
            token_count=response.token_count,
        )

    @strawberry.mutation
    async def acknowledge_communication(
        self,
        info: strawberry.Info,
        communication_id: str
    ) -> bool:
        """Acknowledge a priority communication."""
        user_id = info.context.get("user_id", "dev")
        
        intelligence_service = get_intelligence_service()
        return await intelligence_service.acknowledge_communication(communication_id, user_id)
