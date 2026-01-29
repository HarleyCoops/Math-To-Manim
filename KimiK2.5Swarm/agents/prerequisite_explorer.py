"""
Prerequisite Explorer - Knowledge tree builder using Kimi K2.5.

This module explores prerequisite concepts and builds knowledge trees
with support for:
- TTL-based caching
- Parallel exploration at same depth level
- Tool registry integration
- Both async and sync interfaces
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from config import EnrichmentConfig, TOOLS_ENABLED, FALLBACK_TO_VERBOSE

if TYPE_CHECKING:
    from kimi_client import KimiClient
    from models import KnowledgeNode

logger = logging.getLogger(__name__)


# =============================================================================
# TTL Cache
# =============================================================================


class TTLCache:
    """Simple TTL-based cache for prerequisites."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value with current timestamp."""
        self._cache[key] = (value, time.time())

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        self._cache.clear()


# =============================================================================
# Prerequisite Explorer
# =============================================================================


class PrerequisiteExplorer:
    """
    Explore prerequisite concepts using Kimi K2.5.

    Features:
    - TTL-based caching
    - Parallel exploration at same depth level
    - Tool registry integration
    - Verbose fallback when tools unavailable
    """

    def __init__(
        self,
        max_depth: int = 4,
        use_tools: bool = True,
        client: Optional['KimiClient'] = None,
        config: Optional[EnrichmentConfig] = None,
    ):
        """
        Initialize the prerequisite explorer.

        Args:
            max_depth: Maximum exploration depth
            use_tools: Whether to use tool calling
            client: KimiClient instance
            config: Enrichment configuration
        """
        self.max_depth = max_depth
        self.use_tools = use_tools and TOOLS_ENABLED
        self.config = config or EnrichmentConfig.from_env()

        # Initialize client lazily
        self._client = client

        # TTL cache for prerequisites
        self.cache = TTLCache(ttl_seconds=self.config.cache_ttl_seconds)

        # Metrics
        self._api_calls = 0

    @property
    def client(self) -> 'KimiClient':
        """Get or create Kimi client."""
        if self._client is None:
            from kimi_client import get_kimi_client
            self._client = get_kimi_client()
        return self._client

    async def explore_async(
        self,
        concept: str,
        depth: int = 0,
        verbose: bool = True,
    ) -> 'KnowledgeNode':
        """
        Explore prerequisites for a concept.

        Args:
            concept: The concept to explore
            depth: Current depth in the tree
            verbose: Whether to print progress

        Returns:
            KnowledgeNode with prerequisites
        """
        from models import KnowledgeNode

        if verbose:
            print(f"{'  ' * depth}Exploring: {concept} (depth {depth})")

        # Check max depth
        if depth >= self.max_depth:
            if verbose:
                print(f"{'  ' * depth}  -> Max depth reached")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[],
            )

        # Check if foundation
        is_foundation = await self._is_foundation(concept)
        if is_foundation:
            if verbose:
                print(f"{'  ' * depth}  -> Foundation concept")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[],
            )

        # Get prerequisites
        prerequisites = await self._get_prerequisites(concept, verbose)

        # Explore prerequisites (can be parallelized)
        if self.config.enable_parallel_enrichment:
            prereq_nodes = await self._explore_parallel(prerequisites, depth + 1, verbose)
        else:
            prereq_nodes = []
            for prereq in prerequisites:
                node = await self.explore_async(prereq, depth + 1, verbose)
                prereq_nodes.append(node)

        return KnowledgeNode(
            concept=concept,
            depth=depth,
            is_foundation=False,
            prerequisites=prereq_nodes,
        )

    async def _explore_parallel(
        self,
        concepts: List[str],
        depth: int,
        verbose: bool,
    ) -> List['KnowledgeNode']:
        """Explore multiple concepts in parallel."""
        tasks = [
            self.explore_async(concept, depth, verbose)
            for concept in concepts
        ]
        return await asyncio.gather(*tasks)

    async def _is_foundation(self, concept: str) -> bool:
        """Check if a concept is foundational."""
        system_prompt = """You are an expert educator analyzing whether a concept is foundational.

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

        user_prompt = f'Is "{concept}" a foundational concept?'

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=50,
            temperature=0.3,
        )
        self._api_calls += 1

        response_text = self.client.get_text_content(response)
        return response_text.strip().lower().startswith('yes')

    async def _get_prerequisites(
        self,
        concept: str,
        verbose: bool = True,
    ) -> List[str]:
        """Get prerequisites for a concept."""
        # Check cache
        cached = self.cache.get(concept)
        if cached is not None:
            if verbose:
                print(f"  -> Using cache for {concept}")
            return cached

        system_prompt = """You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding (not just helpful)
2. Order from most to least important
3. Assume high school education as baseline
4. Focus on concepts that enable understanding, not historical context
5. Be specific - prefer "special relativity" over "relativity"
6. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names, nothing else."""

        user_prompt = f'''To understand "{concept}", what are the 3-5 ESSENTIAL prerequisite concepts?

Return format: ["concept1", "concept2", "concept3"]'''

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=1000,
        )
        self._api_calls += 1

        response_text = self.client.get_text_content(response)
        prerequisites = self._parse_prerequisites(response_text)

        # Cache result
        self.cache.set(concept, prerequisites)

        return prerequisites

    def _parse_prerequisites(self, response_text: str) -> List[str]:
        """Parse prerequisites from response text."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try code block extraction
            if "```" in response_text:
                sections = response_text.split("```")
                for section in sections[1::2]:
                    if section.startswith("json"):
                        section = section[4:]
                    try:
                        return json.loads(section.strip())
                    except:
                        continue
            else:
                # Try regex extraction
                match = re.search(r"\[.*?\]", response_text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except:
                        pass

            # Last resort: extract quoted strings
            matches = re.findall(r'"([^"]+)"', response_text)
            if matches:
                return matches[:5]

            raise ValueError(f"Could not parse prerequisites from: {response_text}")

    def explore(
        self,
        concept: str,
        depth: int = 0,
        verbose: bool = True,
    ) -> 'KnowledgeNode':
        """Synchronous wrapper for explore_async."""
        return asyncio.run(self.explore_async(concept, depth, verbose))

    @property
    def api_calls_made(self) -> int:
        return self._api_calls


# =============================================================================
# Legacy Compatibility
# =============================================================================


# Alias for backward compatibility
KimiPrerequisiteExplorer = PrerequisiteExplorer
