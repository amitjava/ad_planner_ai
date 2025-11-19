"""Data models for the application"""
from pydantic import BaseModel
from typing import Dict, Any
from .schemas import *


class FullPlanOutput(BaseModel):
    """Complete plan output with all components"""
    session_id: str
    persona: Persona
    location_recommendation: LocationRecommendation
    competitor_snapshot: CompetitorSnapshot
    scenarios: ScenarioSet
    performance: Dict[str, Any]  # PerformanceSet as dict
    creatives: CreativeAssets
    critic_evaluation: Dict[str, Any]
    rag_insights: Dict[str, Any] = None  # RAGInsights as dict (optional for backward compatibility)
    summary_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "persona": {},
                "competitor_snapshot": {},
                "scenarios": {},
                "performance": {},
                "creatives": {},
                "critic_evaluation": {
                    "overall_score": 0.85,
                    "issues": [],
                    "strengths": ["Good channel mix", "Strong persona alignment"]
                },
                "rag_insights": {
                    "key_patterns": ["Pattern 1"],
                    "confidence_score": 0.8
                },
                "summary_text": "Your personalized marketing plan is ready!"
            }
        }


class FeedbackRequest(BaseModel):
    """Feedback submission"""
    session_id: str
    plan_type: str  # "standard", "aggressive", or "experimental"
    rating: int  # 1-5
    comments: str = ""


class PlanRequest(BaseModel):
    """Request to generate a plan"""
    profile: BusinessProfile
    session_id: str = None
