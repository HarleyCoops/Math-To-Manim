"""Independent Grok audits. The auditor is not the stage that wrote the artifact."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from grok.schemas import Assessment, coerce_assessment

AUDITOR_CHARTER = """You are an independent auditor for one Grok Math-To-Manim stage.
You did not write the artifact. Judge only the evidence files you are given.
Return one JSON object with:
- verdict: "pass" or "fail"
- evidence: filenames you actually used, copied from the supplied list
- repair_stage: the earliest stage that should change if the verdict is fail
  (intent, cartographer, curriculum, math-director, cinematographer, or composer)
- feedback: what to repair
- defects: concrete problems, or an empty list when the verdict is pass
A render review must cite the supplied frame PNG filenames in evidence.
Do not approve a film from a description of frames you were not shown.
"""


def audit_prompt(
    stage: str,
    user_prompt: str,
    filenames: list[str],
    *,
    feedback: str = "",
    frames: list[str] | None = None,
) -> str:
    frame_lines = "\n".join(frames or [])
    return (
        f"STAGE: {stage}\n"
        f"USER REQUEST:\n{user_prompt}\n\n"
        "EVIDENCE FILES:\n"
        + "\n".join(filenames)
        + "\n\nFRAMES:\n"
        + frame_lines
        + "\n\nCite evidence by exact filename from the lists above.\n"
        f"FEEDBACK ALREADY GIVEN:\n{feedback or 'none'}\n"
    )


def cited_names(evidence: list[str]) -> set[str]:
    names: set[str] = set()
    for item in evidence:
        text = str(item).strip().strip("`")
        if not text:
            continue
        names.add(text)
        names.add(Path(text).name)
    return names


def unknown_citations(evidence: list[str], allowed: set[str]) -> list[str]:
    allowed_names = {Path(item).name for item in allowed} | set(allowed)
    bad: list[str] = []
    for item in evidence:
        text = str(item).strip().strip("`")
        if text in allowed_names or Path(text).name in allowed_names:
            continue
        if any(name and name in text for name in allowed_names):
            continue
        bad.append(text)
    return bad


def cites_frames(evidence: list[str], frame_names: set[str]) -> bool:
    if not frame_names:
        return False
    blob = "\n".join(str(item) for item in evidence)
    return any(name in blob for name in frame_names)


def parse_assessment(
    payload: dict,
    allowed: set[str],
    frame_names: set[str] | None,
) -> tuple[Assessment | None, list[str]]:
    try:
        assessment = Assessment.model_validate(coerce_assessment(payload))
    except ValidationError as exc:
        message = exc.errors()[0].get("msg", "invalid assessment")
        return None, [f"assessment schema: {message}"]
    issues: list[str] = []
    bad = unknown_citations(assessment.evidence, allowed)
    if bad:
        issues.append("cited evidence outside the supplied files: " + ", ".join(bad))
    if frame_names is not None and not cites_frames(assessment.evidence, frame_names):
        issues.append("render review must cite the supplied frame filenames")
    return assessment, issues
