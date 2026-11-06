"""The Argon stage table: the single source of stage order, charters, artifacts,
tools and per-stage behaviour for the six-agent Google ADK chain.

Everything that walks the chain (live harness, offline rehearsal, bundle
validation, CLI, operator script) reads this table instead of hard-coding
stage names.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from argon.tools import execute_math_check, verify_scene
from argon.validation import normalize_reverse_tree, validate_reverse_tree

PACKAGE_DIR = Path(__file__).resolve().parent
AGENT_DIR = PACKAGE_DIR / "agents"

Tool = Callable[..., dict]


@dataclass(frozen=True)
class Stage:
    name: str
    charter_file: str
    artifact: str
    tools: tuple[Tool, ...] = ()
    # The user's image attachment is sent to this stage.
    accepts_image: bool = False
    # Applied to the stage payload before it is written to the bundle.
    normalize: Callable[[dict], dict] | None = None
    # Returns failure messages for the (normalized) payload; empty when valid.
    check: Callable[[dict], list[str]] | None = None
    # The stage also delivers the complete Manim scene source.
    writes_scene: bool = False

    @property
    def agent_name(self) -> str:
        """ADK agent name recorded in traces and manifests."""
        return "argon_" + re.sub(r"[^a-zA-Z0-9_]", "_", self.name)

    @property
    def tool_names(self) -> list[str]:
        return [tool.__name__ for tool in self.tools]

    def charter(self) -> str:
        return load_charter(self.charter_file)

    def prepare(self, payload: dict) -> dict:
        """Normalize then check a stage payload; raises ValueError on failure."""
        if self.normalize is not None:
            payload = self.normalize(payload)
        if self.check is not None:
            failures = self.check(payload)
            if failures:
                raise ValueError(f"stage {self.name!r} rejected: {'; '.join(failures)}")
        return payload


STAGES: tuple[Stage, ...] = (
    Stage("intent", "argon-intent.md", "01_intent.json", accepts_image=True),
    Stage(
        "cartographer",
        "argon-cartographer.md",
        "02_knowledge_map.json",
        normalize=normalize_reverse_tree,
        check=validate_reverse_tree,
    ),
    Stage("curriculum", "argon-curriculum.md", "03_curriculum.json"),
    Stage("math-director", "argon-math-director.md", "04_math_dossier.json", tools=(execute_math_check,)),
    Stage("cinematographer", "argon-cinematographer.md", "05_shot_list.json"),
    Stage(
        "composer",
        "argon-composer.md",
        "06_scene_spec.json",
        tools=(verify_scene,),
        writes_scene=True,
    ),
)

COMPOSER: Stage = next(stage for stage in STAGES if stage.writes_scene)

STAGE_ARTIFACTS: tuple[str, ...] = tuple(stage.artifact for stage in STAGES)


def load_charter(filename: str) -> str:
    path = AGENT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"missing Argon charter: {path}")
    return path.read_text(encoding="utf-8")


def all_charters() -> dict[str, str]:
    return {stage.name: stage.charter() for stage in STAGES}


def stage_prompt(stage: Stage, prompt: str, prior: dict[str, dict]) -> str:
    """User turn for one stage: the request plus every upstream artifact."""
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage.name} stage in the Argon Google ADK chain. Read the charter. "
        "Return one JSON object with exactly the keys the charter names.\n"
        "If you write the scene, also include a source field with the complete "
        "Python file, or a fenced python block.\n\n"
        f"Upstream artifacts:\n{dossier}\n"
    )
