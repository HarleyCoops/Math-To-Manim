"""Prompt construction and score parsing helpers for local eval workflows."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any


@dataclass(frozen=True)
class EvalCriterion:
    """One rubric criterion used to build deterministic eval prompts."""

    name: str
    description: str
    weight: float = 1.0


@dataclass(frozen=True)
class PromptScore:
    """Parsed score from an evaluator response."""

    raw_score: float | None
    normalized_score: float
    ok: bool
    explanation: str = ""


def build_eval_prompt(
    *,
    criteria: list[EvalCriterion | str] | tuple[EvalCriterion | str, ...],
    candidate: str,
    reference: str | None = None,
    max_score: int = 5,
) -> str:
    """Build a stable rubric prompt for an external or local evaluator."""

    normalized_criteria = [_normalize_criterion(index, criterion) for index, criterion in enumerate(criteria, start=1)]
    criteria_lines = [
        f"{index}. {criterion.name} (weight {criterion.weight:g}): {criterion.description}"
        for index, criterion in enumerate(normalized_criteria, start=1)
    ]
    sections = [
        "You are scoring generated Manim output.",
        f"Return JSON with keys: score, max_score, explanation. Use an integer score from 0 to {max_score}.",
        "Criteria:",
        "\n".join(criteria_lines),
    ]
    if reference is not None:
        sections.extend(["Reference:", reference.strip()])
    sections.extend(["Candidate:", candidate.strip()])
    return "\n\n".join(sections).strip() + "\n"


def parse_eval_score(text: str, *, min_score: float = 0.0, max_score: float = 5.0) -> PromptScore:
    """Parse and normalize a numeric eval score from JSON or plain text."""

    payload = _extract_json_object(text)
    if payload and "score" in payload:
        raw = _float_or_none(payload.get("score"))
        payload_max = _float_or_none(payload.get("max_score"))
        effective_max = payload_max if payload_max and payload_max > min_score else max_score
        explanation = str(payload.get("explanation") or payload.get("reason") or "")
        if raw is not None:
            return PromptScore(raw, _normalize_score(raw, min_score, effective_max), True, explanation)

    match = re.search(
        r"\bscore\b\s*[:=]\s*(-?\d+(?:\.\d+)?)\s*(?:/\s*(-?\d+(?:\.\d+)?))?",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        raw = float(match.group(1))
        effective_max = float(match.group(2)) if match.group(2) else max_score
        return PromptScore(raw, _normalize_score(raw, min_score, effective_max), True, "")

    return PromptScore(None, 0.0, False, "No score found")


def weighted_score(scores: list[PromptScore | float] | tuple[PromptScore | float, ...], weights: list[float] | tuple[float, ...] | None = None) -> float:
    """Return a deterministic weighted mean of normalized scores."""

    values = [score.normalized_score if isinstance(score, PromptScore) else float(score) for score in scores]
    if not values:
        return 0.0
    if weights is None:
        weights = [1.0] * len(values)
    if len(weights) != len(values):
        raise ValueError("weights length must match scores length")
    total_weight = sum(weights)
    if total_weight <= 0:
        return 0.0
    return sum(max(0.0, min(1.0, value)) * weight for value, weight in zip(values, weights, strict=True)) / total_weight


def _normalize_criterion(index: int, criterion: EvalCriterion | str) -> EvalCriterion:
    if isinstance(criterion, EvalCriterion):
        return criterion
    return EvalCriterion(f"Criterion {index}", criterion)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    for candidate in (stripped, _first_braced_object(stripped)):
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _first_braced_object(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _normalize_score(score: float, min_score: float, max_score: float) -> float:
    if max_score <= min_score:
        return 0.0
    return max(0.0, min(1.0, (score - min_score) / (max_score - min_score)))


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
