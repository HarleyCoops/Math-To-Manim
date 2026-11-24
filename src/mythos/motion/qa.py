"""Stage 5 checks that need no model: format, duration and colour.

Vision checks (text, elements, layout, motion, rules) come from the visual QA
agent; :func:`merge_report` joins both into one QAReport.
"""

from __future__ import annotations

from pathlib import Path

from mythos.motion.contracts import BriefSpec, DURATION_TOLERANCE_S, QACheck, QAReport, Timeline
from mythos.motion.render import Probe

FPS_TOLERANCE = 0.05
#: RGB distance under which a pixel counts as the palette colour.
EXACT_TOLERANCE = 28.0
APPROX_TOLERANCE = 48.0
#: Fraction of sampled pixels (in the best frame) that must match.
MIN_COVERAGE = 0.0004


def frame_times(timeline: Timeline, duration_s: float, fps: float) -> list[float]:
    """Each beat's start, midpoint and last frame, de-duplicated and clamped."""
    last = max(0.0, duration_s - 1.0 / max(fps, 1.0))
    raw: list[float] = []
    for beat in sorted(timeline.beats, key=lambda b: b.start_s):
        raw += [beat.start_s, (beat.start_s + beat.end_s) / 2, beat.end_s - 1.0 / max(fps, 1)]
    times: list[float] = []
    for t in sorted(min(max(0.0, t), last) for t in raw):
        if not times or t - times[-1] >= 0.05:
            times.append(round(t, 3))
    return times


def format_checks(spec: BriefSpec, probe: Probe) -> list[QACheck]:
    return [
        QACheck(field="resolution", field_type="format", method="probe",
                expected=f"{spec.width}x{spec.height}",
                observed=f"{probe.width}x{probe.height}",
                passed=(probe.width, probe.height) == (spec.width, spec.height)),
        QACheck(field="fps", field_type="format", method="probe",
                expected=f"{spec.fps:g}", observed=f"{probe.fps:g}",
                passed=abs(probe.fps - spec.fps) <= FPS_TOLERANCE),
        QACheck(field="duration", field_type="timing", method="probe",
                expected=f"{spec.duration_s:.3f}s +/- {DURATION_TOLERANCE_S}s",
                observed=f"{probe.duration_s:.3f}s",
                passed=abs(probe.duration_s - spec.duration_s) <= DURATION_TOLERANCE_S,
                note=f"error {probe.duration_s - spec.duration_s:+.3f}s"),
    ]


def _hex_rgb(hex_value: str) -> tuple[int, int, int]:
    value = hex_value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def colour_checks(spec: BriefSpec, frames: list[tuple[float, Path]]) -> list[QACheck]:
    """Is each palette colour present on screen in at least one frame?"""
    import numpy as np
    from PIL import Image

    if not frames:
        return []
    arrays = []
    for _, path in frames:
        image = Image.open(path).convert("RGB")
        image.thumbnail((640, 640))
        arrays.append((path, np.asarray(image, dtype=np.float32).reshape(-1, 3)))
    checks = []
    for colour in spec.palette:
        target = np.array(_hex_rgb(colour.hex), dtype=np.float32)
        tolerance = EXACT_TOLERANCE if colour.exact else APPROX_TOLERANCE
        best_path, best = None, 0.0
        for path, pixels in arrays:
            coverage = float((np.linalg.norm(pixels - target, axis=1) <= tolerance).mean())
            if coverage > best:
                best_path, best = path, coverage
        checks.append(QACheck(
            field=f"palette:{colour.role}", field_type="colour", method="pixel",
            expected=f"{colour.hex} on screen ({'exact' if colour.exact else 'approximate'}, "
                     f"RGB distance <= {tolerance:g})",
            observed=f"best coverage {best:.4%}",
            passed=best >= MIN_COVERAGE,
            frame=best_path.name if best_path else None))
    return checks


def merge_report(loop: int, *groups: list[QACheck]) -> QAReport:
    checks: list[QACheck] = []
    for group in groups:
        checks.extend(group)
    return QAReport(loop=loop, checks=checks)


def failure_text(report: QAReport) -> str:
    lines = []
    for n, check in enumerate(report.failures, 1):
        where = f" (frame {check.frame})" if check.frame else ""
        lines.append(f"{n}. [{check.field_type}] {check.field}: expected {check.expected}; "
                     f"observed {check.observed}{where}. {check.note}".rstrip())
    return "\n".join(lines)
