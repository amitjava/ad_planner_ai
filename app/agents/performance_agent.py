"""Performance Agent - Predicts campaign performance using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import MediaPlan, Persona, PerformanceSet, PerformancePrediction, ScenarioSet


class PerformanceAgent(BaseAgent):
    """Agent for predicting campaign performance using Google ADK"""

    SYSTEM_INSTRUCTION = """You are PerformanceAgent, a marketing analytics expert.
For each media plan, estimate realistic performance metrics:

- Reach (e.g., "15,000-20,000 people")
- Clicks (e.g., "800-1,200 clicks")
- CPC estimate (e.g., "$1.50-$2.50")
- ROI range (e.g., "2.5x-3.5x return")

Use reasonable marketing heuristics based on:
- Channel mix
- Budget allocation
- Target audience size
- Competition level
- Industry benchmarks

Return ONLY valid JSON matching the PerformanceSet schema. No other text."""

    def __init__(self):
        """Initialize PerformanceAgent with Google ADK"""
        super().__init__(
            agent_name="performance_agent",
            description="Predicts campaign performance metrics",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.4
        )

    def _format_plan(self, plan: MediaPlan) -> str:
        """Format a media plan for display"""
        channels = "\n".join([
            f"  - {ch.name}: {ch.budget_share_percent}% (${plan.total_budget * ch.budget_share_percent / 100:.2f})"
            for ch in plan.channels
        ])
        return f"Budget: ${plan.total_budget}\nDuration: {plan.duration_weeks} weeks\nChannels:\n{channels}"

    async def predict_performance(
        self,
        scenarios: ScenarioSet,
        persona: Persona,
        business_type: str,
        location: str,
        is_local: bool
    ) -> PerformanceSet:
        """Predict performance for all three scenarios

        Args:
            scenarios: ScenarioSet with three media plans
            persona: Persona object
            business_type: Type of business
            location: Business location
            is_local: Whether business is local

        Returns:
            PerformanceSet with predictions for all three scenarios
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Context:
- Type: {business_type}
- Location: {location}
- Local business: {is_local}

Target Persona:
- Age: {persona.age_range}
- Platforms: {', '.join(persona.platforms)}
- Interests: {', '.join(persona.interests)}

Media Plans:

STANDARD:
{self._format_plan(scenarios.standard_plan)}

AGGRESSIVE:
{self._format_plan(scenarios.aggressive_plan)}

EXPERIMENTAL:
{self._format_plan(scenarios.experimental_plan)}

For each plan, estimate:
1. Total reach (people who will see the ads)
2. Total clicks/engagements
3. Average cost per click
4. Expected ROI range

Be realistic based on industry benchmarks for {business_type} businesses.

Return ONLY JSON with this structure:
{{
    "standard": {{
        "reach": "string (e.g., '10,000-15,000 people')",
        "clicks": "string (e.g., '500-800 clicks')",
        "cpc_estimate": "string (e.g., '$1.50-$2.50')",
        "roi_range": "string (e.g., '2.0x-3.0x return')"
    }},
    "aggressive": {{
        "reach": "string (e.g., '15,000-25,000 people')",
        "clicks": "string (e.g., '1,000-1,500 clicks')",
        "cpc_estimate": "string (e.g., '$1.75-$2.75')",
        "roi_range": "string (e.g., '3.0x-4.5x return')"
    }},
    "experimental": {{
        "reach": "string (e.g., '8,000-12,000 people')",
        "clicks": "string (e.g., '600-900 clicks')",
        "cpc_estimate": "string (e.g., '$2.00-$3.50')",
        "roi_range": "string (e.g., '1.5x-3.0x return')"
    }}
}}
"""

        performance_data = await self.generate_json(user_prompt)
        return PerformanceSet(**performance_data)
