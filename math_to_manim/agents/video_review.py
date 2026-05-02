"""Visual review stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RenderResult, ValidationIssue, VideoReviewReport
from math_to_manim.rendering import probe_video
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
        probe = probe_video(render_result.output_path)
        if probe.ok:
            score = score_video_probe(
                probe,
                file_size_bytes=Path(render_result.output_path).stat().st_size,
                min_duration_seconds=1.0,
                min_width=640,
                min_height=360,
            )
        else:
            score = score_video_file(render_result.output_path)
        return VideoReviewReport(
            approved=score.passed,
            score=score.score,
            observations=[item.reason for item in score.items],
            issues=[],
            recommendations=[] if score.passed else ["Check duration, resolution, and whether the rendered file is non-empty."],
            metadata={
                "score_items": [item.__dict__ for item in score.items],
                "probe_ok": probe.ok,
                "probe_reason": probe.reason,
            },
        )
