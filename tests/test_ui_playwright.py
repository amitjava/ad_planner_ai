"""
Playwright UI Tests for Smart Ad Planner

This test suite uses Playwright to test the UI functionality.
Run with: pytest tests/test_ui_playwright.py
"""

import pytest
from playwright.sync_api import Page, expect
import time


# Base URL for the application
BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


class TestSmartAdPlannerUI:
    """UI tests for Smart Ad Planner"""

    def test_homepage_loads(self, page: Page):
        """Test that the homepage loads correctly"""
        page.goto(BASE_URL)

        # Check title
        expect(page).to_have_title("Smart Ad Planner - Create Your Marketing Plan")

        # Check header
        expect(page.locator("h1")).to_contain_text("AI-Powered Small Business Ad Planner")
        expect(page.locator("h3")).to_contain_text("by Amit Dar")

    def test_form_elements_present(self, page: Page):
        """Test that all form elements are present"""
        page.goto(BASE_URL)

        # Check business information fields
        expect(page.locator("#business_name")).to_be_visible()
        expect(page.locator("#business_type")).to_be_visible()
        expect(page.locator("#zip_code")).to_be_visible()
        expect(page.locator("#miles_radius")).to_be_visible()

        # Check goal field
        expect(page.locator("#goal")).to_be_visible()

        # Check budget field
        expect(page.locator("#monthly_budget")).to_be_visible()
        expect(page.locator("#duration_weeks")).to_be_visible()

        # Check submit button
        expect(page.locator('button[type="submit"]')).to_be_visible()

    def test_form_validation(self, page: Page):
        """Test form validation"""
        page.goto(BASE_URL)

        # Try to submit empty form
        page.click('button[type="submit"]')

        # HTML5 validation should prevent submission
        # Check if business name field is required
        business_name = page.locator("#business_name")
        expect(business_name).to_have_attribute("required", "")

    def test_fill_business_profile(self, page: Page):
        """Test filling out the business profile form"""
        page.goto(BASE_URL)

        # Fill business information
        page.fill("#business_name", "Test Coffee Shop")
        page.fill("#business_type", "Coffee Shop")
        page.fill("#zip_code", "98101")
        page.fill("#miles_radius", "3")

        # Fill goal
        page.fill("#goal", "Increase foot traffic and brand awareness")

        # Fill budget
        page.fill("#monthly_budget", "2500")
        page.fill("#duration_weeks", "8")

        # Add competitors
        page.fill("#competitors", "Starbucks, Local Cafe")

        # Verify values are filled
        expect(page.locator("#business_name")).to_have_value("Test Coffee Shop")
        expect(page.locator("#monthly_budget")).to_have_value("2500")

    def test_competitor_field(self, page: Page):
        """Test adding competitors"""
        page.goto(BASE_URL)

        # Fill competitor field
        page.fill("#competitors", "Competitor 1, Competitor 2, Competitor 3")

        # Verify value
        expect(page.locator("#competitors")).to_have_value("Competitor 1, Competitor 2, Competitor 3")

    def test_response_sections_exist(self, page: Page):
        """Test that response sections exist in the DOM"""
        page.goto(BASE_URL)

        # Check for results container
        expect(page.locator("#result")).to_be_attached()

    def test_navigation_elements(self, page: Page):
        """Test navigation and UI elements"""
        page.goto(BASE_URL)

        # Check form sections
        expect(page.locator("text=Business Information")).to_be_visible()
        expect(page.locator("text=Budget & Timeline")).to_be_visible()
        expect(page.locator("text=Competitive Landscape")).to_be_visible()

    def test_responsive_layout(self, page: Page):
        """Test responsive layout on different viewport sizes"""
        # Desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(BASE_URL)
        expect(page.locator("h1")).to_be_visible()

        # Tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("h1")).to_be_visible()

        # Mobile
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("h1")).to_be_visible()

    def test_form_accessibility(self, page: Page):
        """Test basic accessibility features"""
        page.goto(BASE_URL)

        # Check for labels associated with inputs
        expect(page.locator('label[for="business_name"]')).to_be_visible()
        expect(page.locator('label[for="monthly_budget"]')).to_be_visible()

        # Check for required fields
        expect(page.locator("#business_name")).to_have_attribute("required", "")
        expect(page.locator("#business_type")).to_have_attribute("required", "")


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    @pytest.mark.slow
    def test_complete_form_submission(self, page: Page):
        """Test complete form submission workflow (this will take time due to AI processing)"""
        page.goto(BASE_URL)

        # Set longer timeout for AI processing
        page.set_default_timeout(120000)  # 2 minutes

        # Fill complete form
        page.fill("#business_name", "E2E Test Coffee Shop")
        page.fill("#business_type", "Coffee Shop")
        page.fill("#zip_code", "97201")
        page.fill("#miles_radius", "5")
        page.fill("#goal", "Increase memberships and class attendance")
        page.fill("#monthly_budget", "1500")
        page.fill("#duration_weeks", "12")
        page.fill("#competitors", "Starbucks, Dutch Bros")

        # Submit form
        page.click('button[type="submit"]')

        # Wait for loading indicator or results
        # Note: You may need to add specific selectors based on your UI
        page.wait_for_selector("#result", state="visible", timeout=120000)

        # Check if results are displayed
        expect(page.locator("#result")).to_be_visible()


# Configuration for pytest-playwright
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
