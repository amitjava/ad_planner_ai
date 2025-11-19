"""Creative Agent - Generates creative assets using Google ADK"""
from .base_agent import BaseAgent
from ..schemas import BusinessProfile, Persona, CreativeAssets
import base64
import os
from pathlib import Path
from vertexai.preview.vision_models import ImageGenerationModel


class CreativeAgent(BaseAgent):
    """Agent for generating creative assets using Google ADK"""

    SYSTEM_INSTRUCTION = """You are CreativeAgent, a creative director and copywriter.
Generate compelling creative assets including:

- 3 creative ideas (2–4 lines each)
- 10 hashtags
- 3 slogans
- Short ad copy (12-20 words)
- Long ad copy (60-120 words)
- 3 CTA options

Return ONLY valid JSON matching the CreativeAssets schema. No other text."""

    def __init__(self):
        """Initialize CreativeAgent with Google ADK"""
        super().__init__(
            agent_name="creative_agent",
            description="Generates creative campaign ideas and ad copy",
            instruction=self.SYSTEM_INSTRUCTION,
            model="gemini-2.0-flash",
            temperature=0.9
        )

    async def generate_assets(
        self,
        profile: BusinessProfile,
        persona: Persona
    ) -> CreativeAssets:
        """Generate creative assets based on profile and persona

        Args:
            profile: BusinessProfile object
            persona: Persona object

        Returns:
            CreativeAssets with campaign ideas, copy, and hashtags
        """
        user_prompt = f"""
{self.SYSTEM_INSTRUCTION}

Business Profile:
- Name: {profile.business_name}
- Type: {profile.business_type}
- Location: {profile.location}
- Goal: {profile.goal}

Target Persona:
- Name: {persona.name}
- Age: {persona.age_range}
- Interests: {', '.join(persona.interests)}
- Platforms: {', '.join(persona.platforms)}
- Creative Style: {persona.creative_style}
- Motivation: {persona.motivation}

Generate creative assets that will resonate with this persona:

1. Three creative campaign ideas (each 2-4 sentences)
2. Ten relevant hashtags (mix of branded and trending)
3. Three catchy slogans
4. Short ad copy (12-20 words, punchy and memorable)
5. Long ad copy (60-120 words, engaging story)
6. Three call-to-action options

Return ONLY JSON with this structure:
{{
    "ideas": [
        {{
            "title": "string",
            "description": "string",
            "image_prompt": "detailed image generation prompt for this creative idea",
            "image_alt": "accessibility alt text for the image"
        }}
    ],
    "hashtags": ["string"],
    "slogans": ["string"],
    "short_ad_copy": "string",
    "long_ad_copy": "string",
    "cta_options": ["string"]
}}

IMPORTANT: For each creative idea, generate a detailed image_prompt that describes the visual concept.
The image_prompt should be specific, descriptive, and suitable for AI image generation.
Example: "A warm, inviting coffee shop interior with professionals working on laptops, natural lighting streaming through large windows, modern minimalist design, steaming coffee cups on wooden tables, photorealistic style"
"""

        assets_data = await self.generate_json(user_prompt)

        # Generate images for each creative idea
        try:
            generated_assets = await self._generate_images_for_ideas(assets_data, profile)
            return CreativeAssets(**generated_assets)
        except Exception as e:
            print(f"Image generation failed: {e}, returning text-only assets")
            return CreativeAssets(**assets_data)

    async def _generate_images_for_ideas(self, assets_data: dict, profile: BusinessProfile) -> dict:
        """Generate images for creative ideas using Pexels API

        Args:
            assets_data: Creative assets data with image prompts
            profile: Business profile for context

        Returns:
            Updated assets_data with image URLs from Pexels
        """
        import urllib.parse
        import requests
        import os

        # Pexels API configuration (free tier: 200 requests/hour)
        pexels_api_key = os.getenv('PEXELS_API_KEY')

        # Generate images for each creative idea
        for i, idea in enumerate(assets_data.get('ideas', [])):
            image_prompt = idea.get('image_prompt', '')

            if not image_prompt:
                print(f"No image prompt for idea {i}, using default placeholder")
                idea['image_url'] = f"https://placehold.co/800x800/1a73e8/white?text=Creative+Idea+{i+1}"
                continue

            try:
                # Extract search keywords from prompt
                keywords = self._extract_keywords_from_prompt(image_prompt)
                search_query = ' '.join(keywords[:3])

                if pexels_api_key:
                    # Use Pexels API for real stock photos
                    pexels_url = "https://api.pexels.com/v1/search"
                    headers = {'Authorization': pexels_api_key}
                    params = {
                        'query': search_query,
                        'per_page': 1,
                        'orientation': 'square'
                    }

                    response = requests.get(pexels_url, headers=headers, params=params, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        if 'photos' in data and len(data['photos']) > 0:
                            # Use the large size image
                            image_url = data['photos'][0]['src']['large']
                            idea['image_url'] = image_url
                            print(f"✓ Pexels found image for idea {i+1}: {search_query}")
                            continue
                        else:
                            print(f"No Pexels images found for '{search_query}'")
                    else:
                        print(f"Pexels API error ({response.status_code})")

                # Fallback: Use Lorem Picsum with seed for consistent images
                # Provides random high-quality stock photos without API key
                # Using seed based on search query for consistency
                seed = hash(search_query + str(i)) % 1000
                lorem_picsum_url = f"https://picsum.photos/seed/{seed}/800/800"
                idea['image_url'] = lorem_picsum_url
                print(f"✓ Using Lorem Picsum image for idea {i+1} (seed: {seed})")

            except Exception as img_error:
                print(f"Error fetching image for idea {i}: {img_error}")
                idea['image_url'] = f"https://placehold.co/800x800/1a73e8/white?text=Creative+Idea+{i+1}"

        return assets_data

    def _extract_keywords_from_prompt(self, prompt: str) -> list:
        """Extract relevant keywords from image prompt for Google Image Search

        Args:
            prompt: Image generation prompt

        Returns:
            List of keywords
        """
        # Common keywords that work well with image search
        business_keywords = {
            'coffee', 'cafe', 'shop', 'business', 'professional', 'workspace',
            'laptop', 'meeting', 'food', 'lunch', 'office', 'modern', 'interior',
            'restaurant', 'barista', 'espresso', 'latte', 'bakery', 'boutique',
            'yoga', 'fitness', 'wellness', 'studio', 'retail', 'store', 'shopping',
            'customer', 'service', 'team', 'design', 'marketing', 'advertising'
        }

        # Extract keywords that appear in the prompt
        prompt_lower = prompt.lower()
        keywords = [kw for kw in business_keywords if kw in prompt_lower]

        # If no matches, use generic business keywords
        if not keywords:
            keywords = ['business', 'professional', 'modern']

        return keywords[:5]  # Limit to 5 keywords
