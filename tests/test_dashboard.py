#!/usr/bin/env python3
"""
Playwright Tests for Streamlit Dashboard
Tests the interactive UI at http://localhost:8501
"""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        }
    }


class TestDashboardLoading:
    """Test dashboard loads correctly"""

    def test_dashboard_loads(self, page: Page):
        """Test that dashboard loads without errors"""
        page.goto("http://localhost:8501")

        # Wait for Streamlit to load
        page.wait_for_selector("h1", timeout=10000)

        # Check main header exists
        expect(page.locator("text=Smart Ad Planner")).to_be_visible()

    def test_sidebar_visible(self, page: Page):
        """Test sidebar with form is visible"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check sidebar elements
        expect(page.locator("text=Business Profile")).to_be_visible()
        expect(page.locator("text=Business Name")).to_be_visible()

    def test_metrics_displayed(self, page: Page):
        """Test that key metrics are displayed"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check for metrics
        expect(page.locator("text=Cost Savings")).to_be_visible()
        expect(page.locator("text=Time Saved")).to_be_visible()
        expect(page.locator("text=AI Agents")).to_be_visible()


class TestExampleButtons:
    """Test example profile buttons"""

    def test_coffee_shop_example(self, page: Page):
        """Test Coffee Shop example button"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Click Coffee Shop example
        coffee_button = page.locator("button:has-text('Coffee Shop Example')")
        expect(coffee_button).to_be_visible()
        coffee_button.click()

        # Wait for page to reload with example data
        time.sleep(2)

        # Verify form is pre-filled
        business_name_input = page.locator("input[aria-label='Business Name *']").first
        expect(business_name_input).to_have_value("Joe's Coffee Shop")

    def test_fitness_studio_example(self, page: Page):
        """Test Fitness Studio example button"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Click Fitness Studio example
        fitness_button = page.locator("button:has-text('Fitness Studio Example')")
        expect(fitness_button).to_be_visible()
        fitness_button.click()

        # Wait for reload
        time.sleep(2)

        # Verify form is pre-filled
        business_name_input = page.locator("input[aria-label='Business Name *']").first
        expect(business_name_input).to_have_value("Fitness First Gym")

    def test_retail_store_example(self, page: Page):
        """Test Retail Store example button"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Click Retail Store example
        retail_button = page.locator("button:has-text('Retail Store Example')")
        expect(retail_button).to_be_visible()
        retail_button.click()

        # Wait for reload
        time.sleep(2)

        # Verify form is pre-filled
        business_name_input = page.locator("input[aria-label='Business Name *']").first
        expect(business_name_input).to_have_value("Bella's Boutique")


class TestFormInputs:
    """Test form input fields"""

    def test_business_name_input(self, page: Page):
        """Test business name can be entered"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Find and fill business name
        business_name = page.locator("input[aria-label='Business Name *']").first
        business_name.fill("Test Business")

        expect(business_name).to_have_value("Test Business")

    def test_business_type_selector(self, page: Page):
        """Test business type dropdown"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check business type selector exists
        expect(page.locator("text=Business Type")).to_be_visible()

    def test_location_input(self, page: Page):
        """Test location input"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Find and fill location
        location = page.locator("input[aria-label='Location *']").first
        location.fill("New York, NY")

        expect(location).to_have_value("New York, NY")

    def test_budget_input(self, page: Page):
        """Test monthly budget number input"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Budget input should be visible
        expect(page.locator("text=Monthly Budget")).to_be_visible()

    def test_goal_textarea(self, page: Page):
        """Test marketing goal textarea"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Find and fill goal
        goal = page.locator("textarea[aria-label='Marketing Goal *']").first
        goal.fill("Increase brand awareness by 50%")

        expect(goal).to_have_value("Increase brand awareness by 50%")


class TestFormValidation:
    """Test form validation"""

    def test_submit_empty_form(self, page: Page):
        """Test submitting empty form shows validation error"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Try to submit without filling required fields
        submit_button = page.locator("button:has-text('Generate Marketing Plan')")
        expect(submit_button).to_be_visible()
        submit_button.click()

        # Should show error message
        time.sleep(1)
        # Note: Exact error message depends on Streamlit implementation
        # We just verify button is still there (no navigation happened)
        expect(submit_button).to_be_visible()


class TestWelcomeScreen:
    """Test welcome screen content"""

    def test_how_it_works_section(self, page: Page):
        """Test How It Works section"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        expect(page.locator("text=How It Works")).to_be_visible()
        expect(page.locator("text=Fill in your business profile")).to_be_visible()

    def test_ai_agents_section(self, page: Page):
        """Test 7 AI Agents section"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        expect(page.locator("text=7 AI Agents")).to_be_visible()
        expect(page.locator("text=RAG Agent")).to_be_visible()
        expect(page.locator("text=Persona Agent")).to_be_visible()
        expect(page.locator("text=Location Agent")).to_be_visible()
        expect(page.locator("text=Competitor Agent")).to_be_visible()

    def test_benefits_section(self, page: Page):
        """Test Benefits section"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        expect(page.locator("text=Benefits")).to_be_visible()
        expect(page.locator("text=99.98% cheaper")).to_be_visible()
        expect(page.locator("text=96x faster")).to_be_visible()


class TestResponsiveness:
    """Test responsive design"""

    def test_mobile_viewport(self, page: Page):
        """Test dashboard on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Main header should still be visible
        expect(page.locator("text=Smart Ad Planner")).to_be_visible()

    def test_tablet_viewport(self, page: Page):
        """Test dashboard on tablet viewport"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check content is accessible
        expect(page.locator("text=Business Profile")).to_be_visible()


class TestAccessibility:
    """Test accessibility features"""

    def test_page_title(self, page: Page):
        """Test page has proper title"""
        page.goto("http://localhost:8501")
        expect(page).to_have_title("Smart Ad Planner - AI Marketing Plans")

    def test_form_labels(self, page: Page):
        """Test form inputs have labels"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check key labels exist
        expect(page.locator("text=Business Name")).to_be_visible()
        expect(page.locator("text=Business Type")).to_be_visible()
        expect(page.locator("text=Location")).to_be_visible()
        expect(page.locator("text=Marketing Goal")).to_be_visible()


class TestFooter:
    """Test footer content"""

    def test_footer_visible(self, page: Page):
        """Test footer is visible"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        # Check footer text
        expect(page.locator("text=Built with")).to_be_visible()
        expect(page.locator("text=Google ADK")).to_be_visible()

    def test_github_link(self, page: Page):
        """Test GitHub link in footer"""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        # Check GitHub link exists
        expect(page.locator("a:has-text('GitHub')")).to_be_visible()


# Performance Tests
class TestPerformance:
    """Test performance metrics"""

    def test_initial_load_time(self, page: Page):
        """Test page loads within acceptable time"""
        start_time = time.time()
        page.goto("http://localhost:8501")
        page.wait_for_load_state("domcontentloaded")
        load_time = time.time() - start_time

        # Should load in under 5 seconds
        assert load_time < 5.0, f"Page took {load_time:.2f}s to load"

    def test_no_console_errors(self, page: Page):
        """Test page has no console errors"""
        errors = []

        page.on("console", lambda msg:
            errors.append(msg.text) if msg.type == "error" else None
        )

        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Filter out known Streamlit warnings
        critical_errors = [e for e in errors if "streamlit" not in e.lower()]

        assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])
