"""
Enrichment Agents - Specialized agents for knowledge tree enrichment.

This module provides BaseAgent subclasses for the three enrichment stages:
1. MathematicalEnricher - Adds equations, definitions, and interpretations
2. VisualDesigner - Plans Manim visual presentations
3. NarrativeComposer - Composes the final animation narrative

Each agent uses the tool infrastructure and can be run in parallel.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from .base_agent import AgentRole, BaseAgent, AgentConfig, AgentResult, ROLE_PROMPTS

if TYPE_CHECKING:
    from models import KnowledgeNode
    from kimi_client import KimiClient

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes for Enrichment Content
# =============================================================================


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


@dataclass
class VisualSpec:
    """Visual specification for Manim rendering."""
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


# =============================================================================
# Helper Functions
# =============================================================================


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


# =============================================================================
# Mathematical Enricher
# =============================================================================


class MathematicalEnricher:
    """
    Enriches knowledge nodes with mathematical content.

    Adds equations, definitions, interpretations, and examples using
    the Kimi API with tool calling.
    """

    def __init__(self, client: Optional['KimiClient'] = None):
        from kimi_client import get_kimi_client
        self.client = client or get_kimi_client()
        self.cache: Dict[str, MathematicalContent] = {}
        self._tool_calls = 0

    async def enrich_node(self, node: 'KnowledgeNode') -> 'KnowledgeNode':
        """
        Enrich a single node with mathematical content.

        Args:
            node: The KnowledgeNode to enrich

        Returns:
            The enriched node (modified in place)
        """
        from tools import MATHEMATICAL_CONTENT_TOOL

        # Check cache
        if node.concept in self.cache:
            cached = self.cache[node.concept]
            self._apply_content(node, cached)
            return node

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
        self._tool_calls += 1

        payload = _extract_tool_payload(response)
        if payload is None:
            payload = _parse_json_fallback(self.client.get_text_content(response)) or {}

        math_content = MathematicalContent.from_payload(payload)
        self.cache[node.concept] = math_content
        self._apply_content(node, math_content)

        return node

    def _apply_content(self, node: 'KnowledgeNode', content: MathematicalContent) -> None:
        """Apply mathematical content to a node."""
        node.equations = content.equations
        node.definitions = content.definitions

        if node.visual_spec is None:
            node.visual_spec = {}
        node.visual_spec.setdefault("interpretation", content.interpretation)
        node.visual_spec.setdefault("examples", content.examples)
        node.visual_spec.setdefault("typical_values", content.typical_values)

    async def enrich_tree(self, root: 'KnowledgeNode') -> 'KnowledgeNode':
        """Recursively enrich all nodes in the tree."""
        await self._enrich_recursive(root)
        return root

    async def _enrich_recursive(self, node: 'KnowledgeNode') -> None:
        """Recursively enrich a node and its prerequisites."""
        await self.enrich_node(node)
        for prereq in node.prerequisites:
            await self._enrich_recursive(prereq)

    @property
    def tool_calls_made(self) -> int:
        return self._tool_calls


# =============================================================================
# Visual Designer
# =============================================================================


class VisualDesigner:
    """
    Designs visual specifications for Manim animations.

    Creates visual descriptions, color schemes, animation effects,
    and timing for each concept.
    """

    def __init__(self, client: Optional['KimiClient'] = None):
        from kimi_client import get_kimi_client
        self.client = client or get_kimi_client()
        self.cache: Dict[str, VisualSpec] = {}
        self._tool_calls = 0

    async def design_node(
        self,
        node: 'KnowledgeNode',
        parent_spec: Optional[VisualSpec] = None,
    ) -> VisualSpec:
        """
        Design visual specification for a node.

        Args:
            node: The KnowledgeNode to design for
            parent_spec: Parent's visual spec for continuity

        Returns:
            VisualSpec for this node
        """
        from tools import VISUAL_DESIGN_TOOL

        # Check cache
        if node.concept in self.cache:
            cached_spec = self.cache[node.concept]
            if node.visual_spec is None:
                node.visual_spec = {}
            node.visual_spec.update(cached_spec.to_dict())
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
            "Describe what should appear visually: what objects, shapes, or elements. "
            "Describe colors in natural language. "
            "Describe animations as visual effects. "
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
        self._tool_calls += 1

        payload = _extract_tool_payload(response)
        if payload is None:
            payload = _parse_json_fallback(self.client.get_text_content(response)) or {}

        visual_spec = VisualSpec.from_payload(node.concept, payload)

        if node.visual_spec is None:
            node.visual_spec = {}
        node.visual_spec.update(visual_spec.to_dict())

        self.cache[node.concept] = visual_spec
        return visual_spec

    async def design_tree(self, root: 'KnowledgeNode') -> 'KnowledgeNode':
        """Design visual specs for all nodes in the tree."""
        await self._design_recursive(root, parent_spec=None)
        return root

    async def _design_recursive(
        self,
        node: 'KnowledgeNode',
        parent_spec: Optional[VisualSpec],
    ) -> VisualSpec:
        """Recursively design a node and its prerequisites."""
        spec = await self.design_node(node, parent_spec)
        for prereq in node.prerequisites:
            await self._design_recursive(prereq, spec)
        return spec

    @property
    def tool_calls_made(self) -> int:
        return self._tool_calls


# =============================================================================
# Narrative Composer
# =============================================================================


class NarrativeComposer:
    """
    Composes comprehensive narratives for animation scripts.

    Creates a cohesive narrative that guides Manim code generation,
    integrating mathematical content and visual design.
    """

    def __init__(self, client: Optional['KimiClient'] = None):
        from kimi_client import get_kimi_client, KimiClient
        self.client = client or get_kimi_client()
        self._tool_calls = 0

    async def compose(self, root: 'KnowledgeNode') -> 'Narrative':
        """
        Compose narrative for the entire knowledge tree.

        Args:
            root: The root KnowledgeNode

        Returns:
            Narrative with the composed content
        """
        from models import Narrative
        from tools import NARRATIVE_TOOL

        ordered_nodes = self._topological_order(root)
        concept_order = [node.concept for node in ordered_nodes]
        total_duration = self._estimate_total_duration(ordered_nodes)

        system_prompt = (
            "You are an expert STEM storyteller writing verbose prompts for "
            "Manim. Walk through each concept in order, connecting math and "
            "visuals, and then call 'compose_narrative' with the full text."
        )

        context = "\n".join(
            self._format_node_context(idx + 1, node)
            for idx, node in enumerate(ordered_nodes)
        )

        # Truncate context if too long
        max_context_chars = 18000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n...[context truncated]..."

        user_prompt = (
            f"Target concept: {root.concept}\n"
            f"Concept progression:\n{context}\n\n"
            "Compose a single continuous narrative (aim for ~2000 words) that:\n"
            "- Introduces foundational ideas before advanced ones.\n"
            "- References the provided LaTeX equations exactly as written.\n"
            "- Describes the visual content naturally.\n"
            "- Integrates color schemes, animation descriptions, and transitions.\n"
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
        self._tool_calls += 1

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

    def _topological_order(self, root: 'KnowledgeNode') -> List['KnowledgeNode']:
        """Get nodes in topological order (prerequisites first)."""
        visited = set()
        result: List['KnowledgeNode'] = []

        def dfs(node: 'KnowledgeNode'):
            if node.concept in visited:
                return
            visited.add(node.concept)
            for prereq in node.prerequisites:
                dfs(prereq)
            result.append(node)

        dfs(root)
        return result

    @staticmethod
    def _estimate_total_duration(nodes: List['KnowledgeNode']) -> int:
        """Estimate total animation duration."""
        duration = 0
        for node in nodes:
            if node.visual_spec and isinstance(node.visual_spec, dict):
                duration += int(node.visual_spec.get("duration", 15))
        return duration

    @staticmethod
    def _format_node_context(position: int, node: 'KnowledgeNode') -> str:
        """Format node context for narrative prompt."""
        equations = node.equations or []
        visual_spec = node.visual_spec or {}
        return (
            f"{position}. Concept: {node.concept}\n"
            f"   Depth: {node.depth}, Foundation: {node.is_foundation}\n"
            f"   Equations: {equations}\n"
            f"   Visual description: {visual_spec.get('visual_description', '')}\n"
            f"   Animation: {visual_spec.get('animation_description', '')}\n"
            f"   Colors: {visual_spec.get('color_scheme', '')}\n"
            f"   Transitions: {visual_spec.get('transitions', '')}\n"
        )

    @property
    def tool_calls_made(self) -> int:
        return self._tool_calls


# =============================================================================
# Legacy Compatibility Classes
# =============================================================================


# Aliases for backward compatibility
KimiMathematicalEnricher = MathematicalEnricher
KimiVisualDesigner = VisualDesigner
KimiNarrativeComposer = NarrativeComposer
