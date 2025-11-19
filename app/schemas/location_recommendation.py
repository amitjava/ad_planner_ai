"""Location and Mileage Recommendation Schema"""
from pydantic import BaseModel, Field


class LocationRecommendation(BaseModel):
    """Optimized location targeting recommendation"""
    suggested_miles: int = Field(..., ge=1, le=100, description="Recommended radius in miles")
    current_miles: int = Field(..., ge=1, le=100, description="User's current selection")
    reasoning: str = Field(..., min_length=50, description="Explanation for the recommendation")
    business_type_category: str = Field(..., description="Category: local-service, retail, specialty, etc.")
    typical_customer_travel: str = Field(..., description="How far typical customers travel")
    optimization_factors: list[str] = Field(..., description="Factors considered in recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "suggested_miles": 3,
                "current_miles": 5,
                "reasoning": "Coffee shops are high-frequency, convenience-driven purchases. Most customers won't travel more than 5-10 minutes (3-4 miles) for their daily coffee. A 3-mile radius captures your natural customer base while keeping ad costs efficient.",
                "business_type_category": "local-service",
                "typical_customer_travel": "3-5 miles (5-10 minutes)",
                "optimization_factors": [
                    "High purchase frequency (daily visits)",
                    "Convenience-driven category",
                    "Local competition density",
                    "Cost-per-impression in larger radius"
                ]
            }
        }
