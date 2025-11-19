# Smart Ad Planner - Test Suite

Comprehensive test coverage for the Smart Ad Planner application.

## Test Types

### 1. Unit Tests (`test_agents.py`)
Tests individual agent functionality with mocked responses.

**Coverage:**
- PersonaAgent (generate_persona, generate_personas)
- LocationAgent (recommend_miles, analyze_location)
- CompetitorAgent (analyze_competitors)
- PlannerAgent (generate_scenarios)
- CreativeAgent (generate_assets)
- PerformanceAgent (predict_performance)
- CriticAgent (evaluate_plan)
- Integration workflow tests

**Run:**
```bash
pytest tests/test_agents.py -v
```

### 2. Playwright Tests (`test_dashboard.py`)
End-to-end UI tests for the Streamlit dashboard.

**Coverage:**
- Dashboard loading and rendering
- Example button functionality
- Form inputs and validation
- Responsive design
- Accessibility
- Performance metrics

**Run:**
```bash
# First, ensure Streamlit is running on localhost:8501
streamlit run app_streamlit.py

# In another terminal:
pytest tests/test_dashboard.py -v --headed
```

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Unit Tests Only
```bash
pytest tests/test_agents.py -v
```

### Playwright Tests Only
```bash
pytest tests/test_dashboard.py -v
```

### With Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Specific Test Class
```bash
pytest tests/test_agents.py::TestPersonaAgent -v
```

### Specific Test Method
```bash
pytest tests/test_agents.py::TestPersonaAgent::test_generate_persona -v
```

## Test Configuration

Configured in `pytest.ini`:
- Async test support via pytest-asyncio
- Strict markers enforcement
- Colored output
- Short tracebacks

## Mocking Strategy

Unit tests use `unittest.mock` to mock agent responses:
- `AsyncMock` for async methods
- `patch.object` to mock `generate_json` calls
- Fixtures for common test data

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    playwright install chromium
    pytest tests/test_agents.py -v
    
    # Start Streamlit in background
    streamlit run app_streamlit.py &
    sleep 10
    
    # Run Playwright tests
    pytest tests/test_dashboard.py -v
```

## Test Data

Fixtures provide sample data:
- `sample_profile`: Coffee shop business profile
- `sample_persona`: Target customer persona
- `sample_competitor_snapshot`: Market analysis

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Reuse common test data
3. **Mock external calls**: Don't make real API requests in tests
4. **Test edge cases**: Include error scenarios
5. **Maintain coverage**: Aim for 80%+ code coverage

## Troubleshooting

**Playwright tests fail to connect:**
- Ensure Streamlit is running on http://localhost:8501
- Check firewall settings
- Try `--headed` flag to see browser

**Async tests fail:**
- Verify pytest-asyncio is installed
- Check `asyncio_mode = auto` in pytest.ini

**Import errors:**
- Ensure you're in the project root directory
- Verify `PYTHONPATH` includes the app directory

## Future Enhancements

- [ ] Add API endpoint tests
- [ ] Add load testing
- [ ] Add security testing
- [ ] Increase code coverage to 90%+
- [ ] Add snapshot testing for UI components
