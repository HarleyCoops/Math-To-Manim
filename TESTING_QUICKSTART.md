# Testing Quick Start Guide

**Created**: 2025-10-04
**Goal**: Get you testing your agents in under 5 minutes

---

## Step 1: Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

---

## Step 2: Run Your First Test

### Option A: Live Test Runner (Easiest, Shows Everything)

```bash
python tests/live_test_runner.py
```

**What you'll see**:
- Real-time test execution with colored output
- Each agent method being called
- API calls and responses
- Performance metrics
- Pass/fail status with details
- Final summary with statistics

**Output saved to**: `test_results_YYYYMMDD_HHMMSS.json`

### Option B: Pytest (Industry Standard)

```bash
# Run all tests
pytest tests/test_prerequisite_explorer.py -v

# Skip tests that require API calls (fast, no cost)
pytest tests/test_prerequisite_explorer.py -v -m "not live"
```

---

## Step 3: Test a Specific Concept

```bash
# Test how the system handles "cosmology"
python tests/live_test_runner.py --concept "cosmology"

# Test with "quantum mechanics"
python tests/live_test_runner.py --concept "quantum mechanics"
```

**This will**:
1. Analyze the concept with ConceptAnalyzer
2. Build prerequisite tree with PrerequisiteExplorer
3. Show all API calls made
4. Display the resulting knowledge tree
5. Report performance metrics

---

## Step 4: Run Specific Test Suites

```bash
# Test only the ConceptAnalyzer
python tests/live_test_runner.py --suite analyzer

# Test only the PrerequisiteExplorer
python tests/live_test_runner.py --suite explorer

# Test performance/scaling
python tests/live_test_runner.py --suite performance

# Run everything
python tests/live_test_runner.py --suite all
```

---

## Understanding Test Output

### Console Output Example

```
================================================================================
Running: ConceptAnalyzer.test_analyze_physics_concept
================================================================================

[DONE] PASS: ConceptAnalyzer.test_analyze_physics_concept
   Duration: 1234.56ms
   Message: Successfully analyzed physics concept
   Details: {
      "core_concept": "special relativity",
      "domain": "physics",
      "level": "intermediate",
      "goal": "Understand relativistic effects"
   }
```

**Status Indicators**:
- [DONE] PASS - Test succeeded
- [FAIL] FAIL - Test failed (logic error)
- [ERROR] ERROR - Exception thrown
- [SKIP] SKIP - Test skipped (e.g., no API key)

### JSON Output Example

After running tests, check the JSON file:

```json
{
  "suite_name": "ConceptAnalyzer",
  "start_time": "2025-10-04T10:30:00",
  "end_time": "2025-10-04T10:32:15",
  "total_duration_ms": 135000,
  "results": [
    {
      "test_name": "test_analyze_physics_concept",
      "status": "PASS",
      "duration_ms": 1234.56,
      "message": "Successfully analyzed physics concept",
      "details": {...}
    }
  ]
}
```

---

## Common Test Scenarios

### 1. Verify Foundation Detection Works

```python
# In Python shell
from prerequisite_explorer_claude import PrerequisiteExplorer

explorer = PrerequisiteExplorer()

# Should be True
print(explorer.is_foundation("addition"))
print(explorer.is_foundation("velocity"))

# Should be False
print(explorer.is_foundation("quantum field theory"))
```

### 2. Check Caching Performance

```bash
# Run this twice - second time should be much faster
python tests/live_test_runner.py --concept "algebra"
```

Look for the "Caching working (speedup: X.Xx)" message.

### 3. Test Depth Limits

```python
from prerequisite_explorer_claude import PrerequisiteExplorer

# Limit to depth 2
explorer = PrerequisiteExplorer(max_depth=2)
tree = explorer.explore("cosmology")

# Verify no node exceeds depth 2
def check_depth(node):
    assert node.depth <= 2
    for p in node.prerequisites:
        check_depth(p)

check_depth(tree)
print("[OK] Depth limit respected!")
```

---

## Debugging Failed Tests

### Test Failed: "Foundation detection has errors"

**Cause**: Claude classified a concept incorrectly

**Fix**:
1. Check the test output for which concepts failed
2. Review the prompts in `prerequisite_explorer_claude.py`
3. Adjust the system prompt for `is_foundation()`

### Test Failed: "Tree built with 0 nodes"

**Cause**: Concept was immediately classified as foundation

**Fix**:
1. Check if the concept is actually basic
2. Lower `max_depth` in the test
3. Verify API key is working

### Test Error: "API timeout"

**Cause**: Network issues or API overload

**Fix**:
1. Check internet connection
2. Retry the test
3. Increase timeout in pytest.ini

---

## Performance Benchmarks

After running tests, compare your results:

**Expected Performance** (on Claude Sonnet 4.5):
- ConceptAnalyzer: ~1-2 seconds per concept
- PrerequisiteExplorer (depth 2): ~5-10 seconds
- PrerequisiteExplorer (depth 3): ~15-30 seconds
- Cache hit speedup: 10-100x faster

**If slower**:
- Check internet speed
- Verify API region
- Consider caching more aggressively

---

## Writing Your Own Test

### Quick Template

```python
# tests/test_my_feature.py

import pytest
from prerequisite_explorer_claude import PrerequisiteExplorer

def test_my_feature():
    """Test my new feature"""
    explorer = PrerequisiteExplorer()

    # Your test logic
    result = explorer.explore("my concept")

    # Assertions
    assert result is not None
    assert result.concept == "my concept"

# Run it
# pytest tests/test_my_feature.py -v
```

---

## Next Steps

1. **Run the tests** - Start with `python tests/live_test_runner.py`
2. **Check the output** - Review `test_results_*.json`
3. **Experiment** - Test different concepts
4. **Read the logs** - Understand what agents are doing
5. **Write your own** - Add tests for new features

---

## Need Help?

- **Full testing guide**: [tests/README.md](tests/README.md)
- **Agent inspection**: [docs/AGENT_INSPECTION_GUIDE.md](docs/AGENT_INSPECTION_GUIDE.md)
- **FAQ**: [AGENT_FAQ.md](AGENT_FAQ.md)

---

**Happy Testing!** [TEST]

**Last Updated**: 2025-10-04
