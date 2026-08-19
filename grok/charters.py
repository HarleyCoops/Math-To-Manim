"""Load Grok stage charters and the tools each stage may call."""

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


VERIFY_SCENE_TOOL = {
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
                "description": "Complete Python file contents for grok_scene.py",
            }
        },
        "required": ["source"],
    },
}

STAGES: tuple[Stage, ...] = (
    Stage("intent", "grok-intent.md", "01_intent.json", ()),
    Stage(
        "cartographer",
        "grok-cartographer.md",
        "02_knowledge_map.json",
        ({"type": "web_search"},),
    ),
    Stage("curriculum", "grok-curriculum.md", "03_curriculum.json", ()),
    Stage(
        "math-director",
        "grok-math-director.md",
        "04_math_dossier.json",
        ({"type": "code_interpreter"}, {"type": "web_search"}),
    ),
    Stage(
        "cinematographer",
        "grok-cinematographer.md",
        "05_shot_list.json",
        (
            {"type": "image_generation", "action": "generate"},
            {"type": "x_search"},
        ),
    ),
    Stage(
        "composer",
        "grok-composer.md",
        "06_scene_spec.json",
        (VERIFY_SCENE_TOOL,),
        extra_artifacts=("grok_scene.py",),
    ),
)


def stage_by_name(name: str) -> Stage:
    for stage in STAGES:
        if stage.name == name:
            return stage
    raise ValueError(f"unknown Grok stage: {name}")


def load_charter(filename: str) -> str:
    path = AGENT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"missing Grok charter: {path}")
    return path.read_text(encoding="utf-8")


def all_charters() -> dict[str, str]:
    return {stage.name: load_charter(stage.charter_file) for stage in STAGES}
