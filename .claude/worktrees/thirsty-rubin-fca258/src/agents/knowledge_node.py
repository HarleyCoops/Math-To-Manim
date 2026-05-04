"""Shared KnowledgeNode data structure used by all agents and pipelines.

This is the canonical location for KnowledgeNode. All agents should import
from here rather than defining their own copy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeNode:
    """Represents a concept in the knowledge tree.

    The knowledge tree is built by the PrerequisiteExplorer, which recursively
    asks "What must I understand BEFORE this concept?" until reaching foundation
    concepts (high school level).

    Enrichment agents (MathematicalEnricher, VisualDesigner, NarrativeComposer)
    add content to the optional fields as the tree passes through the pipeline.
    """

    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List[KnowledgeNode] = field(default_factory=list)

    # Added by enrichment agents
    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "concept": self.concept,
            "depth": self.depth,
            "is_foundation": self.is_foundation,
            "prerequisites": [p.to_dict() for p in self.prerequisites],
            "equations": self.equations,
            "definitions": self.definitions,
            "visual_spec": self.visual_spec,
            "narrative": self.narrative,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeNode:
        """Reconstruct a KnowledgeNode from a dictionary."""
        return cls(
            concept=data["concept"],
            depth=data["depth"],
            is_foundation=data["is_foundation"],
            prerequisites=[
                cls.from_dict(p) for p in data.get("prerequisites", [])
            ],
            equations=data.get("equations"),
            definitions=data.get("definitions"),
            visual_spec=data.get("visual_spec"),
            narrative=data.get("narrative"),
        )

    def print_tree(self, indent: int = 0) -> None:
        """Pretty print the knowledge tree."""
        prefix = "  " * indent
        tag = " [FOUNDATION]" if self.is_foundation else ""
        print(f"{prefix}+- {self.concept} (depth {self.depth}){tag}")
        for prereq in self.prerequisites:
            prereq.print_tree(indent + 1)

    def node_count(self) -> int:
        """Return total number of nodes in this subtree."""
        return 1 + sum(p.node_count() for p in self.prerequisites)

    def flatten(self) -> List[KnowledgeNode]:
        """Return all nodes in depth-first order."""
        nodes = [self]
        for prereq in self.prerequisites:
            nodes.extend(prereq.flatten())
        return nodes
