"""
Test Data Generator API
Generates realistic business profile data using Gemini
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import subprocess
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

router = APIRouter()

# Configure google-genai to use Vertex AI with ADC
def _configure_vertex_ai():
    """Configure environment variables for Vertex AI with ADC"""
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


class TestDataRequest(BaseModel):
    business_type: str  # "coffee_shop", "yoga_studio", "boutique"


class TestDataResponse(BaseModel):
    business_name: str
    business_type: str
    zip_code: str
    miles_radius: int
    goal: str
    monthly_budget: int
    duration_weeks: int
    competitors: str
    is_local: bool


async def generate_realistic_data(business_category: str) -> dict:
    """Generate realistic business data using Gemini"""

    prompts = {
        "coffee_shop": """
Generate a realistic coffee shop business profile with the following information:
- business_name: A creative, realistic coffee shop name (not Starbucks or major chains)
- business_type: "Coffee Shop"
- zip_code: A real 5-digit ZIP code from San Francisco area (use: 94102, 94103, 94104, 94105, or 94107)
- miles_radius: 3 (coffee shops are daily-service businesses with small optimal radius)
- goal: A DETAILED marketing goal with multiple sentences that includes:
  * Specific metric/target (e.g., increase morning traffic by 25%, add 100 new loyalty members)
  * Target audience (e.g., office workers within 1 mile, college students, remote workers)
  * Timeframe (e.g., over the next 8 weeks, by end of quarter)
  * Geographic/channel focus (e.g., within 2 mile radius, Instagram and local food blogs)
  Example format: "Increase weekday morning traffic by 30% by targeting remote workers and freelancers within a 1-mile radius. Focus on building a community atmosphere and promoting our specialty pour-over coffee and work-friendly environment through Instagram, local partnerships, and Google My Business optimization."
- monthly_budget: A realistic marketing budget for a small coffee shop (between $1,500 - $5,000)
- duration_weeks: A campaign duration (between 6-12 weeks)
- competitors: 2-3 realistic competitors (mix of local and chain names), comma-separated
- is_local: true

Return ONLY valid JSON with these exact field names, no markdown formatting, no explanations:
""",
        "yoga_studio": """
Generate a realistic yoga studio business profile with the following information:
- business_name: A creative, realistic yoga studio name
- business_type: "Yoga Studio"
- zip_code: A real 5-digit ZIP code from Denver area (use: 80202, 80203, 80204, 80205, or 80206)
- miles_radius: 5 (yoga studios are weekly-service businesses with medium optimal radius)
- goal: A DETAILED marketing goal with multiple sentences that includes:
  * Specific metric/target (e.g., grow membership by 40 students, increase evening class attendance by 50%)
  * Target audience (e.g., busy professionals 30-45, wellness-focused millennials, beginners)
  * Timeframe (e.g., over the next 10 weeks, within 3 months)
  * Geographic/channel focus (e.g., within 3 miles, Facebook and wellness influencers, local health events)
  Example format: "Grow studio membership by 50 new students within the next 10 weeks by targeting wellness-focused millennials and busy professionals (ages 28-45) in the downtown area. Emphasize stress relief, flexibility, and community through targeted Facebook ads, Instagram stories showcasing student success, and partnerships with local health food stores and corporate wellness programs."
- monthly_budget: A realistic marketing budget for a yoga studio (between $1,000 - $4,000)
- duration_weeks: A campaign duration (between 6-10 weeks)
- competitors: 2-3 realistic yoga studio or fitness competitor names, comma-separated
- is_local: true

Return ONLY valid JSON with these exact field names, no markdown formatting, no explanations:
""",
        "boutique": """
