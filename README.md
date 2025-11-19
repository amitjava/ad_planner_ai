# 🚀 Smart Ad Planner - AI-Powered Marketing Advisor for Small Businesses

A sophisticated multi-agent FastAPI application that generates personalized advertising plans for local small businesses using Google Gemini AI-powered agents, complete with creative assets, performance predictions, and professional PDF reports.

**Made by Amit Dar**

## ✨ Features

### 🤖 8 Specialized AI Agents
A sequential chain of AI agents working together to create comprehensive marketing plans:

1. **RAGAgent**: Retrieves historical insights from vector database to inform plan generation with past successes and lessons learned
2. **PersonaAgent**: Generates detailed customer personas with demographics, interests, platform preferences, creative style, and motivations
3. **LocationAgent**: Recommends optimal advertising radius (miles) based on business type, purchase frequency, and customer behavior
4. **CompetitorAgent**: Analyzes competitive landscape to identify strengths, weaknesses, opportunities, and threats
5. **PlannerAgent**: Creates three media plan scenarios with channel-specific budget allocations:
   - **Standard Plan**: Conservative approach focusing on proven channels with predictable ROI
   - **Aggressive Plan**: Higher budget allocation to paid ads for maximum reach and faster results
   - **Experimental Plan**: Creative mix with influencers, content marketing, and emerging platforms
6. **CreativeAgent**: Generates compelling creative assets:
   - 3 campaign ideas with AI-searched images via MCP Server
   - 10 relevant hashtags (branded + trending)
   - 3 catchy slogans
   - Short ad copy (12-20 words)
   - Long ad copy (60-120 words)
   - 3 call-to-action options
7. **PerformanceAgent**: Predicts campaign performance with reach analytics and budget scaling:
   - Estimated reach with percentage infographics
   - Expected clicks and CPC
   - ROI ranges
   - Budget scaling recommendations (to double reach)
8. **CriticAgent**: Evaluates plan quality with 0.0-1.0 score and provides actionable recommendations

### 🎯 Advanced Features

- **Real-time Progress Bar**: Live progress tracking with Server-Sent Events (SSE) showing all 8 agents working in real-time
  - Beautiful purple gradient progress section with agent timeline
  - Animated 0-100% progress bar as agents execute
  - Current agent status with icons and descriptive messages
  - Timeline visualization showing which agents are active/completed
  - Auto-scroll to progress section when plan generation starts
  - Graceful error handling and timeout protection (5-minute max)
- **Location Intelligence**: ZIP code-based targeting with intelligent radius recommendations (3-30 miles) based on business category
- **Reach Analytics**: Visual infographics showing what percentage of target population you'll reach
- **Budget Scaling**: Calculate exactly how much budget needed to 2x your reach, including efficiency warnings for diminishing returns
- **Test Data Generation**: AI-powered realistic test data for Coffee Shop, Yoga Studio, and Fashion Boutique examples
- **Image Search Integration**: MCP Server for Google Image Search to find relevant campaign visuals
- **Professional PDF Export**: Beautiful marketing plan reports with all scenarios and recommendations

### 💾 Long-term Memory

- **Vector Database** (ChromaDB 1.3.4): ✅ **Active** - Semantic search across historical plans and business profiles with persistent storage
- **SQLite Database**: ✅ **Active** - Structured storage for sessions, plans, and feedback (17 users, 14 plans tracked)
- **Historical Analysis**: Learn from past campaigns and feedback with dual-database architecture
- **Persistent Storage**: Both databases survive server restarts with file-based storage

### 📊 Observability & Testing

- **3-Layer Testing Architecture**:
  1. **Unit Tests** (`tests/`): Test individual components
  2. **Evaluation Gates** (`app/evaluation/`): Test AI quality across 15 business scenarios
  3. **Playwright E2E** (`playwright_tests/`): Test full user experience
- **Real-time Metrics**: Request/response logging, agent performance tracking, error monitoring
- **Metrics Dashboard**: `/metrics` endpoint for system health

