"""Deterministic, metadata-only video scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScoreItem:
    """One component of a video score."""

    name: str
    score: float
    weight: float
    reason: str


@dataclass(frozen=True)
class VideoScore:
    """Weighted video quality score in the range [0, 1]."""

    score: float
    passed: bool
    items: tuple[ScoreItem, ...]


def score_video_metadata(
    *,
    duration_seconds: float | None,
    width: int | None,
    height: int | None,
    file_size_bytes: int | None = None,
    min_duration_seconds: float = 1.0,
    min_width: int = 640,
    min_height: int = 360,
    min_file_size_bytes: int = 1,
    pass_threshold: float = 0.75,
) -> VideoScore:
    """Score basic video metadata without decoding media."""

    items = [
        ScoreItem(
            "duration",
            _ratio_score(duration_seconds, min_duration_seconds),
            0.45,
            _duration_reason(duration_seconds, min_duration_seconds),
        ),
        ScoreItem(
            "resolution",
            _resolution_score(width, height, min_width, min_height),
            0.45,
            _resolution_reason(width, height, min_width, min_height),
        ),
    ]
    if file_size_bytes is not None:
        items.append(
            ScoreItem(
                "file_size",
                _ratio_score(float(file_size_bytes), float(min_file_size_bytes)),
                0.10,
                f"{file_size_bytes} bytes, target at least {min_file_size_bytes}",
            )
        )

    weighted = _weighted_average(items)
    return VideoScore(weighted, weighted >= pass_threshold, tuple(items))


def score_video_probe(
    probe: Any,
    *,
    file_size_bytes: int | None = None,
    pass_threshold: float = 0.75,
    **thresholds: Any,
) -> VideoScore:
    """Score an object returned by ``probe_video`` or any matching metadata object."""

    if not getattr(probe, "ok", False):
        item = ScoreItem("probe", 0.0, 1.0, getattr(probe, "reason", None) or "probe failed")
        return VideoScore(0.0, False, (item,))
    return score_video_metadata(
        duration_seconds=getattr(probe, "duration_seconds", None),
        width=getattr(probe, "width", None),
        height=getattr(probe, "height", None),
        file_size_bytes=file_size_bytes,
        pass_threshold=pass_threshold,
        **thresholds,
    )


def score_video_file(
    path: str | Path,
    *,
    probe: Any | None = None,
    pass_threshold: float = 0.75,
    **thresholds: Any,
) -> VideoScore:
    """Score a video file using probe metadata when available."""

    video_path = Path(path)
    file_size = video_path.stat().st_size if video_path.exists() else 0
    if probe is None:
        item = ScoreItem("file_exists", 1.0 if video_path.exists() else 0.0, 1.0, str(video_path))
        return VideoScore(item.score, item.score >= pass_threshold, (item,))
    return score_video_probe(probe, file_size_bytes=file_size, pass_threshold=pass_threshold, **thresholds)


def _ratio_score(value: float | None, target: float) -> float:
    if value is None or target <= 0:
        return 0.0
    return max(0.0, min(1.0, value / target))


def _resolution_score(width: int | None, height: int | None, min_width: int, min_height: int) -> float:
    if width is None or height is None:
        return 0.0
    return min(_ratio_score(float(width), float(min_width)), _ratio_score(float(height), float(min_height)))


def _weighted_average(items: list[ScoreItem]) -> float:
    total_weight = sum(item.weight for item in items)
    if total_weight <= 0:
        return 0.0
    return sum(item.score * item.weight for item in items) / total_weight


def _duration_reason(duration_seconds: float | None, min_duration_seconds: float) -> str:
    if duration_seconds is None:
        return "duration unavailable"
    return f"{duration_seconds:.3f}s, target at least {min_duration_seconds:.3f}s"


def _resolution_reason(width: int | None, height: int | None, min_width: int, min_height: int) -> str:
    if width is None or height is None:
        return "resolution unavailable"
    return f"{width}x{height}, target at least {min_width}x{min_height}"
