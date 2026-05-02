"""Curriculum planning stage."""

from __future__ import annotations

import json

from math_to_manim.agents.base import StageAgent, mark_sdk_metadata, run_structured_sdk_agent
from math_to_manim.schemas import CurriculumModule, CurriculumPlan, CurriculumStep, KnowledgeGraph


class CurriculumAgent(StageAgent[KnowledgeGraph, CurriculumPlan]):
    name = "curriculum"

    def run(self, graph: KnowledgeGraph) -> CurriculumPlan:
        if not self.config.deterministic:
            artifact = run_structured_sdk_agent(
                name="CurriculumAgent",
                instructions=(
                    "Convert a prerequisite graph into a short teachable sequence for a Manim video. "
                    "Order concepts foundation-first. Compress prerequisites when needed. "
                    "Create clear CurriculumStep objectives that can become visual scenes."
                ),
                prompt=json.dumps(graph.to_public_dict(), indent=2),
                model=self.config.model,
                output_type=CurriculumPlan,
            )
            if artifact is not None:
                return mark_sdk_metadata(artifact, agent_name=self.name, model=self.config.model)

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