## 🏗 Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Browser)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         HTML Form (index.html)                       │   │
│  │  • Business Profile Input                            │   │
│  │  • Test Data Buttons (Coffee/Yoga/Boutique)          │   │
│  │  • Results Display with Infographics                 │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP POST/GET
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              main.py (API Layer)                     │   │
│  │  • POST /plan - Generate marketing plan              │   │
│  │  • GET /plan/{session_id} - Retrieve plan            │   │
│  │  • POST /feedback - Submit feedback                  │   │
│  │  • GET /metrics - System metrics                     │   │
│  │  • GET /download-pdf/{session_id} - PDF export       │   │
│  │  • POST /api/test-data/generate - Test data          │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Sequential Agent Chain                     │    │
│  │                                                      │    │
│  │  1. PersonaAgent (Gemini 2.0)                       │    │
│  │       ↓                                              │    │
│  │  2. LocationAgent (Gemini 2.0)                      │    │
│  │       ↓                                              │    │
│  │  3. CompetitorAgent (Gemini 2.5)                    │    │
│  │       ↓                                              │    │
│  │  4. PlannerAgent (Gemini 2.5)                       │    │
│  │       ↓                                              │    │
│  │  5. CreativeAgent (Gemini 2.5) ←→ MCP Image Search  │    │
│  │       ↓                                              │    │
│  │  6. PerformanceAgent (Gemini 2.0)                   │    │
│  │       ↓                                              │    │
│  │  7. CriticAgent (Gemini 2.0)                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Memory Layer                           │    │
│  │  ┌───────────────┐    ┌─────────────────┐          │    │
│  │  │ Vector Memory │    │ SQLite Memory   │          │    │
│  │  │  (ChromaDB)   │    │  (Structured)   │          │    │
│  │  │               │    │                 │          │    │
│  │  │ • Profiles    │    │ • Sessions      │          │    │
│  │  │ • Plans       │    │ • Plans         │          │    │
│  │  │ • Feedback    │    │ • Feedback      │          │    │
│  │  └───────────────┘    └─────────────────┘          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         PDF Generation (ReportLab)                  │    │
│  │  • Professional marketing plan reports              │    │
│  │  • Saved to exports/                                │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│            MCP Server (Model Context Protocol)               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │     Image Search Server (mcp_servers/)               │    │
│  │  • Google Image Search via SerpAPI                   │    │
│  │  • Unsplash fallback                                 │    │
│  │  • Lorem Picsum fallback                             │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Agent Workflow (Sequential Chain Pattern)

```
User Input → PersonaAgent → LocationAgent → CompetitorAgent → PlannerAgent
                                                                    ↓
        CriticAgent ← PerformanceAgent ← CreativeAgent ←───────────┘
              ↓
         Final Plan (with critic score)
```

### Agentic AI Patterns Used

1. **Sequential Chain Pattern**: Agents execute in order, each using outputs from previous agents
2. **Specialist Agents Pattern**: Each agent has a single, focused responsibility
3. **Structured Output Pattern**: Pydantic schemas enforce JSON response format from LLMs
4. **Critic/Evaluation Pattern**: CriticAgent reviews final output quality (0.0-1.0 score)
5. **MCP Tool Integration Pattern**: Agents can call external tools via Model Context Protocol

## 📁 Project Structure

```
ad_planner/
├── app/
│   ├── main.py                       # FastAPI application with 7-agent workflow
│   ├── models.py                     # Pydantic models for API requests/responses
│   │
│   ├── schemas/                      # Pydantic schemas for structured AI output
│   │   ├── business_profile.py       # BusinessProfile with zip_code + miles_radius
│   │   ├── persona.py                # Persona schema
│   │   ├── media_plan.py             # MediaPlan and ScenarioSet schemas
│   │   ├── creative_assets.py        # CreativeAssets with image URLs
│   │   ├── competitor.py             # CompetitorSnapshot schema
│   │   ├── performance.py            # PerformancePrediction with reach analytics
│   │   └── location.py               # LocationRecommendation schema
│   │
│   ├── agents/                       # AI agents (all use Google Gemini)
│   │   ├── base_agent.py             # BaseAgent with Gemini integration
│   │   ├── persona_agent.py          # PersonaAgent (gemini-2.0-flash-exp)
│   │   ├── location_agent.py         # LocationAgent (gemini-2.0-flash-exp)
│   │   ├── competitor_agent.py       # CompetitorAgent (gemini-2.5-flash)
│   │   ├── planner_agent.py          # PlannerAgent (gemini-2.5-flash)
│   │   ├── creative_agent.py         # CreativeAgent (gemini-2.5-flash) + MCP
│   │   ├── performance_agent.py      # PerformanceAgent (gemini-2.0-flash-exp)
│   │   └── critic_agent.py           # CriticAgent (gemini-2.0-flash-exp)
│   │
│   ├── utils/                        # Utility functions
│   │   ├── analytics.py              # Reach analytics & budget scaling calculations
│   │   └── pdf_generator.py          # PDF report generation with ReportLab
│   │
│   ├── api/                          # API routers
│   │   └── test_data.py              # Test data generation endpoint
│   │
│   ├── memory/                       # Storage layer
│   │   ├── vector_memory.py          # ChromaDB for semantic search
│   │   └── sqlite_memory.py          # SQLite for structured data
│   │
│   ├── observability/                # Logging & metrics
│   │   ├── logging_middleware.py     # Request/response logging
│   │   ├── metrics.py                # Metrics collector
│   │   └── agent_logger.py           # Agent performance tracking
│   │
│   ├── evaluation/                   # Evaluation pipeline
│   │   ├── eval_runner.py            # Run evaluations across test scenarios
│   │   └── test_profiles.py          # 15 predefined business profiles
│   │
│   ├── templates/                    # HTML templates
│   │   └── index.html                # Main UI with form and results display
│   │
│   └── static/                       # Static assets
│       └── styles.css                # Professional white theme CSS
│
├── mcp_servers/                      # Model Context Protocol servers
│   └── image_search_server.py        # Google Image Search MCP server
│
├── tests/                            # Unit tests (pytest)
│   ├── test_agents.py                # Agent unit tests
│   ├── test_memory.py                # Memory layer tests
│   └── test_ui_playwright.py         # Playwright browser tests
│
├── playwright_tests/                 # E2E tests (Playwright)
│   └── test_form_submission.py       # Full workflow tests
│
├── db/
│   └── init.sql                      # SQLite database schema
│
├── exports/                          # Generated PDF reports
├── vector_store/                     # ChromaDB persistent storage
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Docker container config
├── PLAYWRIGHT_SETUP.md               # Playwright MCP + Python setup docs
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Google Cloud SDK** (for Application Default Credentials)
- **Google Cloud Project** with Generative AI API enabled
- **Optional**: SerpAPI key for Google Image Search
- **Optional**: Unsplash API key for image fallback

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ad_planner
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt

# Verify ChromaDB installation (v1.3.4)
python -c "import chromadb; print(f'ChromaDB {chromadb.__version__} installed successfully')"
```

