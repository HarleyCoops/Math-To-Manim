"""Load Argon Google ADK stage charters and tool definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
AGENT_DIR = PACKAGE_DIR / "agents"


@dataclass(frozen=True)
class Stage:
    name: str
    charter_file: str
    artifact: str
    tools: tuple[str, ...]
    extra_artifacts: tuple[str, ...] = ()


VERIFY_SCENE_TOOL_SPEC = {
    "type": "function",
    "name": "verify_scene",
    "description": (
        "Compile and statically check a complete Manim Community Edition "
        "scene source string. Returns pass/fail, scene class name, and errors."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "Complete Python file contents for argon_scene.py",
            }
        },
        "required": ["source"],
    },
}

EXECUTE_MATH_CHECK_TOOL_SPEC = {
    "type": "function",
    "name": "execute_math_check",
    "description": (
        "Evaluate a deterministic mathematical expression or numerical invariant "
        "using numpy/math and return the verified result."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A safe mathematical expression using numpy (np) or math.",
            }
        },
        "required": ["expression"],
    },
}

STAGES: tuple[Stage, ...] = (
    Stage("intent", "argon-intent.md", "01_intent.json", ()),
    Stage("cartographer", "argon-cartographer.md", "02_knowledge_map.json", ()),
    Stage("curriculum", "argon-curriculum.md", "03_curriculum.json", ()),
    Stage(
        "math-director",
        "argon-math-director.md",
        "04_math_dossier.json",
        ("execute_math_check",),
    ),
    Stage(
        "cinematographer",
        "argon-cinematographer.md",
        "05_shot_list.json",
        (),
    ),
    Stage(
        "composer",
        "argon-composer.md",
        "06_scene_spec.json",
        ("verify_scene",),
        extra_artifacts=("argon_scene.py",),
    ),
)


def stage_by_name(name: str) -> Stage:
    for stage in STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown Argon stage: {name}")


def load_charter(filename: str) -> str:
    path = AGENT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"missing Argon charter: {path}")
    return path.read_text(encoding="utf-8")


def all_charters() -> dict[str, str]:
    return {stage.name: load_charter(stage.charter_file) for stage in STAGES}


def cinematic_charter() -> str:
    """Composer + cinematography contract for Argon Google ADK runs."""
    return (
        "ARGON GOOGLE ADK CINEMATIC CONTRACT\n"
        "Gemini 4 Argon writes argon_scene.py as a single Manim CE ThreeDScene.\n"
        "Camera: move_camera() or set_camera_orientation() only. "
        "Never .animate on self.camera.\n"
        "CAMERA IS THE NARRATOR. Headlines before symbols. "
        "One core idea per act. Every numerical quantity is verified.\n\n"
        + load_charter("argon-cinematographer.md")
        + "\n\n"
        + load_charter("argon-composer.md")
    )
