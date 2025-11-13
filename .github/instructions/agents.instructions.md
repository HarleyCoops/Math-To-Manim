---
applies_to:
  - "src/agents/**/*.py"
description: Guidelines for working with AI agents in the Math-To-Manim pipeline
---

# Agent Development Guidelines

## Overview

The `src/agents/` directory contains the AI agent implementations that power the Math-To-Manim system. Each agent has a specific role in the pipeline from concept analysis to animation code generation.

## Agent Architecture

### Core Agents

1. **ConceptAnalyzer**: Parses user prompts and identifies core concepts, domain, and difficulty level
2. **PrerequisiteExplorer**: Builds reverse knowledge trees by recursively discovering prerequisites
3. **MathematicalEnricher**: Adds LaTeX equations and mathematical rigor to tree nodes
4. **VisualDesigner**: Specifies camera movements, colors, and visual metaphors
5. **NarrativeComposer**: Creates verbose, LaTeX-rich prompts from enriched trees
6. **CodeGenerator**: Translates prompts into working Manim Python code
7. **VideoReviewAgent**: (Planned) Automated post-render QA

### Agent Communication

Agents communicate through:
- **Knowledge Tree Nodes**: Structured data passed between agents
- **JSON Serialization**: Trees are cached and reused across runs
- **API Calls**: Claude SDK for Claude agents, OpenAI-compatible for Kimi K2

## Development Principles

### Single Responsibility
Each agent should have ONE clear purpose. Don't mix concerns:
```python
# Good - focused agent
class MathematicalEnricher:
    """Adds LaTeX equations to knowledge tree nodes."""
    def enrich_node(self, node: TreeNode) -> TreeNode:
        # Only adds mathematical content
        pass

# Bad - mixed responsibilities  
class MathAndVisualEnricher:
    """Adds both math and visual design."""
    # Violates single responsibility principle
```

### System Prompts

**Structure System Prompts Clearly**:
```python
SYSTEM_PROMPT = """
You are a {role} in the Math-To-Manim pipeline.

Your specific task:
- {task_1}
- {task_2}
- {task_3}

Input format:
{input_description}

Output format:
{output_description}

Constraints:
- {constraint_1}
- {constraint_2}

Remember: {key_principle}
"""
```

**Best Practices for Prompts**:
- Be explicit about input/output formats
- Specify constraints clearly
- Give examples when possible
- Keep prompts focused on the agent's role
- Use markdown formatting for readability
- Test prompts with various inputs

### Error Handling

Always handle API errors gracefully:
```python
from anthropic import Anthropic, APIError, RateLimitError
import time

def safe_api_call(self, prompt: str, max_retries: int = 3) -> str:
    """Make API call with retry logic."""
    for attempt in range(max_retries):
        try:
            response = self.client.messages.create(...)
            return response.content[0].text
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    raise RuntimeError("API call failed after retries")
```

### Caching Strategy

Implement caching to reduce API costs:
```python
import json
from pathlib import Path
from typing import Optional

class CachedAgent:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _cache_key(self, input_data: dict) -> str:
        """Generate cache key from input."""
        import hashlib
        content = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[dict]:
        """Retrieve from cache if exists."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        return None
    
    def _save_cache(self, key: str, data: dict) -> None:
        """Save to cache."""
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(data, indent=2))
```

## PrerequisiteExplorer Specifics

### Foundation Detection
The most critical logic - determines when to stop recursion:
```python
def is_foundation(self, concept: str) -> bool:
    """
    Determines if concept is foundational (high school level or below).
    
    Foundation concepts:
    - Basic arithmetic (addition, multiplication, fractions)
    - Elementary algebra (variables, linear equations)
    - Basic geometry (triangles, circles, angles)
    - Simple physics (velocity, force, energy)
    
    Not foundation:
    - College-level mathematics
    - Advanced physics (quantum, relativity)
    - Specialized concepts
    """
    # Implementation should be conservative - when in doubt, explore further
```

### Recursion Management
```python
def explore(self, concept: str, depth: int = 0, max_depth: int = 5) -> TreeNode:
    """
    Recursively explore prerequisites.
    
    Args:
        concept: The concept to explore
        depth: Current recursion depth (for limiting)
        max_depth: Maximum depth to explore
    
    Returns:
        TreeNode with prerequisites attached
    """
    # Always check depth limit
    if depth >= max_depth:
        return TreeNode(concept=concept, depth=depth, prerequisites=[])
    
    # Check foundation status
    if self.is_foundation(concept):
        return TreeNode(concept=concept, depth=depth, prerequisites=[])
    
    # Explore prerequisites
    prereqs = self._get_prerequisites(concept)
    prereq_nodes = [self.explore(p, depth + 1, max_depth) for p in prereqs]
    
    return TreeNode(concept=concept, depth=depth, prerequisites=prereq_nodes)
```

## Testing Requirements

### Unit Tests
Every agent method needs unit tests:
```python
# tests/unit/test_prerequisite_explorer.py

import pytest
from src.agents.prerequisite_explorer_claude import PrerequisiteExplorer

@pytest.fixture
def explorer():
    """Create explorer instance for tests."""
    return PrerequisiteExplorer()

def test_is_foundation_basic_concepts(explorer):
    """Test foundation detection for basic concepts."""
    assert explorer.is_foundation("addition")
    assert explorer.is_foundation("velocity")
    assert not explorer.is_foundation("quantum field theory")

@pytest.mark.live  # Mark tests requiring API calls
def test_explore_concept_live(explorer):
    """Test live API call for concept exploration."""
    tree = explorer.explore("algebra", max_depth=2)
    assert tree.concept == "algebra"
    assert len(tree.prerequisites) > 0
```