**Note**: All dependencies including ChromaDB 1.3.4 for vector search are included in `requirements.txt`.

4. **Set up authentication** (RECOMMENDED: Application Default Credentials):

**Option 1: ADC (Recommended - Most Secure)**
```bash
# Install Google Cloud SDK if not already installed
# macOS: brew install --cask google-cloud-sdk

# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

**Option 2: API Key (Not Recommended)**
```bash
# Only use if you cannot use ADC
export GEMINI_API_KEY="your-gemini-api-key-here"
```

📖 **See [ADC_SETUP.md](ADC_SETUP.md) for complete authentication setup guide**

5. **Optional: Enhanced image search**:
```bash
export SERPAPI_KEY="your-serpapi-key-here"
export UNSPLASH_ACCESS_KEY="your-unsplash-key-here"
```

6. **Run the application**:
```bash
uvicorn app.main:app --reload
```

You should see:
```
✓ Using Application Default Credentials (Project: your-project-id)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

6. **Open your browser**:
```
http://localhost:8000
```

You should see the Smart Ad Planner form with three example buttons (Coffee Shop, Yoga Studio, Fashion Boutique).

### Quick Test

1. Click "☕ Try Coffee Shop Example" to auto-fill the form
2. Click "Generate Marketing Plan"
3. Wait 30-60 seconds while the 7 AI agents work
4. View your personalized marketing plan with:
   - Target persona
   - Location radius recommendation
   - Competitor analysis
   - 3 media plan scenarios with budget breakdowns
   - Creative assets with AI-generated images
   - Performance predictions with reach infographics
   - Budget scaling recommendations
   - Plan strengths and quality score

## 🐳 Docker Deployment

### Build and run with Docker:

```bash
docker build -t smart-ad-planner .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key-here \
  -e SERPAPI_KEY=your-serpapi-key \
  smart-ad-planner
```

### Using Docker Compose:

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SERPAPI_KEY=${SERPAPI_KEY}
      - UNSPLASH_ACCESS_KEY=${UNSPLASH_ACCESS_KEY}
    volumes:
      - ./exports:/app/exports
      - ./vector_store:/app/vector_store
      - ./ad_planner.db:/app/ad_planner.db
