"""
KnowledgeNode dataclass for representing concepts in knowledge trees.

This module preserves backward compatibility with the original implementation
while adding new factory methods and utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeNode:
    """
    Represents a concept in the knowledge tree.

    This dataclass is the core data structure for the enrichment pipeline.
    It maintains backward compatibility with the original implementation.

    Attributes:
        concept: The name/title of the concept
        depth: Depth in the knowledge tree (0 = root)
        is_foundation: Whether this is a foundational concept (no prerequisites)
        prerequisites: List of prerequisite KnowledgeNode objects
        equations: LaTeX equations associated with this concept
        definitions: Dictionary mapping symbols to their definitions
        visual_spec: Visual specification for Manim rendering
        narrative: Generated narrative text for this concept
    """
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List['KnowledgeNode'] = field(default_factory=list)

    # Metadata from enrichment
    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of this node and its prerequisites
        """
        return {
            'concept': self.concept,
            'depth': self.depth,
            'is_foundation': self.is_foundation,
            'prerequisites': [p.to_dict() for p in self.prerequisites],
            'equations': self.equations,
            'definitions': self.definitions,
            'visual_spec': self.visual_spec,
            'narrative': self.narrative
        }

    def print_tree(self, indent: int = 0) -> None:
        """
        Pretty print the knowledge tree.

        Args:
            indent: Current indentation level
        """
        prefix = "  " * indent
        foundation_mark = " [FOUNDATION]" if self.is_foundation else ""
        print(f"{prefix}|- {self.concept} (depth {self.depth}){foundation_mark}")
        for prereq in self.prerequisites:
            prereq.print_tree(indent + 1)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeNode':
        """
        Create a KnowledgeNode from a dictionary.

        This factory method enables loading trees from JSON.

        Args:
            data: Dictionary with node data

        Returns:
            KnowledgeNode instance
        """
        return cls(
            concept=data["concept"],
            depth=data["depth"],
            is_foundation=data["is_foundation"],
            prerequisites=[cls.from_dict(p) for p in data.get("prerequisites", [])],
            equations=data.get("equations"),
            definitions=data.get("definitions"),
            visual_spec=data.get("visual_spec"),
            narrative=data.get("narrative"),
        )

    def count_nodes(self) -> int:
        """
        Count total nodes in this subtree.

        Returns:
            Total number of nodes including this one
        """
        return 1 + sum(prereq.count_nodes() for prereq in self.prerequisites)

    def get_max_depth(self) -> int:
        """
        Get the maximum depth in this subtree.

        Returns:
            Maximum depth value
        """
        if not self.prerequisites:
            return self.depth
        return max(prereq.get_max_depth() for prereq in self.prerequisites)

    def collect_all_concepts(self) -> List[str]:
        """
        Collect all concept names in the tree.

        Returns:
            List of all concept names in depth-first order
        """
        concepts = [self.concept]
        for prereq in self.prerequisites:
            concepts.extend(prereq.collect_all_concepts())
        return concepts

    def get_nodes_at_depth(self, target_depth: int) -> List['KnowledgeNode']:
        """
        Get all nodes at a specific depth level.

        Args:
            target_depth: The depth level to collect

        Returns:
            List of nodes at the specified depth
        """
        nodes = []
        if self.depth == target_depth:
            nodes.append(self)
        for prereq in self.prerequisites:
            nodes.extend(prereq.get_nodes_at_depth(target_depth))
        return nodes

    def group_by_depth(self) -> Dict[int, List['KnowledgeNode']]:
        """
        Group all nodes by their depth level.

        Returns:
            Dictionary mapping depth -> list of nodes
        """
        groups: Dict[int, List['KnowledgeNode']] = {}

        def collect(node: 'KnowledgeNode'):
            if node.depth not in groups:
                groups[node.depth] = []
            groups[node.depth].append(node)
            for prereq in node.prerequisites:
                collect(prereq)

        collect(self)
        return groups

    def is_enriched(self) -> bool:
        """
        Check if this node has been enriched with mathematical content.

        Returns:
            True if equations and definitions are present
        """
        return bool(self.equations) and bool(self.definitions)

    def has_visual_spec(self) -> bool:
        """
        Check if this node has visual specification.

        Returns:
            True if visual_spec is present and non-empty
        """
        return bool(self.visual_spec)
