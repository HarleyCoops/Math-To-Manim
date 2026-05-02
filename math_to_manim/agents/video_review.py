"""Visual review stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RenderResult, ValidationIssue, VideoReviewReport
from math_to_manim.review import score_video_file


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
        score = score_video_file(render_result.output_path)
        return VideoReviewReport(
            approved=score.passed,
            score=score.score,
            observations=[item.reason for item in score.items],
            issues=[],
            recommendations=[] if score.passed else ["Check duration, resolution, and whether the rendered file is non-empty."],
            metadata={"score_items": [item.__dict__ for item in score.items]},
        )
