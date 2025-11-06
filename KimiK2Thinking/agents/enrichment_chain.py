"""
Kimi K2 Enrichment Chain
========================

This module ports the Claude-based enrichment agents to the Kimi K2
thinking model. It mirrors the original pipeline stages:

1. MathematicalEnricher -> adds equations, definitions, examples
2. VisualDesigner      -> plans Manim visuals for each concept
3. NarrativeComposer   -> stitches everything into a long-form prompt

All stages use Moonshot's OpenAI-compatible tool-calling interface so
that structured data is returned via function arguments rather than
plain text parsing.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from kimi_client import KimiClient, get_kimi_client

from .prerequisite_explorer_kimi import KnowledgeNode


# ---------------------------------------------------------------------------
# Shared helper utilities
# ---------------------------------------------------------------------------


def _extract_tool_payload(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return JSON payload from the first tool call, if present."""
    if not response:
        return None

    choices = response.get("choices", [])
    if not choices:
        return None

    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        return None

    function_call = tool_calls[0].get("function")
    if not function_call:
        return None

    arguments = function_call.get("arguments", "")
    if not arguments:
        return None

    try:
        return json.loads(arguments)
    except json.JSONDecodeError:
        return None


def _parse_json_fallback(text: str) -> Optional[Dict[str, Any]]:
    """Fallback parser when model returned raw JSON instead of a tool call."""
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to extract JSON block from markdown fences
        if "```" in text:
            segments = text.split("```")
            for segment in segments[1::2]:
                normalized = segment.strip()
                if normalized.startswith("json"):
                    normalized = normalized[4:].strip()
                try:
                    return json.loads(normalized)
                except json.JSONDecodeError:
                    continue
        return None


# ---------------------------------------------------------------------------
# Mathematical enrichment
# ---------------------------------------------------------------------------


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


@dataclass
class MathematicalContent:
    """Mathematical content for a concept."""

    equations: List[str] = field(default_factory=list)
    definitions: Dict[str, str] = field(default_factory=dict)
    interpretation: str = ""
    examples: List[str] = field(default_factory=list)
    typical_values: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "MathematicalContent":
        return cls(
            equations=payload.get("equations", []),
            definitions=payload.get("definitions", {}),
            interpretation=payload.get("interpretation", ""),
            examples=payload.get("examples", []),
            typical_values=payload.get("typical_values", {}),
        )


