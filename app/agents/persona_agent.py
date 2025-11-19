"""Persona Agent - Generates customer personas using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import BusinessProfile, Persona


class PersonaAgent(BaseAgent):
    """Agent for generating customer personas using Google ADK"""

    SYSTEM_INSTRUCTION = """You are PersonaAgent, a marketing persona generator.
Given a BusinessProfile JSON, generate ONE persona with:

- Name (creative, specific persona name)
- Age range
- Interests
- Relevant platforms
- Creative style
- Motivation

Return ONLY valid JSON matching the Persona schema. No other text."""

    def __init__(self):
        """Initialize PersonaAgent with Google ADK"""
        super().__init__(
            agent_name="persona_agent",
            description="Generates customer personas based on business profiles",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.7
        )

    async def generate_persona(self, profile: BusinessProfile) -> Persona:
        """Generate a persona based on business profile

        Args:
            profile: BusinessProfile object

        Returns:
            Persona object with generated persona data
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Profile:
- Name: {profile.business_name}
- Type: {profile.business_type}
- Location: {profile.zip_code}
- Goal: {profile.goal}
- Budget: ${profile.monthly_budget}/month
- Local: {profile.is_local}
- Competitors: {', '.join(profile.competitors)}

Generate a detailed customer persona that would be interested in this business.

Return JSON in this exact format:
{{
    "name": "string",
    "age_range": "string",
    "interests": ["string", "string"],
    "platforms": ["string", "string"],
    "creative_style": "string",
    "motivation": "string"
}}
"""

        response_json = await self.generate_json(user_prompt)
        return Persona(**response_json)

    async def generate_personas(self, profile: BusinessProfile, count: int = 3) -> list[Persona]:
        """Generate multiple personas based on business profile

        Args:
            profile: BusinessProfile object
            count: Number of personas to generate (default: 3)

        Returns:
            List of Persona objects
        """
        # Generate personas concurrently for better performance
        import asyncio
        personas = await asyncio.gather(*[
            self.generate_persona(profile) for _ in range(count)
        ])
        return list(personas)
