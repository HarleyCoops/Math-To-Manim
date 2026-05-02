"""Reverse prerequisite graph stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
import re

from math_to_manim.schemas import ConceptIntent, KnowledgeGraph, KnowledgeGraphEdge, KnowledgeGraphNode


class PrerequisiteGraphAgent(StageAgent[ConceptIntent, KnowledgeGraph]):
    name = "prerequisite_graph"

    def run(self, intent: ConceptIntent) -> KnowledgeGraph:
        root_name = normalize_concept_name(intent.primary_concept)
        root_id = concept_id(root_name)
        prerequisites = intent.prerequisites or _default_prerequisites(intent.primary_concept)
        nodes = [
            KnowledgeGraphNode(
                id=root_id,
                label=root_name,
                kind="concept",
                summary=(intent.learning_objectives[0] if intent.learning_objectives else None),
                tags=["target"],
                metadata={"confidence": 0.8},
            )
        ]
        edges: list[KnowledgeGraphEdge] = []
        for index, prereq in enumerate(prerequisites):
            label = normalize_concept_name(prereq)
            node_id = concept_id(label)
            nodes.append(
                KnowledgeGraphNode(
                    id=node_id,
                    label=label,
                    kind="concept",
                    summary=f"Prerequisite for understanding {root_name}.",
                    tags=["foundation" if index < 2 else "prerequisite"],
                    metadata={"confidence": 0.7},
                )
            )
            edges.append(KnowledgeGraphEdge(source=node_id, target=root_id, relationship="prerequisite"))
        return KnowledgeGraph(
            nodes=nodes,
            edges=edges,
            root_node_id=root_id,
            metadata={
                "depth": 1,
                "rationale": "Deterministic seed graph; replace with SDK graph expansion in production.",
                "confidence": 0.7,
                "source_agent": self.name,
                "version": "1.0",
            },
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


def normalize_concept_name(concept: str) -> str:
    return re.sub(r"\s+", " ", concept.strip().lower())


def concept_id(concept: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize_concept_name(concept)).strip("-")
    return slug or "concept"
