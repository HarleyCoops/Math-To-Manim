# Testing Architecture for Math-To-Manim

**Powered by**: Claude Sonnet 4.5 + Claude Agent SDK
**Testing Framework**: pytest + custom validators

---

## Testing Philosophy

### What We're Testing
1. **Agent Reasoning Quality**: Does Claude correctly identify prerequisites?
2. **Knowledge Tree Structure**: Are trees logically sound foundation -> target?
3. **Prompt Quality**: Do generated prompts produce working Manim code?
4. **Code Generation**: Does the final Manim code compile and render?
5. **Mathematical Accuracy**: Are formulas and concepts correct?

### What We're NOT Testing
- Claude's internal reasoning (black box)
- Exact output matching (non-deterministic)
- Perfect LaTeX formatting (flexible)

### Key Principle
**Test outcomes, not implementations**. We care about working animations, not specific intermediate representations.

---

## Testing Pyramid

```
                    /\
                   /  \
                  / E2E \          Manual/Visual (5%)
                 /______\
                /        \
               /Integration\       API Integration (15%)
              /____________\
             /              \
            /   Unit Tests   \    Logic/Validation (80%)
           /__________________\
```

---

## Test Levels

### Level 1: Unit Tests (Fast, Many)

**Purpose**: Test individual components in isolation

**Test Files**:
- `tests/unit/test_concept_analyzer.py`
- `tests/unit/test_prerequisite_explorer.py`
- `tests/unit/test_validators.py`
- `tests/unit/test_knowledge_node.py`

**Example Tests**:

```python
# tests/unit/test_concept_analyzer.py
import pytest
from prerequisite_explorer_claude import ConceptAnalyzer

def test_concept_analyzer_identifies_core_concept():
    """Test that analyzer extracts the main concept"""
    analyzer = ConceptAnalyzer()

    result = analyzer.analyze("Explain quantum mechanics to me")

    assert "quantum" in result["core_concept"].lower()
    assert result["domain"] in ["physics", "physics/quantum mechanics"]
    assert result["level"] in ["beginner", "intermediate", "advanced"]

def test_concept_analyzer_handles_casual_language():
    """Test with casual user input"""
    analyzer = ConceptAnalyzer()

    result = analyzer.analyze("i want to learn about calculus")

    assert "calculus" in result["core_concept"].lower()
    assert result["level"] == "beginner"  # Casual language suggests beginner

def test_concept_analyzer_detects_advanced_topics():
    """Test recognition of advanced concepts"""
    analyzer = ConceptAnalyzer()

    result = analyzer.analyze("Explain differential geometry and gauge theory")

    assert result["level"] == "advanced"
```

```python
# tests/unit/test_prerequisite_explorer.py
import pytest
from prerequisite_explorer_claude import PrerequisiteExplorer, KnowledgeNode

def test_foundation_detection_basic_concepts():
    """Test that basic concepts are marked as foundation"""
    explorer = PrerequisiteExplorer()

    # These should all be foundation
    assert explorer.is_foundation("velocity") == True
    assert explorer.is_foundation("distance") == True
    assert explorer.is_foundation("addition") == True
    assert explorer.is_foundation("triangle") == True

def test_foundation_detection_advanced_concepts():
    """Test that advanced concepts are NOT foundation"""
    explorer = PrerequisiteExplorer()

    # These should NOT be foundation
    assert explorer.is_foundation("Lorentz transformation") == False
    assert explorer.is_foundation("gauge theory") == False
    assert explorer.is_foundation("tensor calculus") == False

def test_prerequisite_discovery_returns_list():
    """Test that prerequisite discovery returns valid list"""
    explorer = PrerequisiteExplorer()

    prereqs = explorer.discover_prerequisites("quantum mechanics")

    assert isinstance(prereqs, list)
    assert len(prereqs) >= 3  # Should get 3-5 prerequisites
    assert len(prereqs) <= 5
    assert all(isinstance(p, str) for p in prereqs)

def test_knowledge_tree_has_correct_depth():
    """Test that tree respects max_depth"""
    explorer = PrerequisiteExplorer(max_depth=2)

    tree = explorer.explore("calculus")

    # Check no node exceeds max depth
    def check_depth(node, max_allowed):
        assert node.depth <= max_allowed
        for child in node.prerequisites:
            check_depth(child, max_allowed)

    check_depth(tree, 2)

def test_knowledge_node_serialization():
    """Test that KnowledgeNode can be serialized to JSON"""
    import json

    node = KnowledgeNode(
        concept="test",
        depth=0,
        is_foundation=False,
        prerequisites=[]
    )

    serialized = node.to_dict()

    assert serialized["concept"] == "test"
    assert serialized["depth"] == 0
    # Should be valid JSON
    json_str = json.dumps(serialized)
    assert json.loads(json_str) == serialized
```