```

Run:
```bash
export GEMINI_API_KEY="your-key"
docker-compose up
```

## 📊 API Endpoints

### `POST /plan`
Generate a complete marketing plan using all 8 AI agents.

**Request:**
```json
{
  "profile": {
    "business_name": "Joe's Coffee Shop",
    "business_type": "Coffee Shop",
    "zip_code": "94102",
    "miles_radius": 3,
    "goal": "Increase weekday morning traffic by 30% by targeting remote workers and freelancers within a 1-mile radius. Focus on building a community atmosphere and promoting our specialty pour-over coffee through Instagram and local partnerships.",
    "monthly_budget": 2500.0,
    "duration_weeks": 8,
    "is_local": true,
    "competitors": ["Starbucks", "Blue Bottle Coffee"]
  },
  "session_id": "optional-session-id"
}
```

**Response:** Complete plan with:
- `session_id`: Unique session identifier
- `persona`: Target customer profile
- `location_recommendation`: Suggested miles radius with reasoning
- `competitor_snapshot`: Competitive analysis
- `scenarios`: 3 media plans (standard/aggressive/experimental)
- `performance`: Predictions for each scenario with reach analytics
- `creatives`: Campaign ideas, slogans, ad copy, hashtags
- `critic_evaluation`: Quality score (0.0-1.0) and strengths
- `rag_insights`: Historical insights from vector database

### `POST /api/plan/plan-with-progress`
Generate a complete marketing plan with **real-time progress tracking** via Server-Sent Events.

**Request:** Same as `/plan` endpoint

**Response:** Same as `/plan` endpoint, but also streams progress updates via SSE

**How it works:**
1. Client submits plan generation request with a `session_id`
2. Server starts generating plan and streams progress updates via SSE
3. Client connects to `/api/plan/progress/{session_id}` to receive updates
4. When complete, server returns the full plan JSON

**Benefits over `/plan`:**
- Real-time visibility into which agent is currently running
- Better user experience with live progress bar
- No silent waiting period during 30-60 second plan generation

### `GET /api/plan/progress/{session_id}`
Server-Sent Events (SSE) endpoint for real-time progress updates.

**Response Format (SSE stream):**
```
event: progress
data: {"step": 1, "total_steps": 8, "progress_percent": 12, "agent_name": "RAGAgent", "status": "running", "message": "🔍 Retrieving historical insights...", "timestamp": "2025-11-17T09:35:20.713583"}

event: progress
data: {"step": 2, "total_steps": 8, "progress_percent": 25, "agent_name": "PersonaAgent", "status": "running", "message": "👥 Generating customer personas...", "timestamp": "2025-11-17T09:35:23.456789"}

...

event: progress
data: {"step": 8, "total_steps": 8, "progress_percent": 100, "agent_name": "CriticAgent", "status": "completed", "message": "✅ Plan evaluation complete!", "timestamp": "2025-11-17T09:35:55.123456"}
```

**Connection lifecycle:**
- Auto-closes when progress reaches 100%
- Sends keep-alive pings every 60 seconds if no updates
- Times out after 5 minutes (5 keep-alive pings) to prevent infinite loops
- Graceful error handling on client disconnect

### `POST /api/test-data/generate`
Generate realistic test data for example businesses.

**Request:**
```json
{
  "business_type": "coffee_shop"
}
```

**Options:** `coffee_shop`, `yoga_studio`, `boutique`

**Response:** Complete BusinessProfile with AI-generated realistic data.

### `GET /plan/{session_id}`
Retrieve a previously generated plan by session ID.

### `POST /feedback`
Submit feedback for a plan.

**Request:**
```json
{
  "session_id": "abc123",
  "plan_type": "aggressive",
  "rating": 5,
  "comments": "Excellent plan!"
}
```

### `GET /metrics`
Get system metrics and statistics.

**Response:**
```json
{
  "system": {
    "total_requests": 42,
    "success_rate": 0.95,
    "avg_latency_ms": 45230,
    "plans_generated": 40,
    "avg_critic_score": 0.82
  },
  "database": {
    "total_plans": 40,
    "total_feedback": 12
  },
  "feedback": {
    "avg_rating": 4.5
  }
}
```

### `GET /health`
Health check endpoint.

### `GET /download-pdf/{session_id}`
Download PDF report for a generated plan.

## 🧠 Agent Details

### 1. PersonaAgent

**Model:** `gemini-2.0-flash-exp`
**Temperature:** 0.7
**Purpose:** Generate ideal customer profiles

**Output Schema:**
```python
class Persona:
    name: str                    # e.g., "Sarah the Remote Worker"
    age_range: str               # e.g., "28-40"
    interests: List[str]         # e.g., ["specialty coffee", "coworking"]
    platforms: List[str]         # e.g., ["Instagram", "Google Maps"]
    creative_style: str          # e.g., "authentic, community-focused"
    motivation: str              # e.g., "seeks productive workspace"
```

### 2. LocationAgent

**Model:** `gemini-2.0-flash-exp`
**Temperature:** 0.3
**Purpose:** Recommend optimal advertising radius based on business type

**Business Categories:**
- **Daily Services** (coffee, lunch, gas): 2-5 miles
- **Weekly Services** (grocery, pharmacy): 5-10 miles
- **Monthly Services** (haircut, dentist): 8-15 miles
- **Occasional Retail** (clothing, electronics): 10-20 miles
- **Specialty/Destination** (jewelry, furniture): 15-30+ miles
- **Professional Services** (lawyer, accountant): 10-25 miles

**Output Schema:**
```python
class LocationRecommendation:
    current_miles: int              # User's selection
    suggested_miles: int            # AI recommendation
    business_type_category: str     # e.g., "Daily Services"
    typical_customer_travel: str    # e.g., "0.5-3 miles"
    reasoning: str                  # Detailed explanation
    optimization_factors: List[str] # Key considerations
