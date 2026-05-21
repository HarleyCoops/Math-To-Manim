from __future__ import annotations

import json
from pathlib import Path

from math_to_manim.cli import main
from math_to_manim.rendering.commands import ToolResult
from math_to_manim.schemas import GeneratedCode, RenderResult, VideoReviewReport


SCENE_CODE = "from manim import Scene\nclass DemoScene(Scene):\n    def construct(self):\n        self.wait()\n"


def test_render_run_renders_existing_bundle(monkeypatch, tmp_path) -> None:
    run_dir = _write_run_bundle(tmp_path)
    rendered_video = run_dir / "media" / "videos" / "generated_scene" / "1080p30" / "DemoScene.mp4"
    seen_kwargs = {}

    def fake_render_manim_scene(*args, **kwargs) -> ToolResult:
        seen_kwargs.update(kwargs)
        rendered_video.parent.mkdir(parents=True)
        rendered_video.write_bytes(b"video")
        return ToolResult(
            ok=True,
            skipped=False,
            command=("python", "-m", "manim", "-ql", str(run_dir / "generated_scene.py"), "DemoScene"),
            returncode=0,
            stdout="rendered",
            output_path=rendered_video,
        )

    monkeypatch.setattr("math_to_manim.agents.render.render_manim_scene", fake_render_manim_scene)

    exit_code = main(["render-run", str(run_dir), "--quality", "l", "--manim-command", "python -m manim"])

    assert exit_code == 0
    validation = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
    render = json.loads((run_dir / "render_result.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert render["status"] == "succeeded"
    assert render["output_path"] == str(rendered_video)
    assert seen_kwargs["manim_command"] == ("python", "-m", "manim")
    assert "validation_report" in manifest["artifacts"]
    assert "render_result" in manifest["artifacts"]


def test_review_run_reviews_existing_render(monkeypatch, tmp_path) -> None:
    run_dir = _write_run_bundle(tmp_path)
    render = RenderResult(
        status="succeeded",
        scene_name="DemoScene",
        output_path=str(run_dir / "media" / "DemoScene.mp4"),
        command=["python", "-m", "manim"],
    )
    (run_dir / "render_result.json").write_text(json.dumps(render.to_public_dict()), encoding="utf-8")

    def fake_review(self, render_result: RenderResult) -> VideoReviewReport:
        return VideoReviewReport(
            approved=False,
            score=1.0,
            observations=["ok"],
            metadata={"draft_review": {"notes_path": str(run_dir / "draft_review.md"), "contact_sheet": None}},
        )

    monkeypatch.setattr("math_to_manim.cli.VideoReviewAgent.run", fake_review)

    exit_code = main(["review-run", str(run_dir)])

    assert exit_code == 0
    review = json.loads((run_dir / "review_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert review["score"] == 1.0
    assert "review_report" in manifest["artifacts"]


def test_recover_render_runs_render_review_and_manifest(monkeypatch, tmp_path) -> None:
    run_dir = _write_run_bundle(tmp_path)
    rendered_video = run_dir / "media" / "videos" / "generated_scene" / "1080p30" / "DemoScene.mp4"

    def fake_render_manim_scene(*args, **kwargs) -> ToolResult:
        rendered_video.parent.mkdir(parents=True)
        rendered_video.write_bytes(b"video")
        return ToolResult(
            ok=True,
            skipped=False,
            command=("python", "-m", "manim", "-ql", str(run_dir / "generated_scene.py"), "DemoScene"),
            returncode=0,
            stdout="rendered",
            output_path=rendered_video,
        )

    def fake_review(self, render_result: RenderResult) -> VideoReviewReport:
        return VideoReviewReport(
            approved=False,
            score=0.75,
            observations=["draft"],
            metadata={
                "draft_review": {
                    "notes_path": str(run_dir / "draft_review" / "draft_review.md"),
                    "contact_sheet": str(run_dir / "draft_review" / "contact_sheet.png"),
                }
            },
        )

    monkeypatch.setattr("math_to_manim.agents.render.render_manim_scene", fake_render_manim_scene)
    monkeypatch.setattr("math_to_manim.cli.VideoReviewAgent.run", fake_review)

    exit_code = main(["recover-render", str(run_dir), "--quality", "l", "--manim-command", "python -m manim"])

    assert exit_code == 0
    render = json.loads((run_dir / "render_result.json").read_text(encoding="utf-8"))
    review = json.loads((run_dir / "review_report.json").read_text(encoding="utf-8"))
    recovery = json.loads((run_dir / "recovery_manifest.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert render["status"] == "succeeded"
    assert review["score"] == 0.75
    assert recovery["render_status"] == "succeeded"
    assert recovery["artifacts"]["contact_sheet"].endswith("contact_sheet.png")
    assert "recovery_manifest" in manifest["artifacts"]


def _write_run_bundle(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    generated = GeneratedCode(
        scene_name="DemoScene",
        code=SCENE_CODE,
        dependencies=["manim"],
        metadata={"file_path": "generated_scene.py"},
    )
    (run_dir / "generated_code.json").write_text(
        json.dumps(generated.to_public_dict(), indent=2),
        encoding="utf-8",
    )
    (run_dir / "generated_scene.py").write_text(SCENE_CODE, encoding="utf-8")
    (run_dir / "manifest.json").write_text(
        json.dumps({"run_dir": str(run_dir), "artifacts": ["generated_code"]}),
        encoding="utf-8",
    )
    return run_dir
