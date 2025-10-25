"""Improved Prerequisite Explorer with integrated caching and validation.

This version enhances the existing prerequisite_explorer_claude.py with:
- Better caching to reduce API calls
- LaTeX validation
- Manim code validation
- Progress tracking

Uses the basic anthropic SDK (no Claude Agent SDK required).
"""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# VALIDATION FUNCTIONS (extracted from claude_sdk_tools.py)
# ============================================================================

def validate_latex(latex_code: str) -> dict:
    """Validate LaTeX syntax - standalone function, no SDK required."""
    errors = []
    warnings = []

    # Basic syntax checks
    if latex_code.count("$") % 2 != 0:
        errors.append("Unmatched $ delimiter")

    if latex_code.count("\\[") != latex_code.count("\\]"):
        errors.append("Unmatched \\[ \\] delimiters")

    # Check for common LaTeX errors
    if "\\frac{}" in latex_code:
        errors.append("Empty \\frac{} command")

    # Check for balanced braces
    brace_count = 0
    for char in latex_code:
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
        if brace_count < 0:
            errors.append("Unmatched closing brace }")
            break

    if brace_count > 0:
        errors.append(f"Unclosed braces: {brace_count} opening brace(s) without closing")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "latex_code": latex_code
    }


def validate_manim_code(manim_code: str) -> dict:
    """Validate Manim code structure - standalone function."""
    errors = []
    warnings = []
    suggestions = []

    # Check for Manim import
    if "from manim import" not in manim_code and "import manim" not in manim_code:
        errors.append("Missing Manim import statement")

    # Check for Scene class definition
    if "class" not in manim_code or "Scene)" not in manim_code:
        errors.append("No Scene class defined")

    # Check for construct method
    if "def construct(self)" not in manim_code:
        errors.append("Missing construct(self) method")

    # Check for common mistakes
    if "self.play(" in manim_code:
        if manim_code.count("self.play(") > 20:
            warnings.append("Many play() calls - consider grouping animations")

    # Check for LaTeX in code
    if "MathTex" in manim_code or "Tex" in manim_code:
        if 'MathTex("' in manim_code or 'Tex("' in manim_code:
            suggestions.append("Use raw strings (r\"...\") for LaTeX to avoid escape issues")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions
    }


def estimate_complexity(manim_code: str) -> dict:
    """Estimate animation rendering complexity - standalone function."""
    # Count complexity indicators
    play_count = manim_code.count("self.play(")
    create_count = manim_code.count("Create(")
    transform_count = manim_code.count("Transform(")
    mathtex_count = manim_code.count("MathTex(")
    mobject_count = (
        manim_code.count("Circle(") +
        manim_code.count("Square(") +
        manim_code.count("Line(") +
        manim_code.count("Dot(")
    )

    # Estimate render time (very rough)
    base_time = 5  # seconds
    time_per_play = 2
    time_per_mathtex = 3
    time_per_mobject = 0.5

    estimated_seconds = (
        base_time +
        (play_count * time_per_play) +
        (mathtex_count * time_per_mathtex) +
        (mobject_count * time_per_mobject)
    )

    complexity_score = play_count + mathtex_count + (mobject_count * 0.5)

    if complexity_score < 10:
        complexity = "low"
    elif complexity_score < 30:
        complexity = "medium"
    else:
        complexity = "high"

    return {
        "complexity": complexity,
        "estimated_render_time_seconds": estimated_seconds,
        "statistics": {
            "play_calls": play_count,
            "create_animations": create_count,
            "transforms": transform_count,
            "latex_objects": mathtex_count,
            "basic_mobjects": mobject_count
        }
    }


# ============================================================================
# KNOWLEDGE NODE (same as before)
# ============================================================================

