"""Main FastAPI Application"""
import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any

from .models import FullPlanOutput, FeedbackRequest, PlanRequest
from .schemas import BusinessProfile
from .agents import (
    PersonaAgent,
    CompetitorAgent,
    PlannerAgent,
    CreativeAgent,
    PerformanceAgent,
    CriticAgent,
    LocationAgent,
    RAGAgent
)
from .memory import SQLiteMemory, VectorMemory
from .observability import LoggingMiddleware, metrics_collector, agent_logger
from .utils import PDFGenerator, calculate_reach_percentage, calculate_budget_scaling
from .api import test_data, plan_with_progress

# Initialize FastAPI app
app = FastAPI(
    title="Smart Ad Planner",
    description="Multi-Agent Marketing Advisor",
    version="1.0.0"
)

# Include routers
app.include_router(test_data.router, prefix="/api/test-data", tags=["Test Data"])
app.include_router(
    plan_with_progress.router,
    prefix="/api/plan",
    tags=["Plan Generation"]
)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize components with Vertex AI and ADC
# No API key needed! Uses Application Default Credentials automatically
# Project ID is auto-detected from gcloud config

# Initialize memory
sqlite_memory = SQLiteMemory()
vector_memory = VectorMemory()

# Initialize agents with Google ADK (uses ADC)
persona_agent = PersonaAgent()
competitor_agent = CompetitorAgent()
planner_agent = PlannerAgent()
creative_agent = CreativeAgent()
performance_agent = PerformanceAgent()
critic_agent = CriticAgent()
location_agent = LocationAgent()
rag_agent = RAGAgent(vector_memory)  # RAG agent needs vector memory

