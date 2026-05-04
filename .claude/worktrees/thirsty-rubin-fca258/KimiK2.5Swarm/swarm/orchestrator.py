"""
Enrichment Orchestrator - Parallel swarm orchestration for knowledge trees.

Provides:
- Task decomposition and parallel agent execution
- Depth-level parallel enrichment
- Progress tracking and metrics
- Result aggregation
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import KnowledgeNode, EnrichmentResult, Narrative
    from kimi_client import KimiClient

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration and Result Dataclasses
# =============================================================================


@dataclass
class EnrichmentSwarmConfig:
    """Configuration for enrichment swarm execution."""
    max_parallel_nodes: int = 10
    max_agents: int = 50
    enable_verification: bool = False
    enable_parallel_math: bool = True
    enable_parallel_visual: bool = True


@dataclass
class EnrichmentSwarmResult:
    """Result from swarm enrichment execution."""
    enriched_tree: 'KnowledgeNode'
    narrative: 'Narrative'
    total_agents: int = 0
    total_tool_calls: int = 0
    execution_time_seconds: float = 0.0
    nodes_enriched: int = 0

    def to_enrichment_result(self) -> 'EnrichmentResult':
        """Convert to standard EnrichmentResult."""
        from models import EnrichmentResult as ER
        return ER(
            enriched_tree=self.enriched_tree,
            narrative=self.narrative,
            total_nodes_enriched=self.nodes_enriched,
            total_tool_calls=self.total_tool_calls,
            execution_time_seconds=self.execution_time_seconds,
        )


# =============================================================================
# Enrichment Orchestrator
# =============================================================================


class EnrichmentOrchestrator:
    """
    Orchestrate parallel enrichment of knowledge trees.

    This orchestrator coordinates multiple enrichment agents to
    process knowledge trees efficiently using parallel execution
    at each depth level.

    Example:
        orchestrator = EnrichmentOrchestrator()
        result = await orchestrator.enrich_tree(root_node)
        print(f"Enriched {result.nodes_enriched} nodes")
    """

    def __init__(
        self,
        client: Optional['KimiClient'] = None,
        config: Optional[EnrichmentSwarmConfig] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            client: KimiClient instance (created if not provided)
            config: Swarm configuration
        """
        self.config = config or EnrichmentSwarmConfig()
        self._client = client
        self._total_tool_calls = 0
        self._agents_used = 0

    @property
    def client(self) -> 'KimiClient':
        """Get or create Kimi client."""
        if self._client is None:
            from kimi_client import get_kimi_client
            self._client = get_kimi_client()
        return self._client

    async def enrich_tree(
        self,
        root: 'KnowledgeNode',
        on_progress: Optional[Callable[[int, int, str], None]] = None,
    ) -> EnrichmentSwarmResult:
        """
        Enrich an entire knowledge tree with parallel processing.

        Args:
            root: The root KnowledgeNode
            on_progress: Callback(completed, total, stage) for progress

        Returns:
            EnrichmentSwarmResult with metrics
        """
        start_time = time.time()

        # Import agents
        from agents.enrichment_agents import (
            MathematicalEnricher,
            VisualDesigner,
            NarrativeComposer,
        )

        # Create agents
        math_enricher = MathematicalEnricher(client=self.client)
        visual_designer = VisualDesigner(client=self.client)
        narrative_composer = NarrativeComposer(client=self.client)

        # Group nodes by depth level
        depth_levels = root.group_by_depth()
        total_nodes = root.count_nodes()

        # Track progress
        enriched_count = 0

        # Stage 1: Mathematical enrichment (by depth level, deepest first)
        logger.info("Stage 1: Mathematical enrichment")
        for depth in sorted(depth_levels.keys(), reverse=True):
            nodes = depth_levels[depth]

            if self.config.enable_parallel_math:
                # Parallel enrichment at this depth
                tasks = [math_enricher.enrich_node(node) for node in nodes]
                await asyncio.gather(*tasks)
            else:
                # Sequential enrichment
                for node in nodes:
                    await math_enricher.enrich_node(node)

            enriched_count += len(nodes)
            if on_progress:
                on_progress(enriched_count, total_nodes * 2, "mathematical")

        # Stage 2: Visual design (by depth level, root first)
        logger.info("Stage 2: Visual design")
        for depth in sorted(depth_levels.keys()):
            nodes = depth_levels[depth]

            if self.config.enable_parallel_visual:
                # Parallel design at this depth
                tasks = [visual_designer.design_node(node) for node in nodes]
                await asyncio.gather(*tasks)
            else:
                # Sequential design
                for node in nodes:
                    await visual_designer.design_node(node)

            enriched_count += len(nodes)
            if on_progress:
                on_progress(enriched_count, total_nodes * 2, "visual")

        # Stage 3: Narrative composition
        logger.info("Stage 3: Narrative composition")
        narrative = await narrative_composer.compose(root)

        execution_time = time.time() - start_time

        # Aggregate metrics
        total_tool_calls = (
            math_enricher.tool_calls_made +
            visual_designer.tool_calls_made +
            narrative_composer.tool_calls_made
        )

        return EnrichmentSwarmResult(
            enriched_tree=root,
            narrative=narrative,
            total_agents=3,  # math, visual, narrative
            total_tool_calls=total_tool_calls,
            execution_time_seconds=execution_time,
            nodes_enriched=total_nodes,
        )

    async def enrich_tree_sequential(
        self,
        root: 'KnowledgeNode',
    ) -> EnrichmentSwarmResult:
        """
        Enrich tree sequentially (for comparison/debugging).

        Uses the traditional recursive approach without parallelization.
        """
        start_time = time.time()

        from agents.enrichment_agents import (
            MathematicalEnricher,
            VisualDesigner,
            NarrativeComposer,
        )

        math_enricher = MathematicalEnricher(client=self.client)
        visual_designer = VisualDesigner(client=self.client)
        narrative_composer = NarrativeComposer(client=self.client)

        # Sequential recursive enrichment
        await math_enricher.enrich_tree(root)
        await visual_designer.design_tree(root)
        narrative = await narrative_composer.compose(root)

        execution_time = time.time() - start_time

        total_tool_calls = (
            math_enricher.tool_calls_made +
            visual_designer.tool_calls_made +
            narrative_composer.tool_calls_made
        )

        return EnrichmentSwarmResult(
            enriched_tree=root,
            narrative=narrative,
            total_agents=3,
            total_tool_calls=total_tool_calls,
            execution_time_seconds=execution_time,
            nodes_enriched=root.count_nodes(),
        )


# =============================================================================
# Legacy Compatibility Pipeline
# =============================================================================


class KimiEnrichmentPipeline:
    """
    Legacy-compatible enrichment pipeline.

    Provides the same interface as the original KimiEnrichmentPipeline
    while using the new swarm orchestrator internally.
    """

    def __init__(self, client: Optional['KimiClient'] = None):
        """Initialize pipeline with optional client."""
        self.orchestrator = EnrichmentOrchestrator(client=client)

    async def run_async(self, root: 'KnowledgeNode') -> 'EnrichmentResult':
        """
        Run the enrichment pipeline asynchronously.

        Args:
            root: The root KnowledgeNode

        Returns:
            EnrichmentResult with enriched tree and narrative
        """
        result = await self.orchestrator.enrich_tree(root)
        return result.to_enrichment_result()

    def run(self, root: 'KnowledgeNode') -> 'EnrichmentResult':
        """Synchronous wrapper for run_async."""
        return asyncio.run(self.run_async(root))
