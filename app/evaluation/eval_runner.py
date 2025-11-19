"""Agent Evaluation Runner"""
import os
import sys
import json
import asyncio
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.schemas import BusinessProfile
from app.agents import (
    PersonaAgent,
    CompetitorAgent,
    PlannerAgent,
    CreativeAgent,
    PerformanceAgent,
    CriticAgent
)


class EvaluationRunner:
    """Runs evaluation tests on the agent system"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.persona_agent = PersonaAgent(api_key)
        self.competitor_agent = CompetitorAgent(api_key)
        self.planner_agent = PlannerAgent(api_key)
        self.creative_agent = CreativeAgent(api_key)
        self.performance_agent = PerformanceAgent(api_key)
        self.critic_agent = CriticAgent(api_key)

    def get_test_profiles(self) -> List[BusinessProfile]:
        """Get predefined test business profiles"""
        return [
            BusinessProfile(
                business_name="Joe's Coffee Shop",
                business_type="Coffee Shop",
                location="San Francisco, CA",
                goal="Increase foot traffic and brand awareness",
                monthly_budget=2500.0,
                duration_weeks=8,
                is_local=True,
                competitors=["Starbucks", "Blue Bottle Coffee"]
            ),
            BusinessProfile(
                business_name="TechStart SaaS",
                business_type="B2B SaaS Company",
                location="Austin, TX",
                goal="Generate qualified leads for enterprise software",
                monthly_budget=10000.0,
                duration_weeks=12,
                is_local=False,
                competitors=["Salesforce", "HubSpot"]
            ),
            BusinessProfile(
                business_name="Green Valley Yoga",
                business_type="Yoga Studio",
                location="Portland, OR",
                goal="Grow membership and class attendance",
                monthly_budget=1500.0,
                duration_weeks=6,
                is_local=True,
                competitors=["CorePower Yoga", "LA Fitness"]
            ),
            BusinessProfile(
                business_name="Urban Threads Boutique",
                business_type="Fashion Boutique",
                location="New York, NY",
                goal="Drive online and in-store sales",
                monthly_budget=5000.0,
                duration_weeks=10,
                is_local=True,
                competitors=["Zara", "Urban Outfitters"]
            ),
            BusinessProfile(
                business_name="Peak Performance Gym",
                business_type="Fitness Center",
                location="Denver, CO",
                goal="Increase memberships and personal training sign-ups",
                monthly_budget=3500.0,
                duration_weeks=8,
                is_local=True,
                competitors=["24 Hour Fitness", "Anytime Fitness"]
            )
        ]

    async def run_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation on all test profiles"""
        print("=" * 60)
        print("AGENT EVALUATION RUNNER")
        print("=" * 60)

        test_profiles = self.get_test_profiles()
        results = []

        for i, profile in enumerate(test_profiles, 1):
            print(f"\nTest {i}/{len(test_profiles)}: {profile.business_name}")
            print("-" * 60)

            try:
                # Generate persona
                print("  Generating persona...")
                persona = self.persona_agent.generate_persona(profile)

                # Analyze competitors
                print("  Analyzing competitors...")
                competitor_snapshot = self.competitor_agent.analyze_competitors(
                    profile.competitors,
                    profile.business_type,
                    profile.location
                )

                # Generate scenarios
                print("  Creating media plans...")
                scenarios = self.planner_agent.generate_scenarios(
                    profile, persona, competitor_snapshot
                )

                # Generate creatives
                print("  Generating creative assets...")
                creatives = await self.creative_agent.generate_assets(profile, persona)

                # Predict performance
                print("  Predicting performance...")
                performance_set = self.performance_agent.predict_performance(
                    scenarios, persona,
                    profile.business_type,
                    profile.location,
                    profile.is_local
                )

                # Evaluate with critic
                print("  Running critic evaluation...")
                critic_evaluation = self.critic_agent.evaluate_plan(
                    scenarios, persona, competitor_snapshot,
                    creatives, profile.goal
                )

                overall_score = critic_evaluation.get('overall_score', 0)
                print(f"  ✓ Score: {overall_score:.2f} / 1.00")

                results.append({
                    "business_name": profile.business_name,
                    "business_type": profile.business_type,
                    "score": overall_score,
                    "evaluation": critic_evaluation,
                    "success": True
                })

            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                results.append({
                    "business_name": profile.business_name,
                    "business_type": profile.business_type,
                    "score": 0,
                    "error": str(e),
                    "success": False
                })

        # Summary
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"\nTotal Tests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")

        if successful:
            scores = [r['score'] for r in successful]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)

            print(f"\nScore Statistics:")
            print(f"  Average: {avg_score:.2f}")
            print(f"  Min: {min_score:.2f}")
            print(f"  Max: {max_score:.2f}")

            print(f"\nResults by Business:")
            for r in successful:
                print(f"  {r['business_name']}: {r['score']:.2f}")

        if failed:
            print(f"\nFailed Tests:")
            for r in failed:
                print(f"  {r['business_name']}: {r.get('error', 'Unknown error')}")

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "avg_score": sum([r['score'] for r in successful]) / len(successful) if successful else 0,
            "results": results
        }

    def save_results(self, results: Dict[str, Any], filename: str = "evaluation_results.json"):
        """Save evaluation results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")


def main():
    """Main evaluation function"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    runner = EvaluationRunner(api_key)
    results = asyncio.run(runner.run_evaluation())
    runner.save_results(results)


if __name__ == "__main__":
    main()
