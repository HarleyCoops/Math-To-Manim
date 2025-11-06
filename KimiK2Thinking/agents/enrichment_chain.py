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
        self.cache: Dict[str, MathematicalContent] = {}

    async def enrich_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        await self._enrich_node(root)
        return root

    async def _enrich_node(self, node: KnowledgeNode) -> None:
        if node.concept in self.cache:
            cached = self.cache[node.concept]
            node.equations = cached.equations
            node.definitions = cached.definitions
            if node.visual_spec is None:
                node.visual_spec = {}
            node.visual_spec.setdefault("interpretation", cached.interpretation)
            node.visual_spec.setdefault("examples", cached.examples)
            node.visual_spec.setdefault("typical_values", cached.typical_values)
            for prereq in node.prerequisites:
                await self._enrich_node(prereq)
            return

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
        self.cache[node.concept] = math_content

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
                        "not the Manim classes. For example: 'rotating wireframe of 4D spacetime', "
                        "'undulating plane waves', 'Feynman diagram with electron and photon lines'."
                    ),
                },
                "color_scheme": {
                    "type": "string",
                    "description": (
                        "Color palette description (e.g., 'red and blue for electric and magnetic fields', "
                        "'gold for field strength tensor'). Use descriptive color names."
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
                    "description": "Camera framing or movement (e.g., 'zoom into origin', 'pan over', 'pull away').",
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


@dataclass
class VisualSpec:
    concept: str
    visual_description: str = ""
    color_scheme: str = ""
    animation_description: str = ""
    transitions: str = ""
    camera_movement: str = ""
    duration: int = 15
    layout: str = ""

    @classmethod
    def from_payload(cls, concept: str, payload: Dict[str, Any]) -> "VisualSpec":
        return cls(
            concept=concept,
            visual_description=payload.get("visual_description", ""),
            color_scheme=payload.get("color_scheme", ""),
            animation_description=payload.get("animation_description", ""),
            transitions=payload.get("transitions", ""),
            camera_movement=payload.get("camera_movement", ""),
            duration=payload.get("duration", 15),
            layout=payload.get("layout", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept,
            "visual_description": self.visual_description,
            "color_scheme": self.color_scheme,
            "animation_description": self.animation_description,
            "transitions": self.transitions,
            "camera_movement": self.camera_movement,
            "duration": self.duration,
            "layout": self.layout,
        }


class KimiVisualDesigner:
    """Design Manim visual specifications using Kimi tool calls."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.client = client or get_kimi_client()
        self.cache: Dict[str, VisualSpec] = {}

    async def design_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        await self._design_node(root, parent_spec=None)
        return root

    async def _design_node(
        self,
        node: KnowledgeNode,
        parent_spec: Optional[VisualSpec],
    ) -> VisualSpec:
        if node.concept in self.cache:
            cached_spec = self.cache[node.concept]
            if node.visual_spec is None:
                node.visual_spec = {}
            node.visual_spec.update(cached_spec.to_dict())
            for prereq in node.prerequisites:
                await self._design_node(prereq, cached_spec)
            return cached_spec

        previous_info = ""
        if parent_spec:
            previous_info = (
                f"Previous concept: {parent_spec.concept}\n"
                f"Previous visual: {parent_spec.visual_description}\n"
                f"Previous colors: {parent_spec.color_scheme}\n"
            )

        system_prompt = (
            "You are a visual designer describing what should appear in an animation. "
            "Focus on describing the visual content and effects, not specific implementation "
            "details. Manim will handle the rendering automatically. Respond by calling "
            "the 'design_visual_plan' tool."
        )

        user_prompt = (
            f"Concept: {node.concept}\n"
            f"Depth: {node.depth}\n"
            f"Is foundational: {node.is_foundation}\n"
            f"Equations to feature: {node.equations or 'None provided'}\n"
            f"Prerequisites: {[p.concept for p in node.prerequisites]}\n"
            f"{previous_info}\n"
            "Describe what should appear visually: what objects, shapes, or elements should be shown. "
            "Describe colors in natural language (e.g., 'red and blue', 'gold'). "
            "Describe animations as visual effects (e.g., 'slowly rotate', 'fade in', 'zoom into'). "
            "Do NOT specify Manim classes like MathTex or VGroup - just describe what should be visible. "
            "Estimate duration in seconds."
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

        self.cache[node.concept] = visual_spec

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

        # Expand context for larger models when available
        client = self.client
        try:
            model_name = getattr(self.client, "model", "")
            if "8k" in model_name:
                client = KimiClient(model=model_name.replace("8k", "32k"))
        except Exception:
            # Fall back to existing client if reinitialization fails
            client = self.client

        system_prompt = (
            "You are an expert STEM storyteller writing verbose prompts for "
            "Manim. Walk through each concept in order, connecting math and "
            "visuals, and then call 'compose_narrative' with the full text."
        )

        context = "\n".join(
            self._format_node_context(idx + 1, node) for idx, node in enumerate(ordered_nodes)
        )
        # Avoid exceeding context window if tree is very large
        max_context_chars = 18000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n...[context truncated]..."

        user_prompt = (
            f"Target concept: {root.concept}\n"
            f"Concept progression:\n{context}\n\n"
            "Compose a single continuous narrative (aim for ~2000 words) that:\n"
            "- Introduces foundational ideas before advanced ones.\n"
            "- References the provided LaTeX equations exactly as written (use raw string form r\"...\" when quoting).\n"
            "- Describes the visual content naturally (what appears, not how Manim implements it).\n"
            "- Integrates color schemes, animation descriptions, and transitions.\n"
            "- Provides pacing/timing suggestions per scene.\n"
            "- Focuses on LaTeX equations for exact math rendering - let Manim handle visual elements.\n"
            "- Ends with a summary that prepares for Manim code generation.\n"
            "Return your work by calling the tool."
        )

        response = client.chat_completion(
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
        visual_desc = visual_spec.get("visual_description", "")
        animation_desc = visual_spec.get("animation_description", "")
        color_scheme = visual_spec.get("color_scheme", "")
        transitions = visual_spec.get("transitions", "")
        return (
            f"{position}. Concept: {node.concept}\n"
            f"   Depth: {node.depth}, Foundation: {node.is_foundation}\n"
            f"   Equations: {equations}\n"
            f"   Visual description: {visual_desc}\n"
            f"   Animation: {animation_desc}\n"
            f"   Colors: {color_scheme}\n"
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