# Initialize PDF generator
pdf_generator = PDFGenerator()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main form page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/plan")
async def create_plan(plan_request: PlanRequest) -> Dict[str, Any]:
    """Generate a complete marketing plan"""
    start_time = time.time()
    agent_call_count = 0

    try:
        profile = plan_request.profile

        # Generate or use existing session ID
        session_id = plan_request.session_id or str(uuid.uuid4())

        # Create user session
        user_id = sqlite_memory.get_user_by_session(session_id)
        if not user_id:
            user_id = sqlite_memory.create_session(session_id)

        # Store business profile in vector memory
        vector_memory.store_business_profile(session_id, profile.model_dump())

        # Step 0: RAG - Retrieve historical insights
        agent_start = time.time()
        rag_augmented = await rag_agent.augment_profile_with_insights(profile.model_dump())
        rag_insights = rag_augmented.get('rag_insights', {})
        agent_logger.log_agent_call(
            "RAGAgent", "augment_profile_with_insights",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 1: Generate Persona
        agent_start = time.time()
        persona = await persona_agent.generate_persona(profile)
        agent_logger.log_agent_call(
            "PersonaAgent", "generate_persona",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 2: Location Recommendation
        agent_start = time.time()
        location_recommendation = await location_agent.recommend_miles(profile)
        agent_logger.log_agent_call(
            "LocationAgent", "recommend_miles",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 3: Analyze Competitors
        agent_start = time.time()
        competitor_snapshot = await competitor_agent.analyze_competitors(
            profile.competitors if profile.competitors else ["Generic Competitor"],
            profile.business_type,
            profile.location
        )
        agent_logger.log_agent_call(
            "CompetitorAgent", "analyze_competitors",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 4: Generate Media Plan Scenarios
        agent_start = time.time()
        scenarios = await planner_agent.generate_scenarios(
            profile, persona, competitor_snapshot
        )
        agent_logger.log_agent_call(
            "PlannerAgent", "generate_scenarios",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 5: Generate Creative Assets
        agent_start = time.time()
        creatives = await creative_agent.generate_assets(profile, persona)
        agent_logger.log_agent_call(
            "CreativeAgent", "generate_assets",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 6: Predict Performance
        agent_start = time.time()
        performance_set = await performance_agent.predict_performance(
            scenarios, persona,
            profile.business_type,
            profile.location,
            profile.is_local
        )

        # Add reach analytics and budget scaling for each scenario
        performance_dict = performance_set.model_dump()
        scenarios_dict = scenarios.model_dump()

        for scenario_name in ['standard', 'aggressive', 'experimental']:
            scenario_perf = performance_dict[scenario_name]

            # Calculate reach analytics
            reach_analytics = calculate_reach_percentage(
                scenario_perf['reach'],
                profile.location,
                profile.is_local
            )
            scenario_perf['reach_analytics'] = reach_analytics

            # Calculate budget scaling (to double reach)
            scenario_plan_key = f"{scenario_name}_plan"
            scenario_budget = scenarios_dict[scenario_plan_key]['total_budget']

            budget_scaling = calculate_budget_scaling(
                current_budget=int(scenario_budget),
                current_reach_min=reach_analytics['reach_min'],
                current_reach_max=reach_analytics['reach_max'],
                target_multiplier=2.0
            )
            scenario_perf['budget_scaling'] = budget_scaling

        # Reconstruct performance_set with analytics
        from .schemas import PerformanceSet, PerformancePrediction
        performance_set = PerformanceSet(
            standard=PerformancePrediction(**performance_dict['standard']),
            aggressive=PerformancePrediction(**performance_dict['aggressive']),
            experimental=PerformancePrediction(**performance_dict['experimental'])
        )

        agent_logger.log_agent_call(
            "PerformanceAgent", "predict_performance",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Step 7: Critic Evaluation
        agent_start = time.time()
        critic_evaluation = await critic_agent.evaluate_plan(
            scenarios, persona, competitor_snapshot,
            creatives, profile.goal
        )
        agent_logger.log_agent_call(
            "CriticAgent", "evaluate_plan",
            time.time() - agent_start, True
        )
        agent_call_count += 1

        # Create full plan output
        full_plan = FullPlanOutput(
            session_id=session_id,
            persona=persona,
            location_recommendation=location_recommendation,
            competitor_snapshot=competitor_snapshot,
            scenarios=scenarios,
            performance=performance_set.model_dump(),
            creatives=creatives,
            critic_evaluation=critic_evaluation,
            rag_insights=rag_insights,  # Include RAG insights
            summary_text=f"Your personalized marketing plan for {profile.business_name} is ready!"
        )

        # Save to database
        sqlite_memory.save_plan(
            user_id,
            profile.model_dump(),
            full_plan.model_dump()
        )

        # Store in vector memory
        vector_memory.store_plan(
            session_id,
            f"plan_{int(time.time())}",
            full_plan.model_dump()
        )

        # Log metrics
        total_duration = time.time() - start_time
        agent_logger.log_plan_generation(
            session_id, total_duration,
            agent_call_count,
            critic_evaluation.get('overall_score', 0)
        )
        metrics_collector.record_request(True, total_duration * 1000)
        metrics_collector.record_plan(
            critic_evaluation.get('overall_score', 0),
            agent_call_count
        )

        return full_plan.model_dump()

    except Exception as e:
        metrics_collector.record_request(False, (time.time() - start_time) * 1000)
        metrics_collector.record_error(str(e), "create_plan")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plan/{session_id}")
async def get_plan(session_id: str) -> Dict[str, Any]:
    """Retrieve a plan by session ID"""
    try:
        # Try to get from vector memory first
        result = vector_memory.get_profile_history(session_id)
        if result:
            return {"status": "found", "data": result}

        # Fall back to SQLite
        user_id = sqlite_memory.get_user_by_session(session_id)
        if user_id:
            plans = sqlite_memory.get_recent_plans(limit=1)
            if plans:
                return {"status": "found", "data": plans[0]}

        raise HTTPException(status_code=404, detail="Plan not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback for a plan"""
    try:
        user_id = sqlite_memory.get_user_by_session(feedback.session_id)
        if not user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        sqlite_memory.save_feedback(
            user_id,
            feedback.plan_type,
            feedback.rating
        )

        vector_memory.store_feedback(
            feedback.session_id,
            feedback.plan_type,
            feedback.rating,
            feedback.comments
        )

        return {"status": "success", "message": "Feedback recorded"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        metrics = metrics_collector.get_metrics()
        db_metrics = sqlite_memory.get_metrics()
        feedback_stats = vector_memory.get_feedback_stats()

        return {
            "system": metrics,
            "database": db_metrics,
            "feedback": feedback_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Ad Planner",
        "version": "1.0.0"
    }


@app.get("/download-pdf/{session_id}")
async def download_pdf(session_id: str):
    """Generate and download PDF report"""
    try:
        # Get plan data
        user_id = sqlite_memory.get_user_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        plans = sqlite_memory.get_recent_plans(limit=1)
        if not plans:
            raise HTTPException(status_code=404, detail="No plans found")

        plan_data = plans[0]['plan']
        full_plan = FullPlanOutput(**plan_data)

        # Generate PDF
        pdf_path = pdf_generator.generate_report(full_plan)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