class KimiMathematicalEnricher:
    """Populate equations/definitions for each knowledge node via Kimi K2."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.client = client or get_kimi_client()

    async def enrich_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        await self._enrich_node(root)
        return root

    async def _enrich_node(self, node: KnowledgeNode) -> None:
        complexity = "high school level" if node.is_foundation else "upper-undergraduate level"

        system_prompt = (
            "You are an expert mathematical physicist preparing content for a "
            "Manim animation. Provide rigorous, properly formatted LaTeX and "
            "clear symbol definitions. Respond by calling the tool "
            "'write_mathematical_content'. Do not include plain text responses."
        )

        user_prompt = (
            f"Concept: {node.concept}\n"
            f"Depth: {node.depth}\n"
            f"Complexity target: {complexity}\n"
            "Return 2-5 LaTeX equations (raw strings with escaped backslashes), "
            "definitions for every symbol, at least one interpretation paragraph, "
            "and any illustrative examples/typical values that help teach the idea."
        )

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            tools=[MATHEMATICAL_CONTENT_TOOL],
            tool_choice="auto",
            max_tokens=1200,
            temperature=0.2,
        )

        payload = _extract_tool_payload(response)
        if payload is None:
            payload = _parse_json_fallback(self.client.get_text_content(response)) or {}

        math_content = MathematicalContent.from_payload(payload)

        node.equations = math_content.equations
        node.definitions = math_content.definitions

        if node.visual_spec is None:
            node.visual_spec = {}
        node.visual_spec.setdefault("interpretation", math_content.interpretation)
        node.visual_spec.setdefault("examples", math_content.examples)
        node.visual_spec.setdefault("typical_values", math_content.typical_values)

        for prereq in node.prerequisites:
            await self._enrich_node(prereq)


# ---------------------------------------------------------------------------
# Visual design
# ---------------------------------------------------------------------------


VISUAL_DESIGN_TOOL = {
    "type": "function",
    "function": {
        "name": "design_visual_plan",
        "description": (
            "Draft the Manim visual plan for a concept, including objects, "
            "colors, animations, transitions, camera moves, and duration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific Manim objects or constructs to create.",
                },
                "colors": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from element names to Manim color constants.",
                },
                "animations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Animation primitives or sequences.",
                },
                "transitions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "How to connect this scene with prerequisites.",
                },
                "camera_movement": {
                    "type": "string",
                    "description": "Camera framing or movement guidance.",
                },
                "duration": {
                    "type": "integer",
                    "description": "Estimated duration in seconds (10-40).",
                },
                "layout": {
                    "type": "string",
                    "description": "Spatial arrangement notes.",
                },
            },
            "required": ["elements", "animations", "duration"],
        },
    },
}


@dataclass
class VisualSpec:
    concept: str
    elements: List[str] = field(default_factory=list)
    colors: Dict[str, str] = field(default_factory=dict)
    animations: List[str] = field(default_factory=list)
    transitions: List[str] = field(default_factory=list)
    camera_movement: str = ""
    duration: int = 15
    layout: str = ""

    @classmethod
    def from_payload(cls, concept: str, payload: Dict[str, Any]) -> "VisualSpec":
        return cls(
            concept=concept,
            elements=payload.get("elements", []),
            colors=payload.get("colors", {}),
            animations=payload.get("animations", []),
            transitions=payload.get("transitions", []),
            camera_movement=payload.get("camera_movement", ""),
            duration=payload.get("duration", 15),
            layout=payload.get("layout", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept,
            "elements": self.elements,
            "colors": self.colors,
            "animations": self.animations,
            "transitions": self.transitions,
            "camera_movement": self.camera_movement,
            "duration": self.duration,
            "layout": self.layout,
        }


class KimiVisualDesigner:
    """Design Manim visual specifications using Kimi tool calls."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.client = client or get_kimi_client()

    async def design_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        await self._design_node(root, parent_spec=None)
        return root

    async def _design_node(
        self,
        node: KnowledgeNode,
        parent_spec: Optional[VisualSpec],
    ) -> VisualSpec:
        previous_info = ""
        if parent_spec:
            previous_info = (
                f"Previous concept: {parent_spec.concept}\n"
                f"Previous elements: {', '.join(parent_spec.elements)}\n"
                f"Previous colors: {json.dumps(parent_spec.colors)}\n"
            )

        system_prompt = (
            "You are a senior Manim animator. Plan the visuals for the current "
            "concept, keeping continuity with prior scenes. Respond by calling "
            "the 'design_visual_plan' tool."
        )

        user_prompt = (
            f"Concept: {node.concept}\n"
            f"Depth: {node.depth}\n"
            f"Is foundational: {node.is_foundation}\n"
            f"Equations to feature: {node.equations or 'None provided'}\n"
            f"Prerequisites: {[p.concept for p in node.prerequisites]}\n"
            f"{previous_info}\n"
            "Propose specific Manim elements (MathTex, VGroup, Axes, etc.), "
            "give a tight color palette (using Manim color constants), outline "
            "key animation beats, camera moves, and how to transition from the "
            "previous concept. Estimate duration in seconds."
        )

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            tools=[VISUAL_DESIGN_TOOL],
            tool_choice="auto",
            temperature=0.4,
            max_tokens=1200,
        )

        payload = _extract_tool_payload(response)
        if payload is None:
            payload = _parse_json_fallback(self.client.get_text_content(response)) or {}

        visual_spec = VisualSpec.from_payload(node.concept, payload)

        if node.visual_spec is None:
            node.visual_spec = {}
        node.visual_spec.update(visual_spec.to_dict())

        for prereq in node.prerequisites:
            await self._design_node(prereq, visual_spec)

        return visual_spec


# ---------------------------------------------------------------------------
# Narrative composition
# ---------------------------------------------------------------------------


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


@dataclass
class Narrative:
    target_concept: str
    verbose_prompt: str
    concept_order: List[str] = field(default_factory=list)
    total_duration: int = 0
    scene_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_concept": self.target_concept,
            "verbose_prompt": self.verbose_prompt,
            "concept_order": self.concept_order,
            "total_duration": self.total_duration,
            "scene_count": self.scene_count,
        }


