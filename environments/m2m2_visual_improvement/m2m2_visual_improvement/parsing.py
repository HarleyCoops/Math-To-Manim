"""Strict parser for the policy's single visual-revision action."""

from __future__ import annotations

import json

from pydantic import ValidationError

from .schemas import VisualRevision

OPEN_TAG = "<visual_revision>"
CLOSE_TAG = "</visual_revision>"
DEFAULT_MAX_BYTES = 256_000


class VisualRevisionParseError(ValueError):
    """The policy output is not one valid ``VisualRevision`` action."""


def parse_visual_revision(
    output: str,
    *,
    baseline_code: str,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> VisualRevision:
    """Parse one exact tagged JSON action and validate it against the baseline."""

    if len(output.encode("utf-8")) > max_bytes:
        raise VisualRevisionParseError(
            f"visual revision exceeds {max_bytes}-byte limit"
        )

    stripped = output.strip()
    if (
        stripped.count(OPEN_TAG) != 1
        or stripped.count(CLOSE_TAG) != 1
        or not stripped.startswith(OPEN_TAG)
        or not stripped.endswith(CLOSE_TAG)
    ):
        raise VisualRevisionParseError(
            "output must contain exactly one visual_revision action and no "
            "surrounding text"
        )

    payload_text = stripped[len(OPEN_TAG) : -len(CLOSE_TAG)]
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise VisualRevisionParseError(
            f"visual revision JSON is invalid at line {exc.lineno}, "
            f"column {exc.colno}"
        ) from None

    try:
        return VisualRevision.model_validate(
            payload,
            context={"baseline_code": baseline_code},
        )
    except ValidationError as exc:
        raise VisualRevisionParseError(
            f"payload is not a valid VisualRevision: {exc}"
        ) from None


__all__ = [
    "CLOSE_TAG",
    "DEFAULT_MAX_BYTES",
    "OPEN_TAG",
    "VisualRevisionParseError",
    "parse_visual_revision",
]