---

### Level 2: Integration Tests (Medium Speed, Fewer)

**Purpose**: Test agent interactions and API calls

**Test Files**:
- `tests/integration/test_knowledge_tree_building.py`
- `tests/integration/test_claude_api.py`
- `tests/integration/test_prompt_expansion.py`

**Example Tests**:

```python
# tests/integration/test_knowledge_tree_building.py
import pytest
from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer

@pytest.mark.integration
@pytest.mark.slow
def test_build_complete_tree_cosmology():
    """Integration test: Build full knowledge tree for cosmology"""
    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=3)

    # Analyze
    analysis = analyzer.analyze("Explain cosmology")

    # Build tree
    tree = explorer.explore(analysis["core_concept"])

    # Assertions
    assert tree.concept.lower() in ["cosmology", "cosmic evolution"]
    assert tree.depth == 0  # Root node
    assert not tree.is_foundation  # Cosmology is not foundational
    assert len(tree.prerequisites) >= 2  # Should have multiple prerequisites

    # Check that we eventually hit foundation concepts
    def has_foundation(node):
        if node.is_foundation:
            return True
        return any(has_foundation(child) for child in node.prerequisites)

    assert has_foundation(tree), "Tree should contain at least one foundation concept"

@pytest.mark.integration
def test_tree_building_caching():
    """Test that prerequisite caching works"""
    explorer = PrerequisiteExplorer(max_depth=2)

    # Build tree twice
    tree1 = explorer.explore("special relativity")
    tree2 = explorer.explore("special relativity")

    # Cache should be populated after first run
    assert len(explorer.cache) > 0
    assert "special relativity" in explorer.cache

@pytest.mark.integration
def test_tree_logical_progression():
    """Test that prerequisites are logically ordered"""
    explorer = PrerequisiteExplorer(max_depth=3)

    tree = explorer.explore("quantum field theory")

    # QFT should require quantum mechanics
    prereq_concepts = [p.concept.lower() for p in tree.prerequisites]

    # Should have physics-related prerequisites
    has_quantum = any("quantum" in c for c in prereq_concepts)
    has_relativity = any("relativity" in c for c in prereq_concepts)

    assert has_quantum or has_relativity, "QFT should require quantum or relativity"
```

---

### Level 3: End-to-End Tests (Slow, Critical)

**Purpose**: Test entire pipeline from user input to rendered animation

**Test Files**:
- `tests/e2e/test_full_pipeline.py`
- `tests/e2e/test_manim_generation.py`

**Example Tests**:

```python
# tests/e2e/test_full_pipeline.py
import pytest
import os
import subprocess
from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer
from anthropic import Anthropic

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_pipeline_pythagorean():
    """E2E: Simple prompt -> working Manim code"""

    # Step 1: Analyze concept
    analyzer = ConceptAnalyzer()
    analysis = analyzer.analyze("Show the Pythagorean theorem")

    assert "pythagorean" in analysis["core_concept"].lower()

    # Step 2: Build knowledge tree (shallow for speed)
    explorer = PrerequisiteExplorer(max_depth=2)
    tree = explorer.explore(analysis["core_concept"])

    assert tree is not None

    # Step 3: Generate verbose prompt (simplified for test)
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Create a detailed Manim animation prompt for the Pythagorean theorem.

The prompt should:
1. Specify visual elements (colors, positions)
2. Include LaTeX equations
3. Provide step-by-step instructions
4. Be 500+ words

Format for Manim Community Edition."""

    response = client.messages.create(
        model="claude-sonnet-4.5-20251022",
        max_tokens=2000,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )

    verbose_prompt = response.content[0].text

    assert len(verbose_prompt) > 500
    assert "manim" in verbose_prompt.lower() or "scene" in verbose_prompt.lower()

    # Step 4: Generate Manim code
    code_prompt = f"""Generate Python code using Manim Community Edition for this animation:

{verbose_prompt}

Requirements:
- Use: from manim import *
- Create a Scene class with construct() method
- Use proper LaTeX escaping (raw strings)
- Include comments

Return ONLY the Python code, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4.5-20251022",
        max_tokens=2000,
        temperature=0.3,
        messages=[{"role": "user", "content": code_prompt}]
    )

    manim_code = response.content[0].text

    # Clean code (remove markdown if present)
    if "```python" in manim_code:
        manim_code = manim_code.split("```python")[1].split("```")[0]
    elif "```" in manim_code:
        manim_code = manim_code.split("```")[1].split("```")[0]

    # Validate code
    assert "from manim import" in manim_code
    assert "class" in manim_code
    assert "Scene" in manim_code
    assert "def construct(self)" in manim_code

    # Step 5: Try to compile the code (syntax check only)
    import ast
    try:
        ast.parse(manim_code)
        code_compiles = True
    except SyntaxError:
        code_compiles = False

    assert code_compiles, "Generated Manim code should be valid Python"

