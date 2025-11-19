"""Metrics Collection and Reporting"""
from typing import Dict, Any, List
from datetime import datetime
import json


class MetricsCollector:
    """Collects and aggregates application metrics"""

    def __init__(self):
        self.reset_metrics()

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency_ms": 0,
            "plans_generated": 0,
            "total_critic_score": 0,
            "agent_calls": 0,
            "errors": [],
            "start_time": datetime.now().isoformat()
        }

    def record_request(self, success: bool, latency_ms: float):
        """Record a request"""
        self.metrics["total_requests"] += 1
        self.metrics["total_latency_ms"] += latency_ms

        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

    def record_plan(self, critic_score: float, agent_calls: int):
        """Record a plan generation"""
        self.metrics["plans_generated"] += 1
        self.metrics["total_critic_score"] += critic_score
        self.metrics["agent_calls"] += agent_calls

    def record_error(self, error: str, context: str = ""):
        """Record an error"""
        self.metrics["errors"].append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 100 errors
        if len(self.metrics["errors"]) > 100:
            self.metrics["errors"] = self.metrics["errors"][-100:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_latency = (
            self.metrics["total_latency_ms"] / self.metrics["total_requests"]
            if self.metrics["total_requests"] > 0
            else 0
        )

        avg_critic_score = (
            self.metrics["total_critic_score"] / self.metrics["plans_generated"]
            if self.metrics["plans_generated"] > 0
            else 0
        )

        return {
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": (
                self.metrics["successful_requests"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0
                else 0
            ),
            "avg_latency_ms": round(avg_latency, 2),
            "plans_generated": self.metrics["plans_generated"],
            "avg_critic_score": round(avg_critic_score, 2),
            "total_agent_calls": self.metrics["agent_calls"],
            "recent_errors": self.metrics["errors"][-10:],
            "uptime_since": self.metrics["start_time"]
        }

    def get_summary(self) -> str:
        """Get metrics summary as string"""
        metrics = self.get_metrics()
        return json.dumps(metrics, indent=2)


# Global metrics collector
metrics_collector = MetricsCollector()