```

### 3. CompetitorAgent

**Model:** `gemini-2.5-flash`
**Temperature:** 0.5
**Purpose:** Analyze competitive landscape

**Output Schema:**
```python
class CompetitorSnapshot:
    summary: str                   # Market overview
    strengths: List[str]           # What competitors do well
    weaknesses: List[str]          # Gaps in market
    opportunities: List[str]       # How to differentiate
    threats: List[str]             # Competitive risks
```

### 4. PlannerAgent

**Model:** `gemini-2.5-flash`
**Temperature:** 0.6
**Purpose:** Create 3 media plan scenarios with channel-specific budget allocation

**Output Schema:**
```python
class ScenarioSet:
    standard_plan: MediaPlan
    aggressive_plan: MediaPlan
    experimental_plan: MediaPlan

class MediaPlan:
    total_budget: float
    duration_weeks: int
    channels: List[Channel]        # e.g., Instagram, Google Ads, Local Radio

class Channel:
    name: str
    budget_share_percent: int      # % of total budget
    reasoning: str                 # Why this channel
```

### 5. CreativeAgent

**Model:** `gemini-2.5-flash`
**Temperature:** 0.9 (high creativity)
**Purpose:** Generate creative assets and campaign ideas

**MCP Integration:** Fetches images via Google Image Search MCP Server

**Output Schema:**
```python
class CreativeAssets:
    ideas: List[CampaignIdea]      # 3 ideas with images
    slogans: List[str]             # 3 slogans
    hashtags: List[str]            # 10 hashtags
    short_ad_copy: str             # 12-20 words
    long_ad_copy: str              # 60-120 words
    cta_options: List[str]         # 3 CTAs

class CampaignIdea:
    title: str
    description: str
    image_url: str                 # Fetched from MCP server
    image_prompt: str
    image_alt: str
```

### 6. PerformanceAgent

**Model:** `gemini-2.0-flash-exp`
**Temperature:** 0.4
**Purpose:** Predict campaign performance with reach analytics and budget scaling

**Calculations:**
- **Reach Analytics**: Percentage of target population (local = 500k, national = 10M)
- **Budget Scaling**: How much budget to double reach, with efficiency warnings

**Output Schema:**
```python
class PerformancePrediction:
    reach: str                     # e.g., "15,000-25,000"
    clicks: str                    # e.g., "1,200-2,000"
    cpc_estimate: str              # e.g., "$1.50-$2.50"
    roi_range: str                 # e.g., "2.5x-4.0x"
    reach_analytics: dict          # Percentage calculations
    budget_scaling: dict           # To double reach
```

### 7. CriticAgent

**Model:** `gemini-2.0-flash-exp`
**Temperature:** 0.2 (low for consistency)
**Purpose:** Evaluate plan quality and provide recommendations

**Evaluation Criteria:**
- Channel mix quality
- Budget allocation logic
- Persona alignment
- Competitor differentiation
- Creative integration
- Feasibility and realism

**Output Schema:**
```python
class CriticEvaluation:
    overall_score: float           # 0.0-1.0
    strengths: List[str]           # What works well
    recommendations: List[str]     # Only if score < 0.70
```

## 🧪 Testing Architecture

### Layer 1: Unit Tests (pytest)

**Location:** `tests/`
**Run:** `pytest tests/`

**What we test:**
- Individual agent outputs match Pydantic schemas
- Memory layer (SQLite + ChromaDB) CRUD operations
- PDF generation
- API endpoint responses

**Example:**
```python
def test_persona_agent():
    agent = PersonaAgent(GEMINI_API_KEY)
    profile = BusinessProfile(...)
    persona = agent.generate_persona(profile)
    assert persona.name
    assert len(persona.interests) > 0
