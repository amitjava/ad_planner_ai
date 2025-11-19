"""Quick test script for Gemini integration"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.schemas import BusinessProfile
from app.agents import PersonaAgent

def test_gemini():
    """Test Gemini API integration"""

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False

    print("✅ Gemini API key found")
    print(f"   Key: {api_key[:20]}...")

    # Create test business profile
    profile = BusinessProfile(
        business_name="Joe's Coffee Shop",
        business_type="Coffee Shop",
        location="San Francisco, CA",
        goal="Increase foot traffic and brand awareness",
        monthly_budget=2500.0,
        duration_weeks=8,
        is_local=True,
        competitors=["Starbucks", "Blue Bottle Coffee"]
    )

    print("\n📝 Test Business Profile:")
    print(f"   Name: {profile.business_name}")
    print(f"   Type: {profile.business_type}")
    print(f"   Budget: ${profile.monthly_budget}")

    # Test PersonaAgent
    print("\n🤖 Testing PersonaAgent with Gemini...")
    try:
        agent = PersonaAgent(api_key)
        print("   ✓ Agent initialized")

        print("   Generating persona...")
        persona = agent.generate_persona(profile)

        print("\n✅ SUCCESS! Persona generated:")
        print(f"   Name: {persona.name}")
        print(f"   Age Range: {persona.age_range}")
        print(f"   Interests: {', '.join(persona.interests[:3])}...")
        print(f"   Platforms: {', '.join(persona.platforms)}")
        print(f"   Motivation: {persona.motivation[:100]}...")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI INTEGRATION TEST")
    print("=" * 60)

    success = test_gemini()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("Gemini integration is working correctly.")
    else:
        print("❌ TESTS FAILED")
        print("Please check the error messages above.")
    print("=" * 60)

    sys.exit(0 if success else 1)
