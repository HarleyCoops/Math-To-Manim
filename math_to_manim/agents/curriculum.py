"""Curriculum planning stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import CurriculumModule, CurriculumPlan, CurriculumStep, KnowledgeGraph


class CurriculumAgent(StageAgent[KnowledgeGraph, CurriculumPlan]):
    name = "curriculum"

    def run(self, graph: KnowledgeGraph) -> CurriculumPlan:
        order = graph.topological_node_ids()
        labels = {node.id: node.label for node in graph.nodes}
        steps = [
            CurriculumStep(
                id=f"step-{index}",
                title=labels[node_id].title(),
                objective=f"Make {labels[node_id]} visually concrete.",
                concept_ids=[node_id],
                estimated_minutes=1,
            )
            for index, node_id in enumerate(order, start=1)
        ]
        target_title = labels.get(graph.root_node_id or "", "Math Animation").title()
        return CurriculumPlan(
            title=target_title,
            modules=[
                CurriculumModule(
                    id="module-1",
                    title=f"Foundations to {target_title}",
                    summary="A dependency-first path from foundations to the requested concept.",
                    steps=steps,
                )
            ],
            learning_objectives=[
                "establish prerequisite intuition",
                "introduce the target visual metaphor",
                "connect the metaphor to formal notation",
                "close with a concise takeaway",
            ],
            estimated_total_minutes=max(1, len(steps)),
            metadata={
                "scene_count": max(3, min(6, len(steps))),
                "misconception_warnings": [
                "do not imply a visual approximation is the formal proof",
                "avoid hiding prerequisite assumptions",
                ],
                "prerequisite_compression_strategy": "Compress foundations into quick visual beats unless the prompt requests a full lesson.",
            },
        )
