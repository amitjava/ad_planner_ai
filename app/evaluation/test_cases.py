"""Comprehensive Test Cases for Agent Evaluation"""
from typing import List, Dict, Any
from ..schemas import BusinessProfile


class TestCaseLibrary:
    """Library of test cases for evaluating the agent system"""

    @staticmethod
    def get_all_test_cases() -> List[Dict[str, Any]]:
        """Get all test cases with expected outcomes"""
        return [
            # 1. Local Coffee Shop - Small Budget
            {
                "id": "test_001",
                "category": "Food & Beverage",
                "profile": BusinessProfile(
                    business_name="Joe's Coffee Shop",
                    business_type="Coffee Shop",
                    location="San Francisco, CA",
                    goal="Increase foot traffic and brand awareness",
                    monthly_budget=2500.0,
                    duration_weeks=8,
                    is_local=True,
                    competitors=["Starbucks", "Blue Bottle Coffee"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-34", "28-35", "25-40"],
                    "persona_platforms": ["Instagram", "TikTok", "Facebook"],
                    "channels_should_include": ["Instagram Ads", "Google Local", "Facebook"],
                    "min_critic_score": 0.65,
                    "budget_range": (2000, 3000)
                }
            },

            # 2. B2B SaaS - Large Budget
            {
                "id": "test_002",
                "category": "Technology/SaaS",
                "profile": BusinessProfile(
                    business_name="TechStart SaaS",
                    business_type="B2B SaaS Company",
                    location="Austin, TX",
                    goal="Generate qualified leads for enterprise software",
                    monthly_budget=10000.0,
                    duration_weeks=12,
                    is_local=False,
                    competitors=["Salesforce", "HubSpot", "Monday.com"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["30-45", "35-50"],
                    "persona_platforms": ["LinkedIn", "Twitter"],
                    "channels_should_include": ["LinkedIn Ads", "Google Ads", "Content Marketing"],
                    "min_critic_score": 0.70,
                    "budget_range": (9000, 11000)
                }
            },

            # 3. Yoga Studio - Medium Budget, Local
            {
                "id": "test_003",
                "category": "Health & Wellness",
                "profile": BusinessProfile(
                    business_name="Green Valley Yoga",
                    business_type="Yoga Studio",
                    location="Portland, OR",
                    goal="Grow membership and class attendance",
                    monthly_budget=1500.0,
                    duration_weeks=6,
                    is_local=True,
                    competitors=["CorePower Yoga", "LA Fitness", "Lifetime Fitness"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-45", "30-50"],
                    "persona_platforms": ["Instagram", "Facebook"],
                    "channels_should_include": ["Instagram", "Facebook", "Google Local"],
                    "min_critic_score": 0.65,
                    "budget_range": (1200, 1800)
                }
            },

            # 4. Fashion Boutique - E-commerce Focus
            {
                "id": "test_004",
                "category": "Retail/Fashion",
                "profile": BusinessProfile(
                    business_name="Urban Threads Boutique",
                    business_type="Fashion Boutique",
                    location="New York, NY",
                    goal="Drive online and in-store sales",
                    monthly_budget=5000.0,
                    duration_weeks=10,
                    is_local=True,
                    competitors=["Zara", "H&M", "Urban Outfitters"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["18-35", "22-40"],
                    "persona_platforms": ["Instagram", "TikTok", "Pinterest"],
                    "channels_should_include": ["Instagram", "TikTok", "Google Shopping"],
                    "min_critic_score": 0.70,
                    "budget_range": (4500, 5500)
                }
            },

            # 5. Fitness Center - Membership Growth
            {
                "id": "test_005",
                "category": "Fitness",
                "profile": BusinessProfile(
                    business_name="Peak Performance Gym",
                    business_type="Fitness Center",
                    location="Denver, CO",
                    goal="Increase memberships and personal training sign-ups",
                    monthly_budget=3500.0,
                    duration_weeks=8,
                    is_local=True,
                    competitors=["24 Hour Fitness", "Anytime Fitness", "Planet Fitness"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-45", "20-40"],
                    "persona_platforms": ["Instagram", "Facebook", "YouTube"],
                    "channels_should_include": ["Instagram", "Facebook", "Google Local"],
                    "min_critic_score": 0.65,
                    "budget_range": (3000, 4000)
                }
            },

            # 6. Restaurant - New Opening
            {
                "id": "test_006",
                "category": "Food & Beverage",
                "profile": BusinessProfile(
                    business_name="Taste of Mumbai",
                    business_type="Indian Restaurant",
                    location="Seattle, WA",
                    goal="Build awareness for new restaurant opening",
                    monthly_budget=4000.0,
                    duration_weeks=6,
                    is_local=True,
                    competitors=["Tandoori Grill", "India Palace", "Masala"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-50", "28-55"],
                    "persona_platforms": ["Instagram", "Yelp", "Google Maps"],
                    "channels_should_include": ["Instagram", "Google Local", "Yelp"],
                    "min_critic_score": 0.65,
                    "budget_range": (3500, 4500)
                }
            },

            # 7. Professional Services - B2B
            {
                "id": "test_007",
                "category": "Professional Services",
                "profile": BusinessProfile(
                    business_name="Smith & Associates Law",
                    business_type="Law Firm",
                    location="Boston, MA",
                    goal="Generate consultation requests for corporate law",
                    monthly_budget=8000.0,
                    duration_weeks=12,
                    is_local=False,
                    competitors=["BigLaw Corp", "Corporate Legal Partners"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["35-55", "40-60"],
                    "persona_platforms": ["LinkedIn", "Google"],
                    "channels_should_include": ["LinkedIn", "Google Ads", "Content Marketing"],
                    "min_critic_score": 0.70,
                    "budget_range": (7500, 8500)
                }
            },

            # 8. E-commerce Store - National
            {
                "id": "test_008",
                "category": "E-commerce",
                "profile": BusinessProfile(
                    business_name="Pet Paradise Online",
                    business_type="Pet Supplies E-commerce",
                    location="Los Angeles, CA",
                    goal="Increase online sales and customer acquisition",
                    monthly_budget=6000.0,
                    duration_weeks=10,
                    is_local=False,
                    competitors=["Chewy", "Petco", "Amazon"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-45", "30-50"],
                    "persona_platforms": ["Facebook", "Instagram", "Pinterest"],
                    "channels_should_include": ["Facebook", "Google Shopping", "Instagram"],
                    "min_critic_score": 0.70,
                    "budget_range": (5500, 6500)
                }
            },

            # 9. Education - Online Courses
            {
                "id": "test_009",
                "category": "Education",
                "profile": BusinessProfile(
                    business_name="Code Academy Pro",
                    business_type="Online Coding Bootcamp",
                    location="Remote/Online",
                    goal="Enroll students in coding bootcamp programs",
                    monthly_budget=7500.0,
                    duration_weeks=8,
                    is_local=False,
                    competitors=["Udemy", "Coursera", "General Assembly"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["22-35", "25-40"],
                    "persona_platforms": ["LinkedIn", "YouTube", "Reddit"],
                    "channels_should_include": ["LinkedIn", "YouTube", "Google Ads"],
                    "min_critic_score": 0.70,
                    "budget_range": (7000, 8000)
                }
            },

            # 10. Home Services - Local
            {
                "id": "test_010",
                "category": "Home Services",
                "profile": BusinessProfile(
                    business_name="Green Clean Landscaping",
                    business_type="Landscaping Service",
                    location="Phoenix, AZ",
                    goal="Book more landscaping projects and consultations",
                    monthly_budget=2000.0,
                    duration_weeks=12,
                    is_local=True,
                    competitors=["Lawn Pros", "Desert Landscaping", "HomeAdvisor Contractors"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["35-65", "40-70"],
                    "persona_platforms": ["Facebook", "Google", "Nextdoor"],
                    "channels_should_include": ["Google Local", "Facebook", "Nextdoor"],
                    "min_critic_score": 0.65,
                    "budget_range": (1800, 2200)
                }
            },

            # 11. Beauty Salon - Premium
            {
                "id": "test_011",
                "category": "Beauty & Personal Care",
                "profile": BusinessProfile(
                    business_name="Luxe Hair Studio",
                    business_type="Premium Hair Salon",
                    location="Miami, FL",
                    goal="Attract high-end clients and increase booking rate",
                    monthly_budget=3000.0,
                    duration_weeks=8,
                    is_local=True,
                    competitors=["Salon 5th Avenue", "Beauty Bar", "Glam Studio"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-50", "28-55"],
                    "persona_platforms": ["Instagram", "Facebook", "Yelp"],
                    "channels_should_include": ["Instagram", "Facebook", "Google Local"],
                    "min_critic_score": 0.70,
                    "budget_range": (2700, 3300)
                }
            },

            # 12. Automotive - Service Center
            {
                "id": "test_012",
                "category": "Automotive",
                "profile": BusinessProfile(
                    business_name="AutoCare Plus",
                    business_type="Auto Repair Shop",
                    location="Chicago, IL",
                    goal="Increase service appointments and build trust",
                    monthly_budget=2500.0,
                    duration_weeks=10,
                    is_local=True,
                    competitors=["Pep Boys", "Jiffy Lube", "Firestone"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-55", "30-60"],
                    "persona_platforms": ["Google", "Facebook", "Yelp"],
                    "channels_should_include": ["Google Local", "Facebook", "YouTube"],
                    "min_critic_score": 0.65,
                    "budget_range": (2200, 2800)
                }
            },

            # 13. Dental Practice - Family
            {
                "id": "test_013",
                "category": "Healthcare",
                "profile": BusinessProfile(
                    business_name="Bright Smiles Family Dentistry",
                    business_type="Dental Practice",
                    location="Charlotte, NC",
                    goal="Attract new patients and promote preventive care",
                    monthly_budget=4500.0,
                    duration_weeks=12,
                    is_local=True,
                    competitors=["Aspen Dental", "Affordable Dentures", "Local Dental Practices"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["30-50", "35-55"],
                    "persona_platforms": ["Google", "Facebook", "Nextdoor"],
                    "channels_should_include": ["Google Local", "Facebook", "Display Ads"],
                    "min_critic_score": 0.70,
                    "budget_range": (4000, 5000)
                }
            },

            # 14. Real Estate - Agency
            {
                "id": "test_014",
                "category": "Real Estate",
                "profile": BusinessProfile(
                    business_name="Premier Properties Realty",
                    business_type="Real Estate Agency",
                    location="San Diego, CA",
                    goal="Generate buyer and seller leads",
                    monthly_budget=5500.0,
                    duration_weeks=8,
                    is_local=True,
                    competitors=["Keller Williams", "RE/MAX", "Coldwell Banker"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["30-55", "35-60"],
                    "persona_platforms": ["Facebook", "Instagram", "Zillow"],
                    "channels_should_include": ["Facebook", "Google Ads", "Instagram"],
                    "min_critic_score": 0.70,
                    "budget_range": (5000, 6000)
                }
            },

            # 15. Craft Brewery - Local
            {
                "id": "test_015",
                "category": "Food & Beverage",
                "profile": BusinessProfile(
                    business_name="Hoppy Hour Brewery",
                    business_type="Craft Brewery & Taproom",
                    location="Portland, ME",
                    goal="Increase taproom visits and build brand community",
                    monthly_budget=3200.0,
                    duration_weeks=10,
                    is_local=True,
                    competitors=["Allagash Brewing", "Shipyard Brewing", "Local Breweries"]
                ),
                "expected_outcomes": {
                    "persona_age_range": ["25-45", "28-50"],
                    "persona_platforms": ["Instagram", "Facebook", "Untappd"],
                    "channels_should_include": ["Instagram", "Facebook", "Local Events"],
                    "min_critic_score": 0.65,
                    "budget_range": (2900, 3500)
                }
            }
        ]

    @staticmethod
    def get_test_case_by_id(test_id: str) -> Dict[str, Any]:
        """Get a specific test case by ID"""
        for test_case in TestCaseLibrary.get_all_test_cases():
            if test_case["id"] == test_id:
                return test_case
        return None

    @staticmethod
    def get_test_cases_by_category(category: str) -> List[Dict[str, Any]]:
        """Get all test cases for a specific category"""
        return [
            tc for tc in TestCaseLibrary.get_all_test_cases()
            if tc["category"] == category
        ]

    @staticmethod
    def get_test_case_categories() -> List[str]:
        """Get list of all test case categories"""
        categories = set()
        for tc in TestCaseLibrary.get_all_test_cases():
            categories.add(tc["category"])
        return sorted(list(categories))
