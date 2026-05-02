"""Final package assembly stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import AnimationPackage, RenderResult, UserRequest, VideoReviewReport


class PublisherAgent(StageAgent[tuple[UserRequest, Path, RenderResult, VideoReviewReport, list[str]], AnimationPackage]):
    name = "publisher"

    def run(self, value: tuple[UserRequest, Path, RenderResult, VideoReviewReport, list[str]]) -> AnimationPackage:
        request, run_dir, render_result, review_report, reports = value
        return AnimationPackage(
            request=request,
            render_result=render_result,
            video_review_report=review_report,
            metadata={
                "final_code_path": str(run_dir / "generated_scene.py"),
                "final_video_path": render_result.output_path,
                "gif_path": None,
                "thumbnail_path": None,
                "reports": reports,
                "readme_snippet": f"Generated animation package for: {request.prompt}",
                "run_trace": str(run_dir / "trace.jsonl"),
                "reproducibility_manifest": str(run_dir / "manifest.json"),
                "review_passed": review_report.approved,
                "draft_review": review_report.metadata.get("draft_review"),
            },
        )
