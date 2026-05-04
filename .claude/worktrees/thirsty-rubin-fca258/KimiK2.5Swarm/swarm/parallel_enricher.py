"""
Parallel Tree Enricher - Depth-level parallel enrichment for knowledge trees.

Provides optimized parallel processing of knowledge trees by:
- Processing all nodes at the same depth level in parallel
- Maintaining parent-child context for visual continuity
- Supporting semaphore-controlled concurrency
- Tracking execution metrics
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import KnowledgeNode
    from agents.enrichment_agents import (
        MathematicalEnricher,
        VisualDesigner,
        MathematicalContent,
        VisualSpec,
    )

logger = logging.getLogger(__name__)


# =============================================================================
# Execution Result
# =============================================================================


@dataclass
class ParallelEnrichmentResult:
    """Result from parallel enrichment execution."""
    nodes_processed: int = 0
    tool_calls: int = 0
    execution_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


# =============================================================================
# Parallel Tree Enricher
# =============================================================================


class ParallelTreeEnricher:
    """
    Enrich knowledge trees with parallel processing by depth level.

    This enricher processes all nodes at the same depth in parallel,
    which can significantly speed up enrichment for wide trees.

    Example:
        enricher = ParallelTreeEnricher(max_concurrent=20)
        result = await enricher.enrich_tree(root)
        print(f"Processed {result.nodes_processed} nodes in {result.execution_time_seconds:.2f}s")
    """

    def __init__(
        self,
        max_concurrent: int = 10,
        client: Optional[Any] = None,
    ):
        """
        Initialize the parallel enricher.

        Args:
            max_concurrent: Maximum concurrent enrichments
            client: KimiClient instance
        """
        self.max_concurrent = max_concurrent
        self._client = client
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._tool_calls = 0
        self._errors: List[str] = []

    @property
    def client(self):
        """Get or create Kimi client."""
        if self._client is None:
            from kimi_client import get_kimi_client
            self._client = get_kimi_client()
        return self._client

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for current event loop."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    async def enrich_math_level(
        self,
        nodes: List['KnowledgeNode'],
        enricher: 'MathematicalEnricher',
    ) -> ParallelEnrichmentResult:
        """
        Enrich all nodes at a depth level with mathematical content.

        Args:
            nodes: List of nodes at the same depth
            enricher: MathematicalEnricher instance

        Returns:
            ParallelEnrichmentResult with metrics
        """
        start_time = time.time()
        semaphore = self._get_semaphore()

        async def enrich_with_semaphore(node: 'KnowledgeNode'):
            async with semaphore:
                try:
                    await enricher.enrich_node(node)
                except Exception as e:
                    self._errors.append(f"Math enrichment failed for {node.concept}: {e}")
                    logger.error(f"Math enrichment failed for {node.concept}: {e}")

        tasks = [enrich_with_semaphore(node) for node in nodes]
        await asyncio.gather(*tasks)

        return ParallelEnrichmentResult(
            nodes_processed=len(nodes),
            tool_calls=enricher.tool_calls_made,
            execution_time_seconds=time.time() - start_time,
            errors=self._errors.copy(),
        )

    async def design_visual_level(
        self,
        nodes: List['KnowledgeNode'],
        designer: 'VisualDesigner',
        parent_specs: Optional[Dict[str, 'VisualSpec']] = None,
    ) -> ParallelEnrichmentResult:
        """
        Design visuals for all nodes at a depth level.

        Args:
            nodes: List of nodes at the same depth
            designer: VisualDesigner instance
            parent_specs: Mapping of concept -> parent VisualSpec

        Returns:
            ParallelEnrichmentResult with metrics
        """
        start_time = time.time()
        semaphore = self._get_semaphore()
        parent_specs = parent_specs or {}

        async def design_with_semaphore(node: 'KnowledgeNode'):
            async with semaphore:
                try:
                    parent_spec = parent_specs.get(node.concept)
                    await designer.design_node(node, parent_spec)
                except Exception as e:
                    self._errors.append(f"Visual design failed for {node.concept}: {e}")
                    logger.error(f"Visual design failed for {node.concept}: {e}")

        tasks = [design_with_semaphore(node) for node in nodes]
        await asyncio.gather(*tasks)

        return ParallelEnrichmentResult(
            nodes_processed=len(nodes),
            tool_calls=designer.tool_calls_made,
            execution_time_seconds=time.time() - start_time,
            errors=self._errors.copy(),
        )

    async def enrich_tree(
        self,
        root: 'KnowledgeNode',
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> ParallelEnrichmentResult:
        """
        Fully enrich a knowledge tree with parallel processing.

        Processes mathematical enrichment and visual design for all
        nodes using depth-level parallelism.

        Args:
            root: The root KnowledgeNode
            on_progress: Callback(completed, total) for progress

        Returns:
            ParallelEnrichmentResult with metrics
        """
        from agents.enrichment_agents import MathematicalEnricher, VisualDesigner

        start_time = time.time()

        # Create enrichers
        math_enricher = MathematicalEnricher(client=self.client)
        visual_designer = VisualDesigner(client=self.client)

        # Group nodes by depth
        depth_levels = root.group_by_depth()
        total_nodes = root.count_nodes()
        completed = 0

        # Phase 1: Mathematical enrichment (deepest first for dependencies)
        for depth in sorted(depth_levels.keys(), reverse=True):
            nodes = depth_levels[depth]
            await self.enrich_math_level(nodes, math_enricher)

            completed += len(nodes)
            if on_progress:
                on_progress(completed, total_nodes * 2)

        # Phase 2: Visual design (root first for parent context)
        parent_specs: Dict[str, 'VisualSpec'] = {}

        for depth in sorted(depth_levels.keys()):
            nodes = depth_levels[depth]
            await self.design_visual_level(nodes, visual_designer, parent_specs)

            # Update parent specs for next level
            for node in nodes:
                if node.visual_spec:
                    from agents.enrichment_agents import VisualSpec
                    parent_specs[node.concept] = VisualSpec.from_payload(
                        node.concept, node.visual_spec
                    )
                # Map children to this parent
                for prereq in node.prerequisites:
                    parent_specs[prereq.concept] = parent_specs.get(node.concept)

            completed += len(nodes)
            if on_progress:
                on_progress(completed, total_nodes * 2)

        total_tool_calls = math_enricher.tool_calls_made + visual_designer.tool_calls_made

        return ParallelEnrichmentResult(
            nodes_processed=total_nodes,
            tool_calls=total_tool_calls,
            execution_time_seconds=time.time() - start_time,
            errors=self._errors,
        )


# =============================================================================
# Utility Functions
# =============================================================================


def group_nodes_by_depth(root: 'KnowledgeNode') -> Dict[int, List['KnowledgeNode']]:
    """
    Group all nodes in a tree by their depth level.

    Args:
        root: The root KnowledgeNode

    Returns:
        Dictionary mapping depth -> list of nodes
    """
    return root.group_by_depth()


async def parallel_map(
    items: List[Any],
    func: Callable,
    max_concurrent: int = 10,
) -> List[Any]:
    """
    Apply an async function to items with controlled concurrency.

    Args:
        items: List of items to process
        func: Async function to apply to each item
        max_concurrent: Maximum concurrent executions

    Returns:
        List of results in the same order as items
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(item):
        async with semaphore:
            return await func(item)

    tasks = [process_with_semaphore(item) for item in items]
    return await asyncio.gather(*tasks)
