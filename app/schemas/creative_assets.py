"""Creative Assets Schema"""
from pydantic import BaseModel, Field
from typing import List


class CreativeIdea(BaseModel):
    """Single creative concept"""
    title: str = Field(..., description="Creative concept title")
    description: str = Field(..., description="Detailed description")
    image_url: str = Field(default="", description="Generated image URL")
    image_prompt: str = Field(default="", description="Image generation prompt")
    image_alt: str = Field(default="", description="Image alt text")


class CreativeAssets(BaseModel):
    """Complete creative asset package"""
    ideas: List[CreativeIdea] = Field(..., min_items=3, max_items=5, description="Creative concepts")
    hashtags: List[str] = Field(..., min_items=8, max_items=15, description="Relevant hashtags")
    slogans: List[str] = Field(..., min_items=3, max_items=5, description="Campaign slogans")
    short_ad_copy: str = Field(..., min_length=10, max_length=200, description="Short form ad copy")
    long_ad_copy: str = Field(..., min_length=50, max_length=1000, description="Long form ad copy")
    cta_options: List[str] = Field(..., min_items=3, max_items=5, description="Call-to-action options")

    class Config:
        json_schema_extra = {
            "example": {
                "ideas": [
                    {
                        "title": "Morning Ritual Series",
                        "description": "Showcase different customer morning routines featuring your coffee"
                    },
                    {
                        "title": "Behind the Beans",
                        "description": "Educational content about coffee sourcing and roasting process"
                    },
                    {
                        "title": "Community Corner",
                        "description": "Highlight local artists, musicians, and regulars who make the shop special"
                    }
                ],
                "hashtags": ["#LocalCoffee", "#SFCoffee", "#CoffeeLovers", "#SpecialtyCoffee", "#SupportLocal", "#CoffeeCommunity", "#MorningRitual", "#CraftCoffee", "#CoffeeAddict", "#SanFrancisco"],
                "slogans": [
                    "Your neighborhood's daily dose of awesome",
                    "Where great coffee meets great people",
                    "Locally roasted, globally inspired"
                ],
                "short_ad_copy": "Start your day right with locally roasted, ethically sourced coffee. Visit Joe's Coffee Shop today!",
                "long_ad_copy": "At Joe's Coffee Shop, we're more than just coffee – we're your neighborhood's gathering place. Every cup is crafted with passion using beans sourced directly from sustainable farms. Whether you're here for your morning espresso, an afternoon pick-me-up, or to catch up with friends, we're brewing something special just for you. Join our community today.",
                "cta_options": [
                    "Visit Us Today",
                    "Try Our Signature Blend",
                    "Join Our Coffee Club"
                ]
            }
        }
