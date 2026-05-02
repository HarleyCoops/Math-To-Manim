"""Reverse prerequisite graph stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import ConceptIntent, KnowledgeEdge, KnowledgeGraph, KnowledgeNode
from math_to_manim.tools.graph_tools import concept_id, normalize_concept_name


class PrerequisiteGraphAgent(StageAgent[ConceptIntent, KnowledgeGraph]):
    name = "prerequisite_graph"

    def run(self, intent: ConceptIntent) -> KnowledgeGraph:
        root_name = normalize_concept_name(intent.core_concept)
        root_id = concept_id(root_name)
        prerequisites = _default_prerequisites(intent.core_concept)
        nodes = [
            KnowledgeNode(
                id=root_id,
                label=root_name,
                kind="target",
                summary=intent.learning_goal,
                confidence=0.8,
            )
        ]
        edges: list[KnowledgeEdge] = []
        for index, prereq in enumerate(prerequisites):
            label = normalize_concept_name(prereq)
            node_id = concept_id(label)
            nodes.append(
                KnowledgeNode(
                    id=node_id,
                    label=label,
                    kind="foundation" if index < 2 else "prerequisite",
                    summary=f"Prerequisite for understanding {root_name}.",
                    confidence=0.7,
                )
            )
            edges.append(KnowledgeEdge(source=node_id, target=root_id, relation="requires"))
        return KnowledgeGraph(
            root_node_id=root_id,
            nodes=nodes,
            edges=edges,
            foundation_nodes=[node.id for node in nodes if node.kind == "foundation"],
            depth=1,
            rationale="Deterministic seed graph; replace with SDK graph expansion in production.",
            confidence=0.7,
            source_agent=self.name,
            version="1.0",
        )


def _default_prerequisites(core: str) -> list[str]:
    text = core.lower()
    if "derivative" in text or "slope" in text:
        return ["functions and graphs", "slope of a line", "secant lines", "limits"]
    if "pythagorean" in text:
        return ["right triangles", "area of squares", "congruence", "similarity"]
    if "fourier" in text:
        return ["periodic motion", "sine and cosine", "vectors in the plane", "superposition"]
    if "lorenz" in text:
        return ["differential equations", "phase space", "sensitive dependence", "trajectories"]
    return ["basic notation", "visual model", "core definition", "worked example"]
