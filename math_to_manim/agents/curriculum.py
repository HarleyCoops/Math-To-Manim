"""Curriculum planning stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import CurriculumPlan, KnowledgeGraph
from math_to_manim.tools.graph_tools import topological_curriculum_order


class CurriculumAgent(StageAgent[KnowledgeGraph, CurriculumPlan]):
    name = "curriculum"

    def run(self, graph: KnowledgeGraph) -> CurriculumPlan:
        order = topological_curriculum_order(graph)
        labels = {node.id: node.label for node in graph.nodes}
        ordered_concepts = [labels[node_id] for node_id in order]
        return CurriculumPlan(
            ordered_concepts=ordered_concepts,
            scene_count=max(3, min(6, len(ordered_concepts))),
            teaching_arc=[
                "establish prerequisite intuition",
                "introduce the target visual metaphor",
                "connect the metaphor to formal notation",
                "close with a concise takeaway",
            ],
            misconception_warnings=[
                "do not imply a visual approximation is the formal proof",
                "avoid hiding prerequisite assumptions",
            ],
            prerequisite_compression_strategy="Compress foundations into quick visual beats unless the prompt requests a full lesson.",
            target_aha_moment=ordered_concepts[-1] if ordered_concepts else graph.root_node_id,
        )
