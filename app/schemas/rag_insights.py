"""RAG Insights Schema"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class RecommendedChannel(BaseModel):
    """Recommended marketing channel based on historical data"""
    channel: str = Field(..., description="Name of the marketing channel")
    reasoning: str = Field(..., description="Why this channel worked well for similar businesses")
    expected_performance: str = Field(..., description="Expected performance based on historical data")


class BudgetInsights(BaseModel):
    """Budget optimization insights from historical data"""
    optimal_range: str = Field(..., description="Recommended budget range based on similar businesses")
    allocation_tips: str = Field(..., description="Tips for effective budget allocation")


class RAGInsights(BaseModel):
    """Insights generated from historical data using RAG"""
    key_patterns: List[str] = Field(
        default_factory=list,
        description="Key patterns observed in successful similar campaigns"
    )
    recommended_channels: List[RecommendedChannel] = Field(
        default_factory=list,
        description="Marketing channels recommended based on historical success"
    )
    budget_insights: BudgetInsights = Field(
        default=BudgetInsights(
            optimal_range="Insufficient data",
            allocation_tips="Consider industry benchmarks"
        ),
        description="Budget-related insights from historical data"
    )
    targeting_recommendations: List[str] = Field(
        default_factory=list,
        description="Targeting strategies that worked for similar businesses"
    )
    potential_pitfalls: List[str] = Field(
        default_factory=list,
        description="Common mistakes to avoid based on historical failures"
    )
    success_factors: List[str] = Field(
        default_factory=list,
        description="Critical success factors identified from high-performing campaigns"
    )
    confidence_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score based on amount and quality of historical data"
    )
    data_points_analyzed: int = Field(
        0,
        ge=0,
        description="Number of similar historical cases analyzed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "key_patterns": [
                    "Coffee shops in urban areas see 30% higher engagement with Instagram ads",
                    "Lunchtime targeting works best between 11 AM - 2 PM for similar businesses"
                ],
                "recommended_channels": [
                    {
                        "channel": "Instagram Ads",
                        "reasoning": "Similar coffee shops achieved 40% higher ROI compared to Facebook",
                        "expected_performance": "15,000-20,000 reach with $1.50 CPC"
                    }
                ],
                "budget_insights": {
                    "optimal_range": "$2,000-$3,500 for similar local coffee shops",
                    "allocation_tips": "60% social media, 30% local search, 10% email for this business type"
                },
                "targeting_recommendations": [
                    "Focus on 25-40 age group based on similar successful campaigns",
                    "Target within 2-mile radius for daily-service businesses"
                ],
                "potential_pitfalls": [
                    "Avoid overspreading budget across too many channels (max 4 recommended)",
                    "Don't neglect mobile optimization - 75% of similar customers use mobile"
                ],
                "success_factors": [
                    "Consistent posting schedule (3-5x per week)",
                    "User-generated content drives 2x higher engagement"
                ],
                "confidence_score": 0.85,
                "data_points_analyzed": 12
            }
        }


class RAGAugmentedProfile(BaseModel):
    """Business profile augmented with RAG insights"""
    original_profile: Dict[str, Any] = Field(..., description="Original business profile")
    rag_insights: RAGInsights = Field(..., description="Insights from historical data analysis")
    similar_context_count: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of similar profiles and plans found"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "original_profile": {
                    "business_name": "The Daily Grind SF",
                    "business_type": "Coffee Shop",
                    "location": "San Francisco",
                    "goal": "Increase lunchtime traffic"
                },
                "rag_insights": {
                    "key_patterns": ["Pattern 1", "Pattern 2"],
                    "confidence_score": 0.75,
                    "data_points_analyzed": 8
                },
                "similar_context_count": {
                    "profiles": 5,
                    "plans": 3
                }
            }
        }
