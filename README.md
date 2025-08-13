# Living Twin — Full Dev & Demo Guide

This is the development stack for **Living Twin** — a RAG-enabled, Neo4j-backed, multi-tenant “organizational twin” system.

## 📜 Architecture (Dev Stack)

```
                          +--------------------+
                          |   React Admin UI   |
                          |  Vite @ :5173      |
                          +---------+----------+
                                    |
                                    | HTTP (JSON)
                                    v
+---------------------+     +-------+--------+       Bolt (7687)
|  Optional Frontend  |     |   FastAPI RAG  |  <--------------------+
|  (Flutter mobile)   | --> |  http://:8080  |                       |
+---------------------+     |  - Ingest      |                       |
             ^              |  - /query      |                       |
             |              |  - /debug/rag  |                       |
             |              +-------+--------+                       |
             |                      |                                |
             |                      | Vector search (Neo4j index)    |
             |                      v                                |
             |              +-------+--------+                       |
             |              |     Neo4j      |  ---------------------+
             |              |  :7474 / :7687 |   HAS_CHUNK edges
             |              |  Doc.embedding |   Source(title, url, tags, tenantId)
             |              +----------------+

 [LLM Provider Options]
 - OpenAI (default): gpt-4o-mini, text-embedding-3-small
 - Ollama (local): llama3
 - Stub (RAG_ONLY): skip LLM, return top snippets
```

## 1️⃣ Prerequisites

- **Docker + Docker Compose**
- **Python 3.11+** (3.13 not recommended — pydantic-core build issues)
- **Node.js 20+** + npm
- (Optional) **Ollama** for local LLM testing:
  ```bash
  brew install ollama
  ollama pull llama3
  ```
- OpenAI account with API key (if using OpenAI models)

> 📋 **New to the project?** Check out our [**Development Environment Setup Guide**](docs/DEVELOPMENT_ENVIRONMENT_SETUP.md) for automated installation scripts and containerization strategies for macOS and Linux.

## 2️⃣ One-time setup

```bash
# Clone repo
git clone <your-repo-url> living_twin_monorepo
cd living_twin_monorepo

# Env
cp .env.example .env
# Fill in:
# OPENAI_API_KEY=sk-...
# Adjust Neo4j creds if needed (dev default: neo4j/password)

# Python venv
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel

# Install backend deps
make install

# Install React admin deps
make node-setup

# Start Neo4j and init schema (vector index, constraints)
make neo4j-up
make neo4j-init
```

## 3️⃣ Verify setup

- **Neo4j** — http://localhost:7474 → login `neo4j` / `password`
  ```cypher
  SHOW INDEXES WHERE name='docEmbeddings';
  ```
- **Python deps**
  ```bash
  .venv/bin/python -c "import fastapi, neo4j, sentence_transformers; print('✅ Python OK')"
  ```
- **React admin**
  ```bash
  make dev-react
  # Visit http://localhost:5173
  ```
- **OpenAI key check**
  ```bash
  make check-billing-py
  ```

## 4️⃣ Run modes

### Local (no OpenAI cost)
```bash
source .env
make dev-local
```
- Local embeddings: `all-MiniLM-L6-v2` (384-dim)
- Stub LLM: RAG_ONLY=1 (just returns top snippets)

### OpenAI (cheap dev)
```bash
source .env
make dev-openai
```
- LLM: `gpt-4o-mini`
- Embeddings: `text-embedding-3-small` (1536-dim)

### Ollama (local LLM)
```bash
ollama serve &
source .env
make dev-ollama
```

## 5️⃣ Demo flow

1. Start API + Neo4j in your preferred mode.
2. In a separate terminal:  
   ```bash
   make dev-react
   ```
3. Open http://localhost:5173
4. **Ingest a snippet**
   - Paste: “Fix bug X and raise NPS by 5 points in Q3”
   - Title: “Retention Strategy Q3”
   - Click **Ingest**
5. **Ask a question**
   - “How do we improve retention according to the latest plan?”
   - Answer should cite `[1] Retention Strategy Q3`
6. **Debug RAG**
   - Show retrieved chunks + scores, grouped by source

## 6️⃣ CLI ingestion/query