```

### Layer 2: Evaluation Gates (AI Quality Testing)

**Location:** `app/evaluation/`
**Run:** `python -m app.evaluation.eval_runner`

**What we test:**
- AI agent quality across 15 diverse business scenarios
- Average critic score across all scenarios
- Consistency of structured outputs
- Performance benchmarking

**Test Scenarios:**
1. Local coffee shop (Seattle)
2. Yoga studio (Denver)
3. Fashion boutique (NYC)
4. Pet grooming (Austin)
5. Pizza restaurant (Chicago)
6. ... (10 more diverse scenarios)

**Output:**
- `evaluation_results.json` with all generated plans
- Statistics: avg score, min/max scores, success rate
- Performance: total time, avg time per plan

### Layer 3: Playwright E2E Tests (Browser Testing)

**Location:** `playwright_tests/` and `tests/test_ui_playwright.py`
**Run:** `pytest tests/test_ui_playwright.py`

**What we test:**
- Full user workflow: fill form → submit → view results
- Test data button functionality
- PDF download
- UI rendering and responsiveness

**Example:**
```python
async def test_coffee_shop_example_loads(page):
    await page.goto("http://localhost:8000")
    await page.click("text=Try Coffee Shop Example")
    await expect(page.locator("#business_name")).to_have_value(".*Coffee.*")
```

**Current Status:**
- 3/9 tests passing
- 6 tests need selector updates (work in progress)

### Running All Tests

```bash
# Quick unit tests
pytest tests/ -v

# Full evaluation (15 scenarios, ~10-15 minutes)
python -m app.evaluation.eval_runner

# Playwright E2E (requires running server)
pytest tests/test_ui_playwright.py

# Quick evaluation (3 scenarios)
./run_evaluation.sh quick
```

## 🖼️ MCP Server - Image Search Integration

### What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI models to external tools and data sources. Our application uses an MCP server to enhance CreativeAgent with Google Image Search capabilities.

### MCP Server Architecture

```
┌─────────────────────────────────────────────────────┐
│              CreativeAgent (Gemini AI)              │
│  "I need an image for a coffee shop campaign"      │
└───────────────────────┬─────────────────────────────┘
                        │ MCP Protocol
                        ▼
┌─────────────────────────────────────────────────────┐
│         MCP Image Search Server (Python)            │
│  • Receives search query via MCP                    │
│  • Searches Google Images (SerpAPI)                 │
│  • Fallback to Unsplash API                         │
│  • Fallback to Lorem Picsum                         │
│  • Returns image URLs via MCP                       │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Image Sources   │
              │  • SerpAPI       │
              │  • Unsplash      │
              │  • Picsum        │
              └──────────────────┘
```

### MCP Server Implementation

**File:** `mcp_servers/image_search_server.py`

**Key Features:**
- Implements MCP protocol with `search_images` tool
- 3-tier fallback: SerpAPI → Unsplash → Picsum
- Safe search enabled
- Returns structured JSON with image URLs and metadata

**Usage in CreativeAgent:**
```python
async def _fetch_images_for_ideas(self, assets, profile):
    for idea in assets.ideas:
        search_query = f"{profile.business_type} {idea.title} marketing"

        # Calls MCP server via HTTP
        image_url = await self._fetch_serpapi_image(search_query)

        if image_url:
            idea.image_url = image_url
            idea.image_prompt = search_query
```

### Setting Up MCP Server

**For Playwright MCP (Claude Desktop integration):**

1. Install Playwright MCP:
```bash
npm install -g @playwright/mcp
```

2. Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"],
      "env": {}
    }
  }
}
```

3. Restart Claude Desktop

**For Python Image Search (used by CreativeAgent):**

Already integrated in `creative_agent.py` - no additional setup needed beyond API keys.

## 📈 Monitoring & Observability

### Metrics Endpoint

Access real-time metrics at `http://localhost:8000/metrics`

**Returns:**
```json
{
  "system": {
    "total_requests": 150,
    "success_rate": 0.94,
    "avg_latency_ms": 42000,
    "plans_generated": 141,
    "avg_critic_score": 0.83,
    "agent_calls": {
      "PersonaAgent": 141,
      "LocationAgent": 141,
      "CompetitorAgent": 141,
      "PlannerAgent": 141,
      "CreativeAgent": 141,
      "PerformanceAgent": 141,
      "CriticAgent": 141
    },
    "recent_errors": [...]
  },
  "database": {
    "total_sessions": 85,
    "total_plans": 141,
    "total_feedback": 23
  },
  "feedback": {
    "avg_rating": 4.2,
    "total_feedback": 23
  }
}
```

### Logging

**Middleware:** `app/observability/logging_middleware.py`

All requests logged with:
- Request method, path, user agent
- Response status, duration
- Structured format for parsing

**Agent Logger:** `app/observability/agent_logger.py`

Tracks:
- Individual agent execution times
- Success/failure rates
- Plan generation metrics
- Critic scores

### Example Log Output

```
INFO: PersonaAgent.generate_persona completed in 2.34s (success)
INFO: LocationAgent.recommend_miles completed in 1.89s (success)
INFO: CompetitorAgent.analyze_competitors completed in 3.12s (success)
INFO: PlannerAgent.generate_scenarios completed in 5.67s (success)
INFO: CreativeAgent.generate_assets completed in 8.45s (success)
INFO: PerformanceAgent.predict_performance completed in 3.21s (success)
INFO: CriticAgent.evaluate_plan completed in 2.78s (success)
INFO: Plan generation completed for session abc123 in 27.46s with score 0.85
```

