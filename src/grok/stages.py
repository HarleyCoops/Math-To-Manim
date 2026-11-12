"""The Grok chain: ordered stages, what each may call and must write, and the
bundle check a finished run must pass.

Everything stage-specific lives in the ``STAGES`` table. The harness loops
over it without knowing stage names.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from grok.models import REVIEW_FILE, SCENE_FILE, VALIDATION_FILE
from grok.tools import VERIFY_SCENE_HANDLERS, VERIFY_SCENE_TOOL
from grok.validation import normalize_reverse_tree, validate_reverse_tree, validate_scene_source

PACKAGE_DIR = Path(__file__).resolve().parent
AGENT_DIR = PACKAGE_DIR / "agents"


@dataclass(frozen=True)
class Stage:
    name: str
    charter_file: str
    artifact: str
    tools: tuple[dict, ...] = ()
    # Responses API tool_choice for this stage (None = model decides).
    tool_choice: str | None = None
    # Whether the request image is attached to this stage's user turn.
    takes_image: bool = False
    # Local handlers for function tools listed in ``tools``.
    function_handlers: Mapping[str, Callable[..., dict]] | None = None
    # Coerce the model's payload into the artifact contract before writing.
    normalize: Callable[[dict], dict] | None = None
    # Contract check for the written artifact (bundle validation).
    validate: Callable[[dict], list[str]] | None = None
    # This stage must also deliver the Manim scene source.
    writes_scene: bool = False
    # Extra line appended to this stage's user turn.
    reply_note: str = ""


STAGES: tuple[Stage, ...] = (
    Stage("intent", "grok-intent.md", "01_intent.json", takes_image=True),
    Stage(
        "cartographer",
        "grok-cartographer.md",
        "02_knowledge_map.json",
        tools=({"type": "web_search"},),
        normalize=normalize_reverse_tree,
        validate=validate_reverse_tree,
    ),
    Stage("curriculum", "grok-curriculum.md", "03_curriculum.json"),
    Stage(
        "math-director",
        "grok-math-director.md",
        "04_math_dossier.json",
        tools=({"type": "code_interpreter"}, {"type": "web_search"}),
        tool_choice="required",
    ),
    Stage(
        "cinematographer",
        "grok-cinematographer.md",
        "05_shot_list.json",
        tools=(
            {"type": "image_generation", "action": "generate"},
            {"type": "x_search"},
        ),
    ),
    Stage(
        "composer",
        "grok-composer.md",
        "06_scene_spec.json",
        tools=(VERIFY_SCENE_TOOL,),
        function_handlers=VERIFY_SCENE_HANDLERS,
        writes_scene=True,
        reply_note=(
            "Also include a source field with the complete Python file, "
            "or a fenced python block."
        ),
    ),
)

COMPOSER = next(stage for stage in STAGES if stage.writes_scene)

# What the chain must produce, then what the wrapper adds. Every run has all of them.
STAGE_ARTIFACTS: tuple[str, ...] = tuple(stage.artifact for stage in STAGES) + (SCENE_FILE,)
ARTIFACT_NAMES: tuple[str, ...] = STAGE_ARTIFACTS + (VALIDATION_FILE, REVIEW_FILE)


def tool_labels(stage: Stage) -> list[str]:
    """Human-readable names of the tools a stage may call, for traces."""
    return [tool.get("name") or tool.get("type") for tool in stage.tools]


def load_charter(filename: str) -> str:
    path = AGENT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"missing Grok charter: {path}")
    return path.read_text(encoding="utf-8")


def cinematic_charter() -> str:
    """Composer + cinematography contract for MCP and review tools."""
    return (
        "GROK CINEMATIC CONTRACT\n"
        f"Grok 4.6 writes {SCENE_FILE} as a single Manim CE ThreeDScene.\n"
        "Camera: move_camera() or set_camera_orientation() only. "
        "Never .animate on self.camera.\n"
        "CAMERA IS THE NARRATOR. Headlines before symbols. "
        "One idea per act. Homework numbers come from code_interpreter.\n\n"
        + load_charter("grok-cinematographer.md")
        + "\n\n"
        + load_charter(COMPOSER.charter_file)
    )


def validate_run(run_dir: Path) -> tuple[list[str], str | None]:
    """Check a run bundle against the stage table.

    Returns (failures, scene_name). Every stage artifact must be a non-empty
    JSON object that passes its stage's contract check; the scene must compile
    and obey the scene rules.
    """
    failures: list[str] = []
    for stage in STAGES:
        path = run_dir / stage.artifact
        if not path.is_file():
            failures.append(f"missing required artifact: {stage.artifact}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{stage.artifact}: invalid JSON ({exc})")
            continue
        if not isinstance(payload, dict) or not payload:
            failures.append(f"{stage.artifact}: expected a non-empty JSON object")
            continue
        if stage.validate is not None:
            failures.extend(stage.validate(payload))

    scene_path = run_dir / SCENE_FILE
    scene_name = None
    if not scene_path.is_file():
        failures.append(f"missing required artifact: {SCENE_FILE}")
    else:
        scene_failures, scene_name = validate_scene_source(
            scene_path.read_text(encoding="utf-8")
        )
        failures.extend(scene_failures)
    return failures, scene_name
