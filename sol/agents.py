"""Sol-native specialist contracts for the staged Codex CLI pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sol.models import RunRequest


@dataclass(frozen=True)
class AgentStage:
    name: str
    artifacts: tuple[str, ...]
    dependencies: tuple[str, ...]
    reasoning_effort: str
    charter: str
    version: str = "1"


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
        artifacts=("06_scene_spec.json", "sol_scene.py"),
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


def stage_by_name(name: str) -> AgentStage:
    for stage in AGENT_STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown Sol stage: {name}")


def build_stage_prompt(stage: AgentStage, request: RunRequest, *, run_dir: Path) -> str:
    by_name = {item.name: item for item in AGENT_STAGES}
    upstream = [
        artifact
        for dependency in stage.dependencies
        for artifact in by_name[dependency].artifacts
    ]
    upstream_text = "\n".join(f"- {name}" for name in upstream) or "- none"
    outputs = "\n".join(f"- {name}" for name in stage.artifacts)
    return f"""You are the {stage.name} specialist in the staged GPT-5.6 Sol
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

Every JSON artifact must be a non-empty UTF-8 JSON object. Preserve complete
LaTeX strings. Finish with only the structured stage summary required by the
supplied output schema. Report only artifacts you actually wrote and checked.
"""
