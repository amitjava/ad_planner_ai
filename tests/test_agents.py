#!/usr/bin/env python3
"""
Unit Tests for Smart Ad Planner Agents
Tests all 7 specialized agents with mocked responses
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.schemas import BusinessProfile, Persona, CompetitorSnapshot, LocationRecommendation
from app.agents import (
    PersonaAgent, LocationAgent, CompetitorAgent,
    PlannerAgent, CreativeAgent, PerformanceAgent, CriticAgent
)


# Test Fixtures
@pytest.fixture
def sample_profile():
    """Sample business profile for testing"""
    return BusinessProfile(
        business_name="Joe's Coffee Shop",
        business_type="Coffee Shop",
        location="San Francisco, CA",
        zip_code="94107",
        miles_radius=3,
        goal="Increase weekday lunchtime traffic by 20%",
        monthly_budget=2500.0,
        duration_weeks=10,
        competitors=["Starbucks", "Blue Bottle Coffee"],
        is_local=True
    )


@pytest.fixture
def sample_persona():
    """Sample persona for testing"""
    return Persona(
        name="Sarah the Professional",
        age_range="28-35",
        interests=["coffee", "productivity", "networking"],
        platforms=["Instagram", "LinkedIn"],
        creative_style="professional and clean",
        motivation="Quick quality coffee near office"
    )


@pytest.fixture
def sample_competitor_snapshot():
    """Sample competitor analysis for testing"""
    return CompetitorSnapshot(
        competitors=[
            {
                "name": "Starbucks",
                "website": "starbucks.com",
                "social_presence": ["Instagram", "Facebook"],
                "advertising_channels": ["Google Ads", "Facebook Ads"],
                "content_style": "corporate professional",
                "strengths": ["Brand recognition", "Convenient locations"],
                "weaknesses": ["Less personal", "Higher prices"]
            }
        ],
        market_insights="Competitive coffee market with established chains",
        opportunities=["Artisan quality", "Local community focus"],
        threats=["Price competition", "Chain convenience"]
    )


# PersonaAgent Tests
class TestPersonaAgent:
    """Test PersonaAgent functionality"""

    @pytest.mark.asyncio
    async def test_generate_persona(self, sample_profile):
        """Test single persona generation"""
        agent = PersonaAgent()

        # Mock the generate_json method
        mock_persona_data = {
            "name": "Test Persona",
            "age_range": "25-35",
            "interests": ["coffee", "work"],
            "platforms": ["Instagram"],
            "creative_style": "modern",
            "motivation": "quality coffee"
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_persona_data):
            persona = await agent.generate_persona(sample_profile)

            assert isinstance(persona, Persona)
            assert persona.name == "Test Persona"
            assert persona.age_range == "25-35"
            assert len(persona.interests) >= 1
            assert len(persona.platforms) >= 1

    @pytest.mark.asyncio
    async def test_generate_personas_multiple(self, sample_profile):
        """Test multiple personas generation"""
        agent = PersonaAgent()

        mock_persona_data = {
            "name": "Test Persona",
            "age_range": "25-35",
            "interests": ["coffee"],
            "platforms": ["Instagram"],
            "creative_style": "modern",
            "motivation": "quality"
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_persona_data):
            personas = await agent.generate_personas(sample_profile, count=3)

            assert len(personas) == 3
            assert all(isinstance(p, Persona) for p in personas)


# LocationAgent Tests
class TestLocationAgent:
    """Test LocationAgent functionality"""

    @pytest.mark.asyncio
    async def test_recommend_miles(self, sample_profile):
        """Test miles radius recommendation"""
        agent = LocationAgent()

        mock_recommendation = {
            "suggested_miles": 5,
            "current_miles": 3,
            "reasoning": "Coffee shops typically serve 3-5 mile radius for daily customers. This is based on convenience and commute patterns for regular coffee purchases.",
            "business_type_category": "daily-service",
            "typical_customer_travel": "3-5 miles",
            "optimization_factors": ["Daily purchase frequency", "Local competition"]
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_recommendation):
            recommendation = await agent.recommend_miles(sample_profile)

            assert isinstance(recommendation, LocationRecommendation)
            assert recommendation.suggested_miles == 5
            assert recommendation.current_miles == 3
            assert len(recommendation.reasoning) > 0

    @pytest.mark.asyncio
    async def test_analyze_location_alias(self, sample_profile):
        """Test analyze_location alias method"""
        agent = LocationAgent()

        mock_recommendation = {
            "suggested_miles": 5,
            "current_miles": 3,
            "reasoning": "Test reasoning for location recommendation with at least 50 characters to meet validation requirements.",
            "business_type_category": "daily-service",
            "typical_customer_travel": "3-5 miles",
            "optimization_factors": ["factor1"]
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_recommendation):
            recommendation = await agent.analyze_location(sample_profile)

            assert isinstance(recommendation, LocationRecommendation)
            assert recommendation.suggested_miles == 5


# CompetitorAgent Tests
class TestCompetitorAgent:
    """Test CompetitorAgent functionality"""

    @pytest.mark.asyncio
    async def test_analyze_competitors(self):
        """Test competitor analysis"""
        agent = CompetitorAgent()

        mock_snapshot = {
            "competitors": [
                {
                    "name": "Starbucks",
                    "website": "starbucks.com",
                    "social_presence": ["Instagram"],
                    "advertising_channels": ["Google Ads"],
                    "content_style": "corporate",
                    "strengths": ["Brand"],
                    "weaknesses": ["Price"]
                }
            ],
            "market_insights": "Competitive market",
            "opportunities": ["Local focus"],
            "threats": ["Price wars"]
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_snapshot):
            snapshot = await agent.analyze_competitors(
                ["Starbucks", "Blue Bottle"],
                "Coffee Shop",
                "San Francisco"
            )

            assert isinstance(snapshot, CompetitorSnapshot)
            assert len(snapshot.competitors) >= 1
            assert len(snapshot.opportunities) >= 1


# PlannerAgent Tests
class TestPlannerAgent:
    """Test PlannerAgent functionality"""

    @pytest.mark.asyncio
    async def test_generate_scenarios(self, sample_profile, sample_persona, sample_competitor_snapshot):
        """Test budget scenario generation"""
        agent = PlannerAgent()

        mock_scenarios = {
            "standard_plan": {
                "total_budget": 2500,
                "duration_weeks": 10,
                "channels": [
                    {"name": "Google Ads", "budget_share_percent": 40.0, "reasoning": "Primary search traffic capture"},
                    {"name": "Facebook Ads", "budget_share_percent": 30.0, "reasoning": "Social media engagement"},
                    {"name": "Instagram Ads", "budget_share_percent": 30.0, "reasoning": "Visual content marketing"}
                ]
            },
            "aggressive_plan": {
                "total_budget": 3000,
                "duration_weeks": 10,
                "channels": [
                    {"name": "Google Ads", "budget_share_percent": 45.0, "reasoning": "Dominant search presence"},
                    {"name": "Facebook Ads", "budget_share_percent": 25.0, "reasoning": "Retargeting campaigns"},
                    {"name": "Instagram Ads", "budget_share_percent": 30.0, "reasoning": "Brand awareness push"}
                ]
            },
            "experimental_plan": {
                "total_budget": 2800,
                "duration_weeks": 10,
                "channels": [
                    {"name": "TikTok Ads", "budget_share_percent": 35.0, "reasoning": "Viral potential content"},
                    {"name": "Instagram Influencers", "budget_share_percent": 35.0, "reasoning": "Influencer partnerships"},
                    {"name": "YouTube Ads", "budget_share_percent": 30.0, "reasoning": "Video content marketing"}
                ]
            }
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_scenarios):
            scenarios = await agent.generate_scenarios(
                sample_profile,
                sample_persona,
                sample_competitor_snapshot
            )

            assert hasattr(scenarios, 'standard_plan')
            assert hasattr(scenarios, 'aggressive_plan')
            assert hasattr(scenarios, 'experimental_plan')
            assert len(scenarios.standard_plan.channels) >= 3


# CreativeAgent Tests
class TestCreativeAgent:
    """Test CreativeAgent functionality"""

    @pytest.mark.asyncio
    async def test_generate_assets(self, sample_profile, sample_persona):
        """Test creative asset generation"""
        agent = CreativeAgent()

        mock_assets = {
            "ideas": [
                {
                    "title": "Morning Rush Special",
                    "description": "Target morning commuters with special offers",
                    "image_prompt": "Coffee and laptop in cozy setting",
                    "image_url": "https://picsum.photos/400/300",
                    "image_alt": "Morning coffee scene"
                },
                {
                    "title": "Afternoon Break",
                    "description": "Afternoon pick-me-up campaign for working professionals",
                    "image_prompt": "Relaxing coffee break atmosphere",
                    "image_url": "https://picsum.photos/400/300",
                    "image_alt": "Afternoon coffee time"
                },
                {
                    "title": "Weekend Brunch",
                    "description": "Weekend special featuring brunch menu items",
                    "image_prompt": "Brunch setting with coffee and pastries",
                    "image_url": "https://picsum.photos/400/300",
                    "image_alt": "Weekend brunch scene"
                }
            ],
            "short_ad_copy": "Best artisan coffee in SF! Locally roasted, ethically sourced. Visit us today!",
            "long_ad_copy": "Discover artisan coffee brewed with care at Joe's Coffee Shop. We source our beans directly from sustainable farms and roast them locally for the freshest flavor.",
            "slogans": ["Your daily brew awaits", "Coffee done right every time", "Where great coffee meets great people"],
            "hashtags": ["#SFCoffee", "#ArtisanBrew", "#LocalCoffee", "#CoffeeLovers", "#SpecialtyCoffee", "#SupportLocal", "#CoffeeCommunity", "#SanFrancisco"],
            "cta_options": ["Order Now", "Visit Us Today", "Join Our Coffee Club"]
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_assets):
            assets = await agent.generate_assets(sample_profile, sample_persona)

            assert len(assets.ideas) >= 1
            assert len(assets.short_ad_copy) > 0
            assert len(assets.slogans) >= 1
            assert len(assets.hashtags) >= 1


# PerformanceAgent Tests
class TestPerformanceAgent:
    """Test PerformanceAgent functionality"""

    @pytest.mark.asyncio
    async def test_predict_performance(self, sample_profile, sample_persona):
        """Test performance prediction"""
        agent = PerformanceAgent()

        # Create minimal mock scenario
        from app.schemas import ScenarioSet, MediaPlan, ChannelAllocation

        mock_plan = MediaPlan(
            total_budget=2500,
            duration_weeks=10,
            channels=[
                ChannelAllocation(name="Google Ads", budget_share_percent=40.0, reasoning="Search traffic"),
                ChannelAllocation(name="Facebook Ads", budget_share_percent=30.0, reasoning="Social engagement"),
                ChannelAllocation(name="Instagram Ads", budget_share_percent=30.0, reasoning="Visual content")
            ]
        )

        scenarios = ScenarioSet(
            standard_plan=mock_plan,
            aggressive_plan=mock_plan,
            experimental_plan=mock_plan
        )

        mock_performance = {
            "standard": {
                "reach": "10,000-12,000 people",
                "clicks": "500-700 clicks",
                "cpc_estimate": "$4.50-$5.50",
                "roi_range": "3-4x return",
                "reach_analytics": {},
                "budget_scaling": {}
            },
            "aggressive": {
                "reach": "15,000-18,000 people",
                "clicks": "750-950 clicks",
                "cpc_estimate": "$3.00-$3.75",
                "roi_range": "4-5x return",
                "reach_analytics": {},
                "budget_scaling": {}
            },
            "experimental": {
                "reach": "20,000-25,000 people",
                "clicks": "1,000-1,300 clicks",
                "cpc_estimate": "$2.50-$3.50",
                "roi_range": "3-5x return",
                "reach_analytics": {},
                "budget_scaling": {}
            }
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_performance):
            performance = await agent.predict_performance(
                scenarios,
                sample_persona,
                sample_profile.business_type,
                sample_profile.location,
                sample_profile.is_local
            )

            assert hasattr(performance, 'standard')
            assert hasattr(performance, 'aggressive')
            assert hasattr(performance, 'experimental')
            assert len(performance.standard.reach) > 0
            assert len(performance.standard.clicks) > 0


# CriticAgent Tests
class TestCriticAgent:
    """Test CriticAgent functionality"""

    @pytest.mark.asyncio
    async def test_evaluate_plan(self, sample_profile, sample_persona, sample_competitor_snapshot):
        """Test plan evaluation"""
        from app.schemas import ScenarioSet, MediaPlan, ChannelAllocation, CreativeAssets, CreativeIdea

        agent = CriticAgent()

        # Create proper mock data structures
        mock_plan = MediaPlan(
            total_budget=2500,
            duration_weeks=10,
            channels=[
                ChannelAllocation(name="Google Ads", budget_share_percent=40.0, reasoning="Search traffic"),
                ChannelAllocation(name="Facebook Ads", budget_share_percent=30.0, reasoning="Social engagement"),
                ChannelAllocation(name="Instagram Ads", budget_share_percent=30.0, reasoning="Visual content")
            ]
        )

        scenarios = ScenarioSet(
            standard_plan=mock_plan,
            aggressive_plan=mock_plan,
            experimental_plan=mock_plan
        )

        creatives = CreativeAssets(
            ideas=[
                CreativeIdea(title="Test 1", description="Test description 1"),
                CreativeIdea(title="Test 2", description="Test description 2"),
                CreativeIdea(title="Test 3", description="Test description 3")
            ],
            hashtags=["#test1", "#test2", "#test3", "#test4", "#test5", "#test6", "#test7", "#test8"],
            slogans=["Slogan 1", "Slogan 2", "Slogan 3"],
            short_ad_copy="Short ad copy for testing with enough characters",
            long_ad_copy="Long ad copy for testing with enough characters to meet the minimum requirement of 50 characters",
            cta_options=["CTA 1", "CTA 2", "CTA 3"]
        )

        mock_evaluation = {
            "overall_score": 0.89,
            "channel_mix_score": 0.85,
            "budget_logic_score": 0.90,
            "persona_alignment_score": 0.88,
            "competitor_differentiation_score": 0.87,
            "creative_integration_score": 0.91,
            "feasibility_score": 0.92,
            "strengths": ["Good budget allocation", "Strong persona fit"],
            "issues": [],
            "summary": "Excellent marketing plan"
        }

        with patch.object(agent, 'generate_json', new_callable=AsyncMock, return_value=mock_evaluation):
            evaluation = await agent.evaluate_plan(
                scenarios,
                sample_persona,
                sample_competitor_snapshot,
                creatives,
                sample_profile.goal
            )

            assert evaluation["overall_score"] >= 0.0
            assert evaluation["overall_score"] <= 1.0
            assert len(evaluation["summary"]) > 0
            assert "strengths" in evaluation


# Integration Tests
class TestAgentIntegration:
    """Test agent workflow integration"""

    @pytest.mark.asyncio
    async def test_full_agent_workflow(self, sample_profile):
        """Test complete agent workflow without actual API calls"""

        # Initialize agents
        persona_agent = PersonaAgent()
        location_agent = LocationAgent()
        competitor_agent = CompetitorAgent()

        # Mock all responses
        mock_persona = {
            "name": "Test", "age_range": "25-35", "interests": ["coffee"],
            "platforms": ["Instagram"], "creative_style": "modern", "motivation": "quality"
        }

        mock_location = {
            "suggested_miles": 5, "current_miles": 3,
            "reasoning": "Test reasoning with at least 50 characters to meet validation requirements for this field",
            "business_type_category": "daily", "typical_customer_travel": "3-5",
            "optimization_factors": ["test"]
        }

        mock_competitors = {
            "competitors": [{
                "name": "Test", "website": "test.com", "social_presence": ["IG"],
                "advertising_channels": ["Google"], "content_style": "test",
                "strengths": ["test"], "weaknesses": ["test"]
            }],
            "market_insights": "test", "opportunities": ["test"], "threats": ["test"]
        }

        with patch.object(persona_agent, 'generate_json', new_callable=AsyncMock, return_value=mock_persona), \
             patch.object(location_agent, 'generate_json', new_callable=AsyncMock, return_value=mock_location), \
             patch.object(competitor_agent, 'generate_json', new_callable=AsyncMock, return_value=mock_competitors):

            # Execute workflow
            personas = await persona_agent.generate_personas(sample_profile, count=2)
            location = await location_agent.analyze_location(sample_profile)
            competitors = await competitor_agent.analyze_competitors(
                sample_profile.competitors,
                sample_profile.business_type,
                sample_profile.location
            )

            # Verify results
            assert len(personas) == 2
            assert isinstance(location, LocationRecommendation)
            assert isinstance(competitors, CompetitorSnapshot)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
