---
applies_to:
  - "tests/**/*.py"
description: Guidelines for writing and maintaining tests in Math-To-Manim
---

# Testing Guidelines

## Overview

The testing infrastructure ensures the reliability of the Math-To-Manim agent pipeline. Tests are organized into unit, integration, and end-to-end (e2e) categories.

## Test Organization

```
tests/
├── unit/           # Test individual functions/methods in isolation
├── integration/    # Test agent interactions and pipeline segments
├── e2e/           # Test complete workflows from input to output
├── conftest.py    # Shared fixtures and configuration
└── *.py           # Top-level test files for main components
```

## Testing Framework

### Core Tools
- **pytest**: Primary testing framework
- **pytest-asyncio**: For testing async code
- **pytest-cov**: Code coverage reporting
- **unittest.mock**: Mocking API calls and external dependencies

### Test Markers

Use pytest markers to categorize tests:
```python
import pytest

@pytest.mark.unit
def test_foundation_detection():
    """Unit test - no external dependencies."""
    pass

@pytest.mark.integration
def test_agent_pipeline():
    """Integration test - tests agent interactions."""
    pass

@pytest.mark.live
def test_with_real_api():
    """Live test - requires API key and makes real API calls."""
    pass

@pytest.mark.slow
def test_full_pipeline():
    """Slow test - takes > 10 seconds to run."""
    pass

@pytest.mark.parametrize("concept,expected", [
    ("addition", True),
    ("quantum mechanics", False),
])
def test_multiple_cases(concept, expected):
    """Parameterized test - runs with multiple inputs."""
    pass
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Skip expensive live tests
pytest tests/ -v -m "not live"

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_prerequisite_explorer.py -v

# Run specific test function
pytest tests/test_prerequisite_explorer.py::test_foundation_detection -v

# Run interactive test runner
python tests/live_test_runner.py
```

## Writing Unit Tests

### Structure
```python
# tests/unit/test_component.py

import pytest
from src.agents.prerequisite_explorer_claude import PrerequisiteExplorer

class TestPrerequisiteExplorer:
    """Test suite for PrerequisiteExplorer."""
    
    @pytest.fixture
    def explorer(self):
        """Create explorer instance for tests."""
        return PrerequisiteExplorer(max_depth=2)
    
    def test_initialization(self, explorer):
        """Test explorer initializes correctly."""
        assert explorer.max_depth == 2
        assert explorer.client is not None
    
    def test_foundation_detection_basic(self, explorer):
        """Test detection of basic foundation concepts."""
        # Test known foundations
        assert explorer.is_foundation("addition")
        assert explorer.is_foundation("multiplication")
        
        # Test non-foundations
        assert not explorer.is_foundation("quantum field theory")
        assert not explorer.is_foundation("differential geometry")
    
    def test_invalid_input_handling(self, explorer):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError, match="empty"):
            explorer.explore("")
        
        with pytest.raises(ValueError, match="empty"):
            explorer.explore("   ")
```

### Mocking API Calls

Always mock external API calls in unit tests:
```python
from unittest.mock import Mock, patch, MagicMock

def test_explore_with_mocked_api(explorer):
    """Test exploration logic without real API calls."""
    # Mock the API client
    mock_response = Mock()
    mock_response.content = [Mock(text='["algebra", "arithmetic"]')]
    
    with patch.object(explorer.client.messages, 'create', return_value=mock_response):
        tree = explorer.explore("calculus")
        
        # Verify behavior
        assert tree.concept == "calculus"
        assert len(tree.prerequisites) == 2
        
        # Verify API was called correctly
        explorer.client.messages.create.assert_called_once()
```

### Fixtures

Use fixtures for reusable test data:
```python
# tests/conftest.py

import pytest
from src.agents.prerequisite_explorer_claude import TreeNode

@pytest.fixture
def sample_tree():
    """Create a sample knowledge tree for testing."""
    return TreeNode(
        concept="calculus",
        depth=0,
        prerequisites=[
            TreeNode(concept="algebra", depth=1, prerequisites=[]),
            TreeNode(concept="trigonometry", depth=1, prerequisites=[])
        ]
    )

@pytest.fixture
def mock_api_key(monkeypatch):
    """Provide mock API key for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")
```

## Writing Integration Tests

