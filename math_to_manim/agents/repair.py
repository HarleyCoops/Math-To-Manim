"""Repair decision stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RepairPatch, ValidationReport


class RepairAgent(StageAgent[ValidationReport, RepairPatch]):
    name = "repair"

    def run(self, report: ValidationReport) -> RepairPatch:
        if report.ast_valid and report.manim_dry_run_pass:
            return RepairPatch(
                target_file=None,
                patch_summary="No repair required.",
                applied=False,
                rationale="Static validation passed.",
            )
        return RepairPatch(
            target_file=None,
            patch_summary="Repair required but deterministic scaffold does not rewrite code automatically.",
            applied=False,
            rationale="OpenAI repair agent should patch only the failing generated file.",
        )
