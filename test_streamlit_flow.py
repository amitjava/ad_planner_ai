#!/usr/bin/env python3
"""
Test Streamlit App Flow
Simulates the exact flow of the Streamlit app
"""
# IMPORTANT: Configure SSL certificates BEFORE any other imports
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import asyncio
import time
from app.schemas import BusinessProfile
from app.agents import (
    PersonaAgent, LocationAgent, CompetitorAgent,
    PlannerAgent, CreativeAgent, PerformanceAgent,
    CriticAgent, RAGAgent
)
from app.memory.vector_memory import VectorMemory

async def generate_plan_async(profile):
    """Simulate the exact Streamlit generate_plan_async function"""

    start_time = time.time()

    # Initialize agents
    print("Initializing agents...")
    agents = {
        'persona': PersonaAgent(),
        'location': LocationAgent(),
        'competitor': CompetitorAgent(),
        'planner': PlannerAgent(),
        'creative': CreativeAgent(),
        'performance': PerformanceAgent(),
        'critic': CriticAgent(),
        'rag': RAGAgent(VectorMemory())
    }

    # Step 0: RAG
    print("\n[0/7] Retrieving historical insights...")
    rag_augmented = await agents['rag'].augment_profile_with_insights(profile.model_dump())
    rag_insights = rag_augmented.get('rag_insights', {})
    print(f"✅ Retrieved RAG insights")

    # Step 1: Personas
    print("\n[1/7] Generating customer personas...")
    personas = await agents['persona'].generate_personas(profile)
    print(f"✅ Generated {len(personas)} personas: {[p.name for p in personas]}")

    # Step 2: Location
    print("\n[2/7] Analyzing location demographics...")
    location_analysis = await agents['location'].analyze_location(profile)
    print(f"✅ Location analysis complete (suggested: {location_analysis.suggested_miles} miles)")

    # Step 3: Competitors
    print("\n[3/7] Researching competitors...")
    competitor_analysis = await agents['competitor'].analyze_competitors(
        profile.competitors if profile.competitors else ["Generic Competitor"],
        profile.business_type,
        profile.location
    )
    print(f"✅ Analyzed {len(competitor_analysis.competitors)} competitors")

    # Step 4: Budget Scenarios
    print("\n[4/7] Creating budget scenarios...")
    scenarios = await agents['planner'].generate_scenarios(
        profile, personas[0], competitor_analysis
    )
    print(f"✅ Generated 3 budget scenarios")

    # Step 5: Creative Assets
    print("\n[5/7] Generating creative assets...")
    creative_assets = await agents['creative'].generate_assets(profile, personas[0])
    print(f"✅ Generated {len(creative_assets.ideas)} creative ideas")

    # Step 6: Performance Predictions
    print("\n[6/7] Predicting performance metrics...")
    performance = await agents['performance'].predict_performance(
        scenarios, personas[0], profile.business_type, profile.location, profile.is_local
    )
    print(f"✅ Performance predictions complete")

    # Step 7: Evaluation
    print("\n[7/7] Evaluating plan quality...")
    evaluation = await agents['critic'].evaluate_plan(
        scenarios=scenarios,
        persona=personas[0],
        competitor_snapshot=competitor_analysis,
        creatives=creative_assets,
        business_goal=profile.goal
    )
    print(f"✅ Plan evaluation complete (score: {evaluation['overall_score']:.2f})")

    # Build full plan for return
    full_plan = {
        "persona": personas[0].model_dump(),
        "personas": [p.model_dump() for p in personas],
        "location_analysis": location_analysis.model_dump(),
        "competitor_analysis": competitor_analysis.model_dump(),
        "scenarios": scenarios.model_dump(),
        "creative_assets": creative_assets.model_dump(),
        "performance": performance.model_dump()
    }

    generation_time = time.time() - start_time

    return {
        "profile": profile.model_dump(),
        "rag_insights": rag_insights,
        "personas": [p.model_dump() for p in personas],
        "location_analysis": location_analysis.model_dump(),
        "competitor_analysis": competitor_analysis.model_dump(),
        "scenarios": scenarios.model_dump(),
        "creative_assets": creative_assets.model_dump(),
        "performance": performance.model_dump(),
        "critic_evaluation": evaluation,  # Already a dict, no .model_dump()
        "generation_time": generation_time
    }

async def test_streamlit_flow():
    """Test the complete Streamlit app flow"""

    print("=" * 70)
    print("TESTING STREAMLIT APP FLOW")
    print("=" * 70)

    # Create test profile
    profile = BusinessProfile(
        business_name="Joe's Coffee Shop",
        business_type="Coffee Shop",
        location="San Francisco, CA",
        zip_code="94107",
        miles_radius=3,
        goal="Increase weekday lunchtime traffic by 20%",
        monthly_budget=2500.0,
        duration_weeks=8,
        competitors=["Starbucks", "Blue Bottle Coffee"],
        is_local=True
    )

    try:
        plan_data = await generate_plan_async(profile)

        print("\n" + "=" * 70)
        print("✅ STREAMLIT FLOW TEST PASSED!")
        print("=" * 70)
        print(f"\nGeneration time: {plan_data['generation_time']:.2f} seconds")
        print(f"Overall score: {plan_data['critic_evaluation']['overall_score']:.2f}")
        print(f"Personas: {len(plan_data['personas'])}")
        print(f"Creative ideas: {len(plan_data['creative_assets']['ideas'])}")

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ STREAMLIT FLOW TEST FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_streamlit_flow())
    exit(0 if success else 1)
