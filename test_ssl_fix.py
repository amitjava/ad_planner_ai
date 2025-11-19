#!/usr/bin/env python3
"""
Test SSL Fix - Verify that SSL certificates are properly configured
"""
# IMPORTANT: Configure SSL certificates BEFORE any other imports
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import asyncio
from app.schemas import BusinessProfile
from app.agents import PersonaAgent

async def test_ssl_connection():
    """Test that we can successfully connect to Vertex AI without SSL errors"""

    print("Testing SSL configuration...")
    print(f"SSL_CERT_FILE: {os.environ.get('SSL_CERT_FILE')}")
    print(f"REQUESTS_CA_BUNDLE: {os.environ.get('REQUESTS_CA_BUNDLE')}")

    # Create a test profile
    profile = BusinessProfile(
        business_name="Test Coffee Shop",
        business_type="Coffee Shop",
        location="San Francisco, CA",
        zip_code="94107",
        miles_radius=3,
        goal="Test SSL connection",
        monthly_budget=2500.0,
        duration_weeks=4,
        competitors=["Starbucks"],
        is_local=True
    )

    print("\nInitializing PersonaAgent...")
    agent = PersonaAgent()

    print("Attempting to generate persona (this will test SSL connection)...")
    try:
        persona = await agent.generate_persona(profile)
        print("\n✅ SUCCESS! SSL connection working properly")
        print(f"Generated persona: {persona.name}")
        return True
    except Exception as e:
        print(f"\n❌ FAILED! SSL error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ssl_connection())
    exit(0 if success else 1)
