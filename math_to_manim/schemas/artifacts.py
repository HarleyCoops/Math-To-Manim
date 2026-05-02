from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, Iterable, List, Literal, Optional, Set, Tuple

from .base import ArtifactModel, Field, PYDANTIC_V2, model_validator, root_validator


GraphNodeKind = Literal[
    "concept",
    "skill",
    "definition",
    "theorem",
    "example",
    "exercise",
    "visual",
]
GraphRelationship = Literal[
    "prerequisite",
    "depends_on",
    "introduces",
    "extends",
    "example_of",
    "visualizes",
    "assesses",
    "supports",
    "contrasts",
    "next",
]
IssueSeverity = Literal["info", "warning", "error"]
ValidationStatus = Literal["passed", "warning", "failed", "skipped"]
RenderStatus = Literal["queued", "running", "succeeded", "failed"]

DEPENDENCY_RELATIONSHIPS: Tuple[str, ...] = ("prerequisite", "depends_on")


class UserRequest(ArtifactModel):
    request_id: Optional[str] = None
    prompt: str = Field(..., min_length=1)
    topic: Optional[str] = None
    target_audience: Optional[str] = None
    objectives: List[str] = Field(default_factory=list)
    duration_seconds: Optional[int] = Field(default=None, ge=1)
    style: Optional[str] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConceptIntent(ArtifactModel):
    primary_concept: str = Field(..., min_length=1)
    related_concepts: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphNode(ArtifactModel):
    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    kind: GraphNodeKind = "concept"
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(ArtifactModel):
    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    relationship: GraphRelationship
    label: Optional[str] = None
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


GraphNode = KnowledgeGraphNode
GraphEdge = KnowledgeGraphEdge


def _validate_graph_integrity(
    nodes: List[KnowledgeGraphNode],
    edges: List[KnowledgeGraphEdge],
    root_node_id: Optional[str],
) -> None:
    node_ids = [node.id for node in nodes]
    duplicate_node_ids = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    if duplicate_node_ids:
        raise ValueError(f"duplicate node ids: {', '.join(duplicate_node_ids)}")

    known_ids = set(node_ids)
    if root_node_id is not None and root_node_id not in known_ids:
        raise ValueError(f"root_node_id references unknown node id: {root_node_id}")

    dangling_edges = [
        f"{edge.source}->{edge.target}"
        for edge in edges
        if edge.source not in known_ids or edge.target not in known_ids
    ]
    if dangling_edges:
        raise ValueError(f"edges reference unknown node ids: {', '.join(dangling_edges)}")

    self_loops = [f"{edge.source}->{edge.target}" for edge in edges if edge.source == edge.target]
    if self_loops:
        raise ValueError(f"self-loop edges are not allowed: {', '.join(self_loops)}")

    edge_keys = [(edge.source, edge.target, edge.relationship) for edge in edges]
    duplicate_edges = sorted({edge_key for edge_key in edge_keys if edge_keys.count(edge_key) > 1})
    if duplicate_edges:
        formatted = ", ".join(f"{source}->{target}:{relationship}" for source, target, relationship in duplicate_edges)
        raise ValueError(f"duplicate edges: {formatted}")


