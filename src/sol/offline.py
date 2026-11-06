"""Deterministic full-pipeline rehearsal with no Codex call or render.

Writes every stage artifact; validation.json and review.json are owned by the
harness and written by its validate-and-review pass.
"""

from __future__ import annotations

import json
from pathlib import Path

from sol.agents import AGENT_STAGES
from sol.models import RunRequest

OFFLINE_SCENE_NAME = "SolOfflineScene"


def write_offline_bundle(run_dir: Path, request: RunRequest) -> None:
    sequence = 0
    for stage in AGENT_STAGES:
        for name in stage.artifacts:
            sequence += 1
            path = run_dir / name
            if name.endswith(".json"):
                path.write_text(json.dumps({
                    "offline": True,
                    "stage": name.removesuffix(".json"),
                    "topic": request.prompt,
                    "sequence": sequence,
                    "content": ["deterministic full-pipeline rehearsal"],
                }, indent=2), encoding="utf-8")
            else:
                path.write_text(_OFFLINE_SCENE, encoding="utf-8")


_OFFLINE_SCENE = f'''from manim import *


class {OFFLINE_SCENE_NAME}(Scene):
    """Deterministic rehearsal of the complete Sol artifact contract."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        title = Text("Sol pipeline: offline rehearsal", color="#faf9f5")
        stages = VGroup(*[
            Text(label, font_size=24, color=color)
            for label, color in [
                ("intent", "#6a9bcc"),
                ("prerequisites", "#d97757"),
                ("curriculum", "#e5b566"),
                ("scene", "#788c5d"),
            ]
        ]).arrange(DOWN, buff=0.25)
        self.play(FadeIn(title))
        self.play(title.animate.to_edge(UP), LaggedStart(*[FadeIn(item) for item in stages]))
        self.wait(0.5)
'''
