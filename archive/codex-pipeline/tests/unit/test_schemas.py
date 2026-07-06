import json

import pytest
from pydantic import ValidationError

from math_to_manim.schemas import (
    AnimationPackage,
    ConceptIntent,
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    ManimSceneSpec,
    UserRequest,
    ValidationIssue,
    ValidationReport,
)


def test_animation_package_serializes_and_round_trips() -> None:
    graph = KnowledgeGraph(
        nodes=[
            GraphNode(id="slope", label="Slope"),
            GraphNode(id="derivative", label="Derivative"),
        ],
        edges=[
            GraphEdge(source="slope", target="derivative", relationship="prerequisite"),
        ],
        root_node_id="slope",
    )
    package = AnimationPackage(
        package_id="pkg-001",
        request=UserRequest(prompt="Animate the derivative as the slope of a tangent line."),
        intent=ConceptIntent(
            primary_concept="derivative",
            prerequisites=["slope"],
            learning_objectives=["Connect secant slopes to tangent slope."],
        ),
        knowledge_graph=graph,
        scene_specs=[
            ManimSceneSpec(
                scene_name="DerivativeIntro",
                imports=["from manim import *"],
                code_requirements=["Show a secant line approaching a tangent line."],
            )
        ],
        validation_report=ValidationReport(status="warning"),
    )

    dumped = package.model_dump(mode="json")
    assert dumped["request"]["prompt"].startswith("Animate the derivative")
    assert dumped["knowledge_graph"]["edges"][0]["relationship"] == "prerequisite"

    rehydrated = AnimationPackage.model_validate(dumped)
    assert rehydrated.knowledge_graph is not None
    assert rehydrated.knowledge_graph.topological_node_ids() == ["slope", "derivative"]

    json_payload = package.model_dump_json()
    from_json = AnimationPackage.model_validate(json.loads(json_payload))
    assert from_json.scene_specs[0].scene_name == "DerivativeIntro"


def test_knowledge_graph_rejects_dangling_edges() -> None:
    with pytest.raises(ValidationError, match="unknown node ids"):
        KnowledgeGraph(
            nodes=[GraphNode(id="a", label="A")],
            edges=[GraphEdge(source="a", target="missing", relationship="prerequisite")],
        )


def test_knowledge_graph_rejects_duplicate_nodes_and_edges() -> None:
    with pytest.raises(ValidationError, match="duplicate node ids"):
        KnowledgeGraph(
            nodes=[
                GraphNode(id="a", label="A"),
                GraphNode(id="a", label="A again"),
            ],
        )

    with pytest.raises(ValidationError, match="duplicate edges"):
        KnowledgeGraph(
            nodes=[
                GraphNode(id="a", label="A"),
                GraphNode(id="b", label="B"),
            ],
            edges=[
                GraphEdge(source="a", target="b", relationship="prerequisite"),
                GraphEdge(source="a", target="b", relationship="prerequisite"),
            ],
        )


def test_knowledge_graph_cycle_helpers_detect_dependency_cycles() -> None:
    graph = KnowledgeGraph(
        nodes=[
            GraphNode(id="a", label="A"),
            GraphNode(id="b", label="B"),
        ],
        edges=[
            GraphEdge(source="a", target="b", relationship="prerequisite"),
            GraphEdge(source="b", target="a", relationship="depends_on"),
        ],
    )

    assert graph.has_cycle()
    with pytest.raises(ValueError, match="contains a cycle"):
        graph.topological_node_ids()


def test_validation_report_cannot_pass_with_error_issues() -> None:
    with pytest.raises(ValidationError, match="passed validation reports"):
        ValidationReport(
            status="passed",
            issues=[ValidationIssue(code="syntax", message="Syntax error", severity="error")],
        )
