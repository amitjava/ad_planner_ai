#!/usr/bin/env python3
"""
End-to-End Integration Test
Verifies the complete workflow from profile to evaluation
"""
# IMPORTANT: Configure SSL certificates BEFORE any other imports
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import asyncio
from app.schemas import BusinessProfile
from app.agents import (
    PersonaAgent, LocationAgent, CompetitorAgent,
    PlannerAgent, CreativeAgent, PerformanceAgent, CriticAgent
)

async def test_full_workflow():
    """Test the complete ad planning workflow"""

    print("=" * 60)
    print("TESTING COMPLETE WORKFLOW")
    print("=" * 60)

    # Create test profile
    profile = BusinessProfile(
        business_name="Test Coffee Shop",
        business_type="Coffee Shop",
        location="San Francisco, CA",
        zip_code="94107",
        miles_radius=3,
        goal="Increase weekday lunchtime traffic by 20%",
        monthly_budget=2500.0,
        duration_weeks=8,
        competitors=["Starbucks"],
        is_local=True
    )

    try:
        # Step 1: Personas
        print("\n[1/6] Generating personas...")
        persona_agent = PersonaAgent()
        personas = await persona_agent.generate_personas(profile, count=1)
        print(f"✅ Generated persona: {personas[0].name}")

        # Step 2: Location
        print("\n[2/6] Analyzing location...")
        location_agent = LocationAgent()
        location_analysis = await location_agent.analyze_location(profile)
        print(f"✅ Recommended miles: {location_analysis.suggested_miles}")

        # Step 3: Competitors
        print("\n[3/6] Analyzing competitors...")
        competitor_agent = CompetitorAgent()
        competitor_analysis = await competitor_agent.analyze_competitors(
            profile.competitors,
            profile.business_type,
            profile.location
        )
        print(f"✅ Analyzed {len(competitor_analysis.competitors)} competitors")

        # Step 4: Scenarios
        print("\n[4/6] Generating budget scenarios...")
        planner_agent = PlannerAgent()
        scenarios = await planner_agent.generate_scenarios(
            profile, personas[0], competitor_analysis
        )
        print(f"✅ Generated 3 scenarios")

        # Step 5: Creative Assets
        print("\n[5/6] Generating creative assets...")
        creative_agent = CreativeAgent()
        creative_assets = await creative_agent.generate_assets(profile, personas[0])
        print(f"✅ Generated {len(creative_assets.ideas)} creative ideas")

        # Step 6: Performance
        print("\n[6/6] Predicting performance...")
        performance_agent = PerformanceAgent()
        performance = await performance_agent.predict_performance(
            scenarios, personas[0], profile.business_type, profile.location, profile.is_local
        )
        print(f"✅ Generated performance predictions")

        # Step 7: Evaluation
        print("\n[7/7] Evaluating plan...")
        critic_agent = CriticAgent()
        evaluation = await critic_agent.evaluate_plan(
            scenarios=scenarios,
            persona=personas[0],
            competitor_snapshot=competitor_analysis,
            creatives=creative_assets,
            business_goal=profile.goal
        )
        print(f"✅ Overall score: {evaluation['overall_score']:.2f}")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - WORKFLOW COMPLETE!")
        print("=" * 60)

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_workflow())
    exit(0 if success else 1)