## 🔧 Configuration

### Environment Variables

**Required:**
- `GEMINI_API_KEY`: Your Google Gemini API key ([Get it here](https://aistudio.google.com/))

**Optional:**
- `SERPAPI_KEY`: For enhanced Google Image Search
- `UNSPLASH_ACCESS_KEY`: For Unsplash image fallback
- `SQLITE_DB_PATH`: Path to SQLite database (default: `ad_planner.db`)
- `VECTOR_STORE_PATH`: Path to ChromaDB storage (default: `./vector_store`)

### Model Configuration

All agents use Google Gemini models. You can customize in `app/agents/base_agent.py`:

```python
# Current model assignments
PersonaAgent:      gemini-2.0-flash-exp  (temp: 0.7)
LocationAgent:     gemini-2.0-flash-exp  (temp: 0.3)
CompetitorAgent:   gemini-2.5-flash      (temp: 0.5)
PlannerAgent:      gemini-2.5-flash      (temp: 0.6)
CreativeAgent:     gemini-2.5-flash      (temp: 0.9)
PerformanceAgent:  gemini-2.0-flash-exp  (temp: 0.4)
CriticAgent:       gemini-2.0-flash-exp  (temp: 0.2)
```

### Database Access

**View your database:**
```bash
# Quick summary view
python3 view_db.py

# SQLite command line
sqlite3 ad_planner.db
.tables
SELECT * FROM plans ORDER BY created_at DESC LIMIT 5;

# Or use GUI tools
brew install --cask db-browser-for-sqlite
open -a "DB Browser for SQLite" ad_planner.db
```

**Database Locations:**
- **SQLite**: `ad_planner.db` (332 KB, 17 users, 14 plans)
- **ChromaDB**: `vector_store/` directory (vector embeddings)

**For complete database documentation**, see `DATABASE_INFO.md`.

## 🎯 Usage Example

### Web UI Flow

1. **Navigate to** `http://localhost:8000`

2. **Try an example** by clicking one of the test data buttons:
   - ☕ Try Coffee Shop Example
   - 🧘 Try Yoga Studio Example
   - 👗 Try Fashion Boutique Example

3. **Review auto-filled form**:
   - Business name, type, ZIP code
   - Miles radius (with explanation)
   - Marketing goal (detailed, multi-sentence)
   - Monthly budget (with ROI explanation)
   - Campaign duration (with momentum explanation)
   - Competitors (with differentiation explanation)

4. **Click "Generate Marketing Plan"**

5. **Wait 30-60 seconds** while agents work:
   - Generating persona...
   - Analyzing location...
   - Studying competitors...
   - Creating scenarios...
   - Designing creatives...
   - Predicting performance...
   - Evaluating quality...

6. **View comprehensive results**:

   **🎯 Target Persona**
   - Name, age range, interests
   - Platform preferences
   - Creative style and motivation

   **📍 Location Recommendation**
   - Your selection vs. AI recommendation
   - Business category and typical travel
   - Reasoning and optimization factors

   **📊 Media Plan Scenarios**
   - Standard, Aggressive, Experimental plans
   - Channel breakdowns with budget percentages
   - Expected reach with percentage infographics
   - Clicks, CPC, ROI predictions

   **💰 Budget Scaling**
   - Current budget and reach
   - Recommended budget to double reach
   - Cost per person efficiency analysis
   - Diminishing returns warnings

   **🎨 Creative Assets**
   - 3 campaign ideas with AI-searched images
   - 10 relevant hashtags
   - 3 catchy slogans
   - Short and long ad copy
   - 3 CTA options

   **💡 Plan Strengths**
   - Key advantages with emoji icons
   - Overall quality score (0.0-1.0)

7. **Download PDF Report**

### Programmatic API Usage

```python
import requests

# Generate plan
response = requests.post("http://localhost:8000/plan", json={
    "profile": {
        "business_name": "Joe's Coffee Shop",
        "business_type": "Coffee Shop",
        "zip_code": "94102",
        "miles_radius": 3,
        "goal": "Increase morning traffic by 30% targeting remote workers",
        "monthly_budget": 2500.0,
        "duration_weeks": 8,
        "is_local": True,
        "competitors": ["Starbucks", "Blue Bottle"]
    }
})

plan = response.json()

print(f"Session ID: {plan['session_id']}")
print(f"Persona: {plan['persona']['name']}")
print(f"Recommended Radius: {plan['location_recommendation']['suggested_miles']} miles")
print(f"Critic Score: {plan['critic_evaluation']['overall_score']}")

# Download PDF
pdf_response = requests.get(
    f"http://localhost:8000/download-pdf/{plan['session_id']}"
)
with open("marketing_plan.pdf", "wb") as f:
    f.write(pdf_response.content)
```

## 🚀 Deployment Options

### Railway

```bash
railway init
railway up
railway variables set GEMINI_API_KEY=your-key-here
```

### Fly.io

```bash
fly launch
fly secrets set GEMINI_API_KEY=your-key-here
fly deploy
```

### Render

1. Connect your GitHub repository
2. Set environment variable: `GEMINI_API_KEY`
3. Deploy with one click

### Heroku

```bash
heroku create smart-ad-planner
heroku config:set GEMINI_API_KEY=your-key-here
git push heroku main
```

### Azure App Service

Use the Azure CLI or portal to deploy the Docker container:

```bash
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name smart-ad-planner --deployment-container-image-name smart-ad-planner:latest
az webapp config appsettings set --resource-group myResourceGroup --name smart-ad-planner --settings GEMINI_API_KEY=your-key-here
```

## 📝 Future Enhancements

- [ ] **A2A Protocol**: Agent-to-Agent communication for collaborative planning
- [ ] **Real-time Collaboration**: Multiple users working on same plan
- [ ] **Ad Platform Integration**: Direct Google Ads, Facebook Ads API integration
- [ ] **Advanced Analytics Dashboard**: Track campaign performance over time
- [ ] **Multi-language Support**: Generate plans in multiple languages
- [ ] **Budget Optimization Algorithms**: ML-based budget allocation
- [ ] **A/B Testing Recommendations**: Suggest campaign variations to test
- [ ] **Competitive Intelligence**: Real-time competitor ad monitoring
- [ ] **Image Generation**: DALL-E/Imagen integration for custom visuals
- [ ] **Voice Input**: Voice-to-text for business profile input
- [ ] **Mobile App**: Native iOS/Android applications

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Ensure all tests pass before submitting PR
- Use type hints for all functions
- Add docstrings to all classes and methods

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini** for powerful AI models
- **FastAPI** for modern, fast web framework
- **Pydantic** for robust data validation
- **ChromaDB** for vector storage
- **ReportLab** for PDF generation
- **Playwright** for browser automation
- **pytest** for testing framework
- **MCP (Model Context Protocol)** for tool integration

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY environment variable must be set"**
- Make sure you've exported the API key: `export GEMINI_API_KEY="your-key"`
- Or create a `.env` file with the key

**2. "Failed to generate marketing plan"**
- Check your Gemini API quota and billing
- Verify API key is valid
- Check server logs for detailed error messages

**3. "ZIP code and miles radius not populating from test data"**
- This was fixed in `app/api/test_data.py` with backward compatibility
- Restart the server to pick up changes

**4. "Budget field validation error"**
- This was fixed by removing `step="100"` attribute
- Update your `index.html` if using older version

**5. Images not loading in creative assets**
- Set `SERPAPI_KEY` for Google Image Search
- Falls back to Unsplash (requires `UNSPLASH_ACCESS_KEY`)
- Final fallback: Lorem Picsum (no key needed)

**6. "ChromaDB not available" warning**
- ✅ **Fixed**: ChromaDB 1.3.4 is now installed and active by default
- Vector memory features are fully enabled
- If you see this warning, run: `pip install chromadb`

### Recent Improvements (2025)

**Code Organization & Cleanup:**
- ✅ Created `app/utils/` directory for better organization
- ✅ Moved PDF generation and analytics utilities to `app/utils/`
- ✅ Removed redundant code (`image_generator.py`, `mcp_client.py`)
- ✅ Clean imports: `from app.utils import PDFGenerator, calculate_reach_percentage, calculate_budget_scaling`

**Database Enhancements:**
- ✅ ChromaDB 1.3.4 activated for vector search and semantic similarity
- ✅ Dual-database architecture: SQLite (structured) + ChromaDB (vector)
- ✅ Persistent storage for both databases (survives restarts)
- ✅ 17 users and 14 plans tracked in production database

**What This Means:**
- More organized codebase with logical folder structure
- Faster development with clean separation of concerns
- Full vector search capabilities for historical plan analysis
- Better scalability and maintainability

### Debug Mode

Run with debug logging:
```bash
uvicorn app.main:app --reload --log-level debug
```

### Getting Help

- 📖 **Documentation**: Read this README and `PLAYWRIGHT_SETUP.md`
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ by Amit Dar for small businesses seeking smart marketing solutions**

**Powered by Google Gemini AI • FastAPI • ChromaDB • ReportLab**