Generate a realistic fashion boutique business profile with the following information:
- business_name: A creative, realistic boutique name
- business_type: "Fashion Boutique"
- zip_code: A real 5-digit ZIP code from New York area (use: 10001, 10011, 10012, 10013, or 10014)
- miles_radius: 10 (fashion boutiques are occasional-retail businesses with larger optimal radius)
- goal: A DETAILED marketing goal with multiple sentences that includes:
  * Specific metric/target (e.g., drive 25% increase in online sales, attract 200 new customers, increase foot traffic by 40%)
  * Target audience (e.g., fashion-forward women 25-40, sustainable fashion enthusiasts, young professionals)
  * Timeframe (e.g., over 12-week campaign, by end of season)
  * Geographic/channel focus (e.g., local neighborhood + online, Instagram and TikTok, fashion bloggers)
  Example format: "Drive a 30% increase in both online and in-store sales for our new spring collection over the next 12 weeks by targeting fashion-forward women aged 25-40 in the metro area. Build brand awareness as a sustainable, locally-curated fashion destination through Instagram shopping posts, TikTok styling videos, partnerships with local fashion influencers, and exclusive in-store events for VIP customers."
- monthly_budget: A realistic marketing budget for a boutique (between $3,000 - $8,000)
- duration_weeks: A campaign duration (between 8-12 weeks)
- competitors: 2-3 realistic boutique or fashion retailer competitor names, comma-separated
- is_local: true

Return ONLY valid JSON with these exact field names, no markdown formatting, no explanations:
"""
    }

    prompt = prompts.get(business_category)
    if not prompt:
        raise ValueError(f"Unknown business category: {business_category}")

    try:
        # Use Google ADK with ADC
        agent = Agent(
            name="test_data_generator",
            model="gemini-2.0-flash",
            description="Generates test data for businesses",
            instruction="Generate realistic business data based on the provided prompt",
            generate_content_config=types.GenerateContentConfig(
                temperature=0.8,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
        )

        runner = InMemoryRunner(agent=agent, app_name="test_data_app")

        # Create or get session
        session = await runner.session_service.get_session(
            app_name="test_data_app",
            user_id="test_user",
            session_id=f"test_{business_category}"
        )
        if not session:
            session = await runner.session_service.create_session(
                app_name="test_data_app",
                user_id="test_user",
                session_id=f"test_{business_category}"
            )

        # Create message
        message = types.Content(role="user", parts=[types.Part(text=prompt)])

        # Run agent and collect response
        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        # Clean and parse JSON
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        data = json.loads(response_text)

        # Handle backward compatibility: if AI returns 'location' instead of 'zip_code'
        if "location" in data and "zip_code" not in data:
            # Map business type to appropriate zip code and miles
            zip_mappings = {
                "coffee_shop": {"zip_code": "94102", "miles_radius": 3},
                "yoga_studio": {"zip_code": "80202", "miles_radius": 5},
                "boutique": {"zip_code": "10001", "miles_radius": 10}
            }
            mapping = zip_mappings.get(business_category, {"zip_code": "10001", "miles_radius": 5})
            data["zip_code"] = mapping["zip_code"]
            data["miles_radius"] = mapping["miles_radius"]
            # Remove old location field
            del data["location"]

        # Validate required fields
        required_fields = ["business_name", "business_type", "zip_code", "miles_radius", "goal",
                         "monthly_budget", "duration_weeks", "competitors", "is_local"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Response text: {response_text}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse generated data as JSON: {str(e)}"
        )
    except Exception as e:
        print(f"Error generating test data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test data: {str(e)}"
        )


@router.post("/generate", response_model=TestDataResponse)
async def generate_test_data(request: TestDataRequest):
    """
    Generate realistic test data for a specific business type

    Args:
        request: TestDataRequest with business_type

    Returns:
        TestDataResponse with generated business profile data
    """
    # ADC or API key should be configured at startup
    # No validation needed here - if genai wasn't configured, agents won't work

    business_type = request.business_type.lower()

    # Map frontend business types to internal categories
    type_mapping = {
        "coffee_shop": "coffee_shop",
        "yoga_studio": "yoga_studio",
        "boutique": "boutique"
    }

    if business_type not in type_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported business type. Must be one of: {', '.join(type_mapping.keys())}"
        )

    try:
        data = await generate_realistic_data(type_mapping[business_type])
        return TestDataResponse(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test data: {str(e)}"
        )
