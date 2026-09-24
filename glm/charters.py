"""Load GLM stage charters plus each stage's allowed chat/completions tools."""

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
    tools: tuple[dict, ...]
    extra_artifacts: tuple[str, ...] = ()


# Z.ai chat/completions tool shape: nested under "function".
VERIFY_SCENE_TOOL = {
    "type": "function",
    "function": {
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
                    "description": "Complete Python file contents for glm_scene.py",
                }
            },
            "required": ["source"],
        },
    },
}

NO_TOOLS = ({"type": "note", "label": "no-tools-hop"},)
PRIMARY_SOURCES = ({"type": "web_search"},)
SANDBOX = ({"type": "code_interpreter"},)


STAGES: tuple[Stage, ...] = (
    Stage("intent", "glm-intent.md", "01_intent.json", NO_TOOLS),
    Stage(
        "cartographer",
        "glm-cartographer.md",
        "02_knowledge_map.json",
        PRIMARY_SOURCES,
    ),
    Stage("curriculum", "glm-curriculum.md", "03_curriculum.json", NO_TOOLS),
    Stage(
        "math-director",
        "glm-math-director.md",
        "04_math_dossier.json",
        SANDBOX + PRIMARY_SOURCES,
    ),
    Stage(
        "cinematographer",
        "glm-cinematographer.md",
        "05_shot_list.json",
        PRIMARY_SOURCES,
    ),
    Stage(
        "composer",
        "glm-composer.md",
        "06_scene_spec.json",
        (VERIFY_SCENE_TOOL,),
        extra_artifacts=("glm_scene.py",),
    ),
)


def stage_by_name(name: str) -> Stage:
    for stage in STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown GLM stage: {name}")


def load_charter(filename: str) -> str:
    path = AGENT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"missing GLM charter: {path}")
    return path.read_text(encoding="utf-8")


def cinematic_charter() -> str:
    """Composer + cinematography contract for MCP and review tools."""
    return (
        "GLM CINEMATIC CONTRACT\n"
        "GLM-5.3-Flash writes glm_scene.py as a single Manim CE ThreeDScene "
        "on paper #f3ecd8.\n"
        "Camera: set_camera_orientation() or move_camera() only. Never .animate "
        "on self.camera.\n"
        "THINKING IS ALWAYS ON. Headlines before symbols. One idea per act.\n\n"
        + load_charter("glm-cinematographer.md")
        + "\n\n"
        + load_charter("glm-composer.md")
    )


def all_charters() -> dict[str, str]:
    return {stage.name: load_charter(stage.charter_file) for stage in STAGES}
