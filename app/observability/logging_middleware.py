"""Logging Middleware for FastAPI"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details"""

        # Start timing
        start_time = time.time()

        # Get request details
        request_id = request.headers.get('X-Request-ID', 'unknown')
        method = request.method
        path = request.url.path

        # Log request
        logger.info(f"Request started: {method} {path} [ID: {request_id}]")

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {method} {path} "
                f"[Status: {response.status_code}] "
                f"[Duration: {duration:.3f}s] "
                f"[ID: {request_id}]"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                f"Request failed: {method} {path} "
                f"[Error: {str(e)}] "
                f"[Duration: {duration:.3f}s] "
                f"[ID: {request_id}]"
            )
            raise


class AgentCallLogger:
    """Logger for agent calls"""

    def __init__(self):
        self.logger = logging.getLogger("agents")

    def log_agent_call(
        self,
        agent_name: str,
        method: str,
        duration: float,
        success: bool,
        error: str = None
    ):
        """Log an agent method call"""

        log_data = {
            "agent": agent_name,
            "method": method,
            "duration_seconds": round(duration, 3),
            "success": success
        }

        if error:
            log_data["error"] = error

        if success:
            self.logger.info(f"Agent call: {json.dumps(log_data)}")
        else:
            self.logger.error(f"Agent call failed: {json.dumps(log_data)}")

    def log_plan_generation(
        self,
        session_id: str,
        total_duration: float,
        agent_calls: int,
        critic_score: float
    ):
        """Log complete plan generation"""

        log_data = {
            "event": "plan_generated",
            "session_id": session_id,
            "total_duration_seconds": round(total_duration, 3),
            "agent_calls": agent_calls,
            "critic_score": round(critic_score, 2)
        }

        self.logger.info(f"Plan generation: {json.dumps(log_data)}")


# Global agent logger instance
agent_logger = AgentCallLogger()
