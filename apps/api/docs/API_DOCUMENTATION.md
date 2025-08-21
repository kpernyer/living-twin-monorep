# Living Twin API
**Version:** 2.0.0

# Living Twin Strategic Intelligence Platform

A comprehensive API for strategic intelligence, competitive analysis, and AI-powered business insights.

## Key Capabilities

* **Strategic Intelligence**: SWOT analysis, Porter's Five Forces, competitive intelligence
* **RAG System**: Document ingestion, semantic search, conversational AI
* **Health Monitoring**: Comprehensive system health and performance monitoring  
* **Testing Framework**: End-to-end testing for strategic intelligence workflows

## Authentication

All endpoints require Firebase authentication via the `Authorization` header:
```
Authorization: Bearer <firebase-jwt-token>
```

Development environments support bypass mode for testing.

## Tenant Isolation

All data is isolated by tenant. Cross-tenant access is controlled by role-based permissions.

## Contact
**Name:** Living Twin API Support
**Email:** support@livingtwin.com
**URL:** https://github.com/kpernyer/living-twin-monorep

## Servers
- **Production server**: `https://api.livingtwin.com`
- **Staging server**: `https://staging-api.livingtwin.com`
- **Development server**: `http://localhost:8000`

## Authentication
All endpoints require Firebase JWT authentication via the `Authorization` header:
```
Authorization: Bearer <firebase-jwt-token>
```

## Health
System health monitoring and operational status endpoints. Includes comprehensive health checks, system metrics, and service status monitoring for production deployments.

### Health Check
`GET /health`

Basic health check endpoint for load balancers.

**Responses:**

- `200`: Successful Response

---

### Healthz
`GET /healthz`

Simple health check endpoint (Kubernetes style).

**Responses:**

- `200`: Successful Response

---

### Readyz
`GET /readyz`

Simple readiness check endpoint (Kubernetes style).

**Responses:**

- `200`: Successful Response

---

### Liveness Probe
`GET /health/live`

Kubernetes liveness probe endpoint.

**Responses:**

- `200`: Successful Response

---

### Readiness Probe
`GET /health/ready`

Kubernetes readiness probe with detailed service checks.

**Parameters:**

- `request` (string) *(required)*: 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Metrics
`GET /health/metrics`

Get detailed system and application metrics.

**Responses:**

- `200`: Successful Response

---

### Shutdown
`POST /health/shutdown`

Graceful shutdown endpoint (should be protected in production).

**Responses:**

- `200`: Successful Response

---

## intelligence
Strategic intelligence operations including SWOT analysis, competitive intelligence, and organizational insights. Provides AI-powered strategic decision support and business intelligence capabilities.

### Generate Strategic Intelligence
`POST /intelligence/generate`

