"""RAG Agent - Retrieval Augmented Generation using Google ADK"""
from .base_agent import BaseAgent
from ..memory.vector_memory import VectorMemory
from typing import Dict, Any, List, Optional
import json


class RAGAgent(BaseAgent):
    """Agent for intelligent retrieval and context augmentation using Google ADK

    This agent:
    1. Retrieves similar historical business profiles and successful plans
    2. Analyzes patterns and insights from past successful campaigns
    3. Augments current planning with learned knowledge
    4. Provides context-aware recommendations based on vector similarity
    """

    SYSTEM_INSTRUCTION = """You are RAGAgent, an expert at analyzing historical marketing campaigns and extracting actionable insights.

Your role is to:
1. Analyze similar past business profiles and their successful marketing plans
2. Identify patterns, trends, and winning strategies from historical data
3. Extract key insights that are relevant to the current business context
4. Provide specific, actionable recommendations based on learned patterns

You will be given:
- Current business profile
- Similar historical profiles and their plans
- Performance feedback from past campaigns

Return structured insights that help improve the current marketing plan."""

    def __init__(self, vector_memory: VectorMemory):
        """Initialize RAGAgent with Google ADK and vector memory

        Args:
            vector_memory: VectorMemory instance for retrieving historical data
        """
        super().__init__(
            agent_name="rag_agent",
            description="Retrieves and analyzes historical data to improve recommendations",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.5
        )
        self.vector_memory = vector_memory

    async def retrieve_similar_context(
        self,
        business_profile: Dict[str, Any],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Retrieve similar business profiles and plans from vector memory

        Args:
            business_profile: Current business profile
            n_results: Number of similar results to retrieve

        Returns:
            Dictionary containing similar profiles and plans
        """
        # Create a rich query text from the business profile
        query_text = f"""
        Business Type: {business_profile.get('business_type')}
        Location: {business_profile.get('location')}
        ZIP Code: {business_profile.get('zip_code')}
        Goal: {business_profile.get('goal')}
        Monthly Budget: ${business_profile.get('monthly_budget')}
        Competitors: {', '.join(business_profile.get('competitors', []))}
        Is Local: {business_profile.get('is_local')}
        """

        # Retrieve similar profiles
        similar_profiles = self.vector_memory.query_similar_profiles(
            query_text, n_results=n_results
        )

        # Retrieve similar plans
        similar_plans = self.vector_memory.query_similar_plans(
            query_text, n_results=n_results
        )

        return {
            "similar_profiles": similar_profiles,
            "similar_plans": similar_plans,
            "query_text": query_text
        }

    async def generate_insights(
        self,
        current_profile: Dict[str, Any],
        similar_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable insights from historical data using ADK

        Args:
            current_profile: Current business profile
            similar_context: Retrieved similar profiles and plans

        Returns:
            Structured insights and recommendations
        """
        prompt = f"""
{self.SYSTEM_INSTRUCTION}

CURRENT BUSINESS PROFILE:
- Business Name: {current_profile.get('business_name')}
- Type: {current_profile.get('business_type')}
- Location: {current_profile.get('location')} (ZIP: {current_profile.get('zip_code')})
- Goal: {current_profile.get('goal')}
- Monthly Budget: ${current_profile.get('monthly_budget')}
- Campaign Duration: {current_profile.get('duration_weeks')} weeks
- Competitors: {', '.join(current_profile.get('competitors', []))}
- Is Local Business: {current_profile.get('is_local')}

SIMILAR HISTORICAL PROFILES:
{self._format_similar_profiles(similar_context.get('similar_profiles', []))}

SIMILAR SUCCESSFUL PLANS:
{self._format_similar_plans(similar_context.get('similar_plans', []))}

Based on the historical data above, provide insights and recommendations in this JSON format:

{{
    "key_patterns": [
        "Pattern 1: Description of successful pattern observed",
        "Pattern 2: Another successful pattern",
        "Pattern 3: Additional insight"
    ],
    "recommended_channels": [
        {{
            "channel": "Channel Name",
            "reasoning": "Why this channel worked well for similar businesses",
            "expected_performance": "What results similar businesses achieved"
        }}
    ],
    "budget_insights": {{
        "optimal_range": "Based on similar businesses, the recommended budget range",
        "allocation_tips": "How similar businesses allocated their budget effectively"
    }},
    "targeting_recommendations": [
        "Recommendation 1 based on similar successful campaigns",
        "Recommendation 2 based on patterns observed"
    ],
    "potential_pitfalls": [
        "Common mistake 1 to avoid based on historical data",
        "Common mistake 2 observed in similar campaigns"
    ],
    "success_factors": [
        "Critical success factor 1 from historical analysis",
        "Critical success factor 2"
    ],
    "confidence_score": 0.0-1.0,
    "data_points_analyzed": number_of_similar_cases
}}

If there is insufficient historical data, indicate this in the confidence_score and provide general best practices instead.

Return ONLY valid JSON, no markdown formatting.
"""

        try:
            insights = await self.generate_json(prompt)
            return insights
        except Exception as e:
            print(f"Error generating RAG insights: {e}")
            # Return default structure if generation fails
            return {
                "key_patterns": [],
                "recommended_channels": [],
                "budget_insights": {
                    "optimal_range": "Insufficient historical data",
                    "allocation_tips": "Consider industry benchmarks"
                },
                "targeting_recommendations": [],
                "potential_pitfalls": [],
                "success_factors": [],
                "confidence_score": 0.0,
                "data_points_analyzed": 0
            }

    def _format_similar_profiles(self, profiles: List[Dict[str, Any]]) -> str:
        """Format similar profiles for prompt"""
        if not profiles:
            return "No similar historical profiles found."

        formatted = []
        for i, profile in enumerate(profiles[:3], 1):  # Limit to top 3
            doc = profile.get('document', '')
            distance = profile.get('distance', 1.0)
            similarity = max(0, 1 - distance)
            formatted.append(f"{i}. (Similarity: {similarity:.2f})\n{doc}")

        return "\n\n".join(formatted)

    def _format_similar_plans(self, plans: List[Dict[str, Any]]) -> str:
        """Format similar plans for prompt"""
        if not plans:
            return "No similar historical plans found."

        formatted = []
        for i, plan in enumerate(plans[:2], 1):  # Limit to top 2
            doc = plan.get('document', '')
            distance = plan.get('distance', 1.0)
            similarity = max(0, 1 - distance)

            # Try to parse and summarize the plan
            try:
                plan_data = json.loads(doc)
                summary = f"{i}. (Similarity: {similarity:.2f})\n"

                # Extract key information
                if 'scenarios' in plan_data:
                    scenarios = plan_data['scenarios']
                    summary += f"  Scenarios offered: {', '.join(scenarios.keys())}\n"

                if 'performance' in plan_data:
                    performance = plan_data['performance']
                    if 'standard' in performance:
                        std_perf = performance['standard']
                        summary += f"  Standard Performance: {std_perf.get('reach', 'N/A')} reach, {std_perf.get('roi_range', 'N/A')} ROI\n"

                if 'critic_evaluation' in plan_data:
                    critic = plan_data['critic_evaluation']
                    summary += f"  Overall Score: {critic.get('overall_score', 'N/A')}\n"

                formatted.append(summary)
            except:
                formatted.append(f"{i}. (Similarity: {similarity:.2f})\n{doc[:200]}...")

        return "\n\n".join(formatted)

    async def augment_profile_with_insights(
        self,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main method: Retrieve context and generate insights for a business profile

        Args:
            profile: Business profile to augment

        Returns:
            Dictionary containing original profile plus RAG insights
        """
        # Retrieve similar historical data
        similar_context = await self.retrieve_similar_context(profile, n_results=5)

        # Generate insights from historical data
        insights = await self.generate_insights(profile, similar_context)

        return {
            "original_profile": profile,
            "rag_insights": insights,
            "similar_context_count": {
                "profiles": len(similar_context.get('similar_profiles', [])),
                "plans": len(similar_context.get('similar_plans', []))
            }
        }