### Testing Agent Interactions
```python
# tests/integration/test_enrichment_pipeline.py

import pytest
from src.agents.prerequisite_explorer_claude import PrerequisiteExplorer
from src.agents.mathematical_enricher import MathematicalEnricher

@pytest.mark.integration
@pytest.mark.slow
def test_explorer_to_enricher_pipeline():
    """Test passing tree from explorer to enricher."""
    # Build tree
    explorer = PrerequisiteExplorer(max_depth=2)
    tree = explorer.explore("linear algebra")
    
    # Enrich tree
    enricher = MathematicalEnricher()
    enriched_tree = enricher.enrich(tree)
    
    # Verify enrichment
    assert enriched_tree.latex_content is not None
    assert "$$" in enriched_tree.latex_content  # Has equations
    
    # Verify structure preserved
    assert enriched_tree.concept == tree.concept
    assert len(enriched_tree.prerequisites) == len(tree.prerequisites)
```

### Testing Data Flow
```python
@pytest.mark.integration
def test_tree_serialization_roundtrip():
    """Test tree can be serialized and deserialized."""
    import json
    
    # Create tree
    explorer = PrerequisiteExplorer()
    original_tree = explorer.explore("geometry", max_depth=1)
    
    # Serialize
    tree_json = json.dumps(original_tree.to_dict())
    
    # Deserialize
    restored_dict = json.loads(tree_json)
    restored_tree = TreeNode.from_dict(restored_dict)
    
    # Verify equivalence
    assert restored_tree.concept == original_tree.concept
    assert restored_tree.depth == original_tree.depth
```

## Writing E2E Tests

### Full Pipeline Tests
```python
# tests/e2e/test_full_workflow.py

import pytest
from pathlib import Path

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.live
def test_complete_workflow_simple_concept(tmp_path):
    """Test complete workflow from prompt to animation code."""
    # User input
    user_prompt = "explain the Pythagorean theorem"
    
    # Run full pipeline
    from src.app_claude import run_pipeline
    result = run_pipeline(user_prompt)
    
    # Verify outputs
    assert result.knowledge_tree is not None
    assert result.verbose_prompt is not None
    assert len(result.verbose_prompt) > 500  # Verbose
    assert result.manim_code is not None
    assert "class" in result.manim_code  # Has Python class
    assert "Scene" in result.manim_code  # Inherits from Scene
    
    # Verify animation renders
    output_file = tmp_path / "test_animation.py"
    output_file.write_text(result.manim_code)
    
    import subprocess
    render_result = subprocess.run(
        ["manim", "-ql", "--dry_run", str(output_file)],
        capture_output=True
    )
    assert render_result.returncode == 0
```

## Live Tests (API Tests)

### Marking Live Tests
```python
@pytest.mark.live
def test_real_claude_api():
    """Test with real Claude API - costs money, use sparingly."""
    # Check for API key
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
    
    # Run real API test
    explorer = PrerequisiteExplorer()
    tree = explorer.explore("physics")
    
    # Basic validation
    assert tree is not None
    assert tree.concept == "physics"
```

### Caching Live Test Results
```python
import json
from pathlib import Path

@pytest.mark.live
def test_with_caching():
    """Live test that caches results to avoid repeated API calls."""
    cache_file = Path(".test_cache/physics_tree.json")
    
    if cache_file.exists():
        # Use cached result
        tree_dict = json.loads(cache_file.read_text())
        tree = TreeNode.from_dict(tree_dict)
    else:
        # Make live API call
        explorer = PrerequisiteExplorer()
        tree = explorer.explore("physics", max_depth=2)
        
        # Cache for next time
        cache_file.parent.mkdir(exist_ok=True)
        cache_file.write_text(json.dumps(tree.to_dict()))
    
    # Run assertions
    assert tree.concept == "physics"
```

## Testing Best Practices

### Test Naming
```python
# Good - descriptive names
def test_foundation_detection_identifies_arithmetic():
    """Test that arithmetic is recognized as foundation."""
    pass

def test_explore_raises_error_on_empty_concept():
    """Test that empty concept raises ValueError."""
    pass

# Bad - unclear names
def test_1():
    pass

def test_stuff():
    pass
```

### Assertions
```python
# Good - specific assertions with messages
assert len(tree.prerequisites) > 0, "Tree should have prerequisites"
assert tree.depth == 0, f"Root depth should be 0, got {tree.depth}"

# Use pytest assertions
assert "algebra" in prereq_concepts
assert explorer.is_foundation("addition")

# Bad - vague assertions
assert tree
assert prereq_list
```

### Test Independence
```python
# Good - each test is independent
def test_feature_a():
    explorer = PrerequisiteExplorer()
    # Test feature A
    
def test_feature_b():
    explorer = PrerequisiteExplorer()  # Fresh instance
    # Test feature B

# Bad - tests depend on each other
def test_step_1():
    global explorer
    explorer = PrerequisiteExplorer()
    
def test_step_2():
    # Depends on test_step_1 running first
    explorer.explore("math")
```

