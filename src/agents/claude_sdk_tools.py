"""Custom MCP tools for Math-To-Manim agents using Claude Agent SDK.

This module defines in-process tools that agents can use for:
- Prerequisite caching and retrieval
- LaTeX validation
- Knowledge graph querying
- Manim code validation
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_agent_sdk import tool

# Cache for prerequisites (in-memory for now, can be Redis/DB later)
_PREREQUISITE_CACHE: Dict[str, List[str]] = {}


@tool(
    name="cache_prerequisites",
    description="Cache discovered prerequisites for a concept to avoid redundant API calls",
    input_schema={"concept": str, "prerequisites": list},
)
async def cache_prerequisites(args: Dict[str, Any]) -> Dict[str, Any]:
    """Store prerequisites for a concept in the cache."""
    concept = args["concept"]
    prerequisites = args["prerequisites"]

    _PREREQUISITE_CACHE[concept] = prerequisites

    return {
        "content": [
            {
                "type": "text",
                "text": f"Cached {len(prerequisites)} prerequisites for '{concept}'"
            }
        ]
    }


@tool(
    name="get_cached_prerequisites",
    description="Retrieve previously discovered prerequisites for a concept",
    input_schema={"concept": str},
)
async def get_cached_prerequisites(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve prerequisites from cache if they exist."""
    concept = args["concept"]

    if concept in _PREREQUISITE_CACHE:
        prerequisites = _PREREQUISITE_CACHE[concept]
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "found": True,
                        "prerequisites": prerequisites,
                        "count": len(prerequisites)
                    })
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"found": False, "prerequisites": []})
                }
            ]
        }


@tool(
    name="validate_latex",
    description="Validate LaTeX syntax and check if it compiles correctly",
    input_schema={"latex_code": str},
)
async def validate_latex(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate LaTeX code for syntax errors."""
    latex_code = args["latex_code"]

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

    # Check for unescaped special characters
    unescaped_chars = ["&", "%", "#"]
    for char in unescaped_chars:
        if char in latex_code and f"\\{char}" not in latex_code:
            warnings.append(f"Unescaped special character: {char}")

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

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "latex_code": latex_code
    }

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


@tool(
    name="validate_manim_imports",
    description="Check if Manim code has proper imports and basic syntax",
    input_schema={"manim_code": str},
)
async def validate_manim_imports(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Manim code for common issues."""
    manim_code = args["manim_code"]

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
        # Check for raw strings
        if 'MathTex("' in manim_code or 'Tex("' in manim_code:
            suggestions.append("Use raw strings (r\"...\") for LaTeX to avoid escape issues")

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions
    }

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


@tool(
    name="search_knowledge_tree",
    description="Search the local knowledge tree cache for related concepts",
    input_schema={"concept": str, "max_results": int},
)
async def search_knowledge_tree(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search for related concepts in cached knowledge trees."""
    concept = args["concept"]
    max_results = args.get("max_results", 5)

    # Search in cache for similar concepts
    results = []
    concept_lower = concept.lower()

    for cached_concept, prerequisites in _PREREQUISITE_CACHE.items():
        # Simple similarity check
        if (concept_lower in cached_concept.lower() or
            cached_concept.lower() in concept_lower):
            results.append({
                "concept": cached_concept,
                "prerequisites": prerequisites,
                "similarity": "partial_match"
            })

    # Limit results
    results = results[:max_results]

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps({
                    "query": concept,
                    "results": results,
                    "count": len(results)
                }, indent=2)
            }
        ]
    }


@tool(
    name="estimate_animation_complexity",
    description="Estimate the rendering complexity of a Manim scene",
    input_schema={"manim_code": str},
)
async def estimate_animation_complexity(args: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate how long a Manim animation will take to render."""
    manim_code = args["manim_code"]

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

    result = {
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

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


# Export all tools
ALL_TOOLS = [
    cache_prerequisites,
    get_cached_prerequisites,
    validate_latex,
    validate_manim_imports,
    search_knowledge_tree,
    estimate_animation_complexity,
]


__all__ = [
    "cache_prerequisites",
    "get_cached_prerequisites",
    "validate_latex",
    "validate_manim_imports",
    "search_knowledge_tree",
    "estimate_animation_complexity",
    "ALL_TOOLS",
]