Generate comprehensive strategic intelligence reports from agent-collected market data.
    
    This endpoint orchestrates the strategic intelligence pipeline to:
    1. Collect data from specified intelligence agents
    2. Apply strategic analysis frameworks (SWOT, Porter's Forces)
    3. Generate actionable insights and recommendations
    4. Create priority communications for stakeholders
    
    **Strategic Analysis Capabilities:**
    - Market trend analysis and competitive intelligence
    - Risk assessment and opportunity identification
    - Strategic alignment scoring and recommendations
    - Executive briefings and priority alerts
    
    **Agent Integration:**
    - News monitoring and sentiment analysis
    - Competitor tracking and benchmarking
    - Regulatory change detection
    - Technology trend analysis
    
    **Output Formats:**
    - Strategic truths and organizational insights
    - Executive reports and briefings
    - Priority communication queue
    - Strategic alignment scorecards

**Request Body:**
Schema: `IntelligenceRequest`

**Responses:**

- `200`: Generated strategic intelligence with insights, reports, and communications
- `422`: Validation Error

---

### Get Strategic Insights
`GET /intelligence/truths`

Get strategic insights based on query criteria.

**Parameters:**

- `categories` (string): 
- `impact_levels` (string): 
- `confidence_min` (string): 
- `date_from` (string): 
- `date_to` (string): 
- `limit` (integer): 
- `offset` (integer): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Priority Communications
`GET /intelligence/communications`

Get priority communications for the current user.

**Parameters:**

- `types` (string): 
- `priority_min` (string): 
- `delivered` (string): 
- `acknowledged` (string): 
- `limit` (integer): 
- `offset` (integer): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Acknowledge Priority Communication
`POST /intelligence/communications/{communication_id}/acknowledge`

Acknowledge a priority communication.

**Parameters:**

- `communication_id` (string) *(required)*: 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Templates
`GET /intelligence/templates`

Get available prompt templates.

**Parameters:**

- `role` (string): 
- `category` (string): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Create Template
`POST /intelligence/templates`

Create a new prompt template.

**Request Body:**
Schema: `PromptTemplate`

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Strategic Intelligence Dashboard
`GET /intelligence/dashboard`

Get strategic intelligence dashboard data.

**Responses:**

- `200`: Successful Response

---

### Process Escalations
`POST /intelligence/process-escalations`

Process escalation rules for communications.

**Responses:**

- `200`: Successful Response

---

### Get Intelligence Metrics
`GET /intelligence/metrics`

Get intelligence system metrics.

**Parameters:**

- `date_from` (string): 
- `date_to` (string): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Setup Demo Strategic Intelligence
`POST /intelligence/setup-demo`

Setup demo strategic intelligence data.

**Responses:**

- `200`: Successful Response

---

### Get Strategic Alignment Scorecard
`GET /intelligence/alignment/scorecard`

Get strategic alignment scorecard for the current tenant.

**Parameters:**

- `date_from` (string): 
- `date_to` (string): 
- `include_details` (boolean): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Strategic Alignment History
`GET /intelligence/alignment/history`

Get historical strategic alignment data.

**Parameters:**

- `date_from` (string): 
- `date_to` (string): 
- `limit` (integer): 
- `offset` (integer): 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Calculate Strategic Alignment
`POST /intelligence/alignment/calculate`

Calculate and update strategic alignment scorecard.

**Responses:**

- `200`: Successful Response

---

## Strategic Test
Testing framework for strategic intelligence and signal detection capabilities. Provides comprehensive test scenarios, data setup, and validation for the strategic intelligence pipeline.

### Setup Test Data
`POST /strategic-test/setup`

Set up comprehensive test data for strategic signal detection.

**Request Body:**
Schema: `TestSetupRequest`

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Test Signal Detection
`POST /strategic-test/signal-detection`

Test the complete signal detection pipeline.

**Request Body:**
Schema: `TestSignalDetectionRequest`

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Test Sources
`GET /strategic-test/sources`

Get strategic test sources with different update frequencies.

**Responses:**

- `200`: Successful Response

---

### Get Taxonomy
`GET /strategic-test/taxonomy`

Get the strategic intelligence taxonomy structure.

**Responses:**

- `200`: Successful Response

---

### Get Available Scenarios
`GET /strategic-test/scenarios`

Get list of available test scenarios.

**Responses:**

- `200`: Successful Response

---

### Get Megatrend
`GET /strategic-test/megatrend/{trend_name}`

Get a specific megatrend analysis.

**Parameters:**

- `trend_name` (string) *(required)*: 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Regional Factor
`GET /strategic-test/regional/{region_name}/{factor_type}`

Get a specific regional factor analysis.

**Parameters:**

- `region_name` (string) *(required)*: 
- `factor_type` (string) *(required)*: 

**Responses:**

- `200`: Successful Response
- `422`: Validation Error

---

### Get Test Agent Results
`GET /strategic-test/agent-results`

Get test agent results for signal detection.

**Responses:**

- `200`: Successful Response

---

### Test Complete Round Trip
`POST /strategic-test/round-trip`

Test the complete round-trip: setup → signal detection → analysis.

**Responses:**

- `200`: Successful Response

---

## Data Models

### AnalysisDepth
Analysis depth levels.
**Type:** `string`

---

### Body_upload_file_query_ingest_upload_post
**Type:** `object`

**Properties:**

- `file` (string) *(required)*: 
- `title` (string) *(required)*: 
- `tenantId` (string): 

---

### CommunicationQueue
Priority communication item in the queue.
**Type:** `object`

**Properties:**

- `id` (string): 
- `user_id` (string) *(required)*: 
- `tenant_id` (string) *(required)*: 
- `topic` (string) *(required)*: 
- `content` (string) *(required)*: 
- `type` (string): 
- `priority` (integer): Priority 1-10, higher = more important
- `created_at` (string): 
- `scheduled_for` (string): 
- `attempts` (integer): 
- `escalation_level` (integer): 0=nudge, 1=recommendation, 2=order
- `related_truths` (array): 
- `related_goals` (array): 
- `source_report` (string): 
- `delivered` (boolean): 
- `acknowledged` (boolean): 
- `acknowledged_at` (string): 
- `metadata` (object): 

---

### CommunicationType
Types of priority communications.
**Type:** `string`

---

### CompiledReport
Compiled analysis report based on agent results.
**Type:** `object`

**Properties:**

- `id` (string): 
- `title` (string) *(required)*: 
- `summary` (string) *(required)*: 
- `insights` (array): 
- `recommendations` (array): 
- `data_sources` (array): 
- `analysis_depth` (string) *(required)*: 
- `tenant_id` (string) *(required)*: 
- `created_at` (string): 
- `expires_at` (string): 
- `priority` (string): 
- `related_truths` (array): 
- `agent_results` (array): 
- `metadata` (object): 

---

### ConversationDetailSchema
**Type:** `object`

**Properties:**

- `id` (string) *(required)*: Conversation ID
- `title` (string) *(required)*: Conversation title
- `createdAt` (string) *(required)*: Creation timestamp
- `updatedAt` (string) *(required)*: Last update timestamp
- `messages` (array) *(required)*: Conversation messages

---

### ConversationalQueryRequestSchema
**Type:** `object`

**Properties:**

- `conversationId` (string): Existing conversation ID
- `question` (string) *(required)*: The question to ask
- `k` (integer): Number of context chunks
- `tenantId` (string): Target tenant ID
- `memoryWindow` (string): Memory window size

---

### ConversationalQueryResponseSchema
**Type:** `object`

**Properties:**

- `answer` (string) *(required)*: Generated answer
- `sources` (array) *(required)*: Source documents used
- `confidence` (string): Confidence score
- `conversationId` (string) *(required)*: Conversation ID
- `queryId` (string) *(required)*: Query ID

---

### ConversationsResponseSchema
Response model for listing conversations.
**Type:** `object`

**Properties:**

- `conversations` (array): 

---

### DeleteResponseSchema
**Type:** `object`

**Properties:**

- `success` (boolean) *(required)*: Deletion success status

---

### DetailedHealthResponse
Detailed health check response.
**Type:** `object`

**Properties:**

- `status` (string) *(required)*: Overall health status
- `timestamp` (string) *(required)*: Timestamp of health check
- `version` (string) *(required)*: API version
- `environment` (string) *(required)*: Environment (dev/staging/prod)
- `uptime_seconds` (number) *(required)*: Service uptime in seconds
- `services` (array) *(required)*: Individual service health
- `system` (string) *(required)*: System metrics
- `checks_passed` (integer) *(required)*: Number of health checks passed
- `checks_failed` (integer) *(required)*: Number of health checks failed

---

### HTTPValidationError
**Type:** `object`

**Properties:**

- `detail` (array): 

---

### HealthStatus
Health status model.
**Type:** `object`

**Properties:**

- `status` (string) *(required)*: Overall health status
- `timestamp` (string) *(required)*: Timestamp of health check
- `version` (string) *(required)*: API version
- `uptime_seconds` (number) *(required)*: Service uptime in seconds

---

### ImpactLevel
Impact levels for strategic insights.
**Type:** `string`

---

### IngestAcceptedResponseSchema
**Type:** `object`

**Properties:**

- `ok` (boolean) *(required)*: 
- `jobId` (string) *(required)*: 
- `status` (string) *(required)*: 

---

### IngestJobStatusSchema
**Type:** `object`

**Properties:**

- `jobId` (string) *(required)*: 
- `status` (string) *(required)*: 
- `tenantId` (string): 
- `userId` (string): 
- `title` (string): 
- `sourceId` (string): 
- `chunkCount` (string): 
- `durationMs` (string): 
- `error` (string): 
- `createdAt` (string): 
- `updatedAt` (string): 

---

### IngestRequestSchema
**Type:** `object`

**Properties:**

- `title` (string) *(required)*: Human-readable title for the document - Example: `Q4 2024 Strategic Plan`
- `text` (string) *(required)*: Full text content of the document to be ingested and indexed - Example: `Strategic Plan 2024

Executive Summary: This document outlines our strategic priorities for Q4 2024...`
- `tenantId` (string): Target tenant ID for document storage (defaults to user's tenant) - Example: `acme_corp`

---

### IngestResponseSchema
**Type:** `object`

**Properties:**

- `ok` (boolean) *(required)*: Whether the ingestion completed successfully - Example: `True`
- `sourceId` (string) *(required)*: Unique identifier for the ingested document - Example: `doc_abc123def456`
- `chunks` (integer) *(required)*: Number of text chunks created from the document for retrieval - Example: `15`

---

### IntelligenceRequest
Request to generate strategic intelligence from market intelligence data.
**Type:** `object`

**Properties:**

- `agent_ids` (array) *(required)*: Agent IDs to analyze
- `template_id` (string) *(required)*: Prompt template to use
- `analysis_depth` (string): 
- `variables` (object): 
- `tenant_id` (string) *(required)*: 
- `user_id` (string) *(required)*: 
- `priority` (string): 

---

### IntelligenceResponse
Response from strategic intelligence generation.
**Type:** `object`

**Properties:**

- `id` (string): 
- `request_id` (string) *(required)*: 
- `truths` (array): 
- `reports` (array): 
- `communications` (array): 
- `generated_at` (string): 
- `processing_time_seconds` (string): 
- `token_count` (string): 

---

### MessageSchema
**Type:** `object`

**Properties:**

- `id` (string) *(required)*: Message ID
- `role` (string) *(required)*: Message role (user/assistant)
- `content` (string) *(required)*: Message content
- `timestamp` (string) *(required)*: Message timestamp
- `metadata` (object): Message metadata

---

### OrganizationalTruth
Strategic insight entity representing fundamental organizational knowledge.
**Type:** `object`

**Properties:**

- `id` (string): 
- `statement` (string) *(required)*: Clear, actionable statement
- `confidence` (number) *(required)*: Confidence score 0-1
- `evidence_count` (integer): Number of supporting data points
- `last_updated` (string): 
- `version` (integer): 
- `category` (string) *(required)*: 
- `impact_level` (string) *(required)*: 
- `tenant_id` (string) *(required)*: 
- `created_at` (string): 
- `strategic_goals` (array): 
- `compiled_reports` (array): 
- `raw_data_sources` (array): 
- `related_truths` (array): 
- `metadata` (object): 

---

### PriorityLevel
Priority levels for priority communications.
**Type:** `string`

---

### PromptTemplate
Template for generating insights from agent results.
**Type:** `object`

**Properties:**

- `id` (string): 
- `name` (string) *(required)*: 
- `description` (string) *(required)*: 
- `role` (string) *(required)*: Target role: ceo, cto, cfo, etc.
- `category` (string) *(required)*: Category: technology, market, competitive, etc.
- `template` (string) *(required)*: Prompt template with variables
- `variables` (array): 
- `analysis_depth` (string): daily, weekly, monthly
- `output_format` (string): truth, report, insight
- `tenant_id` (string): 
- `created_at` (string): 
- `is_active` (boolean): 

---

### QueryRequestSchema
**Type:** `object`

**Properties:**

- `question` (string) *(required)*: The question to ask about your documents - Example: `What are the key risks mentioned in our quarterly report?`
- `k` (integer): Number of context chunks to retrieve for generating the answer - Example: `5`
- `tenantId` (string): Target tenant ID (defaults to user's tenant) - Example: `tenant_123`

---

### QueryResponseSchema
**Type:** `object`

**Properties:**

- `answer` (string) *(required)*: AI-generated answer based on retrieved document context - Example: `Based on the strategy documents, the main competitive advantages are: 1) Advanced AI technology, 2) Strong brand recognition, 3) Extensive distribution network...`
- `sources` (array) *(required)*: Source documents and chunks used to generate the answer, including relevance scores - Example: `[{'content': 'Our competitive advantages include...', 'id': 'doc_123', 'score': 0.92, 'title': 'Q3 Strategy Document'}]`
- `confidence` (string): Confidence score for the generated answer (0.0 = low, 1.0 = high) - Example: `0.85`
- `query_id` (string) *(required)*: Unique identifier for this query, used for tracking and debugging - Example: `query_abc123def456`

---

### RecentDocumentSchema
**Type:** `object`

**Properties:**

- `id` (string) *(required)*: Document ID
- `title` (string) *(required)*: Document title
- `type` (string) *(required)*: Document type
- `createdAt` (string) *(required)*: Creation timestamp
- `chunks` (integer) *(required)*: Number of chunks

---

### RecentDocumentsResponseSchema
**Type:** `object`

**Properties:**

- `items` (array) *(required)*: List of recent documents

---

### ServiceHealth
Individual service health status.
**Type:** `object`

**Properties:**

- `name` (string) *(required)*: Service name
- `status` (string) *(required)*: Service status (healthy/degraded/unhealthy)
- `latency_ms` (string): Service latency in milliseconds
- `error` (string): Error message if unhealthy
- `metadata` (string): Additional service metadata

---

### StrategicAlignmentScorecard
Comprehensive strategic alignment scorecard for an organization.
**Type:** `object`

**Properties:**

- `id` (string): 
- `tenant_id` (string) *(required)*: 
- `measurement_date` (string): 
- `strategic_initiative_velocity` (number): 
- `goal_cascade_alignment` (number): 
- `decision_strategy_consistency` (number): 
- `resource_allocation_efficiency` (number): 
- `strategic_response_time` (number): 
- `cross_functional_alignment` (number): 
- `strategic_communication_effectiveness` (number): 
- `adaptation_speed` (number): 
- `overall_alignment_score` (number): 
- `alignment_zone` (string): 
- `strategic_velocity` (number): 
- `trend_30_days` (string): improving, declining, stable
- `trend_60_days` (string): improving, declining, stable
- `trend_90_days` (string): improving, declining, stable
- `risk_indicators` (array): 
- `priority_interventions` (array): 
- `metadata` (object): 

---

### StrategicAlignmentZone
Strategic alignment health zones.
**Type:** `string`

---

### SystemMetrics
System metrics model.
**Type:** `object`

**Properties:**

- `cpu_percent` (number) *(required)*: CPU usage percentage
- `memory_percent` (number) *(required)*: Memory usage percentage
- `memory_used_mb` (number) *(required)*: Memory used in MB
- `memory_available_mb` (number) *(required)*: Available memory in MB
- `disk_percent` (number) *(required)*: Disk usage percentage
- `disk_used_gb` (number) *(required)*: Disk used in GB
- `disk_free_gb` (number) *(required)*: Free disk space in GB
- `active_connections` (integer) *(required)*: Number of active connections
- `process_count` (integer) *(required)*: Number of running processes

---

### TestResult
Test result summary.
**Type:** `object`

**Properties:**

- `success` (boolean) *(required)*: 
- `message` (string) *(required)*: 
- `data` (object) *(required)*: 
- `execution_time_ms` (number) *(required)*: 

---

### TestSetupRequest
Request to set up test data.
**Type:** `object`

**Properties:**

- `tenant_id` (string) *(required)*: 
- `user_id` (string) *(required)*: 
- `industry` (string): 
- `test_scenario` (string): 
- `scope` (string): 

---

### TestSignalDetectionRequest
Request to test signal detection.
**Type:** `object`

**Properties:**

- `tenant_id` (string) *(required)*: 
- `swot_analysis_id` (string) *(required)*: 
- `porters_analysis_id` (string) *(required)*: 
- `test_agent_results` (boolean): 

---

### TruthCategory
Categories for strategic insights.
**Type:** `string`

---

### ValidationError
**Type:** `object`

**Properties:**

- `loc` (array) *(required)*: 
- `msg` (string) *(required)*: 
- `type` (string) *(required)*: 

---
