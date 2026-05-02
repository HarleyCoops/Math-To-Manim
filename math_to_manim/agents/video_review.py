"""Visual review stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RenderResult, ValidationIssue, VideoReviewReport
from math_to_manim.rendering import extract_frame, make_contact_sheet, probe_video
from math_to_manim.review import score_video_file, score_video_probe


class VideoReviewAgent(StageAgent[RenderResult, VideoReviewReport]):
    name = "video_review"

    def run(self, render_result: RenderResult) -> VideoReviewReport:
        if render_result.status != "succeeded" or not render_result.output_path:
            return VideoReviewReport(
                approved=False,
                score=0.0,
                observations=["Render did not produce a video artifact."],
                issues=[
                    ValidationIssue(
                        code="render-missing",
                        message=render_result.stderr or "No render output path was available.",
                        severity="warning",
                    )
                ],
                recommendations=["Run Manim after local dependencies are installed, then rerun video review."],
                metadata={"render_status": render_result.status},
            )
        video_path = Path(render_result.output_path)
        probe = probe_video(video_path)
        if probe.ok:
            score = score_video_probe(
                probe,
                file_size_bytes=video_path.stat().st_size,
                min_duration_seconds=1.0,
                min_width=640,
                min_height=360,
            )
        else:
            score = score_video_file(video_path)
        draft_review = _write_draft_review_handoff(video_path, probe, [item.reason for item in score.items])
        render_integrity_passed = score.passed
        recommendations = _draft_recommendations(render_integrity_passed, draft_review)
        issues = []
        if not render_integrity_passed:
            issues.append(
                ValidationIssue(
                    code="render-integrity",
                    message="Rendered video did not pass basic duration/resolution/file-size checks.",
                    severity="warning",
                    artifact=str(video_path),
                )
            )
        issues.append(
            ValidationIssue(
                code="draft-review-required",
                message="First-pass renders are treated as drafts until an editor or vision review checks the frame samples.",
                severity="info",
                artifact=draft_review.get("notes_path"),
            )
        )
        return VideoReviewReport(
            approved=False,
            score=score.score,
            observations=[item.reason for item in score.items],
            issues=issues,
            recommendations=recommendations,
            metadata={
                "score_items": [item.__dict__ for item in score.items],
                "probe_ok": probe.ok,
                "probe_reason": probe.reason,
                "render_integrity_passed": render_integrity_passed,
                "review_mode": "draft_editor_review",
                "requires_editor_review": True,
                "draft_review": draft_review,
            },
        )


def _write_draft_review_handoff(video_path: Path, probe: object, score_observations: list[str]) -> dict[str, object]:
    run_dir = _infer_run_dir(video_path)
    review_dir = run_dir / "draft_review"
    frame_dir = review_dir / "frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    duration = getattr(probe, "duration_seconds", None)
    timestamps = _sample_timestamps(duration)
    frame_paths: list[str] = []
    asset_warnings: list[str] = []
    for index, timestamp in enumerate(timestamps, start=1):
        frame_path = frame_dir / f"frame_{index:02d}_{int(timestamp):03d}s.png"
        result = extract_frame(video_path, frame_path, timestamp_seconds=timestamp)
        if result.ok and result.output_path:
            frame_paths.append(str(result.output_path))
        elif result.reason:
            asset_warnings.append(f"frame {index}: {result.reason}")

    contact_path = review_dir / "contact_sheet.png"
    contact_interval = max((float(duration) / 9.0) if duration else 10.0, 1.0)
    contact = make_contact_sheet(video_path, contact_path, interval_seconds=contact_interval, columns=3, rows=3)
    contact_sheet = str(contact.output_path) if contact.ok and contact.output_path else None
    if not contact.ok and contact.reason:
        asset_warnings.append(f"contact sheet: {contact.reason}")

    notes_path = review_dir / "draft_review.md"
    notes_path.write_text(
        _draft_review_markdown(
            video_path=video_path,
            contact_sheet=contact_sheet,
            frame_paths=frame_paths,
            score_observations=score_observations,
            asset_warnings=asset_warnings,
        ),
        encoding="utf-8",
    )
    return {
        "directory": str(review_dir),
        "notes_path": str(notes_path),
        "contact_sheet": contact_sheet,
        "sample_frames": frame_paths,
        "asset_warnings": asset_warnings,
    }


def _infer_run_dir(video_path: Path) -> Path:
    for parent in video_path.parents:
        if parent.name == "media":
            return parent.parent
    return video_path.parent


def _sample_timestamps(duration_seconds: float | None) -> list[float]:
    if not duration_seconds or duration_seconds <= 1.0:
        return [0.0]
    fractions = (0.05, 0.18, 0.32, 0.50, 0.68, 0.85, 0.95)
    return [max(0.0, min(duration_seconds - 0.1, duration_seconds * fraction)) for fraction in fractions]


def _draft_recommendations(render_integrity_passed: bool, draft_review: dict[str, object]) -> list[str]:
    recommendations = []
    if not render_integrity_passed:
        recommendations.append("Fix render integrity first: duration, resolution, or non-empty output failed.")
    recommendations.extend(
        [
            f"Open the draft review notes: {draft_review.get('notes_path')}",
            "Inspect the contact sheet and sampled frames for stale overlays, cropped text, dim contrast, clutter, and missing requested visuals.",
            "Use the observations as input to the next repair/edit loop; this stage intentionally does not treat a first render as final approval.",
        ]
    )
    return recommendations


def _draft_review_markdown(
    *,
    video_path: Path,
    contact_sheet: str | None,
    frame_paths: list[str],
    score_observations: list[str],
    asset_warnings: list[str],
) -> str:
    lines = [
        "# Draft Render Review",
        "",
        "This is the natural second stage after the first successful render. Treat the video as a draft, not a final approval.",
        "",
        f"- Video: `{video_path}`",
        f"- Contact sheet: `{contact_sheet or 'not created'}`",
        "",
        "## Basic Checks",
        "",
    ]
    lines.extend(f"- {observation}" for observation in score_observations)
    lines.extend(
        [
            "",
            "## Sample Frames",
            "",
        ]
    )
    if frame_paths:
        lines.extend(f"- `{path}`" for path in frame_paths)
    else:
        lines.append("- No sample frames were created.")
    lines.extend(
        [
            "",
            "## Improvement Pass Checklist",
            "",
            "- Look for stale labels or equations that remain after their scene ends.",
            "- Look for cropped, offscreen, overlapping, or distorted text.",
            "- Check that formulas are readable long enough to understand.",
            "- Check that the requested visual metaphor is present, not replaced by generic title cards.",
            "- Check that color contrast and brightness make the main objects visible.",
            "- Check that the pacing leaves room for the target audience.",
            "- Check that the final video has a coherent teaching arc rather than disconnected scenes.",
            "",
            "## Current Limitation",
            "",
            "This stage creates review assets and a checklist. Vision-based scoring and automatic visual repair are the next loop.",
        ]
    )
    if asset_warnings:
        lines.extend(["", "## Asset Warnings", ""])
        lines.extend(f"- {warning}" for warning in asset_warnings)
    return "\n".join(lines) + "\n"
