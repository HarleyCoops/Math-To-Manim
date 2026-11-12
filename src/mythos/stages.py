"""The Mythos reasoning chain: one table describing every stage.

Each stage names its charter (``src/mythos/agents/*.md``), the artifact it
writes into the run directory, its key in the manifest's ``artifacts`` map,
and what a healthy reply must contain. The harness and the operator script
loop over ``STAGES`` without knowing stage names.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Stage:
    slug: str
    charter_file: str
    artifact: str
    manifest_key: str
    #: Replies smaller than this (JSON bytes) are degenerate.
    min_bytes: int = 200
    #: A list field the reply must populate, with the minimum length.
    required_list: str | None = None
    min_items: int = 1
    #: The cartographer's knowledge map feeds the prerequisite cache.
    caches_prerequisites: bool = False
    #: Extra fields of the deterministic offline stand-in artifact.
    offline_extra: dict[str, Any] = field(default_factory=dict)

    @property
    def stem(self) -> str:
        return self.artifact.split(".")[0]


STAGES: tuple[Stage, ...] = (
    Stage("intent", "mythos-intent.md", "01_intent.json", "intent"),
    Stage("cartographer", "mythos-cartographer.md", "02_knowledge_map.json",
          "knowledge_map", caches_prerequisites=True),
    Stage("curriculum", "mythos-curriculum.md", "03_curriculum.json", "curriculum"),
    # A real failure mode: the math-director once returned
    # {"formulas": [], "color_identity": {}, "numbers": []} (48 bytes) and
    # every downstream agent faithfully storyboarded an empty film.
    Stage("math-director", "mythos-math-director.md", "04_math_dossier.json",
          "math_dossier", min_bytes=500, required_list="formulas"),
    Stage("cinematographer", "mythos-cinematographer.md", "05_shot_list.json",
          "shot_list", min_bytes=500, required_list="shots", min_items=8,
          offline_extra={"shots": [
              {"beat": 1, "move": "HEADLINE", "text": "A deterministic rehearsal."},
              {"beat": 2, "move": "ZOOM_IN", "target": "formula"},
              {"beat": 3, "move": "PULL_BACK"},
          ]}),
    Stage("scene-composer", "mythos-scene-composer.md", "06_scene_spec.json",
          "scene_spec", offline_extra={"scene_name": "MythosOfflineScene"}),
)

STAGES_BY_SLUG: dict[str, Stage] = {stage.slug: stage for stage in STAGES}


def validate_stage_artifact(slug: str, artifact: Any) -> str | None:
    """Reject degenerate stage output before it poisons the chain.

    Returns a human-readable problem description, or None when healthy.
    """
    stage = STAGES_BY_SLUG[slug]
    if not isinstance(artifact, dict) or not artifact:
        return "artifact is not a non-empty JSON object"
    if stage.required_list:
        items = artifact.get(stage.required_list)
        if isinstance(items, list) and len(items) < stage.min_items:
            if not items:
                return f"'{stage.required_list}' list is empty"
            return (f"'{stage.required_list}' has only {len(items)} entries "
                    f"(need at least {stage.min_items})")
    size = len(json.dumps(artifact))
    if size < stage.min_bytes:
        return f"artifact is only {size} bytes"
    return None


def offline_artifact(stage: Stage, prompt: str, prior: dict) -> dict:
    """Deterministic stand-in so the chain runs without a CLI login."""
    return {"stage": stage.slug, "topic": prompt, "offline": True,
            "prior_keys": sorted(prior), **stage.offline_extra}


OFFLINE_SCENE = '''from manim import *


class MythosOfflineScene(ThreeDScene):
    """Offline rehearsal scene: proves the harness plumbing end to end."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        title = Text("Mythos harness: offline rehearsal", font_size=40, color="#faf9f5")
        formula = MathTex(r"e^{i\\pi} + 1 = 0", font_size=64, color="#d97757")
        self.play(FadeIn(title))
        self.wait(0.6)
        self.play(title.animate.scale(0.5).to_edge(UP), FadeIn(formula))
        self.move_camera(frame_center=formula.get_center(), zoom=2.2, run_time=1.2)
        self.wait(0.6)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.0)
        self.play(FadeOut(formula), FadeOut(title))
'''
