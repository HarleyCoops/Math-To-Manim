"""MiMo 2.6 specialist stage contracts and tool-calling prompts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mimo.models import RunRequest
from mimo.tools import STAGE_TOOLS


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
            "Infer the learner, core claim, emotional arc, scope, duration, title "
            "options, and the single big zoom. Resolve ambiguity without weakening "
            "explicit requirements. Reverse-thinking lives downstream — you name "
            "the belief the film must install."
        ),
    ),
    AgentStage(
        name="cartographer",
        artifacts=("02_knowledge_map.json",),
        dependencies=("intent",),
        reasoning_effort="high",
        charter=(
            "Reverse-map prerequisites of the core claim as a knowledge DAG. "
            "Walk backward: for each node ask what must be understood BEFORE it. "
            "Mark foundation leaves a typical high-school graduate already owns. "
            "Record misconception corrections and which facts must be earned visually. "
            "This is reverse thinking made explicit — not a flat outline."
        ),
    ),
    AgentStage(
        name="curriculum",
        artifacts=("03_curriculum.json",),
        dependencies=("cartographer",),
        reasoning_effort="medium",
        charter=(
            "Turn the prerequisite DAG into a forward teaching sequence of beats. "
            "Each beat names its learning job, prior dependency, visual evidence, "
            "notation budget, and transition. Headline before notation."
        ),
    ),
    AgentStage(
        name="math-director",
        artifacts=("04_math_dossier.json",),
        dependencies=("intent",),
        reasoning_effort="high",
        charter=(
            "Build the checked mathematical dossier. Preserve hypotheses, exact "
            "statements, constants, numerical checks, and honest limitations. Never "
            "invent a missing formula. Use verify_geometry when claiming twist "
            "parity, frame orthonormality, or path properties."
        ),
    ),
    AgentStage(
        name="cinematographer",
        artifacts=("05_shot_list.json",),
        dependencies=("curriculum", "math-director"),
        reasoning_effort="high",
        charter=(
            "Design the visual argument and camera grammar in ordinary 3-space when "
            "the request demands it. Geometry and motion carry meaning. Protect the "
            "big zoom. Specify palette, camera moves (move_camera/set_camera_orientation "
            "only), whitespace, timing, readability shot by shot."
        ),
    ),
    AgentStage(
        name="scene-composer",
        artifacts=("06_scene_spec.json", "mimo_scene.py"),
        dependencies=("cinematographer",),
        reasoning_effort="max",
        charter=(
            "Compile the dossier and shot list into one self-contained Manim CE "
            "ThreeDScene. Use tools aggressively: verify_geometry on ribbon/frame "
            "claims, verify_scene on the source, write_artifact for both outputs. "
            "Compile mentally via verify_scene; the wrapper owns rendering."
        ),
    ),
)


def stage_by_name(name: str) -> AgentStage:
    for stage in AGENT_STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown MiMo stage: {name}")


def tools_for_stage(name: str) -> tuple[dict, ...]:
    return STAGE_TOOLS[name]


def build_stage_prompt(
    stage: AgentStage,
    request: RunRequest,
    *,
    run_dir: Path,
    feedback: str | None = None,
) -> str:
    by_name = {item.name: item for item in AGENT_STAGES}
    upstream = [
        artifact
        for dependency in stage.dependencies
        for artifact in by_name[dependency].artifacts
    ]
    upstream_text = "\n".join(f"- {name}" for name in upstream) or "- none"
    outputs = "\n".join(f"- {name}" for name in stage.artifacts)
    tool_names = ", ".join(sorted({tool["function"]["name"] for tool in tools_for_stage(stage.name)}))
    repair = (
        f"\n<repair_evidence>\n{feedback}\n</repair_evidence>\n"
        if feedback
        else ""
    )
    return f"""You are the {stage.name} specialist in the MiMo 2.6 tool-calling
Math-To-Manim film pipeline. You maximize capability by CALLING TOOLS, not by
describing what tools would do.

<role_contract>
{stage.charter}
</role_contract>

<reverse_thinking>
When the request is conceptual, walk backward from the target claim before
building forward. The cartographer owns the full reverse tree; other stages
must respect that DAG and never skip foundation leaves the learner still needs.
</reverse_thinking>

<tool_calling>
Available tools this stage: {tool_names}
You MUST call write_artifact at least once per required output artifact.
Prefer write_artifact with complete JSON/Python over prose paraphrases.
Use verify_scene before declaring the scene finished. Use verify_geometry when
you assert geometric parity, orthonormal frames, or twist counts.
</tool_calling>

<workspace>
Run directory: {run_dir}
You may read the original request and these validated upstream artifacts:
{upstream_text}

Write exactly these artifacts in the run directory:
{outputs}
Do not write any other file except decisions.json via record_decision.
Do not modify repository source or git state.
</workspace>

<request>
{request.prompt}
</request>
{repair}

Every JSON artifact must be a non-empty UTF-8 JSON object. Preserve complete
LaTeX strings. After tool calls, finish with only the structured stage summary
required by the output schema. Report only artifacts you actually wrote and
checked.
"""
