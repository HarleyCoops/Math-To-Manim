"""Repair decision stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RepairPatch, ValidationReport


class RepairAgent(StageAgent[ValidationReport, RepairPatch]):
    name = "repair"

    def run(self, report: ValidationReport) -> RepairPatch:
        if report.is_successful:
            return RepairPatch(
                target_artifact="generated_scene.py",
                summary="No repair required.",
                issue_codes=[],
                validation_expectations=["Static validation passed."],
                metadata={"applied": False, "rationale": "Static validation passed."},
            )
        return RepairPatch(
            target_artifact="generated_scene.py",
            summary="Repair required but deterministic scaffold does not rewrite code automatically.",
            issue_codes=[issue.code for issue in report.issues],
            validation_expectations=["OpenAI repair agent should patch only the failing generated file."],
            metadata={"applied": False},
        )
