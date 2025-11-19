"""Planner Agent - Creates media plans using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import BusinessProfile, Persona, CompetitorSnapshot, ScenarioSet, MediaPlan


class PlannerAgent(BaseAgent):
    """Agent for generating media plans using Google ADK"""

    SYSTEM_INSTRUCTION = """You are PlannerAgent, an expert media planner.
Given BusinessProfile, Persona, and CompetitorSnapshot, produce THREE plans:

1. Standard — balanced, safe, proven channels
2. Aggressive — high risk, high return, maximum impact
3. Experimental — influencer/collab/viral/creative heavy, innovative

Each plan must include:
- total_budget (match the business budget)
- duration_weeks (match the business duration)
- exactly 4 channels
- budget_share_percent (must sum to 100)
- reasoning for each channel

Return ONLY valid JSON matching the ScenarioSet schema. No other text."""

    def __init__(self):
        """Initialize PlannerAgent with Google ADK"""
        super().__init__(
            agent_name="planner_agent",
            description="Creates three distinct media plan scenarios",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.6
        )

    async def generate_scenarios(
        self,
        profile: BusinessProfile,
        persona: Persona,
        competitor_snapshot: CompetitorSnapshot
    ) -> ScenarioSet:
        """Generate three media plan scenarios

        Args:
            profile: BusinessProfile object
            persona: Persona object
            competitor_snapshot: CompetitorSnapshot object

        Returns:
            ScenarioSet with three media plans
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Profile:
{profile.model_dump_json(indent=2)}

Target Persona:
{persona.model_dump_json(indent=2)}

Competitor Analysis:
Market Insights: {competitor_snapshot.market_insights}
Opportunities: {', '.join(competitor_snapshot.opportunities)}
Threats: {', '.join(competitor_snapshot.threats)}

Generate THREE distinct media plans:

1. STANDARD: Safe, balanced approach using proven channels
2. AGGRESSIVE: Bold strategy maximizing reach and impact
3. EXPERIMENTAL: Creative approach with influencers, partnerships, viral tactics

Each plan should have exactly 4 channels with budget allocations that sum to 100%.
Consider the persona's platforms and the competitive landscape.

Return ONLY JSON with this structure:
{{
    "standard_plan": {{
        "total_budget": {profile.monthly_budget},
        "duration_weeks": {profile.duration_weeks},
        "channels": [
            {{
                "name": "string",
                "budget_share_percent": number,
                "reasoning": "string"
            }}
        ]
    }},
    "aggressive_plan": {{ ... }},
    "experimental_plan": {{ ... }}
}}
"""

        scenarios_data = await self.generate_json(user_prompt)
        return ScenarioSet(**scenarios_data)
