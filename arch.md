# Architecture Overview

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                       Frontend (Browser)                    │
│  • HTML Form for business profile input                    │
│  • Real-time progress bar with SSE                         │
│  • Results display with visualizations                     │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTP/SSE
                       ▼
┌────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ API Endpoints:                                       │ │
│  │  • POST /plan - Generate marketing plan              │ │
│  │  • POST /api/plan/plan-with-progress - With SSE      │ │
│  │  • GET /api/plan/progress/{id} - SSE stream          │ │
│  │  • GET /metrics - System metrics                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 8-Agent Sequential Chain:                            │ │
│  │                                                       │ │
│  │  1. RAGAgent - Historical insights retrieval         │ │
│  │  2. PersonaAgent - Customer persona generation       │ │
│  │  3. LocationAgent - Radius optimization              │ │
│  │  4. CompetitorAgent - Competitive analysis           │ │
│  │  5. PlannerAgent - 3 budget scenarios                │ │
│  │  6. CreativeAgent - Campaign ideas + images          │ │
│  │  7. PerformanceAgent - ROI predictions               │ │
│  │  8. CriticAgent - Quality evaluation (0-1 score)     │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│                   Google Gemini AI                         │
│  • Model: Gemini 2.0 Flash (fast agents)                  │
│  • Model: Gemini 2.5 Flash (reasoning agents)             │
│  • Auth: Application Default Credentials (ADC)            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   Dual Memory System                       │
│  ┌─────────────────────┐  ┌────────────────────────────┐  │
│  │ ChromaDB (Vector)   │  │ SQLite (Relational)        │  │
│  │  • 28+ plans        │  │  • Sessions                │  │
│  │  • Semantic search  │  │  • Plans                   │  │
│  │  • Embeddings       │  │  • Feedback                │  │
│  └─────────────────────┘  └────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   MCP Integration                          │
│  • Image Search Server (mcp_servers/)                     │
│  • Google Image Search via SerpAPI                        │
│  • Fallback: Unsplash API → Lorem Picsum                 │
└────────────────────────────────────────────────────────────┘
```

## Data Flow

### Sequential Agent Execution

```
User Request
    │
    ▼
BusinessProfile Input
    │
    ▼
RAGAgent (Step 0)
    │ → rag_insights
    ▼
PersonaAgent (Step 1)
    │ → persona
    ▼
LocationAgent (Step 2)
    │ → location_recommendation
    ▼
CompetitorAgent (Step 3)
    │ → competitor_snapshot
    ▼
PlannerAgent (Step 4)
    │ (uses: persona, competitor_snapshot)
    │ → scenarios (3 budget plans)
    ▼
CreativeAgent (Step 5)
    │ (uses: persona)
    │ → creatives (ideas, images, copy)
    │ → calls MCP Image Search
    ▼
PerformanceAgent (Step 6)
    │ (uses: scenarios, persona)
    │ → performance_predictions
    ▼
CriticAgent (Step 7)
    │ (uses: ALL previous outputs)
    │ → evaluation (score 0-1, strengths, issues)
    ▼
Complete Marketing Plan
    │
    ├─> Store in SQLite
    ├─> Store in ChromaDB
    └─> Return to user
```

## Technology Stack

### Backend
- **Framework:** FastAPI (async Python)
- **AI SDK:** Google Agent Development Kit (ADK)
- **Models:** Gemini 2.0 Flash + 2.5 Flash
- **Validation:** Pydantic schemas
- **Progress:** sse-starlette (Server-Sent Events)

### Memory
- **Vector DB:** ChromaDB 1.3.4
- **Relational DB:** SQLite
- **Dual writes:** Every plan stored in both

### Frontend
- **UI:** HTML5 + CSS3 + Vanilla JavaScript
- **Progress:** EventSource API for SSE
- **Styling:** Purple gradient theme

### External Integrations
- **Authentication:** Google ADC
- **Image Search:** SerpAPI (Google Images)
- **Fallback Images:** Unsplash API, Lorem Picsum
- **MCP Protocol:** HTTP-based tool integration

### Deployment
- **Containerization:** Docker + docker-compose
- **PDF Export:** ReportLab
- **Testing:** pytest + Playwright

## Key Design Patterns

1. **Sequential Chain Pattern**
   - Each agent waits for previous with `await`
   - Outputs become inputs for downstream agents
   - Orchestrated in `app/main.py` (lines 78-260)

2. **Dual Memory Architecture**
   - ChromaDB for semantic similarity search (RAG)
   - SQLite for structured queries (API retrieval)
   - Synergy: Same data, different access patterns

3. **Agentic RAG**
   - RAGAgent actively queries vector DB
   - Analyzes similarity scores
   - Generates contextual insights
   - Not just passive document retrieval

4. **Self-Evaluating System**
   - CriticAgent evaluates all outputs
   - 6-dimension scoring system
   - Quality threshold: 0.70

5. **Real-time Progress Tracking**
   - Server-Sent Events (SSE) stream
   - 8 progress updates (one per agent)
   - Auto-scroll, timeout protection

## Folder Structure

```
ad_planner/
├── app/
│   ├── agents/              # 8 AI agents
│   ├── api/                 # API routers (SSE progress)
│   ├── memory/              # ChromaDB + SQLite
│   ├── schemas/             # Pydantic models
│   ├── utils/               # PDF, analytics
│   ├── observability/       # Logging, metrics
│   ├── templates/           # HTML UI
│   ├── static/              # CSS, JS
│   └── main.py              # FastAPI app + orchestration
├── mcp_servers/             # Image search server
├── tests/                   # pytest + Playwright
├── docs/                    # Documentation
├── exports/                 # Generated PDFs
└── vector_store/            # ChromaDB persistent storage
```

## Performance Metrics

- **Total Pipeline:** 30-60 seconds (all 8 agents)
- **Individual Agent:** 2-8 seconds
- **Success Rate:** 98%+
- **Avg Quality Score:** 0.85+
- **Cost per Plan:** ~$0.50 (Gemini API)

## Scalability

- **Async Support:** FastAPI handles concurrent requests
- **Horizontal Scaling:** Multiple instances behind load balancer
- **Database:** ChromaDB partitioning, SQLite indexing
- **Caching:** Future optimization for frequent queries