class KnowledgeGraph(ArtifactModel):
    nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    edges: List[KnowledgeGraphEdge] = Field(default_factory=list)
    root_node_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    if PYDANTIC_V2:

        @model_validator(mode="after")
        def _validate_graph(self) -> "KnowledgeGraph":
            _validate_graph_integrity(self.nodes, self.edges, self.root_node_id)
            return self

    else:

        @root_validator(skip_on_failure=True)
        def _validate_graph(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            _validate_graph_integrity(
                values.get("nodes") or [],
                values.get("edges") or [],
                values.get("root_node_id"),
            )
            return values

    @property
    def node_ids(self) -> Set[str]:
        return {node.id for node in self.nodes}

    def get_node(self, node_id: str) -> Optional[KnowledgeGraphNode]:
        return next((node for node in self.nodes if node.id == node_id), None)

    def require_node(self, node_id: str) -> KnowledgeGraphNode:
        node = self.get_node(node_id)
        if node is None:
            raise KeyError(f"unknown node id: {node_id}")
        return node

    def edges_from(
        self,
        node_id: str,
        relationship: Optional[str] = None,
    ) -> List[KnowledgeGraphEdge]:
        self.require_node(node_id)
        return [
            edge
            for edge in self.edges
            if edge.source == node_id and (relationship is None or edge.relationship == relationship)
        ]

    def edges_to(
        self,
        node_id: str,
        relationship: Optional[str] = None,
    ) -> List[KnowledgeGraphEdge]:
        self.require_node(node_id)
        return [
            edge
            for edge in self.edges
            if edge.target == node_id and (relationship is None or edge.relationship == relationship)
        ]

    def adjacent_node_ids(
        self,
        node_id: str,
        relationship: Optional[str] = None,
    ) -> Set[str]:
        outgoing = {edge.target for edge in self.edges_from(node_id, relationship)}
        incoming = {edge.source for edge in self.edges_to(node_id, relationship)}
        return outgoing | incoming

    def validate_references(self) -> "KnowledgeGraph":
        _validate_graph_integrity(self.nodes, self.edges, self.root_node_id)
        return self

    def topological_node_ids(
        self,
        relationships: Optional[Iterable[str]] = DEPENDENCY_RELATIONSHIPS,
    ) -> List[str]:
        selected_relationships = None if relationships is None else set(relationships)
        adjacency: Dict[str, List[str]] = {node.id: [] for node in self.nodes}
        indegree: Dict[str, int] = {node.id: 0 for node in self.nodes}

        for edge in self.edges:
            if selected_relationships is not None and edge.relationship not in selected_relationships:
                continue
            adjacency[edge.source].append(edge.target)
            indegree[edge.target] += 1

        ordered_ids = [node.id for node in self.nodes]
        queue: Deque[str] = deque(node_id for node_id in ordered_ids if indegree[node_id] == 0)
        result: List[str] = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            for target_id in adjacency[node_id]:
                indegree[target_id] -= 1
                if indegree[target_id] == 0:
                    queue.append(target_id)

        if len(result) != len(self.nodes):
            relationship_label = "all" if selected_relationships is None else ", ".join(sorted(selected_relationships))
            raise ValueError(f"knowledge graph contains a cycle for relationships: {relationship_label}")

        return result

    def has_cycle(
        self,
        relationships: Optional[Iterable[str]] = DEPENDENCY_RELATIONSHIPS,
    ) -> bool:
        try:
            self.topological_node_ids(relationships=relationships)
        except ValueError:
            return True
        return False


class CurriculumStep(ArtifactModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    objective: str = Field(..., min_length=1)
    concept_ids: List[str] = Field(default_factory=list)
    estimated_minutes: int = Field(default=5, ge=1)
    assessment_prompt: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CurriculumModule(ArtifactModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    summary: Optional[str] = None
    steps: List[CurriculumStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CurriculumPlan(ArtifactModel):
    title: str = Field(..., min_length=1)
    modules: List[CurriculumModule] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    estimated_total_minutes: Optional[int] = Field(default=None, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Equation(ArtifactModel):
    latex: str = Field(..., min_length=1)
    description: Optional[str] = None
    variables: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MathPacket(ArtifactModel):
    concept_id: Optional[str] = None
    definitions: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    key_equations: List[Equation] = Field(default_factory=list)
    worked_examples: List[str] = Field(default_factory=list)
    common_errors: List[str] = Field(default_factory=list)
    source_notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StoryboardScene(ArtifactModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    narration: Optional[str] = None
    visual_actions: List[str] = Field(default_factory=list)
    concept_ids: List[str] = Field(default_factory=list)
    duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    camera: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VisualStoryboard(ArtifactModel):
    title: str = Field(..., min_length=1)
    scenes: List[StoryboardScene] = Field(default_factory=list)
    target_duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ManimObjectSpec(ArtifactModel):
    id: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ManimAnimationSpec(ArtifactModel):
    action: str = Field(..., min_length=1)
    target: Optional[str] = None
    args: Dict[str, Any] = Field(default_factory=dict)
    start_time: Optional[float] = Field(default=None, ge=0.0)
    duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ManimSceneSpec(ArtifactModel):
    scene_name: str = Field(..., min_length=1)
    storyboard_scene_id: Optional[str] = None
    manim_version: Optional[str] = None
    imports: List[str] = Field(default_factory=list)
    objects: List[ManimObjectSpec] = Field(default_factory=list)
    animations: List[ManimAnimationSpec] = Field(default_factory=list)
    camera: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    code_requirements: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GeneratedCode(ArtifactModel):
    scene_name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    language: Literal["python"] = "python"
    dependencies: List[str] = Field(default_factory=list)
    manim_version: Optional[str] = None
    source_spec_id: Optional[str] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationIssue(ArtifactModel):
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    severity: IssueSeverity = "error"
    artifact: Optional[str] = None
    path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _validate_report_status(status: str, issues: List[ValidationIssue]) -> None:
    has_error = any(issue.severity == "error" for issue in issues)
    if status == "passed" and has_error:
        raise ValueError("passed validation reports cannot contain error issues")


class ValidationReport(ArtifactModel):
    status: ValidationStatus
    issues: List[ValidationIssue] = Field(default_factory=list)
    checked_artifacts: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    if PYDANTIC_V2:

        @model_validator(mode="after")
        def _validate_status(self) -> "ValidationReport":
            _validate_report_status(self.status, self.issues)
            return self

    else:

        @root_validator(skip_on_failure=True)
        def _validate_status(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            _validate_report_status(values.get("status"), values.get("issues") or [])
            return values

    @property
    def is_successful(self) -> bool:
        return self.status in {"passed", "warning"} and not any(issue.severity == "error" for issue in self.issues)


class RenderResult(ArtifactModel):
    status: RenderStatus
    scene_name: Optional[str] = None
    output_path: Optional[str] = None
    preview_path: Optional[str] = None
    command: List[str] = Field(default_factory=list)
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    validation_report: Optional[ValidationReport] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoReviewReport(ArtifactModel):
    approved: bool = False
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    observations: List[str] = Field(default_factory=list)
    issues: List[ValidationIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RepairPatch(ArtifactModel):
    target_artifact: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    unified_diff: Optional[str] = None
    replacement_code: Optional[str] = None
    issue_codes: List[str] = Field(default_factory=list)
    validation_expectations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnimationPackage(ArtifactModel):
    package_id: Optional[str] = None
    request: UserRequest
    intent: Optional[ConceptIntent] = None
    knowledge_graph: Optional[KnowledgeGraph] = None
    curriculum_plan: Optional[CurriculumPlan] = None
    math_packet: Optional[MathPacket] = None
    storyboard: Optional[VisualStoryboard] = None
    scene_specs: List[ManimSceneSpec] = Field(default_factory=list)
    generated_code: List[GeneratedCode] = Field(default_factory=list)
    validation_report: Optional[ValidationReport] = None
    render_result: Optional[RenderResult] = None
    video_review_report: Optional[VideoReviewReport] = None
    repair_patches: List[RepairPatch] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