@dataclass
class KnowledgeNode:
    """Represents a concept in the knowledge tree"""
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List['KnowledgeNode']

    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[Dict] = None
    narrative: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'concept': self.concept,
            'depth': self.depth,
            'is_foundation': self.is_foundation,
            'prerequisites': [p.to_dict() for p in self.prerequisites],
            'equations': self.equations,
            'definitions': self.definitions,
            'visual_spec': self.visual_spec,
            'narrative': self.narrative
        }

    def print_tree(self, indent: int = 0):
        prefix = "  " * indent
        foundation_mark = " [FOUNDATION]" if self.is_foundation else ""
        print(f"{prefix}+- {self.concept} (depth {self.depth}){foundation_mark}")
        for prereq in self.prerequisites:
            prereq.print_tree(indent + 1)


# ============================================================================
# IMPROVED PREREQUISITE EXPLORER
# ============================================================================

class ImprovedPrerequisiteExplorer:
    """
    Improved prerequisite explorer with better caching and validation.

    Uses basic anthropic SDK - no Claude Agent SDK required.
    Integrates validation functions for better error prevention.
    """

    def __init__(self, model: str = "claude-sonnet-4-5", max_depth: int = 4):
        self.model = model
        self.max_depth = max_depth

        # Caching
        self.cache = {}  # In-memory cache for prerequisites

        # Statistics
        self.stats = {
            "api_calls": 0,
            "cache_hits": 0,
            "concepts_explored": 0
        }

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set.")
        self.client = Anthropic(api_key=api_key)

    def explore(self, concept: str, depth: int = 0, verbose: bool = True) -> KnowledgeNode:
        """Explore prerequisites recursively with caching."""
        if verbose:
            print(f"{'  ' * depth}Exploring: {concept} (depth {depth})")

        self.stats["concepts_explored"] += 1

        # Check max depth
        if depth >= self.max_depth:
            if verbose:
                print(f"{'  ' * depth}  -> Max depth reached")
            return KnowledgeNode(concept=concept, depth=depth, is_foundation=True, prerequisites=[])

        # Check if foundation
        if self.is_foundation(concept):
            if verbose:
                print(f"{'  ' * depth}  -> Foundation concept")
            return KnowledgeNode(concept=concept, depth=depth, is_foundation=True, prerequisites=[])

        # Get prerequisites (with caching)
        prerequisites = self.lookup_prerequisites(concept, verbose=verbose)

        # Recursively explore prerequisites
        prereq_nodes = []
        for prereq in prerequisites:
            node = self.explore(prereq, depth + 1, verbose)
            prereq_nodes.append(node)

        return KnowledgeNode(concept=concept, depth=depth, is_foundation=False, prerequisites=prereq_nodes)

    def is_foundation(self, concept: str) -> bool:
        """Check if a concept is foundational."""
        system_prompt = """You are an expert educator analyzing whether a concept is foundational.

A concept is foundational if a typical high school graduate would understand it
without further mathematical or scientific explanation.

Examples of foundational concepts:
- velocity, distance, time, acceleration
- force, mass, energy
- waves, frequency, wavelength

Examples of non-foundational concepts:
- Lorentz transformations
- gauge theory
- differential geometry

Answer with ONLY "yes" or "no"."""

        user_prompt = f'Is "{concept}" a foundational concept?'

        self.stats["api_calls"] += 1

        response = self.client.messages.create(
            model=self.model,
            max_tokens=10,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        answer = response.content[0].text
        return answer.strip().lower().startswith('yes')

    def lookup_prerequisites(self, concept: str, verbose: bool = True) -> List[str]:
        """Get prerequisites with caching to reduce API calls."""

        # Check cache first
        if concept in self.cache:
            if verbose:
                print(f"  -> Cache hit for '{concept}'")
            self.stats["cache_hits"] += 1
            return self.cache[concept]

        # Not in cache - query Claude
        prerequisites = self.discover_prerequisites(concept)

        # Cache the result
        self.cache[concept] = prerequisites

        return prerequisites

    def discover_prerequisites(self, concept: str) -> List[str]:
        """Discover prerequisites from Claude."""
        system_prompt = """You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding
2. Order from most to least important
3. Assume high school education as baseline
4. Be specific - prefer "special relativity" over "relativity"
5. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names, nothing else."""

        user_prompt = f'''To understand "{concept}", what are the 3-5 ESSENTIAL prerequisite concepts?

Return format: ["concept1", "concept2", "concept3"]'''

        self.stats["api_calls"] += 1

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text

        # Parse JSON response
        try:
            prerequisites = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            if "```" in content:
                section = content.split("```")[1]
                if section.startswith("json"):
                    section = section[4:]
                prerequisites = json.loads(section.strip())
            else:
                import re
                match = re.search(r"\[.*?\]", content, re.DOTALL)
                if match:
                    prerequisites = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse prerequisites from: {content}")

        return prerequisites[:5]

    def print_stats(self):
        """Print caching statistics."""
        print("\n" + "="*70)
        print("STATISTICS")
        print("="*70)
        print(f"Total concepts explored: {self.stats['concepts_explored']}")
        print(f"API calls made: {self.stats['api_calls']}")
        print(f"Cache hits: {self.stats['cache_hits']}")

        if self.stats['api_calls'] > 0:
            cache_rate = (self.stats['cache_hits'] / (self.stats['api_calls'] + self.stats['cache_hits'])) * 100
            print(f"Cache hit rate: {cache_rate:.1f}%")

        print(f"Cache size: {len(self.cache)} concepts")
        print("="*70)


# ============================================================================
# DEMO
# ============================================================================

def demo():
    """Demo the improved prerequisite explorer."""
    print("""
======================================================================
          Improved Prerequisite Explorer - No SDK Required
======================================================================

Features:
  * Uses basic anthropic SDK (works anywhere)
  * Integrated caching to reduce API calls
  * LaTeX validation functions
  * Manim code validation
  * Complexity estimation

This is production-ready for your Math-To-Manim project!
======================================================================
    """)

    # Verify API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set")
        print("Please create a .env file with: ANTHROPIC_API_KEY=your_key_here")
        return

    print("\n[OK] API key found\n")

    # Create explorer
    explorer = ImprovedPrerequisiteExplorer(max_depth=3)

    # Build knowledge tree
    concept = "quantum mechanics"
    print(f"{'='*70}")
    print(f"Building knowledge tree for: {concept}")
    print('='*70)

    try:
        tree = explorer.explore(concept, verbose=True)

        print(f"\n{'='*70}")
        print("KNOWLEDGE TREE")
        print('='*70)
        tree.print_tree()

        # Print stats
        explorer.print_stats()

        # Save to JSON
        output_file = f"knowledge_tree_{concept.replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(tree.to_dict(), f, indent=2)
        print(f"\nSaved tree to: {output_file}")

        # Demo validation functions
        print(f"\n{'='*70}")
        print("VALIDATION DEMOS")
        print('='*70)

        # LaTeX validation
        print("\n1. LaTeX Validation:")
        latex_result = validate_latex(r"\frac{x}{y}")
        print(f"   {latex_result['latex_code']}: {latex_result['valid']}")

        latex_result = validate_latex(r"\frac{x}{y")
        print(f"   {latex_result['latex_code']}: {latex_result['valid']} - {latex_result['errors']}")

        # Manim validation
        print("\n2. Manim Code Validation:")
        code = """from manim import *
class MyScene(Scene):
    def construct(self):
        pass"""
        manim_result = validate_manim_code(code)
        print(f"   Valid code: {manim_result['valid']}")

        # Complexity estimation
        print("\n3. Complexity Estimation:")
        complex_result = estimate_complexity(code)
        print(f"   Complexity: {complex_result['complexity']}")
        print(f"   Estimated render time: {complex_result['estimated_render_time_seconds']}s")

        print("\n" + "="*70)
        print("ALL DEMOS COMPLETED")
        print("="*70)
        print("\nNext steps:")
        print("  1. Integrate caching into your existing agents")
        print("  2. Add validation before rendering")
        print("  3. Use complexity estimation for planning")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo()
