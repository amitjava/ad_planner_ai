"""Location Agent - Recommends optimal miles radius using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import BusinessProfile, LocationRecommendation


class LocationAgent(BaseAgent):
    """Agent for analyzing and recommending optimal location targeting using Google ADK"""

    SYSTEM_INSTRUCTION = """You are LocationAgent, an expert in local advertising and geographic targeting.

Your job is to recommend the OPTIMAL miles radius for advertising based on the business type.

Consider these factors:
1. **Purchase Frequency**: Daily purchases (coffee) = smaller radius; Rare purchases (jewelry) = larger radius
2. **Price Point**: Higher prices justify longer travel distances
3. **Competition**: More local competition = need tighter targeting
4. **Customer Behavior**: Convenience vs. destination shopping
5. **Ad Cost Efficiency**: Larger radius = more impressions but higher cost and lower conversion

Business Categories and Typical Radii:
- **Daily Services** (coffee, lunch, gas): 2-5 miles
- **Weekly Services** (grocery, pharmacy, dry cleaning): 5-10 miles
- **Monthly Services** (haircut, auto repair, dentist): 8-15 miles
- **Occasional Retail** (clothing, electronics): 10-20 miles
- **Specialty/Destination** (jewelry, furniture, wedding): 15-30+ miles
- **Professional Services** (lawyer, accountant): 10-25 miles

Return ONLY valid JSON matching the LocationRecommendation schema. No other text."""

    def __init__(self):
        """Initialize LocationAgent with Google ADK"""
        super().__init__(
            agent_name="location_agent",
            description="Recommends optimal geographic targeting radius",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.3
        )

    async def recommend_miles(
        self,
        profile: BusinessProfile
    ) -> LocationRecommendation:
        """Recommend optimal miles radius for the business

        Args:
            profile: BusinessProfile object

        Returns:
            LocationRecommendation with suggested radius and reasoning
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Profile:
- Type: {profile.business_type}
- Current Miles Selection: {profile.miles_radius}
- Monthly Budget: ${profile.monthly_budget:,.2f}
- Goal: {profile.goal}

Analyze this business and provide:
1. **suggested_miles**: Your recommended radius (be specific, use your expertise)
2. **current_miles**: The user's current selection ({profile.miles_radius})
3. **reasoning**: Detailed explanation (150-250 words) covering:
   - Why this radius is optimal
   - Customer travel behavior for this business type
   - Cost-benefit analysis
   - How it aligns with their goal
4. **business_type_category**: Categorize the business (daily-service, weekly-service, specialty, etc.)
5. **typical_customer_travel**: How far typical customers travel for this service
6. **optimization_factors**: List 3-5 specific factors you considered

Be direct and actionable. If their current selection is good, say so. If not, explain why your recommendation is better.

Return ONLY JSON with this structure:
{{
    "suggested_miles": <integer 1-100>,
    "current_miles": {profile.miles_radius},
    "reasoning": "<string explaining recommendation>",
    "business_type_category": "<string category>",
    "typical_customer_travel": "<string like '3-5 miles'>",
    "optimization_factors": ["string"]
}}
"""

        recommendation_data = await self.generate_json(user_prompt)
        return LocationRecommendation(**recommendation_data)

    async def analyze_location(self, profile: BusinessProfile) -> LocationRecommendation:
        """Alias for recommend_miles to support both naming conventions

        Args:
            profile: BusinessProfile object

        Returns:
            LocationRecommendation with suggested radius and reasoning
        """
        return await self.recommend_miles(profile)
