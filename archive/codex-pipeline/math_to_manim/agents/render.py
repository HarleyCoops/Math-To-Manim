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
            manim_command=self.config.manim_command,
            working_dir=file_path.parent,
            timeout_seconds=self.config.render_timeout_seconds,
        )
        status = "succeeded" if result.ok else "skipped" if result.skipped else "failed"
        return RenderResult(
            status=status,
            scene_name=generated.scene_name,
            output_path=str(result.output_path) if result.output_path else None,
            command=list(result.command),
            stdout=result.stdout,
            stderr=result.stderr or result.reason,
            metadata={"skipped": result.skipped, "returncode": result.returncode},
        )
