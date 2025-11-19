"""Media Plan Schemas"""
from pydantic import BaseModel, Field
from typing import List


class ChannelAllocation(BaseModel):
    """Individual channel allocation"""
    name: str = Field(..., description="Channel name (e.g., Instagram Ads)")
    budget_share_percent: float = Field(..., ge=0, le=100, description="Percentage of budget")
    reasoning: str = Field(..., description="Why this channel and allocation")


class MediaPlan(BaseModel):
    """Complete media plan for one scenario"""
    total_budget: float = Field(..., gt=0, description="Total budget for this plan")
    duration_weeks: int = Field(..., ge=1, description="Duration in weeks")
    channels: List[ChannelAllocation] = Field(..., min_items=3, max_items=6, description="Channel mix")

    class Config:
        json_schema_extra = {
            "example": {
                "total_budget": 2500.0,
                "duration_weeks": 8,
                "channels": [
                    {
                        "name": "Instagram Ads",
                        "budget_share_percent": 40.0,
                        "reasoning": "High engagement with target demographic"
                    },
                    {
                        "name": "Google Local Ads",
                        "budget_share_percent": 30.0,
                        "reasoning": "Captures local search intent"
                    },
                    {
                        "name": "Facebook Ads",
                        "budget_share_percent": 20.0,
                        "reasoning": "Broader reach and retargeting"
                    },
                    {
                        "name": "Local Event Sponsorship",
                        "budget_share_percent": 10.0,
                        "reasoning": "Community engagement and brand building"
                    }
                ]
            }
        }


class ScenarioSet(BaseModel):
    """Three different campaign scenarios"""
    standard_plan: MediaPlan = Field(..., description="Balanced, safe approach")
    aggressive_plan: MediaPlan = Field(..., description="High risk, high return approach")
    experimental_plan: MediaPlan = Field(..., description="Creative/influencer heavy approach")
