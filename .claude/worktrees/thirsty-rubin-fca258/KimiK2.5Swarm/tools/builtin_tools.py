"""
Built-in tools for the KimiK2Thinking enrichment pipeline.

Defines the tool schemas and placeholder implementations for:
- Mathematical content enrichment
- Visual design planning
- Narrative composition
"""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .tool_registry import ToolRegistry


# =============================================================================
# Mathematical Content Tool
# =============================================================================


MATHEMATICAL_CONTENT_TOOL = {
    "type": "function",
    "function": {
        "name": "write_mathematical_content",
        "description": (
            "Return the key mathematical information needed to present this "
            "concept in a Manim animation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "equations": {
                    "type": "array",
                    "description": "2-5 LaTeX strings wrapped for MathTex.",
                    "items": {"type": "string"},
                },
                "definitions": {
                    "type": "object",
                    "description": "Dictionary mapping symbols to definitions.",
                    "additionalProperties": {"type": "string"},
                },
                "interpretation": {
                    "type": "string",
                    "description": "Physical or mathematical meaning.",
                },
                "examples": {
                    "type": "array",
                    "description": "Worked examples or sample calculations.",
                    "items": {"type": "string"},
                },
                "typical_values": {
                    "type": "object",
                    "description": "Reference magnitudes or constants.",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["equations", "definitions", "interpretation"],
        },
    },
}


# =============================================================================
# Visual Design Tool
# =============================================================================


VISUAL_DESIGN_TOOL = {
    "type": "function",
    "function": {
        "name": "design_visual_plan",
        "description": (
            "Describe the visual presentation for a concept. Focus on what should "
            "be shown visually, not specific Manim implementation details. Manim "
            "will handle the rendering automatically."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "visual_description": {
                    "type": "string",
                    "description": (
                        "Detailed description of what should appear visually: what objects, "
                        "shapes, or elements should be shown. Describe the visual content, "
                        "not the Manim classes."
                    ),
                },
                "color_scheme": {
                    "type": "string",
                    "description": (
                        "Color palette description (e.g., 'red and blue for electric and "
                        "magnetic fields'). Use descriptive color names."
                    ),
                },
                "animation_description": {
                    "type": "string",
                    "description": (
                        "How elements should animate or move: 'slowly rotate', 'fade in', "
                        "'zoom into', 'morph from X to Y'. Describe the visual effect."
                    ),
                },
                "transitions": {
                    "type": "string",
                    "description": "How to transition from previous concept to this one.",
                },
                "camera_movement": {
                    "type": "string",
                    "description": "Camera framing or movement (e.g., 'zoom into origin').",
                },
                "duration": {
                    "type": "integer",
                    "description": "Estimated duration in seconds (10-40).",
                },
                "layout": {
                    "type": "string",
                    "description": "Spatial arrangement or positioning notes.",
                },
            },
            "required": ["visual_description", "animation_description", "duration"],
        },
    },
}


# =============================================================================
# Narrative Tool
# =============================================================================


NARRATIVE_TOOL = {
    "type": "function",
    "function": {
        "name": "compose_narrative",
        "description": (
            "Assemble the final narrative prompt describing the animation "
            "sequence in depth."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "concept_order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ordered list from foundations to target concept.",
                },
                "verbose_prompt": {
                    "type": "string",
                    "description": (
                        "Full narrative prompt (2000+ words) with LaTeX, visuals, "
                        "timing, transitions, and Manim directions."
                    ),
                },
                "total_duration": {
                    "type": "integer",
                    "description": "Cumulative duration across scenes.",
                },
                "scene_count": {
                    "type": "integer",
                    "description": "Number of scenes/segments described.",
                },
            },
            "required": ["concept_order", "verbose_prompt"],
        },
    },
}


# =============================================================================
# Tool Collections
# =============================================================================


ENRICHMENT_TOOLS = [
    MATHEMATICAL_CONTENT_TOOL,
    VISUAL_DESIGN_TOOL,
    NARRATIVE_TOOL,
]

MATH_TOOLS = [MATHEMATICAL_CONTENT_TOOL]
VISUAL_TOOLS = [VISUAL_DESIGN_TOOL]
NARRATIVE_TOOLS = [NARRATIVE_TOOL]


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def write_mathematical_content(
    equations: List[str],
    definitions: Dict[str, str],
    interpretation: str,
    examples: List[str] = None,
    typical_values: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Process mathematical content for enrichment.

    This is a pass-through function that validates and returns the content.
    The actual content is generated by the LLM via tool calling.
    """
    return {
        "equations": equations or [],
        "definitions": definitions or {},
        "interpretation": interpretation or "",
        "examples": examples or [],
        "typical_values": typical_values or {},
    }


def design_visual_plan(
    visual_description: str,
    animation_description: str,
    duration: int,
    color_scheme: str = "",
    transitions: str = "",
    camera_movement: str = "",
    layout: str = "",
) -> Dict[str, Any]:
    """
    Process visual design plan for enrichment.

    This is a pass-through function that validates and returns the content.
    """
    return {
        "visual_description": visual_description,
        "color_scheme": color_scheme,
        "animation_description": animation_description,
        "transitions": transitions,
        "camera_movement": camera_movement,
        "duration": duration,
        "layout": layout,
    }


def compose_narrative(
    concept_order: List[str],
    verbose_prompt: str,
    total_duration: int = 0,
    scene_count: int = 0,
) -> Dict[str, Any]:
    """
    Process narrative composition for enrichment.

    This is a pass-through function that validates and returns the content.
    """
    return {
        "concept_order": concept_order,
        "verbose_prompt": verbose_prompt,
        "total_duration": total_duration,
        "scene_count": scene_count,
    }


# =============================================================================
# Registry Integration
# =============================================================================


def register_enrichment_tools(registry: 'ToolRegistry') -> None:
    """
    Register all enrichment tools with a registry.

    Args:
        registry: The ToolRegistry instance to register tools with
    """
    registry.register(
        name="write_mathematical_content",
        func=write_mathematical_content,
        description=MATHEMATICAL_CONTENT_TOOL["function"]["description"],
        parameters=MATHEMATICAL_CONTENT_TOOL["function"]["parameters"],
        category="math",
        tags=["enrichment", "mathematical", "latex"],
    )

    registry.register(
        name="design_visual_plan",
        func=design_visual_plan,
        description=VISUAL_DESIGN_TOOL["function"]["description"],
        parameters=VISUAL_DESIGN_TOOL["function"]["parameters"],
        category="visual",
        tags=["enrichment", "visual", "manim"],
    )

    registry.register(
        name="compose_narrative",
        func=compose_narrative,
        description=NARRATIVE_TOOL["function"]["description"],
        parameters=NARRATIVE_TOOL["function"]["parameters"],
        category="narrative",
        tags=["enrichment", "narrative", "composition"],
    )
