"""Static validation stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import GeneratedCode, ValidationIssue, ValidationReport
from math_to_manim.tools import discover_scene_classes_in_file, validate_python_source


class StaticReviewAgent(StageAgent[tuple[GeneratedCode, Path], ValidationReport]):
    name = "static_review"

    def run(self, value: tuple[GeneratedCode, Path]) -> ValidationReport:
        generated, file_path = value
        ast_report = validate_python_source(generated.code, filename=str(file_path))
        schema_issues = [
            ValidationIssue(
                code=issue.code,
                message=issue.message,
                severity=issue.severity,
                artifact=str(file_path),
                metadata={"line": issue.lineno, "column": issue.col_offset},
            )
            for issue in ast_report.issues
        ]
        scenes = []
        scene_found = False
        if ast_report.ok:
            scenes = [scene.name for scene in discover_scene_classes_in_file(file_path, require_construct=True)]
            scene_found = generated.scene_name in scenes
            if not scene_found:
                schema_issues.append(
                    ValidationIssue(
                        code="scene-class-missing",
                        message=f"Expected scene class {generated.scene_name!r}; discovered {scenes or 'none'}.",
                        severity="error",
                        artifact=str(file_path),
                    )
                )
        status = "passed" if not schema_issues else "failed"
        return ValidationReport(
            status=status,
            issues=schema_issues,
            checked_artifacts=[str(file_path)],
            summary="Static validation passed." if status == "passed" else "Static validation failed.",
            metadata={
                "ast_valid": ast_report.ok,
                "scene_found": scene_found,
                "scene_classes": scenes,
                "repair_hints": [] if ast_report.ok and scene_found else ["ensure generated file is valid Python and contains the requested Scene class"],
            },
        )
