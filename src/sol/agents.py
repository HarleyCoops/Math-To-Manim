"""Sol-native specialist contracts for the staged Codex CLI pipeline.

``AGENT_STAGES`` is the single source of stage structure: artifacts, the
dependency graph, default reasoning effort, and the charter. Everything that
needs stage order, record names, or the artifact contract derives it here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sol.layout import REVIEW_FILE, SCENE_FILE, STAGES_DIR, VALIDATION_FILE
from sol.models import RunRequest


@dataclass(frozen=True)
class AgentStage:
    name: str
    artifacts: tuple[str, ...]
    dependencies: tuple[str, ...]
    reasoning_effort: str
    charter: str


AGENT_STAGES = (
    AgentStage(
        name="intent",
        artifacts=("01_intent.json",),
        dependencies=(),
        reasoning_effort="medium",
        charter=(
            "Infer the learner, scope, mathematical promise, visual goal, hard "
            "constraints, and measurable definition of done. Resolve ambiguity "
            "without weakening explicit requirements."
        ),
    ),
    AgentStage(
        name="cartographer",
        artifacts=("02_knowledge_map.json",),
        dependencies=("intent",),
        reasoning_effort="medium",
        charter=(
            "Reverse-map the concepts and prerequisites required to understand "
            "the requested result. Record dependency edges, likely misconceptions, "
            "and which facts must be earned visually."
        ),
    ),
    AgentStage(
        name="curriculum",
        artifacts=("03_curriculum.json",),
        dependencies=("cartographer",),
        reasoning_effort="medium",
        charter=(
            "Turn the prerequisite graph into a forward teaching sequence. Each "
            "beat must name its learning job, prior dependency, visual evidence, "
            "notation budget, and transition."
        ),
    ),
    AgentStage(
        name="math-director",
        artifacts=("04_math_dossier.json",),
        dependencies=("intent",),
        reasoning_effort="high",
        charter=(
            "Build the checked mathematical dossier. Preserve hypotheses, proof "
            "direction, exact constants, derivations, assumptions, certificate "
            "boundaries, numerical checks, and honest limitations. Never invent "
            "a missing formula."
        ),
    ),
    AgentStage(
        name="cinematographer",
        artifacts=("05_shot_list.json",),
        dependencies=("curriculum", "math-director"),
        reasoning_effort="high",
        charter=(
            "Design the visual argument and camera grammar. Geometry and motion "
            "must carry meaning; headline before notation; perspective changes, "
            "pull-backs, whitespace, timing, palette, and readability must be "
            "specified shot by shot."
        ),
    ),
    AgentStage(
        name="scene-composer",
        artifacts=("06_scene_spec.json", SCENE_FILE),
        dependencies=("cinematographer",),
        reasoning_effort="high",
        charter=(
            "Compile the validated dossier and shot list into one self-contained "
            "Manim Community Edition scene. Write an implementable scene spec and "
            "safe Python source. Compile the source, but do not render it; the "
            "wrapper owns rendering and evidence extraction."
        ),
    ),
)

STAGE_NAMES = tuple(stage.name for stage in AGENT_STAGES)

# Every file a complete run bundle must contain: the stage artifacts plus the
# two wrapper-owned verdict files.
ARTIFACT_NAMES = (
    *(artifact for stage in AGENT_STAGES for artifact in stage.artifacts),
    VALIDATION_FILE,
    REVIEW_FILE,
)


def stage_by_name(name: str) -> AgentStage:
    for stage in AGENT_STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown Sol stage: {name}")


def stage_index(stage: AgentStage) -> int:
    """1-based position in the table; fixes stage record and trace names."""
    return AGENT_STAGES.index(stage) + 1


def stage_record_path(stage: AgentStage) -> str:
    return f"{STAGES_DIR}/{stage_index(stage):02d}-{stage.name}.json"


def stage_effort(stage: AgentStage, request: RunRequest) -> str:
    return request.reasoning_effort or stage.reasoning_effort


def upstream_artifacts(stage: AgentStage) -> tuple[str, ...]:
    """Artifacts of the direct dependencies, in table order."""
    return tuple(
        artifact
        for dependency in stage.dependencies
        for artifact in stage_by_name(dependency).artifacts
    )


def downstream_of(name: str) -> set[str]:
    """``name`` and every stage that transitively depends on it."""
    stage_by_name(name)
    selected = {name}
    changed = True
    while changed:
        changed = False
        for stage in AGENT_STAGES:
            if stage.name not in selected and set(stage.dependencies) & selected:
                selected.add(stage.name)
                changed = True
    return selected


def build_stage_prompt(
    stage: AgentStage,
    request: RunRequest,
    *,
    run_dir: Path,
    feedback: str | None = None,
) -> str:
    upstream_text = "\n".join(f"- {name}" for name in upstream_artifacts(stage)) or "- none"
    outputs = "\n".join(f"- {name}" for name in stage.artifacts)
    repair = (
        f"\n<repair_evidence>\n{feedback}\n</repair_evidence>\n"
        if feedback
        else ""
    )
    return f"""You are the {stage.name} specialist in the staged GPT-6 Astra
Math-To-Manim film pipeline.

<role_contract>
{stage.charter}
</role_contract>

<workspace>
Run directory: {run_dir}
You may read the original request and these validated upstream artifacts:
{upstream_text}

Write exactly these artifacts in the run directory:
{outputs}
Do not write any other file. Do not modify repository source or git state.
</workspace>

<request>
{request.prompt}
</request>
{repair}

Every JSON artifact must be a non-empty UTF-8 JSON object. Preserve complete
LaTeX strings. Finish with only the structured stage summary required by the
supplied output schema. Report only artifacts you actually wrote and checked.
"""