class KimiNarrativeComposer:
    """Compose the long-form animation narrative using Kimi tool calling."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.client = client or get_kimi_client()

    async def compose_async(self, root: KnowledgeNode) -> Narrative:
        ordered_nodes = self._topological_order(root)
        concept_order = [node.concept for node in ordered_nodes]
        total_duration = self._estimate_total_duration(ordered_nodes)

        system_prompt = (
            "You are an expert STEM storyteller writing verbose prompts for "
            "Manim. Walk through each concept in order, connecting math and "
            "visuals, and then call 'compose_narrative' with the full text."
        )

        context = "\n".join(
            self._format_node_context(idx + 1, node) for idx, node in enumerate(ordered_nodes)
        )

        user_prompt = (
            f"Target concept: {root.concept}\n"
            f"Concept progression:\n{context}\n\n"
            "Compose a single continuous narrative (aim for ~2000 words) that:\n"
            "- Introduces foundational ideas before advanced ones.\n"
            "- References the provided LaTeX equations (use raw string form r\"...\" when quoting).\n"
            "- Integrates the visual plans (elements, color themes, transitions).\n"
            "- Provides pacing/timing suggestions per scene.\n"
            "- Ends with a summary that prepares for Manim code generation.\n"
            "Return your work by calling the tool."
        )

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            tools=[NARRATIVE_TOOL],
            tool_choice="auto",
            temperature=0.6,
            max_tokens=4000,
        )

        payload = _extract_tool_payload(response)
        if payload is None:
            payload = _parse_json_fallback(self.client.get_text_content(response)) or {}

        verbose_prompt = payload.get("verbose_prompt", "")
        total_duration = payload.get("total_duration", total_duration)
        scene_count = payload.get("scene_count", len(ordered_nodes))
        concept_order = payload.get("concept_order", concept_order)

        root.narrative = verbose_prompt

        return Narrative(
            target_concept=root.concept,
            verbose_prompt=verbose_prompt,
            concept_order=concept_order,
            total_duration=total_duration,
            scene_count=scene_count,
        )

    def _topological_order(self, root: KnowledgeNode) -> List[KnowledgeNode]:
        visited = set()
        result: List[KnowledgeNode] = []

        def dfs(node: KnowledgeNode):
            if node.concept in visited:
                return
            visited.add(node.concept)
            for prereq in node.prerequisites:
                dfs(prereq)
            result.append(node)

        dfs(root)
        return result

    @staticmethod
    def _estimate_total_duration(nodes: List[KnowledgeNode]) -> int:
        duration = 0
        for node in nodes:
            if node.visual_spec and isinstance(node.visual_spec, dict):
                duration += int(node.visual_spec.get("duration", 15))
        return duration

    @staticmethod
    def _format_node_context(position: int, node: KnowledgeNode) -> str:
        equations = node.equations or []
        visual_spec = node.visual_spec or {}
        animations = visual_spec.get("animations", [])
        colors = visual_spec.get("colors", {})
        transitions = visual_spec.get("transitions", [])
        return (
            f"{position}. Concept: {node.concept}\n"
            f"   Depth: {node.depth}, Foundation: {node.is_foundation}\n"
            f"   Equations: {equations}\n"
            f"   Visual elements: {visual_spec.get('elements', [])}\n"
            f"   Animations: {animations}\n"
            f"   Colors: {colors}\n"
            f"   Transitions: {transitions}\n"
        )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class EnrichmentResult:
    enriched_tree: KnowledgeNode
    narrative: Narrative


class KimiEnrichmentPipeline:
    """Run mathematical enrichment, visual design, and narrative composition."""

    def __init__(self, client: Optional[KimiClient] = None):
        client = client or get_kimi_client()
        self.math = KimiMathematicalEnricher(client=client)
        self.visual = KimiVisualDesigner(client=client)
        self.narrative = KimiNarrativeComposer(client=client)

    async def run_async(self, root: KnowledgeNode) -> EnrichmentResult:
        await self.math.enrich_tree(root)
        await self.visual.design_tree(root)
        narrative = await self.narrative.compose_async(root)
        return EnrichmentResult(enriched_tree=root, narrative=narrative)

    def run(self, root: KnowledgeNode) -> EnrichmentResult:
        return asyncio.run(self.run_async(root))
