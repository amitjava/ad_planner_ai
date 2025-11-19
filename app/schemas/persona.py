"""Persona Schema"""
from pydantic import BaseModel, Field
from typing import List


class Persona(BaseModel):
    """Customer persona model"""
    name: str = Field(..., description="Persona name")
    age_range: str = Field(..., description="Age range (e.g., 25-34)")
    interests: List[str] = Field(..., description="List of interests")
    platforms: List[str] = Field(..., description="Preferred social media platforms")
    creative_style: str = Field(..., description="Preferred creative/visual style")
    motivation: str = Field(..., description="Core motivation for purchasing")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Urban Professional Sarah",
                "age_range": "28-35",
                "interests": ["specialty coffee", "remote work", "sustainability"],
                "platforms": ["Instagram", "LinkedIn", "TikTok"],
                "creative_style": "Modern, clean aesthetics with authentic lifestyle shots",
                "motivation": "Quality over quantity, seeks authentic local experiences"
            }
        }
