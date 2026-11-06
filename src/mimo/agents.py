"""The MiMo 2.6 stage table: one row per specialist, in dependency order.

Everything that varies per stage lives here: artifacts written, upstream
dependencies, tools the stage may call, and the charter file under
``agents/``. The pipeline, CLI choices, validation requirements and prompts
are all derived from this table.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from mimo.models import DECISIONS_FILE, SCENE_FILE, RunRequest
from mimo.tools import tool_specs

CHARTER_DIR = Path(__file__).resolve().parent / "agents"


@dataclass(frozen=True)
class AgentStage:
    name: str
    artifacts: tuple[str, ...]
    dependencies: tuple[str, ...]
    tools: tuple[str, ...]

    @property
    def charter_path(self) -> Path:
        return CHARTER_DIR / f"mimo-{self.name}.md"

    @property
    def charter(self) -> str:
        return _read_charter(self.charter_path)

    @property
    def tool_specs(self) -> tuple[dict, ...]:
        return tool_specs(self.tools)


@lru_cache(maxsize=None)
def _read_charter(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


AGENT_STAGES = (
    AgentStage(
        name="intent",
        artifacts=("01_intent.json",),
        dependencies=(),
        tools=("write_artifact", "read_artifact", "list_artifacts"),
    ),
    AgentStage(
        name="cartographer",
        artifacts=("02_knowledge_map.json",),
        dependencies=("intent",),
        tools=("write_artifact", "read_artifact", "record_decision"),
    ),
    AgentStage(
        name="curriculum",
        artifacts=("03_curriculum.json",),
        dependencies=("cartographer",),
        tools=("write_artifact", "read_artifact"),
    ),
    AgentStage(
        name="math-director",
        artifacts=("04_math_dossier.json",),
        dependencies=("intent",),
        tools=("write_artifact", "read_artifact", "verify_geometry", "record_decision"),
    ),
    AgentStage(
        name="cinematographer",
        artifacts=("05_shot_list.json",),
        dependencies=("curriculum", "math-director"),
        tools=("write_artifact", "read_artifact", "verify_geometry"),
    ),
    AgentStage(
        name="scene-composer",
        artifacts=("06_scene_spec.json", SCENE_FILE),
        dependencies=("cinematographer",),
        tools=("write_artifact", "read_artifact", "verify_scene", "verify_geometry", "list_artifacts"),
    ),
)

STAGE_NAMES = tuple(stage.name for stage in AGENT_STAGES)

# The scheduler and stages_from rely on every stage following its dependencies.
for _position, _stage in enumerate(AGENT_STAGES):
    _missing = set(_stage.dependencies) - set(STAGE_NAMES[:_position])
    if _missing:
        raise ValueError(f"MiMo stage {_stage.name!r} is listed before its dependencies {sorted(_missing)}")
STAGE_ARTIFACTS = tuple(artifact for stage in AGENT_STAGES for artifact in stage.artifacts)
# The stage that writes the scene file is the one the harness re-runs to repair it.
SCENE_STAGE = next(stage for stage in AGENT_STAGES if SCENE_FILE in stage.artifacts)


def stage_by_name(name: str) -> AgentStage:
    for stage in AGENT_STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown MiMo stage: {name}")


def stages_from(name: str) -> frozenset[str]:
    """``name`` plus every stage that depends on it, transitively."""
    stage_by_name(name)
    forced = {name}
    for stage in AGENT_STAGES:  # table is in dependency order: one pass suffices
        if set(stage.dependencies) & forced:
            forced.add(stage.name)
    return frozenset(forced)


def build_stage_prompt(
    stage: AgentStage,
    request: RunRequest,
    *,
    run_dir: Path,
    feedback: str | None = None,
) -> str:
    upstream = [
        artifact
        for dependency in stage.dependencies
        for artifact in stage_by_name(dependency).artifacts
    ]
    upstream_text = "\n".join(f"- {name}" for name in upstream) or "- none"
    outputs = "\n".join(f"- {name}" for name in stage.artifacts)
    tool_names = ", ".join(sorted(stage.tools))
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
Do not write any other file except {DECISIONS_FILE} via record_decision.
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
