# Testing Guide for Math-To-Manim

This directory contains comprehensive tests for the Math-To-Manim agent system.

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration and fixtures
├── test_prerequisite_explorer.py    # Unit and integration tests
├── live_test_runner.py             # Live testing against Claude API
└── README.md                        # This file
```

## Running Tests

### Quick Start

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_prerequisite_explorer.py -v

# Run with coverage
pytest tests/ --cov=prerequisite_explorer_claude --cov-report=html
```

### Unit Tests (No API Calls)

```bash
# Run only mocked tests (fast, no API costs)
pytest tests/test_prerequisite_explorer.py -v -m "not live"
```

### Integration Tests (With API Calls)

```bash
# Run tests that call Claude API (slower, incurs costs)
pytest tests/test_prerequisite_explorer.py -v -m live
```

### Async Tests

```bash
# Run async/concurrent tests
pytest tests/test_prerequisite_explorer.py::TestAsyncExploration -v
```

### Live Test Runner

```bash
# Run all live test suites
python tests/live_test_runner.py

# Test a specific concept
python tests/live_test_runner.py --concept "cosmology"

# Run specific test suite
python tests/live_test_runner.py --suite analyzer
python tests/live_test_runner.py --suite explorer
python tests/live_test_runner.py --suite performance
```

## Test Categories

### 1. ConceptAnalyzer Tests
- Input parsing and validation
- Concept extraction accuracy
- Domain categorization
- Level determination

### 2. PrerequisiteExplorer Tests
- Foundation detection
- Prerequisite discovery
- Tree building and structure
- Caching mechanism
- Depth limit enforcement

### 3. Integration Tests
- Full pipeline (analyze -> explore)
- Tree validation
- Error handling
- Edge cases

### 4. Async Tests
- Concurrent analysis
- Parallel prerequisite discovery
- Performance under load

### 5. Performance Tests
- Cache efficiency
- Depth scaling
- API call optimization

## Test Markers

Tests are marked with custom markers for selective running:

- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.live` - Tests requiring API calls

Example:
```bash
# Skip slow tests
pytest -v -m "not slow"

# Run only integration tests
pytest -v -m integration

# Run everything except live API tests
pytest -v -m "not live"
```

## Environment Setup

### Required
```bash
ANTHROPIC_API_KEY=your_claude_api_key
```

### Optional
```bash
TEST_MAX_DEPTH=2          # Default tree depth for tests
TEST_TIMEOUT=30           # Timeout for API calls (seconds)
```

## Mocking vs. Live Tests

### Mocked Tests (Fast, Free)
- Use `unittest.mock` to simulate API responses
- No API costs
- Run in CI/CD pipelines
- Useful for development

### Live Tests (Slow, Costs Money)
- Make real API calls to Claude
- Verify actual behavior
- Run before releases
- Use sparingly

## Writing New Tests

### Unit Test Template

```python
import pytest
from prerequisite_explorer_claude import ConceptAnalyzer

class TestMyFeature:
    """Test suite for my feature"""

    def setup_method(self):
        """Setup before each test"""
        self.analyzer = ConceptAnalyzer()

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_my_feature(self):
        """Test description"""
        result = self.analyzer.analyze("test input")

        assert 'core_concept' in result
        assert result['level'] in ['beginner', 'intermediate', 'advanced']
```

### Async Test Template

```python
import pytest
import asyncio

class TestAsyncFeature:

    @pytest.mark.asyncio
    async def test_concurrent_operation(self):
        """Test async operation"""
        async def task():
            # Your async code here
            pass

        results = await asyncio.gather(task(), task(), task())
        assert len(results) == 3
```

## Test Output

### Console Output
Tests print detailed information including:
- Test name and status (PASS/FAIL/SKIP/ERROR)
- Duration in milliseconds
- Detailed error messages
- Summary statistics

### JSON Reports
Live test runner saves results to:
```
test_results_YYYYMMDD_HHMMSS.json
```

Format:
```json
[
  {
    "suite_name": "ConceptAnalyzer",
    "start_time": "2025-10-04T10:30:00",
    "results": [
      {
        "test_name": "test_analyze_physics",
        "status": "PASS",
        "duration_ms": 1234.5,
        "message": "Test passed",
        "details": {...}
      }
    ]
  }
]
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run unit tests (mocked)
      run: pytest tests/ -v -m "not live"

    - name: Run live tests (on main branch only)
      if: github.ref == 'refs/heads/main'
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: pytest tests/ -v -m live
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Create `.env` file with your API key
- Or export: `export ANTHROPIC_API_KEY=your_key`

### Tests timing out
- Increase timeout: `pytest --timeout=60`
- Check your internet connection
- Verify API key is valid

### Import errors
- Run from project root: `pytest tests/`
- Check Python path: `echo $PYTHONPATH`

### Async tests failing
- Install pytest-asyncio: `pip install pytest-asyncio`
- Use `@pytest.mark.asyncio` decorator

## Best Practices

1. **Mock by default** - Use live API sparingly
2. **Test edge cases** - Empty input, malformed data, API errors
3. **Measure performance** - Track API calls, cache hits, duration
4. **Clean up** - Reset state between tests
5. **Document** - Explain what each test validates

## Coverage

Generate coverage report:
```bash
pytest tests/ --cov=prerequisite_explorer_claude --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

Target coverage: >80% for core modules

## Next Steps

1. Add more edge case tests
2. Implement performance benchmarks
3. Add visual regression tests for Manim output
4. Create load tests for concurrent users
5. Add security tests (API key handling, input sanitization)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Last Updated**: 2025-10-04
**Maintainer**: @HarleyCoops