### Integration Tests
Test agent interactions:
```python
# tests/integration/test_pipeline.py

def test_full_enrichment_pipeline():
    """Test complete pipeline from concept to verbose prompt."""
    # 1. Analyze concept
    analyzer = ConceptAnalyzer()
    analysis = analyzer.analyze("special relativity")
    
    # 2. Build tree
    explorer = PrerequisiteExplorer()
    tree = explorer.explore(analysis.core_concept)
    
    # 3. Enrich with math
    enricher = MathematicalEnricher()
    enriched_tree = enricher.enrich(tree)
    
    # 4. Add visuals
    designer = VisualDesigner()
    designed_tree = designer.design(enriched_tree)
    
    # 5. Compose narrative
    composer = NarrativeComposer()
    prompt = composer.compose(designed_tree)
    
    assert len(prompt) > 1000  # Verbose prompt
    assert "$$" in prompt  # Has LaTeX equations
```

## Code Quality Standards

### Type Hints
Always use type hints:
```python
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class TreeNode:
    concept: str
    depth: int
    prerequisites: List['TreeNode']
    latex_content: Optional[str] = None
    visual_description: Optional[str] = None

def enrich_node(self, node: TreeNode) -> TreeNode:
    """Enrich a node with mathematical content."""
    # Implementation
```

### Docstrings
Document all public methods:
```python
def explore(self, concept: str, max_depth: int = 5) -> TreeNode:
    """
    Explore prerequisites for a concept recursively.
    
    Args:
        concept: The mathematical/scientific concept to explore
        max_depth: Maximum recursion depth to prevent infinite loops
    
    Returns:
        TreeNode: Root of the knowledge tree with prerequisites attached
    
    Raises:
        ValueError: If concept is empty or invalid
        APIError: If Claude API call fails after retries
    
    Example:
        >>> explorer = PrerequisiteExplorer()
        >>> tree = explorer.explore("quantum mechanics", max_depth=3)
        >>> print(f"Found {len(tree.prerequisites)} prerequisites")
    """
```

### Logging
Use logging, not print statements:
```python
import logging

logger = logging.getLogger(__name__)

class PrerequisiteExplorer:
    def explore(self, concept: str) -> TreeNode:
        logger.info(f"Exploring concept: {concept}")
        
        try:
            prereqs = self._get_prerequisites(concept)
            logger.debug(f"Found {len(prereqs)} prerequisites")
        except APIError as e:
            logger.error(f"API error while exploring {concept}: {e}")
            raise
```

## Common Patterns

### API Client Initialization
```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=self.api_key)
```

### Structured Output Parsing
```python
import json
import re

def parse_structured_response(self, response: str) -> dict:
    """Parse JSON from Claude's response."""
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        # Return safe default or raise
        raise ValueError(f"Invalid JSON in response: {response[:100]}...")
```

## Performance Considerations

### Async Operations
Use async for parallel agent calls when possible:
```python
import asyncio

async def enrich_nodes_parallel(self, nodes: List[TreeNode]) -> List[TreeNode]:
    """Enrich multiple nodes in parallel."""
    tasks = [self.enrich_node_async(node) for node in nodes]
    return await asyncio.gather(*tasks)
```

### Batch Processing
Process multiple items in a single API call when applicable:
```python
def batch_analyze(self, concepts: List[str]) -> List[Analysis]:
    """Analyze multiple concepts in one API call."""
    prompt = f"Analyze these concepts: {', '.join(concepts)}"
    # Single API call instead of N calls
    response = self.client.messages.create(...)
    return self._parse_batch_response(response)
```

## Security Considerations

### API Key Handling
```python
# Never commit API keys
# Always use environment variables
# Don't log API keys

def __init__(self):
    self.api_key = os.getenv("ANTHROPIC_API_KEY")
    # Don't do: logger.info(f"Using key: {self.api_key}")
```

### Input Validation
```python
def explore(self, concept: str) -> TreeNode:
    """Explore with input validation."""
    # Validate input
    if not concept or not concept.strip():
        raise ValueError("Concept cannot be empty")
    
    # Sanitize if needed (though Claude handles this)
    concept = concept.strip()
    
    # Proceed with safe input
    return self._explore_impl(concept)
```

## Documentation

### Update Agent Documentation
When modifying agents:
1. Update docstrings for changed methods
2. Update `docs/ARCHITECTURE.md` if changing pipeline
3. Update `README.md` if changing user-facing behavior
4. Add examples for new functionality

### Migration Notes
If changing agent interfaces:
```python
# Mark old method as deprecated
import warnings

def old_method(self):
    """Deprecated: Use new_method instead."""
    warnings.warn(
        "old_method is deprecated, use new_method",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

## Getting Help

- **Architecture Overview**: `docs/ARCHITECTURE.md`
- **Agent Testing**: `TESTING_QUICKSTART.md`
- **Claude SDK Docs**: https://docs.anthropic.com/
- **Ask Questions**: Open an issue with "agent:" prefix

## Remember

Agents are the core innovation of this project. Keep them:
- **Focused**: Single responsibility per agent
- **Reliable**: Comprehensive error handling
- **Efficient**: Caching and batching where possible
- **Testable**: Full test coverage
- **Documented**: Clear docstrings and comments
