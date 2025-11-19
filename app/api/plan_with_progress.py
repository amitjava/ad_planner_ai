"""
Plan generation endpoint with real-time progress tracking
"""
import time
import uuid
import asyncio
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from ..models import PlanRequest
from ..schemas import BusinessProfile
from ..agents import (
    PersonaAgent, CompetitorAgent, PlannerAgent,
    CreativeAgent, PerformanceAgent, CriticAgent,
    LocationAgent, RAGAgent
)
from ..memory import SQLiteMemory, VectorMemory
from ..observability import agent_logger
from ..progress_tracker import progress_tracker, AGENT_STEPS, get_agent_step_info
from ..utils import calculate_reach_percentage, calculate_budget_scaling

router = APIRouter()

# Initialize components
sqlite_memory = SQLiteMemory()
vector_memory = VectorMemory()

# Initialize agents
persona_agent = PersonaAgent()
location_agent = LocationAgent()
competitor_agent = CompetitorAgent()
planner_agent = PlannerAgent()
creative_agent = CreativeAgent()
performance_agent = PerformanceAgent()
critic_agent = CriticAgent()
rag_agent = RAGAgent(vector_memory)


@router.get("/progress/{session_id}")
async def stream_progress(session_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates
    """
    queue = await progress_tracker.subscribe(session_id)

    async def event_generator():
        keep_alive_count = 0
        max_keep_alives = 5  # Maximum 5 minutes of waiting (5 * 60s)

        try:
            while True:
                # Wait for update with timeout
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=60.0)
                    keep_alive_count = 0  # Reset counter on successful update
                    yield {
                        "event": "progress",
                        "data": json.dumps(update)
                    }

                    # Stop if completed
                    if update.get("progress_percent") == 100:
                        break

                except asyncio.TimeoutError:
                    keep_alive_count += 1
                    if keep_alive_count >= max_keep_alives:
                        # Stop after too many keep-alives to prevent infinite loop
                        yield {
                            "event": "error",
                            "data": json.dumps({"status": "timeout", "message": "No progress updates received"})
                        }
                        break

                    # Send keep-alive
                    yield {
                        "event": "ping",
                        "data": json.dumps({"status": "alive"})
                    }

        finally:
            progress_tracker.unsubscribe(session_id)

    return EventSourceResponse(event_generator())


@router.post("/plan-with-progress")
async def create_plan_with_progress(plan_request: PlanRequest) -> Dict[str, Any]:
    """
    Generate a complete marketing plan with real-time progress updates
    """
    start_time = time.time()
    total_steps = len(AGENT_STEPS)

    try:
        profile = plan_request.profile
        session_id = plan_request.session_id or str(uuid.uuid4())

        # Create user session
        user_id = sqlite_memory.get_user_by_session(session_id)
        if not user_id:
            user_id = sqlite_memory.create_session(session_id)

        # Store business profile in vector memory
        vector_memory.store_business_profile(session_id, profile.model_dump())

        # Step 1: RAG Agent
        await progress_tracker.update_progress(
            session_id, 1, total_steps, "RAGAgent", "running",
            "🔍 Retrieving historical insights from vector database..."
        )
        agent_start = time.time()
        rag_augmented = await rag_agent.augment_profile_with_insights(profile.model_dump())
        rag_insights = rag_augmented.get('rag_insights', {})
        agent_logger.log_agent_call(
            "RAGAgent", "augment_profile_with_insights",
            time.time() - agent_start, True
        )

        # Step 2: Persona Agent
        await progress_tracker.update_progress(
            session_id, 2, total_steps, "PersonaAgent", "running",
            "👥 Generating 3 detailed customer personas..."
        )
        agent_start = time.time()
        persona = await persona_agent.generate_persona(profile)
        agent_logger.log_agent_call(
            "PersonaAgent", "generate_persona",
            time.time() - agent_start, True
        )

        # Step 3: Location Agent
        await progress_tracker.update_progress(
            session_id, 3, total_steps, "LocationAgent", "running",
            "📍 Analyzing location demographics and optimal radius..."
        )
        agent_start = time.time()
        location_recommendation = await location_agent.recommend_miles(profile)
        agent_logger.log_agent_call(
            "LocationAgent", "recommend_miles",
            time.time() - agent_start, True
        )

        # Step 4: Competitor Agent
        await progress_tracker.update_progress(
            session_id, 4, total_steps, "CompetitorAgent", "running",
            "🏆 Researching competitors and market opportunities..."
        )
        agent_start = time.time()
        competitor_snapshot = await competitor_agent.analyze_competitors(
            profile.competitors if profile.competitors else ["Generic Competitor"],
            profile.business_type,
            f"{profile.zip_code}"  # Use ZIP code as location
        )
        agent_logger.log_agent_call(
            "CompetitorAgent", "analyze_competitors",
            time.time() - agent_start, True
        )

        # Step 5: Planner Agent
        await progress_tracker.update_progress(
            session_id, 5, total_steps, "PlannerAgent", "running",
            "💰 Creating 3 budget scenarios with channel allocation..."
        )
        agent_start = time.time()
        scenarios = await planner_agent.generate_scenarios(
            profile, persona, competitor_snapshot
        )
        agent_logger.log_agent_call(
            "PlannerAgent", "generate_scenarios",
            time.time() - agent_start, True
        )

        # Step 6: Creative Agent
        await progress_tracker.update_progress(
            session_id, 6, total_steps, "CreativeAgent", "running",
            "🎨 Generating creative assets and ad copy..."
        )
        agent_start = time.time()
        creatives = await creative_agent.generate_assets(profile, persona)
        agent_logger.log_agent_call(
            "CreativeAgent", "generate_assets",
            time.time() - agent_start, True
        )

        # Step 7: Performance Agent
        await progress_tracker.update_progress(
            session_id, 7, total_steps, "PerformanceAgent", "running",
            "📈 Predicting performance metrics and ROI..."
        )
        agent_start = time.time()
        performance = await performance_agent.predict_performance(
            scenarios, persona, profile.business_type, f"{profile.zip_code}", profile.is_local
        )
        agent_logger.log_agent_call(
            "PerformanceAgent", "predict_performance",
            time.time() - agent_start, True
        )

        # Add reach analytics and budget scaling for each scenario
        performance_dict = performance.model_dump()
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

        # Reconstruct performance with analytics
        from ..schemas import PerformanceSet, PerformancePrediction
        performance = PerformanceSet(
            standard=PerformancePrediction(**performance_dict['standard']),
            aggressive=PerformancePrediction(**performance_dict['aggressive']),
            experimental=PerformancePrediction(**performance_dict['experimental'])
        )

        # Step 8: Critic Agent
        await progress_tracker.update_progress(
            session_id, 8, total_steps, "CriticAgent", "running",
            "✅ Evaluating plan quality and scoring..."
        )
        agent_start = time.time()
        evaluation = await critic_agent.evaluate_plan(
            scenarios, persona, competitor_snapshot, creatives, profile.goal
        )
        agent_logger.log_agent_call(
            "CriticAgent", "evaluate_plan",
            time.time() - agent_start, True
        )

        # Mark as complete
        await progress_tracker.update_progress(
            session_id, total_steps, total_steps, "Complete", "done",
            "✨ Marketing plan generation complete!"
        )

        # Prepare response
        generation_time = time.time() - start_time

        result = {
            "session_id": session_id,
            "persona": persona,
            "location_recommendation": location_recommendation,
            "competitor_snapshot": competitor_snapshot,
            "scenarios": scenarios,
            "performance": performance.model_dump(),
            "creatives": creatives,
            "critic_evaluation": evaluation,  # Match the field name from /plan endpoint
            "rag_insights": rag_insights,
            "summary_text": f"Your personalized marketing plan for {profile.business_name} is ready!"
        }

        # Convert result to dict for database storage (serialize Pydantic models)
        result_for_db = {
            "session_id": session_id,
            "persona": persona.model_dump() if hasattr(persona, 'model_dump') else persona,
            "location_recommendation": location_recommendation.model_dump() if hasattr(location_recommendation, 'model_dump') else location_recommendation,
            "competitor_snapshot": competitor_snapshot.model_dump() if hasattr(competitor_snapshot, 'model_dump') else competitor_snapshot,
            "scenarios": scenarios.model_dump() if hasattr(scenarios, 'model_dump') else scenarios,
            "performance": performance.model_dump(),
            "creatives": creatives.model_dump() if hasattr(creatives, 'model_dump') else creatives,
            "critic_evaluation": evaluation,
            "rag_insights": rag_insights,
            "summary_text": f"Your personalized marketing plan for {profile.business_name} is ready!"
        }

        # Store plan in databases
        sqlite_memory.save_plan(user_id, profile.model_dump(), result_for_db)
        vector_memory.store_plan(session_id, f"plan_{int(time.time())}", result_for_db)

        return result

    except Exception as e:
        # Send error update
        await progress_tracker.update_progress(
            session_id, 0, total_steps, "Error", "error",
            f"❌ Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))
