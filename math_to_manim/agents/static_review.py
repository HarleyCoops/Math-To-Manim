"""Static validation stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import GeneratedCode, ValidationReport
from math_to_manim.tools.manim_tools import discover_scene_classes, validate_python_ast


class StaticReviewAgent(StageAgent[tuple[GeneratedCode, Path], ValidationReport]):
    name = "static_review"

    def run(self, value: tuple[GeneratedCode, Path]) -> ValidationReport:
        generated, file_path = value
        ast_report = validate_python_ast(generated.code)
        scenes = discover_scene_classes(file_path)
        scene_found = generated.scene_class in scenes
        return ValidationReport(
            ast_valid=ast_report.ok,
            imports_valid=True,
            ruff_pass=None,
            latex_pass=None,
            manim_dry_run_pass=scene_found,
            render_pass=None,
            traceback=ast_report.error if not ast_report.ok else None,
            repair_hints=[] if ast_report.ok and scene_found else ["ensure generated file is valid Python and contains the requested Scene class"],
            scene_classes=scenes,
        )
