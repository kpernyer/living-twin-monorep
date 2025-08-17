# AI Agent Architecture Diagrams

## Mermaid Architecture Diagram

```mermaid
graph TB
    %% External Systems
    subgraph "External Data Sources"
        RSS[RSS Feeds<br/>BBC, CNN, TechCrunch]
        NEWSAPI[NewsAPI<br/>Paid Service]
        WEB[Web Scraping<br/>Fallback]
    end

    %% API Layer
    subgraph "API Layer"
        API[FastAPI Server]
        ROUTER[Agent Router<br/>/agents/*]
        AUTH[Firebase Auth<br/>Tenant Isolation]
    end

    %% Agent System
    subgraph "Agent System"
        SERVICE[Agent Service<br/>Lifecycle Management]
        SCHEDULER[Agent Scheduler<br/>Cron-like Execution]
        FACTORY[Agent Factory<br/>Plug-and-Play]
        
        subgraph "Agent Types"
            TENANT[Tenant-Specific Agents<br/>Custom Keywords]
            SHARED[Shared Agents<br/>Global Trends]
        end
        
        subgraph "Agent Implementations"
            NEWS[NewsMonitoringAgent<br/>RSS + APIs]
            TECH[TechnologyTrendsAgent<br/>Tech News]
        end
    end

    %% Execution Modes
    subgraph "Execution Modes"
        API_MODE[API Mode<br/>Same Process]
        WORKER_MODE[Worker Mode<br/>Isolated Jobs]
    end

    %% Storage
    subgraph "Storage & Cache"
        RESULTS[Agent Results<br/>In-Memory Cache]
        EXECUTIONS[Execution History<br/>Health Metrics]
        CONFIG[Agent Configs<br/>Tenant Settings]
    end

    %% Monitoring
    subgraph "Monitoring"
        HEALTH[Health Checks<br/>Success Rates]
        METRICS[Performance Metrics<br/>Response Times]
        ALERTS[Error Alerts<br/>Status Notifications]
    end

    %% Connections
    API --> ROUTER
    ROUTER --> AUTH
    AUTH --> SERVICE
    
    SERVICE --> SCHEDULER
    SERVICE --> FACTORY
    FACTORY --> TENANT
    FACTORY --> SHARED
    
    TENANT --> NEWS
    SHARED --> TECH
    
    NEWS --> API_MODE
    NEWS --> WORKER_MODE
    TECH --> API_MODE
    TECH --> WORKER_MODE
    
    RSS --> NEWS
    NEWSAPI --> NEWS
    WEB --> NEWS
    RSS --> TECH
    
    SERVICE --> RESULTS
    SERVICE --> EXECUTIONS
    SERVICE --> CONFIG
    
    SERVICE --> HEALTH
    HEALTH --> METRICS
    METRICS --> ALERTS
    
    %% Styling
    classDef apiLayer fill:#e1f5fe
    classDef agentSystem fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef monitoring fill:#fff3e0
    classDef external fill:#fce4ec
    
    class API,ROUTER,AUTH apiLayer
    class SERVICE,SCHEDULER,FACTORY,TENANT,SHARED,NEWS,TECH agentSystem
    class RESULTS,EXECUTIONS,CONFIG storage
    class HEALTH,METRICS,ALERTS monitoring
    class RSS,NEWSAPI,WEB external
```

## Agent Lifecycle Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Factory
    participant Agent
    participant Sources
    participant Cache

    %% Agent Creation
    Client->>API: POST /agents/ (Create Agent)
    API->>Service: create_agent(request)
    Service->>Factory: create_agent(agent)
    Factory->>Agent: new AgentInstance(config)
    Service->>Cache: store_agent(agent)
    Service->>API: return agent
    API->>Client: 201 Created

    %% Agent Activation
    Client->>API: POST /agents/{id}/activate
    API->>Service: activate_agent(id)
    Service->>Cache: update_status(ACTIVE)
    Service->>API: success
    API->>Client: 200 OK

    %% Scheduled Execution
    loop Every minute
        Service->>Service: check_scheduled_agents()
        Service->>Agent: should_run()?
        alt Should Run
            Service->>Agent: execute(isolation_mode)
            Agent->>Sources: fetch_data()
            Sources->>Agent: results
            Agent->>Service: return results
            Service->>Cache: store_results()
            Service->>Cache: update_execution_history()
        end
    end

    %% Manual Execution
    Client->>API: POST /agents/{id}/execute
    API->>Service: execute_agent(request)
    Service->>Agent: run(isolation_mode)
    Agent->>Sources: fetch_data()
    Sources->>Agent: results
    Agent->>Service: return execution
    Service->>API: execution
    API->>Client: 200 OK

    %% Health Check
    Client->>API: GET /agents/{id}/health
    API->>Service: get_agent_health(id)
    Service->>Cache: get_execution_history()
    Service->>Service: calculate_metrics()
    Service->>API: health_status
    API->>Client: 200 OK
