"""Critic Agent - Evaluates and improves plans using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import ScenarioSet, Persona, CompetitorSnapshot, CreativeAssets, MediaPlan
from typing import Dict, Any


class CriticAgent(BaseAgent):
    """Agent for evaluating and critiquing plans using Google ADK"""

    SYSTEM_INSTRUCTION = """You are CriticAgent, a senior marketing strategist and quality evaluator.
Evaluate marketing plans on:

- Channel mix quality (alignment with goals and audience)
- Budget logic (allocations make sense)
- Persona alignment (plan fits the target audience)
- Competitor alignment (differentiates from competition)
- Creative integration (creatives match the plan)
- Clarity & feasibility (plan is actionable and realistic)

Score: 0.0 – 1.0 (where 1.0 is excellent)
If score < 0.70 → highlight specific issues for improvement.

Return ONLY valid JSON. No other text."""

    def __init__(self):
        """Initialize CriticAgent with Google ADK"""
        super().__init__(
            agent_name="critic_agent",
            description="Evaluates and critiques marketing plans",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.2
        )

    def _format_plan_summary(self, plan: MediaPlan) -> str:
        """Format a media plan summary"""
        channels = ', '.join([f"{ch.name} ({ch.budget_share_percent}%)" for ch in plan.channels])
        return f"${plan.total_budget} over {plan.duration_weeks} weeks | {channels}"

    async def evaluate_plan(
        self,
        scenarios: ScenarioSet,
        persona: Persona,
        competitor_snapshot: CompetitorSnapshot,
        creatives: CreativeAssets,
        business_goal: str
    ) -> Dict[str, Any]:
        """Evaluate the complete marketing plan

        Args:
            scenarios: ScenarioSet with three media plans
            persona: Persona object
            competitor_snapshot: CompetitorSnapshot object
            creatives: CreativeAssets object
            business_goal: Business goal statement

        Returns:
            Dictionary with evaluation scores and feedback
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Goal: {business_goal}

Target Persona:
{persona.model_dump_json(indent=2)}

Competitor Landscape:
{competitor_snapshot.market_insights}

Media Plans:
STANDARD: {self._format_plan_summary(scenarios.standard_plan)}
AGGRESSIVE: {self._format_plan_summary(scenarios.aggressive_plan)}
EXPERIMENTAL: {self._format_plan_summary(scenarios.experimental_plan)}

Creative Assets:
- Ideas: {', '.join([idea.title for idea in creatives.ideas])}
- Slogans: {', '.join(creatives.slogans)}
- CTAs: {', '.join(creatives.cta_options)}

Evaluate this complete marketing strategy on:

1. Channel mix quality (0.0-1.0)
2. Budget logic (0.0-1.0)
3. Persona alignment (0.0-1.0)
4. Competitor differentiation (0.0-1.0)
5. Creative integration (0.0-1.0)
6. Feasibility & clarity (0.0-1.0)

Calculate overall score (average of above).
If score < 0.70, list specific issues.
Always list 3-5 key strengths of the plan.

Return ONLY JSON with this structure:
{{
    "channel_mix_score": number,
    "budget_logic_score": number,
    "persona_alignment_score": number,
    "competitor_differentiation_score": number,
    "creative_integration_score": number,
    "feasibility_score": number,
    "overall_score": number,
    "summary": "string",
    "strengths": ["string (3-5 key advantages of this plan)"],
    "issues": ["string"] or []
}}
"""

        evaluation = await self.generate_json(user_prompt)
        return evaluation