```bash
# Ingest
curl -s -X POST http://localhost:8080/ingest/text   -H 'Content-Type: application/json'   -d '{"title":"Retention Strategy Q3","text":"Fix bug X and raise NPS by 5 points.","tenantId":"demo"}' | jq

# Recent
curl -s http://localhost:8080/ingest/recent | jq

# Query
curl -s -X POST http://localhost:8080/query   -H 'Content-Type: application/json'   -d '{"question":"How do we improve retention?", "k":5, "tenantId":"demo"}' | jq
```

## 7️⃣ Common gotchas

| Issue | Fix |
|-------|-----|
| **`No such vector schema index: docEmbeddings`** | Run `make neo4j-init` |
| **Quota exceeded** from OpenAI | Enable Pay-as-you-go in OpenAI billing, or switch to LOCAL_EMBEDDINGS=1 |
| **pydantic-core build error** | Use Python 3.11 or 3.12 |
| **Auth error to Neo4j** | Reset volume: `docker compose down -v && make neo4j-up && make neo4j-init` |
| **Vectors dim mismatch** | Re-ingest docs after changing embedding model |

## 8️⃣ Environment toggles

In `.env`:

```
LLM_PROVIDER=openai       # openai | ollama | stub
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small
LOCAL_EMBEDDINGS=0        # 1 = use sentence-transformers locally
LOCAL_EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_ONLY=0                # 1 = skip LLM, just return top snippets

# Ollama settings
OLLAMA_BASE=http://localhost:11434
OLLAMA_MODEL=llama3
```

## 9️⃣ Full stack in Docker Compose

```bash
source .env
make compose-up
# Neo4j :7474 / FastAPI :8080 / React :5173
```

## 🔟 Next steps

- Add PDF/DOCX ingestion (`unstructured` lib)
- Wire API Gateway + Firebase Auth in staging
- Add multi-tenant plugin marketplace
- Extend graph schema for goals/teams/projects links
- Introduce agents with **Ping / Act / Aggregate** modes

## 📚 Documentation

For detailed documentation on specific topics, see the [`docs/`](docs/) directory:

### Architecture & Design
- [**Architecture Overview**](docs/ARCHITECTURE.md) - System architecture and design patterns
- [**Schema Consistency Guide**](docs/SCHEMA_CONSISTENCY_GUIDE.md) - Data models and schema management
- [**Configuration Sync**](docs/CONFIGURATION_SYNC.md) - Environment and configuration management

### Development & Deployment
- [**Development Environment Setup**](docs/DEVELOPMENT_ENVIRONMENT_SETUP.md) - External tools, containerization strategies, and automated setup scripts
- [**Local Development Setup**](docs/README_LOCAL_DEV.md) - Detailed local development guide
- [**Deployment Setup**](docs/DEPLOYMENT_SETUP.md) - Production deployment instructions
- [**Deployment Sprint Guide**](docs/DEPLOYMENT_SPRINT_GUIDE.md) - Step-by-step deployment process
- [**Scaling & Cost Guide**](docs/SCALING_AND_COST_GUIDE.md) - Performance optimization and cost management

### Features & Implementation
- [**Conversational Evolution Guide**](docs/CONVERSATIONAL_EVOLUTION_GUIDE.md) - Chat and conversation features
- [**Conversational Implementation Guide**](docs/CONVERSATIONAL_IMPLEMENTATION_GUIDE.md) - Technical implementation details
- [**PubSub Event System**](docs/PUBSUB_EVENT_SYSTEM.md) - Event-driven architecture
- [**PDF/DOCX Ingestion**](docs/pdf-docx-ingestion.md) - Document processing capabilities

### Security & Operations
- [**Security & Performance Testing**](docs/SECURITY_AND_PERFORMANCE_TESTING.md) - Testing strategies and security
- [**Tenant Isolation & Authorization**](docs/TENANT_ISOLATION_AND_AUTHORIZATION.md) - Multi-tenant security

### Release Notes
- [**README Patch Notes**](docs/README_PATCH.md) - Recent changes and updates

### Development Workflow
- [**Git Setup Guide**](docs/GIT_SETUP_GUIDE.md) - Repository initialization and Git best practices
- [**GitHub Setup Guide**](docs/GITHUB_SETUP_GUIDE.md) - GitHub integration and CI/CD configuration

Each document provides in-depth coverage of its respective topic with implementation details, best practices, and troubleshooting guides.
