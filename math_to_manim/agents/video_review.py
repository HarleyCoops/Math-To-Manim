"""Visual review stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import RenderResult, VideoReviewReport
from math_to_manim.tools.video_tools import review_video_result


class VideoReviewAgent(StageAgent[RenderResult, VideoReviewReport]):
    name = "video_review"

    def run(self, render_result: RenderResult) -> VideoReviewReport:
        return review_video_result(render_result)