### Error Testing
```python
# Test expected errors
def test_invalid_api_key():
    """Test handling of invalid API key."""
    with pytest.raises(ValueError, match="API key"):
        PrerequisiteExplorer(api_key="invalid")

def test_network_error_retry():
    """Test retry logic on network errors."""
    # Mock network failure
    with patch.object(client, 'call', side_effect=NetworkError):
        with pytest.raises(NetworkError):
            agent.call_api()
```

## Performance Testing

### Timing Tests
```python
import time

@pytest.mark.performance
def test_foundation_detection_performance():
    """Test foundation detection is fast."""
    explorer = PrerequisiteExplorer()
    
    start = time.time()
    for _ in range(100):
        explorer.is_foundation("algebra")
    duration = time.time() - start
    
    # Should be very fast (< 1ms per call)
    assert duration < 0.1, f"Too slow: {duration:.3f}s for 100 calls"
```

### Memory Tests
```python
import tracemalloc

@pytest.mark.performance
def test_tree_memory_usage():
    """Test tree doesn't use excessive memory."""
    tracemalloc.start()
    
    explorer = PrerequisiteExplorer()
    tree = explorer.explore("mathematics", max_depth=3)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Should use less than 10MB
    assert peak < 10 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.1f}MB"
```

## Coverage Requirements

### Minimum Coverage
- Overall: 80%
- Core agents: 90%
- Utilities: 70%

### Checking Coverage
```bash
# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html

# Check specific module
pytest tests/ --cov=src.agents.prerequisite_explorer_claude --cov-report=term-missing
```

## Test Data Management

### Using Test Fixtures
```python
# tests/fixtures/sample_trees.json
{
  "simple_tree": {
    "concept": "algebra",
    "depth": 0,
    "prerequisites": []
  }
}

# tests/conftest.py
import json
from pathlib import Path

@pytest.fixture
def test_data():
    """Load test data from fixtures."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_trees.json"
    return json.loads(fixtures_path.read_text())
```

### Temporary Files
```python
def test_with_temporary_files(tmp_path):
    """Test using pytest's tmp_path fixture."""
    # tmp_path is automatically cleaned up
    test_file = tmp_path / "test_tree.json"
    test_file.write_text('{"concept": "math"}')
    
    # Run test
    result = load_tree(test_file)
    assert result.concept == "math"
```

## Debugging Tests

### Verbose Output
```bash
# Show print statements
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -v -l

# Drop into debugger on failure
pytest tests/ --pdb

# Show slowest tests
pytest tests/ --durations=10
```

### Logging in Tests
```python
import logging

def test_with_logging(caplog):
    """Test with captured log output."""
    caplog.set_level(logging.DEBUG)
    
    explorer = PrerequisiteExplorer()
    explorer.explore("math")
    
    # Check log messages
    assert "Exploring concept" in caplog.text
```

## Continuous Integration

### GitHub Actions
Tests should pass in CI:
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests (excluding live)
        run: pytest tests/ -v -m "not live" --cov=src
```

## Common Issues

### Flaky Tests
```python
# Mark flaky tests
@pytest.mark.flaky(reruns=3)
def test_sometimes_fails():
    """Test that occasionally fails due to timing."""
    pass
```

### Slow Tests
```python
# Mark and skip in CI
@pytest.mark.slow
def test_takes_long_time():
    """Test that takes minutes to run."""
    pass

# In CI: pytest -m "not slow"
```

## Documentation

Document test intent:
```python
def test_prerequisite_ordering():
    """
    Test that prerequisites are explored in breadth-first order.
    
    This ensures that concepts at the same depth are processed before
    going deeper, which is important for the narrative composer.
    
    Given: A concept with multiple prerequisites at different depths
    When: The explorer builds the tree
    Then: Nodes at depth N are all processed before depth N+1
    """
    # Test implementation
```

## Getting Help

- **pytest docs**: https://docs.pytest.org/
- **Testing guide**: `TESTING_QUICKSTART.md`
- **Architecture**: `docs/TESTING_ARCHITECTURE.md`

## Remember

Good tests:
- **Are fast**: Run quickly so developers run them often
- **Are focused**: Test one thing clearly
- **Are independent**: Don't depend on other tests
- **Are readable**: Clear what is being tested and why
- **Are maintainable**: Easy to update when code changes
