"""Deterministic full-pipeline rehearsal with no Codex call or render."""

from __future__ import annotations

import json
from pathlib import Path

from sol.models import ARTIFACT_NAMES, CodexRunResult, RunRequest
from sol.scene_checks import validation_from_scene


def write_offline_bundle(run_dir: Path, request: RunRequest) -> CodexRunResult:
    for index, name in enumerate(ARTIFACT_NAMES, start=1):
        path = run_dir / name
        if name == "sol_scene.py":
            path.write_text(_OFFLINE_SCENE, encoding="utf-8")
        elif name == "validation.json":
            path.write_text(
                json.dumps(validation_from_scene(_OFFLINE_SCENE), indent=2),
                encoding="utf-8",
            )
        elif name == "review.json":
            path.write_text(json.dumps({
                "offline": True,
                "checks": ["artifact contract", "python compilation", "static safety"],
                "rendered": False,
                "limitations": ["deterministic rehearsal; no Codex call"],
            }, indent=2), encoding="utf-8")
        else:
            path.write_text(json.dumps({
                "offline": True,
                "stage": name.removesuffix(".json"),
                "topic": request.prompt,
                "sequence": index,
                "content": ["deterministic full-pipeline rehearsal"],
            }, indent=2), encoding="utf-8")
    return CodexRunResult(
        status="completed",
        scene_file="sol_scene.py",
        scene_name="SolOfflineScene",
        artifacts=list(ARTIFACT_NAMES),
        rendered=False,
        video_path=None,
        checks=["offline artifact contract", "python compilation", "static safety"],
        notes=["No Codex CLI call or render was performed"],
    )


_OFFLINE_SCENE = '''from manim import *


class SolOfflineScene(Scene):
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
