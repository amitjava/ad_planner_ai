"""Competitor Agent - Analyzes competitors using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import CompetitorSnapshot, CompetitorInfo
from typing import List


class CompetitorAgent(BaseAgent):
    """Agent for analyzing competitors using Google ADK"""

    SYSTEM_INSTRUCTION = """You are CompetitorAgent, a competitive intelligence analyst.
Analyze competitor information and provide insights about:

- Website summary
- Social media presence
- Advertising channels used
- Content/creative style
- Strengths & weaknesses
- Market opportunities
- Competitive threats

Return ONLY valid JSON matching the CompetitorSnapshot schema. No other text."""

    def __init__(self):
        """Initialize CompetitorAgent with Google ADK"""
        super().__init__(
            agent_name="competitor_agent",
            description="Analyzes competitors and provides market insights",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.5
        )

    async def analyze_competitors(
        self,
        competitor_names: List[str],
        business_type: str,
        location: str
    ) -> CompetitorSnapshot:
        """Analyze competitors and generate insights

        Args:
            competitor_names: List of competitor names
            business_type: Type of business
            location: Business location

        Returns:
            CompetitorSnapshot with analysis data
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Analyze these competitors for a {business_type} business in {location}:
{', '.join(competitor_names)}

For each competitor, provide:
- Name
- Likely website
- Social media platforms they use
- Advertising channels
- Content style
- Strengths (2-3)
- Weaknesses (2-3)

Then provide:
- Overall market insights
- Opportunities for differentiation (3-5)
- Competitive threats (2-4)

Return ONLY the JSON object with this structure:
{{
    "competitors": [
        {{
            "name": "string",
            "website": "string or null",
            "social_presence": ["string"],
            "advertising_channels": ["string"],
            "content_style": "string",
            "strengths": ["string"],
            "weaknesses": ["string"]
        }}
    ],
    "market_insights": "string",
    "opportunities": ["string"],
    "threats": ["string"]
}}
"""

        snapshot_data = await self.generate_json(user_prompt)
        return CompetitorSnapshot(**snapshot_data)

    async def get_competitor_info(self, competitor_name: str, business_type: str) -> CompetitorInfo:
        """Get detailed info about a single competitor

        Args:
            competitor_name: Name of competitor
            business_type: Type of business

        Returns:
            CompetitorInfo with detailed data
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Analyze this competitor: {competitor_name} (in the {business_type} industry)

Provide detailed information including:
- Website
- Social presence
- Advertising channels
- Content style
- Strengths
- Weaknesses

Return ONLY JSON matching this structure:
{{
    "name": "string",
    "website": "string or null",
    "social_presence": ["string"],
    "advertising_channels": ["string"],
    "content_style": "string",
    "strengths": ["string"],
    "weaknesses": ["string"]
}}
"""

        info_data = await self.generate_json(user_prompt)
        return CompetitorInfo(**info_data)
