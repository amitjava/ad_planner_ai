"""Performance Prediction Schema"""
from pydantic import BaseModel, Field
from typing import Dict


class PerformancePrediction(BaseModel):
    """Performance metrics prediction for a plan"""
    reach: str = Field(..., description="Estimated reach (e.g., '15,000-20,000 people')")
    clicks: str = Field(..., description="Estimated clicks/engagements")
    cpc_estimate: str = Field(..., description="Cost per click estimate")
    roi_range: str = Field(..., description="Expected ROI range")
    reach_analytics: Dict = Field(default_factory=dict, description="Detailed reach analytics")
    budget_scaling: Dict = Field(default_factory=dict, description="Budget recommendations to scale reach")

    class Config:
        json_schema_extra = {
            "example": {
                "reach": "15,000-20,000 people",
                "clicks": "800-1,200 clicks",
                "cpc_estimate": "$1.50-$2.50",
                "roi_range": "2.5x-3.5x return"
            }
        }


class PerformanceSet(BaseModel):
    """Performance predictions for all three scenarios"""
    standard: PerformancePrediction
    aggressive: PerformancePrediction
    experimental: PerformancePrediction
