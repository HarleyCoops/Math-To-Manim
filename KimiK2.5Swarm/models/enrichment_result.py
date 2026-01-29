"""
EnrichmentResult and Narrative dataclasses for pipeline outputs.

These dataclasses preserve backward compatibility while adding metrics
for tracking parallel execution performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .knowledge_node import KnowledgeNode


@dataclass
class Narrative:
    """
    Narrative composition for a knowledge tree.

    Contains the verbose prompt and metadata for Manim code generation.

    Attributes:
        target_concept: The main concept this narrative covers
        verbose_prompt: Full narrative text (2000+ words typically)
        concept_order: Topologically sorted concept list
        total_duration: Estimated total animation duration in seconds
        scene_count: Number of scenes described
    """
    target_concept: str
    verbose_prompt: str
    concept_order: List[str] = field(default_factory=list)
    total_duration: int = 0
    scene_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "target_concept": self.target_concept,
            "verbose_prompt": self.verbose_prompt,
            "concept_order": self.concept_order,
            "total_duration": self.total_duration,
            "scene_count": self.scene_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Narrative':
        """Create a Narrative from a dictionary."""
        return cls(
            target_concept=data.get("target_concept", ""),
            verbose_prompt=data.get("verbose_prompt", ""),
            concept_order=data.get("concept_order", []),
            total_duration=data.get("total_duration", 0),
            scene_count=data.get("scene_count", 0),
        )

    def word_count(self) -> int:
        """Get the word count of the verbose prompt."""
        return len(self.verbose_prompt.split())


@dataclass
class EnrichmentResult:
    """
    Result from the enrichment pipeline.

    This dataclass maintains backward compatibility with the original
    implementation while adding metrics for tracking execution performance.

    Attributes:
        enriched_tree: The knowledge tree with mathematical and visual enrichment
        narrative: The composed narrative for Manim generation
        total_nodes_enriched: Number of nodes that were enriched
        total_tool_calls: Number of tool calls made during enrichment
        execution_time_seconds: Total execution time
    """
    enriched_tree: 'KnowledgeNode'
    narrative: Narrative

    # New metrics for tracking performance
    total_nodes_enriched: int = 0
    total_tool_calls: int = 0
    execution_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "enriched_tree": self.enriched_tree.to_dict(),
            "narrative": self.narrative.to_dict(),
            "total_nodes_enriched": self.total_nodes_enriched,
            "total_tool_calls": self.total_tool_calls,
            "execution_time_seconds": self.execution_time_seconds,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichmentResult':
        """Create an EnrichmentResult from a dictionary."""
        from .knowledge_node import KnowledgeNode

        return cls(
            enriched_tree=KnowledgeNode.from_dict(data["enriched_tree"]),
            narrative=Narrative.from_dict(data["narrative"]),
            total_nodes_enriched=data.get("total_nodes_enriched", 0),
            total_tool_calls=data.get("total_tool_calls", 0),
            execution_time_seconds=data.get("execution_time_seconds", 0.0),
        )

    def summary(self) -> str:
        """Generate a human-readable summary of the enrichment result."""
        return (
            f"Enrichment Result for '{self.narrative.target_concept}':\n"
            f"  - Nodes enriched: {self.total_nodes_enriched}\n"
            f"  - Tool calls: {self.total_tool_calls}\n"
            f"  - Execution time: {self.execution_time_seconds:.2f}s\n"
            f"  - Narrative words: {self.narrative.word_count()}\n"
            f"  - Total duration: {self.narrative.total_duration}s\n"
            f"  - Scene count: {self.narrative.scene_count}"
        )
