"""Progress Tracking for Agent Execution"""
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

class ProgressTracker:
    """Tracks progress of agent execution and sends updates to clients"""

    def __init__(self):
        self.progress_data: Dict[str, Any] = {}
        self.subscribers: Dict[str, asyncio.Queue] = {}

    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """Subscribe to progress updates for a session"""
        queue = asyncio.Queue()
        self.subscribers[session_id] = queue
        return queue

    def unsubscribe(self, session_id: str):
        """Unsubscribe from progress updates"""
        if session_id in self.subscribers:
            del self.subscribers[session_id]

    async def update_progress(
        self,
        session_id: str,
        step: int,
        total_steps: int,
        agent_name: str,
        status: str,
        message: str
    ):
        """Send progress update to subscribers"""
        progress_percent = int((step / total_steps) * 100)

        update = {
            "step": step,
            "total_steps": total_steps,
            "progress_percent": progress_percent,
            "agent_name": agent_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        # Store latest progress
        self.progress_data[session_id] = update

        # Send to subscribers
        if session_id in self.subscribers:
            await self.subscribers[session_id].put(update)

    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a session"""
        return self.progress_data.get(session_id)

# Global progress tracker instance
progress_tracker = ProgressTracker()

# Agent configuration with descriptions
AGENT_STEPS = [
    {
        "step": 1,
        "name": "RAGAgent",
        "icon": "🔍",
        "description": "Retrieving historical insights from vector database..."
    },
    {
        "step": 2,
        "name": "PersonaAgent",
        "icon": "👥",
        "description": "Generating 3 detailed customer personas..."
    },
    {
        "step": 3,
        "name": "LocationAgent",
        "icon": "📍",
        "description": "Analyzing location demographics and optimal radius..."
    },
    {
        "step": 4,
        "name": "CompetitorAgent",
        "icon": "🏆",
        "description": "Researching competitors and market opportunities..."
    },
    {
        "step": 5,
        "name": "PlannerAgent",
        "icon": "💰",
        "description": "Creating 3 budget scenarios with channel allocation..."
    },
    {
        "step": 6,
        "name": "CreativeAgent",
        "icon": "🎨",
        "description": "Generating creative assets and ad copy..."
    },
    {
        "step": 7,
        "name": "PerformanceAgent",
        "icon": "📈",
        "description": "Predicting performance metrics and ROI..."
    },
    {
        "step": 8,
        "name": "CriticAgent",
        "icon": "✅",
        "description": "Evaluating plan quality and scoring..."
    }
]

def get_agent_step_info(agent_name: str) -> Dict[str, Any]:
    """Get step information for an agent"""
    for step_info in AGENT_STEPS:
        if step_info["name"] == agent_name:
            return step_info
    return {"step": 0, "name": agent_name, "icon": "🤖", "description": f"Processing {agent_name}..."}
