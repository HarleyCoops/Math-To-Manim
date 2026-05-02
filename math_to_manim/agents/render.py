"""Render stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import GeneratedCode, RenderResult
from math_to_manim.tools.manim_tools import render_manim_scene


class RenderAgent(StageAgent[tuple[GeneratedCode, Path, str], RenderResult]):
    name = "render"

    def run(self, value: tuple[GeneratedCode, Path, str]) -> RenderResult:
        generated, file_path, quality = value
        return render_manim_scene(file_path=file_path, scene=generated.scene_class, quality=quality)
