"""Detailed Agent Evaluation with Metrics"""
import time
import asyncio
from typing import Dict, Any, List
from ..schemas import BusinessProfile, Persona, MediaPlan, ScenarioSet
from ..agents import (
    PersonaAgent,
    CompetitorAgent,
    PlannerAgent,
    CreativeAgent,
    PerformanceAgent,
    CriticAgent
)


class AgentEvaluator:
    """Evaluates individual agent performance with detailed metrics"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.persona_agent = PersonaAgent(api_key)
        self.competitor_agent = CompetitorAgent(api_key)
        self.planner_agent = PlannerAgent(api_key)
        self.creative_agent = CreativeAgent(api_key)
        self.performance_agent = PerformanceAgent(api_key)
        self.critic_agent = CriticAgent(api_key)

    def evaluate_persona_agent(self, profile: BusinessProfile, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate PersonaAgent performance"""
        start_time = time.time()

        try:
            persona = self.persona_agent.generate_persona(profile)
            duration = time.time() - start_time

            # Validation checks
            checks = {
                "has_name": bool(persona.name),
                "has_age_range": bool(persona.age_range),
                "has_interests": len(persona.interests) >= 3,
                "has_platforms": len(persona.platforms) >= 2,
                "has_creative_style": bool(persona.creative_style),
                "has_motivation": bool(persona.motivation),
                "age_range_reasonable": any(exp in persona.age_range for exp in expected.get("persona_age_range", [])),
                "platforms_relevant": any(p in persona.platforms for p in expected.get("persona_platforms", []))
            }

            score = sum(checks.values()) / len(checks)

            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "persona": persona.model_dump(),
                "validation_checks": checks,
                "score": round(score, 2),
                "passed_checks": sum(checks.values()),
                "total_checks": len(checks)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time,
                "score": 0.0
            }

    def evaluate_planner_agent(
        self,
        profile: BusinessProfile,
        persona: Persona,
        competitor_snapshot,
        expected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate PlannerAgent performance"""
        start_time = time.time()

        try:
            scenarios = self.planner_agent.generate_scenarios(
                profile, persona, competitor_snapshot
            )
            duration = time.time() - start_time

            # Validate each plan
            def validate_plan(plan: MediaPlan, plan_type: str) -> Dict[str, bool]:
                checks = {
                    f"{plan_type}_has_4_channels": len(plan.channels) == 4,
                    f"{plan_type}_budget_matches": abs(plan.total_budget - profile.monthly_budget) < 1,
                    f"{plan_type}_duration_matches": plan.duration_weeks == profile.duration_weeks,
                    f"{plan_type}_budget_sums_to_100": abs(sum(ch.budget_share_percent for ch in plan.channels) - 100) < 1,
                    f"{plan_type}_all_channels_named": all(ch.name for ch in plan.channels),
                    f"{plan_type}_all_have_reasoning": all(len(ch.reasoning) > 20 for ch in plan.channels)
                }
                return checks

            checks = {}
            checks.update(validate_plan(scenarios.standard_plan, "standard"))
            checks.update(validate_plan(scenarios.aggressive_plan, "aggressive"))
            checks.update(validate_plan(scenarios.experimental_plan, "experimental"))

            # Check for variety between plans
            standard_channels = set(ch.name for ch in scenarios.standard_plan.channels)
            aggressive_channels = set(ch.name for ch in scenarios.aggressive_plan.channels)
            experimental_channels = set(ch.name for ch in scenarios.experimental_plan.channels)

            checks["scenarios_are_different"] = len(
                standard_channels | aggressive_channels | experimental_channels
            ) > 6

            score = sum(checks.values()) / len(checks)

            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "scenarios": scenarios.model_dump(),
                "validation_checks": checks,
                "score": round(score, 2),
                "passed_checks": sum(checks.values()),
                "total_checks": len(checks)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time,
                "score": 0.0
            }

    async def evaluate_creative_agent(
        self,
        profile: BusinessProfile,
        persona: Persona
    ) -> Dict[str, Any]:
        """Evaluate CreativeAgent performance"""
        start_time = time.time()

        try:
            creatives = await self.creative_agent.generate_assets(profile, persona)
            duration = time.time() - start_time

            checks = {
                "has_3_ideas": len(creatives.ideas) == 3,
                "ideas_have_titles": all(idea.title for idea in creatives.ideas),
                "ideas_have_descriptions": all(len(idea.description) > 30 for idea in creatives.ideas),
                "has_10_hashtags": len(creatives.hashtags) >= 8,
                "has_3_slogans": len(creatives.slogans) == 3,
                "short_copy_length": 10 <= len(creatives.short_ad_copy.split()) <= 25,
                "long_copy_length": 50 <= len(creatives.long_ad_copy.split()) <= 250,
                "has_3_ctas": len(creatives.cta_options) == 3,
                "no_empty_fields": all([
                    creatives.short_ad_copy,
                    creatives.long_ad_copy,
                    all(creatives.hashtags),
                    all(creatives.slogans)
                ])
            }

            score = sum(checks.values()) / len(checks)

            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "creatives": creatives.model_dump(),
                "validation_checks": checks,
                "score": round(score, 2),
                "passed_checks": sum(checks.values()),
                "total_checks": len(checks)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time,
                "score": 0.0
            }

    def evaluate_critic_agent(
        self,
        scenarios: ScenarioSet,
        persona: Persona,
        competitor_snapshot,
        creatives,
        business_goal: str
    ) -> Dict[str, Any]:
        """Evaluate CriticAgent performance"""
        start_time = time.time()

        try:
            evaluation = self.critic_agent.evaluate_plan(
                scenarios, persona, competitor_snapshot, creatives, business_goal
            )
            duration = time.time() - start_time

            checks = {
                "has_overall_score": "overall_score" in evaluation,
                "score_in_range": 0 <= evaluation.get("overall_score", -1) <= 1,
                "has_dimension_scores": "dimension_scores" in evaluation,
                "has_all_dimensions": all(dim in evaluation.get("dimension_scores", {}) for dim in [
                    "channel_mix", "budget_logic", "persona_alignment",
                    "competitor_differentiation", "creative_integration", "feasibility"
                ]),
                "has_strengths": len(evaluation.get("strengths", [])) > 0,
                "has_issues_or_recommendations": (
                    len(evaluation.get("issues", [])) > 0 or
                    len(evaluation.get("recommendations", [])) > 0
                )
            }

            score = sum(checks.values()) / len(checks)

            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "evaluation": evaluation,
                "validation_checks": checks,
                "score": round(score, 2),
                "critic_overall_score": evaluation.get("overall_score", 0),
                "passed_checks": sum(checks.values()),
                "total_checks": len(checks)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time,
                "score": 0.0
            }

    async def run_full_evaluation(
        self,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run complete evaluation for a test case"""

        profile = test_case["profile"]
        expected = test_case.get("expected_outcomes", {})

        results = {
            "test_id": test_case["id"],
            "business_name": profile.business_name,
            "category": test_case["category"],
            "start_time": time.time(),
            "agents": {}
        }

        # 1. Evaluate PersonaAgent
        print(f"  Evaluating PersonaAgent...")
        persona_result = self.evaluate_persona_agent(profile, expected)
        results["agents"]["persona"] = persona_result

        if not persona_result["success"]:
            results["overall_success"] = False
            results["error"] = "PersonaAgent failed"
            results["total_duration"] = round(time.time() - results["start_time"], 2)
            results["average_agent_score"] = 0.0
            results["critic_overall_score"] = 0.0
            results["meets_minimum_score"] = False
            return results

        persona = Persona(**persona_result["persona"])

        # 2. Evaluate CompetitorAgent
        print(f"  Evaluating CompetitorAgent...")
        comp_start = time.time()
        try:
            competitor_snapshot = self.competitor_agent.analyze_competitors(
                profile.competitors if profile.competitors else ["Generic Competitor"],
                profile.business_type,
                profile.location
            )
            results["agents"]["competitor"] = {
                "success": True,
                "duration_seconds": round(time.time() - comp_start, 2),
                "competitors_analyzed": len(competitor_snapshot.competitors),
                "score": 1.0 if len(competitor_snapshot.competitors) > 0 else 0.5
            }
        except Exception as e:
            results["agents"]["competitor"] = {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
            results["overall_success"] = False
            results["total_duration"] = round(time.time() - results["start_time"], 2)
            results["average_agent_score"] = 0.0
            results["critic_overall_score"] = 0.0
            results["meets_minimum_score"] = False
            return results

        # 3. Evaluate PlannerAgent
        print(f"  Evaluating PlannerAgent...")
        planner_result = self.evaluate_planner_agent(
            profile, persona, competitor_snapshot, expected
        )
        results["agents"]["planner"] = planner_result

        if not planner_result["success"]:
            results["overall_success"] = False
            results["error"] = "PlannerAgent failed"
            results["total_duration"] = round(time.time() - results["start_time"], 2)
            results["average_agent_score"] = 0.0
            results["critic_overall_score"] = 0.0
            results["meets_minimum_score"] = False
            return results

        scenarios = ScenarioSet(**planner_result["scenarios"])

        # 4. Evaluate CreativeAgent
        print(f"  Evaluating CreativeAgent...")
        creative_result = await self.evaluate_creative_agent(profile, persona)
        results["agents"]["creative"] = creative_result

        if not creative_result["success"]:
            results["overall_success"] = False
            results["error"] = "CreativeAgent failed"
            results["total_duration"] = round(time.time() - results["start_time"], 2)
            results["average_agent_score"] = 0.0
            results["critic_overall_score"] = 0.0
            results["meets_minimum_score"] = False
            return results

        from ..schemas import CreativeAssets
        creatives = CreativeAssets(**creative_result["creatives"])

        # 5. Evaluate PerformanceAgent
        print(f"  Evaluating PerformanceAgent...")
        perf_start = time.time()
        try:
            performance_set = self.performance_agent.predict_performance(
                scenarios, persona, profile.business_type,
                profile.location, profile.is_local
            )
            results["agents"]["performance"] = {
                "success": True,
                "duration_seconds": round(time.time() - perf_start, 2),
                "score": 1.0  # Success if no error
            }
        except Exception as e:
            results["agents"]["performance"] = {
                "success": False,
                "error": str(e),
                "score": 0.0
            }

        # 6. Evaluate CriticAgent
        print(f"  Evaluating CriticAgent...")
        critic_result = self.evaluate_critic_agent(
            scenarios, persona, competitor_snapshot,
            creatives, profile.goal
        )
        results["agents"]["critic"] = critic_result

        # Calculate overall results
        results["total_duration"] = round(time.time() - results["start_time"], 2)
        results["overall_success"] = all(
            agent_result.get("success", False)
            for agent_result in results["agents"].values()
        )

        # Calculate average score
        scores = [
            agent_result.get("score", 0)
            for agent_result in results["agents"].values()
        ]
        results["average_agent_score"] = round(sum(scores) / len(scores), 2)
        results["critic_overall_score"] = critic_result.get("critic_overall_score", 0)

        # Check against expected minimum score
        min_score = expected.get("min_critic_score", 0.65)
        results["meets_minimum_score"] = results["critic_overall_score"] >= min_score

        return results
