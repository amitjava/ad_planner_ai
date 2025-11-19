"""Competitor Analysis Schema"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class CompetitorInfo(BaseModel):
    """Information about a single competitor"""
    name: str
    website: Optional[str] = None
    social_presence: List[str] = Field(default_factory=list, description="Social platforms they're on")
    advertising_channels: List[str] = Field(default_factory=list, description="Where they advertise")
    content_style: str = Field(default="Unknown", description="Their creative/content approach")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class CompetitorSnapshot(BaseModel):
    """Aggregate competitor intelligence"""
    competitors: List[CompetitorInfo] = Field(..., description="List of analyzed competitors")
    market_insights: str = Field(..., description="Overall market analysis")
    opportunities: List[str] = Field(..., description="Market opportunities identified")
    threats: List[str] = Field(..., description="Competitive threats")

    class Config:
        json_schema_extra = {
            "example": {
                "competitors": [
                    {
                        "name": "Starbucks",
                        "website": "starbucks.com",
                        "social_presence": ["Instagram", "Facebook", "Twitter", "TikTok"],
                        "advertising_channels": ["TV", "Digital Display", "Mobile App", "Email"],
                        "content_style": "Lifestyle-focused, seasonal campaigns, user-generated content",
                        "strengths": ["Brand recognition", "Loyalty program", "Convenience"],
                        "weaknesses": ["Less focus on specialty coffee", "Corporate feel"]
                    }
                ],
                "market_insights": "Local coffee market is competitive but has room for differentiation through authenticity and community focus",
                "opportunities": ["Emphasize local/artisanal positioning", "Build stronger community connections", "Leverage sustainability"],
                "threats": ["Chain convenience", "Price competition", "Delivery apps"]
            }
        }