@pytest.mark.e2e
@pytest.mark.manual
def test_render_simple_animation():
    """E2E: Actually render a Manim animation (manual verification)"""

    # Generate simple test code
    test_code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Testing Math-To-Manim")
        equation = MathTex(r"a^2 + b^2 = c^2")

        self.play(Write(text))
        self.wait(1)
        self.play(Transform(text, equation))
        self.wait(2)
'''

    # Write to temp file
    with open("test_scene_temp.py", "w") as f:
        f.write(test_code)

    # Try to render
    result = subprocess.run(
        ["python", "-m", "manim", "-ql", "test_scene_temp.py", "TestScene"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Cleanup
    os.remove("test_scene_temp.py")

    # Check if rendering succeeded
    assert result.returncode == 0, f"Manim rendering failed: {result.stderr}"
```

---

### Level 4: Quality Tests (Validation)

**Purpose**: Validate mathematical and pedagogical correctness

**Test Files**:
- `tests/quality/test_math_accuracy.py`
- `tests/quality/test_prerequisite_logic.py`
- `tests/quality/test_latex_validity.py`

```python
# tests/quality/test_math_accuracy.py
import pytest
from prerequisite_explorer_claude import PrerequisiteExplorer

@pytest.mark.quality
def test_calculus_prerequisites_correct():
    """Validate that calculus prerequisites are mathematically sound"""
    explorer = PrerequisiteExplorer(max_depth=2)

    prereqs = explorer.discover_prerequisites("calculus")
    prereqs_lower = [p.lower() for p in prereqs]

    # Calculus MUST require functions and algebra
    has_functions = any("function" in p for p in prereqs_lower)
    has_algebra = any("algebra" in p for p in prereqs_lower)

    assert has_functions or has_algebra, "Calculus must require functions or algebra"

@pytest.mark.quality
def test_quantum_mechanics_prerequisites():
    """Validate QM prerequisites include necessary physics"""
    explorer = PrerequisiteExplorer(max_depth=2)

    prereqs = explorer.discover_prerequisites("quantum mechanics")
    prereqs_lower = [p.lower() for p in prereqs]

    # QM should mention waves or classical mechanics
    has_waves = any("wave" in p for p in prereqs_lower)
    has_classical = any("classical" in p or "mechanics" in p for p in prereqs_lower)

    assert has_waves or has_classical, "QM should require waves or classical mechanics"

# tests/quality/test_latex_validity.py
import pytest
import re

def validate_latex(latex_string):
    """Check for common LaTeX errors"""
    errors = []

    # Check balanced braces
    if latex_string.count('{') != latex_string.count('}'):
        errors.append("Unbalanced braces")

    # Check balanced dollars
    if latex_string.count('$') % 2 != 0:
        errors.append("Unbalanced dollar signs")

    # Check for begin/end pairs
    begins = re.findall(r'\\begin\{(\w+)\}', latex_string)
    ends = re.findall(r'\\end\{(\w+)\}', latex_string)

    if sorted(begins) != sorted(ends):
        errors.append("Mismatched begin/end environments")

    return errors

@pytest.mark.quality
def test_generated_prompt_latex_validity():
    """Test that generated prompts have valid LaTeX"""
    from anthropic import Anthropic
    import os

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4.5-20251022",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": "Write a short Manim prompt showing Einstein's mass-energy equation. Include LaTeX."
        }]
    )

    prompt = response.content[0].text

    # Extract LaTeX (look for $ or \begin{})
    latex_matches = re.findall(r'\$.*?\$|\$\$.*?\$\$|\\begin\{.*?\}.*?\\end\{.*?\}',
                                prompt, re.DOTALL)

    for latex in latex_matches:
        errors = validate_latex(latex)
        assert len(errors) == 0, f"LaTeX validation failed: {errors}"
```

---

## Test Fixtures and Data

### Fixture: Standard Test Topics

```python
# tests/fixtures/test_topics.py
import pytest

@pytest.fixture
def simple_topics():
    """Topics that should work well (foundation level)"""
    return [
        "addition",
        "multiplication",
        "triangle",
        "circle",
        "velocity"
    ]

@pytest.fixture
def intermediate_topics():
    """Medium complexity topics"""
    return [
        "Pythagorean theorem",
        "quadratic equations",
        "trigonometry",
        "derivatives",
        "basic probability"
    ]

@pytest.fixture
def advanced_topics():
    """Complex topics requiring multiple prerequisites"""
    return [
        "quantum mechanics",
        "general relativity",
        "differential geometry",
        "Fourier analysis",
        "quantum field theory"
    ]

@pytest.fixture
def cross_domain_topics():
    """Topics spanning multiple domains"""
    return [
        "machine learning",
        "cryptography",
        "game theory",
        "information theory",
        "chaos theory"
    ]
```

### Fixture: Expected Prerequisites

```python
# tests/fixtures/expected_prerequisites.py
import pytest

@pytest.fixture
def known_prerequisite_chains():
    """Known correct prerequisite relationships"""
    return {
        "calculus": {
            "must_include": ["functions", "algebra", "limits"],
            "should_not_include": ["quantum mechanics", "relativity"]
        },
        "quantum mechanics": {
            "must_include": ["waves", "classical mechanics"],
            "should_not_include": ["cooking", "history"]
        },
        "linear algebra": {
            "must_include": ["matrices", "vectors"],
            "should_not_include": ["calculus"]  # Not strictly required
        }
    }
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, no API calls)
    integration: Integration tests (API calls, slower)
    e2e: End-to-end tests (full pipeline)
    quality: Quality validation tests
    slow: Tests that take >5 seconds
    manual: Tests requiring manual verification

addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Timeout for tests (prevent hanging)
timeout = 300

# Coverage
[coverage:run]
source = .
omit =
    tests/*
    venv/*
    */site-packages/*
```

### conftest.py

```python
# tests/conftest.py
import pytest
import os

def pytest_configure(config):
    """Validate environment before running tests"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.exit("ANTHROPIC_API_KEY not set. Cannot run tests.")

@pytest.fixture(scope="session")
def anthropic_client():
    """Shared Anthropic client for tests"""
    from anthropic import Anthropic
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir

# Slow test handling
def pytest_collection_modifyitems(config, items):
    """Mark slow tests automatically"""
    for item in items:
        if "integration" in item.keywords or "e2e" in item.keywords:
            item.add_marker(pytest.mark.slow)
```

---

## Running Tests

### Quick Tests (Development)
```bash
# Unit tests only (fast)
pytest tests/unit -v

# Specific test file
pytest tests/unit/test_prerequisite_explorer.py -v

# Specific test function
pytest tests/unit/test_prerequisite_explorer.py::test_foundation_detection_basic_concepts -v
```

### Full Test Suite
```bash
# All tests except manual
pytest -m "not manual"

# Integration tests
pytest tests/integration -v

# E2E tests (slow)
pytest tests/e2e -v
```

### Coverage Report
```bash
pytest --cov=. --cov-report=html tests/
```

### CI/CD (Fast Subset)
```bash
# Run only fast tests in CI
pytest -m "unit and not slow" --maxfail=3
```

---

## Success Metrics

### Unit Test Goals
- **Coverage**: 80%+ of core logic
- **Speed**: All unit tests complete in <10 seconds
- **Reliability**: 100% pass rate (deterministic)

### Integration Test Goals
- **API Success Rate**: 95%+ successful Claude API calls
- **Tree Building**: 90%+ of topics produce valid trees
- **Caching**: Verify all repeated queries use cache

### E2E Test Goals
- **Code Generation**: 80%+ generate syntactically valid Python
- **Manim Compatibility**: 70%+ render without errors
- **Mathematical Correctness**: Human review of 10 examples

---

## Test Data Management

### Input: Test Topics (tests/fixtures/topics.json)
```json
{
  "basic": ["addition", "triangle", "velocity"],
  "intermediate": ["calculus", "trigonometry"],
  "advanced": ["quantum mechanics", "topology"]
}
```

### Output: Test Results (tests/results/)
```
tests/results/
├── knowledge_trees/          # Saved trees for verification
│   ├── calculus.json
│   ├── quantum_mechanics.json
│   └── ...
├── generated_prompts/        # Sample prompts
│   ├── calculus_prompt.txt
│   └── ...
└── manim_code/              # Generated code samples
    ├── calculus_scene.py
    └── ...
```

---

## Continuous Testing Strategy

### Pre-Commit
```bash
# Fast smoke tests
pytest tests/unit -m "not slow" --maxfail=1
```

### On Pull Request
```bash
# Full unit + integration
pytest tests/unit tests/integration -v
```

### Nightly Build
```bash
# Everything including E2E
pytest tests/ -v
# Generate quality report
```

### Weekly Audit
```bash
# Manual review of 10 random generated animations
# Validate mathematical accuracy
# Check pedagogical quality
```

---

## Next Steps

1. Create basic test structure
2. Implement unit tests for PrerequisiteExplorer
3. Add integration tests for tree building
4. Set up pytest configuration
5. Create CI/CD workflow
6. Document test failure triage process

Want me to start implementing these tests?
