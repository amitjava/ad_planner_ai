"""Base Agent using Google ADK (Agent Development Kit)"""
import json
import os
import ssl
import subprocess
from typing import Dict, Any, Optional
import certifi
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Configure SSL to use certifi certificates
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Configure google-genai to use Vertex AI with ADC
def _configure_vertex_ai():
    """Configure environment variables for Vertex AI with ADC"""
    # Get project ID from environment or gcloud config
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VERTEX_AI_PROJECT_ID")
    if not project_id:
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True
            )
            project_id = result.stdout.strip()
        except:
            pass

    if project_id:
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# Configure on module import
_configure_vertex_ai()


class BaseAgent:
    """Base class for all agents using Google ADK

    Uses Application Default Credentials (ADC) for authentication.
    This is the production-ready approach for Google Cloud.
    """

    def __init__(
        self,
        agent_name: str,
        description: str,
        instruction: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        tools: Optional[list] = None
    ):
        """Initialize the agent with Google ADK

        Args:
            agent_name: Unique name for the agent
            description: Agent's capability description
            instruction: System instructions for the agent
            model: Google AI model (e.g., "gemini-2.0-flash", "gemini-1.5-flash")
            temperature: Generation temperature (0.0-1.0)
            tools: Optional list of tool functions

        Authentication:
            Uses Application Default Credentials (ADC) automatically.
            No API key needed!
        """
        self.agent_name = agent_name
        self.description = description
        self.instruction = instruction
        self.model = model
        self.temperature = temperature

        # Create ADK Agent
        self.agent = Agent(
            name=agent_name,
            model=model,
            description=description,
            instruction=instruction,
            tools=tools or [],
            generate_content_config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
            )
        )

        # Create InMemoryRunner for agent execution
        self.runner = InMemoryRunner(
            agent=self.agent,
            app_name=f"{agent_name}_app"
        )

        print(f"✓ Initialized {agent_name} with Google ADK (Model: {model})")

    async def _create_or_get_session(
        self,
        user_id: str = "default_user",
        session_id: str = "default_session"
    ):
        """Create or get an existing session

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Session object
        """
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=user_id,
            session_id=session_id
        )

        if not session:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id
            )

        return session

    def _clean_json_response(self, response_text: str) -> str:
        """Clean JSON response from markdown code blocks and common issues"""
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Remove any trailing commas before closing braces/brackets (common JSON error)
        import re
        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)

        return response_text

    async def generate_json(
        self,
        prompt: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate JSON response from prompt using ADK

        Args:
            prompt: The prompt to send to the model
            user_id: User identifier
            session_id: Session identifier (auto-generated if None)

        Returns:
            Parsed JSON response as dictionary
        """
        # Generate unique session ID if not provided
        if session_id is None:
            import uuid
            session_id = f"json_{uuid.uuid4().hex[:8]}"

        # Ensure session exists
        await self._create_or_get_session(user_id, session_id)

        # Create message
        message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        # Run agent and collect response
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        # Clean and parse JSON with better error handling
        cleaned_text = self._clean_json_response(response_text)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error in {self.agent_name}:")
            print(f"Error: {e}")
            print(f"Raw response (first 500 chars): {response_text[:500]}")
            print(f"Cleaned text (first 500 chars): {cleaned_text[:500]}")

            # Try to extract JSON from response if it's embedded in text
            try:
                # Look for JSON object boundaries
                start_idx = cleaned_text.find('{')
                end_idx = cleaned_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_portion = cleaned_text[start_idx:end_idx+1]
                    json_portion = self._clean_json_response(json_portion)
                    print(f"Attempting to parse extracted JSON portion...")
                    return json.loads(json_portion)
            except:
                pass

            # If all else fails, re-raise the original error
            raise

    async def generate_text(
        self,
        prompt: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None
    ) -> str:
        """Generate text response from prompt using ADK

        Args:
            prompt: The prompt to send to the model
            user_id: User identifier
            session_id: Session identifier (auto-generated if None)

        Returns:
            Generated text response
        """
        # Generate unique session ID if not provided
        if session_id is None:
            import uuid
            session_id = f"text_{uuid.uuid4().hex[:8]}"

        # Ensure session exists
        await self._create_or_get_session(user_id, session_id)

        # Create message
        message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        # Run agent and collect response
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return response_text.strip()

    async def close(self):
        """Close the runner and cleanup resources"""
        await self.runner.close()