```

## Isolation Mode Architecture

```mermaid
graph LR
    subgraph "API Server"
        API[FastAPI]
        SERVICE[Agent Service]
    end

    subgraph "Worker Jobs"
        W1[Agent Worker 1<br/>Agent ID: 123]
        W2[Agent Worker 2<br/>Agent ID: 456]
        W3[Agent Worker 3<br/>Agent ID: 789]
    end

    subgraph "External Sources"
        RSS[RSS Feeds]
        API_SOURCES[News APIs]
    end

    API --> SERVICE
    SERVICE --> W1
    SERVICE --> W2
    SERVICE --> W3

    W1 --> RSS
    W2 --> API_SOURCES
    W3 --> RSS

    style W1 fill:#e8f5e8
    style W2 fill:#e8f5e8
    style W3 fill:#e8f5e8
    style API fill:#e1f5fe
    style SERVICE fill:#f3e5f5
```

## ASCII Art Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LIVING TWIN AI AGENT SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   External      │    │   External      │
│   Data Sources  │    │   Data Sources  │    │   Data Sources  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • BBC RSS       │    │ • NewsAPI       │    │ • Web Scraping  │
│ • CNN RSS       │    │ • Paid Service  │    │ • Fallback      │
│ • TechCrunch    │    │ • Enhanced      │    │ • Demo Data     │
│ • Reuters       │    │   Results       │    │ • Testing       │
│ • Wired         │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────────────────┐
                    │           API LAYER                 │
                    ├─────────────────────────────────────┤
                    │  ┌─────────────────────────────────┐ │
                    │  │      FastAPI Server             │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │    Agent Router             │ │ │
                    │  │  │  • POST /agents/            │ │ │
                    │  │  │  • GET /agents/             │ │ │
                    │  │  │  • POST /agents/{id}/execute│ │ │
                    │  │  │  • GET /agents/{id}/health  │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │    Firebase Auth            │ │ │
                    │  │  │  • Tenant Isolation         │ │ │
                    │  │  │  • User Authentication      │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────────────────────────┘
                                 │
                    ┌─────────────────────────────────────┐
                    │         AGENT SYSTEM                │
                    ├─────────────────────────────────────┤
                    │  ┌─────────────────────────────────┐ │
                    │  │      Agent Service              │ │
                    │  │  • Lifecycle Management         │ │
                    │  │  • Scheduling                   │ │
                    │  │  • Health Monitoring            │ │
                    │  │  • Result Caching               │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │      Agent Factory              │ │
                    │  │  • Plug-and-Play Creation       │ │
                    │  │  • Capability Mapping           │ │
                    │  │  • Configuration Validation     │ │
                    │  └─────────────────────────────────┘ │
                    │                                     │
                    │  ┌─────────────────────────────────┐ │
                    │  │        Agent Types              │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │   Tenant-Specific Agents    │ │ │
                    │  │  │  • Custom Keywords (5 max)  │ │ │
                    │  │  │  • Competitor Monitoring    │ │ │
                    │  │  │  • Industry Tracking        │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │      Shared Agents          │ │ │
                    │  │  │  • Global Tech Trends       │ │ │
                    │  │  │  • AI/ML Developments       │ │ │
                    │  │  │  • Cloud Computing News     │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  └─────────────────────────────────┘ │
                    │                                     │
                    │  ┌─────────────────────────────────┐ │
                    │  │    Agent Implementations       │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │   NewsMonitoringAgent       │ │ │
                    │  │  │  • RSS Feed Processing      │ │ │
                    │  │  │  • NewsAPI Integration      │ │ │
                    │  │  │  • Keyword Matching         │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  │  ┌─────────────────────────────┐ │ │
                    │  │  │  TechnologyTrendsAgent      │ │ │
                    │  │  │  • Tech News Aggregation    │ │ │
                    │  │  │  • Trend Analysis           │ │ │
                    │  │  │  • Global Intelligence      │ │ │
                    │  │  └─────────────────────────────┘ │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────────────────────────┘
                                 │
                    ┌─────────────────────────────────────┐
                    │       EXECUTION MODES               │
                    ├─────────────────────────────────────┤
                    │  ┌─────────────────────────────────┐ │
                    │  │         API Mode                │ │
                    │  │  • Same Process Execution       │ │
                    │  │  • Shared Resources             │ │
                    │  │  • Faster Response              │ │
                    │  │  • Less Isolation               │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │       Worker Mode               │ │
                    │  │  • Isolated Cloud Run Jobs      │ │
                    │  │  • Separate Memory/CPU          │ │
                    │  │  • Error Containment            │ │
                    │  │  • Independent Scaling          │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────────────────────────┘
                                 │
                    ┌─────────────────────────────────────┐
                    │      STORAGE & CACHE                │
                    ├─────────────────────────────────────┤
                    │  ┌─────────────────────────────────┐ │
                    │  │      Agent Results              │ │
                    │  │  • In-Memory Cache              │ │
                    │  │  • Configurable Retention       │ │
                    │  │  • Query Optimization           │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │    Execution History            │ │
                    │  │  • Success/Failure Tracking     │ │
                    │  │  • Performance Metrics          │ │
                    │  │  • Health Indicators            │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │     Agent Configurations        │ │
                    │  │  • Tenant Settings              │ │
                    │  │  • Keyword Lists                │ │
                    │  │  • Update Frequencies           │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────────────────────────┘
                                 │
                    ┌─────────────────────────────────────┐
                    │         MONITORING                  │
                    ├─────────────────────────────────────┤
                    │  ┌─────────────────────────────────┐ │
                    │  │       Health Checks             │ │
                    │  │  • Success Rate (7-day)         │ │
                    │  │  • Error Count Tracking         │ │
                    │  │  • Execution Time Monitoring    │ │
                    │  │  • Status Indicators            │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │     Performance Metrics         │ │
                    │  │  • Response Times               │ │
                    │  │  • Resource Utilization         │ │
                    │  │  • Throughput Monitoring        │ │
                    │  │  • Queue Lengths                │ │
                    │  └─────────────────────────────────┘ │
                    │  ┌─────────────────────────────────┐ │
                    │  │        Error Alerts             │ │
                    │  │  • Health Degradation           │ │
                    │  │  • High Error Rates             │ │
                    │  │  • Execution Timeouts           │ │
                    │  │  • Resource Exhaustion          │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              KEY FEATURES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🔌 Plug-and-Play Architecture  │  🔒 Tenant Isolation & Security          │
│ 🚀 Configurable & Extensible   │  📊 Health Monitoring & Metrics          │
│ 🛡️  Isolation Mode Support     │  ⚡ Scheduled & Manual Execution         │
│ 📰 Free News Sources Built-in  │  🎯 Custom Keyword Monitoring (5 max)     │
│ 🔄 Shared & Tenant Agents      │  📈 Scalable Cloud Run Deployment        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │    API      │    │   Agent     │    │   Sources   │
│  Request    │───▶│   Router    │───▶│  Service    │───▶│   (RSS/API) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │              ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │              │   Agent     │    │   Agent     │    │   Results   │
       │              │  Factory    │───▶│ Instance    │◀───│  Processing │
       │              └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │              ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │              │   Config    │    │  Execution  │    │   Cache     │
       │              │ Validation  │    │  History    │    │  Storage    │
       │              └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │              ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │              │   Health    │    │  Metrics    │    │   Alerts    │
       │              │  Monitoring │───▶│ Collection  │───▶│ Generation  │
       │              └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Response  │    │   Status    │    │  Results    │    │  Monitoring │
│  (JSON)     │    │  Updates    │    │  Cache      │    │  Dashboard  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Isolation Mode Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXECUTION MODE COMPARISON                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              API MODE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   FastAPI       │    │   Agent         │    │   Agent         │         │
│  │   Server        │    │   Service       │    │   Instances     │         │
│  │                 │    │                 │    │                 │         │
│  │  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│         │
│  │  │   Router    ││    │  │ Scheduler   ││    │  │ Agent 1     ││         │
│  │  └─────────────┘│    │  └─────────────┘│    │  └─────────────┘│         │
│  │  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│         │
│  │  │   Auth      ││    │  │ Factory     ││    │  │ Agent 2     ││         │
│  │  └─────────────┘│    │  └─────────────┘│    │  └─────────────┘│         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  ✅ Faster Response Times                                                   │
│  ✅ Shared Resources                                                        │
│  ✅ Simpler Deployment                                                      │
│  ❌ Less Isolation                                                          │
│  ❌ Resource Contention                                                     │
│  ❌ Error Propagation Risk                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            WORKER MODE                                     │
├─────────────────────────────────────────────────────────────────────────────┘
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   FastAPI       │    │   Cloud Run     │    │   Cloud Run     │         │
│  │   Server        │    │   Job 1         │    │   Job 2         │         │
│  │                 │    │                 │    │                 │         │
│  │  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│         │
│  │  │   Router    ││    │  │ Agent       ││    │  │ Agent       ││         │
│  │  └─────────────┘│    │  │ Worker 1    ││    │  │ Worker 2    ││         │
│  │  ┌─────────────┐│    │  └─────────────┘│    │  └─────────────┘│         │
│  │  │   Auth      ││    │  ┌─────────────┐│    │  ┌─────────────┐│         │
│  │  └─────────────┘│    │  │ Agent       ││    │  │ Agent       ││         │
│  └─────────────────┘    │  │ Instance 1  ││    │  │ Instance 2  ││         │
│                         │  └─────────────┘│    │  └─────────────┘│         │
│                         └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  ✅ Complete Isolation                                                      │
│  ✅ Independent Scaling                                                     │
│  ✅ Error Containment                                                       │
│  ✅ Resource Dedication                                                     │
│  ❌ Higher Latency                                                          │
│  ❌ More Complex Deployment                                                 │
│  ❌ Higher Resource Usage                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
