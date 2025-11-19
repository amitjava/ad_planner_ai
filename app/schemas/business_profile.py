"""Business Profile Schema"""
from pydantic import BaseModel, Field
from typing import List


class BusinessProfile(BaseModel):
    """Business profile input from user"""
    business_name: str = Field(..., min_length=1, description="Name of the business")
    business_type: str = Field(..., description="Type/industry of business")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code of business location")
    miles_radius: int = Field(..., ge=1, le=100, description="Target radius in miles for advertising")
    goal: str = Field(..., description="Marketing goal (e.g., brand awareness, sales)")
    monthly_budget: float = Field(..., gt=0, description="Monthly advertising budget in USD")
    duration_weeks: int = Field(..., ge=1, le=52, description="Campaign duration in weeks")
    is_local: bool = Field(default=True, description="Whether business is local or national")
    competitors: List[str] = Field(default_factory=list, description="List of competitor names")

    # Computed properties
    @property
    def location(self) -> str:
        """Get location string for backward compatibility"""
        return self.zip_code

    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Joe's Coffee Shop",
                "business_type": "Coffee Shop",
                "zip_code": "94102",
                "miles_radius": 3,
                "goal": "Increase foot traffic and brand awareness",
                "monthly_budget": 2500.0,
                "duration_weeks": 8,
                "is_local": True,
                "competitors": ["Starbucks", "Blue Bottle Coffee"]
            }
        }
