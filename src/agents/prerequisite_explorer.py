"""Unified Prerequisite Explorer — the core innovation of Math-To-Manim.

Recursively decomposes concepts by asking "What must I understand BEFORE this?"
to build complete knowledge trees with NO training data.

This module consolidates the five previous implementations into one with a
pluggable LLM client interface.  Any backend (Claude, DeepSeek, Kimi, etc.)
can be used by passing the appropriate ``LLMClient``.

Usage::

    from src.agents.llm_client import create_client
    from src.agents.prerequisite_explorer import PrerequisiteExplorer, ConceptAnalyzer

    client = create_client("anthropic")                 # or "deepseek", "kimi"
    explorer = PrerequisiteExplorer(client, max_depth=3)
    tree = explorer.explore("quantum field theory")
    tree.print_tree()
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from src.agents.knowledge_node import KnowledgeNode
from src.agents.llm_client import LLMClient, parse_json_response

logger = logging.getLogger(__name__)

# Re-export for backwards compatibility
__all__ = [
    "KnowledgeNode",
    "PrerequisiteExplorer",
    "ConceptAnalyzer",
]

# ---------------------------------------------------------------------------
# Shared prompts
# ---------------------------------------------------------------------------

_FOUNDATION_SYSTEM = """You are an expert educator analyzing whether a concept is foundational.

A concept is foundational if a typical high school graduate would understand it
without further mathematical or scientific explanation.

Examples of foundational concepts:
- velocity, distance, time, acceleration
- force, mass, energy
- waves, frequency, wavelength
- numbers, addition, multiplication
- basic geometry (points, lines, angles)
- functions, graphs

Examples of non-foundational concepts:
- Lorentz transformations
- gauge theory
- differential geometry
- tensor calculus
- quantum operators
- Hilbert spaces

Answer with ONLY "yes" or "no"."""

_PREREQUISITES_SYSTEM = """You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding (not just helpful)
2. Order from most to least important
3. Assume high school education as baseline (don't list truly basic things)
4. Focus on concepts that enable understanding, not just historical context
5. Be specific - prefer "special relativity" over "relativity"
6. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names, nothing else."""

_CONCEPT_ANALYSIS_SYSTEM = """You are an expert at analyzing educational requests and extracting key information.

Analyze the user's question and extract:
1. The MAIN concept they want to understand (be specific)
2. The scientific/mathematical domain
3. The appropriate complexity level
4. Their learning goal

Return ONLY valid JSON with these exact keys:
- core_concept
- domain
- level (must be: "beginner", "intermediate", or "advanced")
- goal"""


# ---------------------------------------------------------------------------
# PrerequisiteExplorer
# ---------------------------------------------------------------------------


class PrerequisiteExplorer:
    """Recursively discover prerequisites for any concept.

    This is the key innovation — no training data needed!  The explorer calls
    an LLM to answer "What must I understand BEFORE X?" and recurses until it
    hits foundation concepts or the depth limit.

    Parameters
    ----------
    client : LLMClient
        The LLM backend to use for queries.
    max_depth : int
        Maximum recursion depth (default 4).
    """

    def __init__(self, client: LLMClient, max_depth: int = 4):
        self.client = client
        self.max_depth = max_depth
        self.cache: Dict[str, List[str]] = {}
        self._stats = {"api_calls": 0, "cache_hits": 0, "concepts": 0}

    # -- public API ---------------------------------------------------------

    def explore(self, concept: str, depth: int = 0) -> KnowledgeNode:
        """Recursively explore prerequisites for *concept*."""
        logger.info("%sExploring: %s (depth %d)", "  " * depth, concept, depth)
        self._stats["concepts"] += 1

        if depth >= self.max_depth or self.is_foundation(concept):
            logger.info("%s  -> Foundation concept", "  " * depth)
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[],
            )

        prereqs = self.lookup_prerequisites(concept)
        nodes = [self.explore(p, depth + 1) for p in prereqs]

        return KnowledgeNode(
            concept=concept,
            depth=depth,
            is_foundation=False,
            prerequisites=nodes,
        )

    def is_foundation(self, concept: str) -> bool:
        """Return True if *concept* is understood at a high-school level."""
        self._stats["api_calls"] += 1
        answer = self.client.query(
            user_prompt=f'Is "{concept}" a foundational concept?\n\nAnswer with ONLY "yes" or "no".',
            system_prompt=_FOUNDATION_SYSTEM,
            max_tokens=10,
            temperature=0,
        )
        return answer.strip().lower().startswith("yes")

    def lookup_prerequisites(self, concept: str) -> List[str]:
        """Return prerequisites, using cache when available."""
        if concept in self.cache:
            self._stats["cache_hits"] += 1
            logger.debug("  -> Cache hit for %s", concept)
            return self.cache[concept]

        prereqs = self.discover_prerequisites(concept)
        self.cache[concept] = prereqs
        return prereqs

    def discover_prerequisites(self, concept: str) -> List[str]:
        """Query the LLM for 3-5 prerequisite concepts."""
        self._stats["api_calls"] += 1
        content = self.client.query(
            user_prompt=(
                f'To understand "{concept}", what are the 3-5 ESSENTIAL '
                f'prerequisite concepts?\n\nReturn format: ["concept1", "concept2", "concept3"]'
            ),
            system_prompt=_PREREQUISITES_SYSTEM,
            max_tokens=500,
            temperature=0.3,
        )
        result = parse_json_response(content)
        if not isinstance(result, list):
            raise ValueError(f"Expected a JSON array, got: {type(result)}")
        return result[:5]

    @property
    def stats(self) -> dict:
        """Return exploration statistics."""
        return {**self._stats, "cache_size": len(self.cache)}


# ---------------------------------------------------------------------------
# ConceptAnalyzer
# ---------------------------------------------------------------------------


class ConceptAnalyzer:
    """Analyzes user input to extract the core concept and metadata."""

    def __init__(self, client: LLMClient):
        self.client = client

    def analyze(self, user_input: str) -> Dict:
        """Parse *user_input* and return structured analysis as a dict."""
        user_prompt = (
            f'User asked: "{user_input}"\n\n'
            "Return JSON analysis with: core_concept, domain, level, goal\n\n"
            "Example:\n"
            '{\n  "core_concept": "quantum entanglement",\n'
            '  "domain": "physics/quantum mechanics",\n'
            '  "level": "intermediate",\n'
            '  "goal": "Understand how entangled particles maintain correlation"\n}'
        )
        content = self.client.query(
            user_prompt=user_prompt,
            system_prompt=_CONCEPT_ANALYSIS_SYSTEM,
            max_tokens=500,
            temperature=0.3,
        )
        result = parse_json_response(content)
        if not isinstance(result, dict):
            raise ValueError(f"Expected a JSON object, got: {type(result)}")
        return result


# ---------------------------------------------------------------------------
# Backwards-compatible aliases
# ---------------------------------------------------------------------------

# These constants are imported by other modules (mathematical_enricher, etc.)
CLAUDE_MODEL = "claude-opus-4-5-20251101"
