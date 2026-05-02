"""Render stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import GeneratedCode, RenderResult
from math_to_manim.rendering import render_manim_scene


class RenderAgent(StageAgent[tuple[GeneratedCode, Path, str], RenderResult]):
    name = "render"

    def run(self, value: tuple[GeneratedCode, Path, str]) -> RenderResult:
        generated, file_path, quality = value
        result = render_manim_scene(
            file_path,
            scene_name=generated.scene_name,
            output_dir=file_path.parent / "media",
            quality=quality,
            working_dir=file_path.parent,
        )
        return RenderResult(
            status="succeeded" if result.ok else "failed",
            scene_name=generated.scene_name,
            output_path=str(result.output_path) if result.output_path else None,
            command=list(result.command),
            stdout=result.stdout,
            stderr=result.stderr or result.reason,
            metadata={"skipped": result.skipped, "returncode": result.returncode},
        )
