from __future__ import annotations

import json
from pathlib import Path

import pytest

from m2m2_visual_improvement.renderer import (
    CandidateRenderError,
    InfrastructureRenderError,
    ProcessResult,
    RenderRequest,
    RenderSettings,
    Renderer,
    parse_ffprobe_duration,
    write_json_atomic,
)


SOURCE = """
from manim import *

class Lesson(Scene):
    def construct(self):
        self.add(Text("Visible"))
"""


class RecordingRunner:
    def __init__(
        self,
        result: ProcessResult | None = None,
        *,
        create_video: bool = True,
        missing_executable: bool = False,
    ):
        self.result = result or ProcessResult(
            returncode=0,
            stdout="rendered",
            stderr="",
            timed_out=False,
        )
        self.create_video = create_video
        self.missing_executable = missing_executable
        self.calls: list[dict[str, object]] = []

    def run(
        self,
        args: tuple[str, ...],
        *,
        cwd: Path,
        timeout_seconds: float,
        env: dict[str, str],
    ) -> ProcessResult:
        self.calls.append(
            {
                "args": args,
                "cwd": cwd,
                "timeout_seconds": timeout_seconds,
                "env": env,
            }
        )
        if self.missing_executable:
            raise FileNotFoundError(args[0])
        if self.create_video and self.result.returncode == 0:
            video = cwd / "media" / "videos" / "lesson" / "480p15" / "Lesson.mp4"
            video.parent.mkdir(parents=True, exist_ok=True)
            video.write_bytes(b"fake-mp4")
        return self.result


def request(tmp_path: Path, *, role: str = "candidate") -> RenderRequest:
    return RenderRequest(
        task_id="scene_01.off_frame_right",
        source_code=SOURCE,
        scene_name="Lesson",
        role=role,
        output_dir=tmp_path / role,
    )


def test_renderer_constructs_exact_low_resolution_manim_command(
    tmp_path: Path,
) -> None:
    runner = RecordingRunner()
    renderer = Renderer(
        runner=runner,
        settings=RenderSettings(
            manim_command=("python", "-m", "manim"),
            width=854,
            height=480,
            fps=15,
            timeout_seconds=90,
        ),
    )

    outcome = renderer.render(request(tmp_path))

    call = runner.calls[0]
    args = call["args"]
    assert args[:3] == ("python", "-m", "manim")
    assert "-r" in args and args[args.index("-r") + 1] == "854,480"
    assert "--fps" in args and args[args.index("--fps") + 1] == "15"
    assert "--media_dir" in args
    assert args[-1] == "Lesson"
    assert call["timeout_seconds"] == 90
    assert outcome.video_path.read_bytes() == b"fake-mp4"
    assert outcome.role == "candidate"
    assert (tmp_path / "candidate" / "scene.py").read_text(
        encoding="utf-8"
    ) == SOURCE


def test_baseline_and_candidate_outputs_are_separate(tmp_path: Path) -> None:
    renderer = Renderer(runner=RecordingRunner())
    baseline = renderer.render(request(tmp_path, role="baseline"))
    candidate = renderer.render(request(tmp_path, role="candidate"))
    assert baseline.video_path != candidate.video_path
    assert baseline.video_path.is_relative_to(tmp_path / "baseline")
    assert candidate.video_path.is_relative_to(tmp_path / "candidate")


def test_candidate_nonzero_and_timeout_are_model_attributable(
    tmp_path: Path,
) -> None:
    failed = RecordingRunner(
        ProcessResult(
            returncode=1,
            stdout="",
            stderr="OPENAI_API_KEY=secret-value\nrender error",
            timed_out=False,
        ),
        create_video=False,
    )
    renderer = Renderer(
        runner=failed,
        settings=RenderSettings(max_log_chars=96),
    )
    with pytest.raises(CandidateRenderError) as captured:
        renderer.render(request(tmp_path))
    assert "secret-value" not in str(captured.value)
    assert "[REDACTED]" in str(captured.value)

    timed_out = RecordingRunner(
        ProcessResult(
            returncode=None,
            stdout="",
            stderr="",
            timed_out=True,
        ),
        create_video=False,
    )
    with pytest.raises(CandidateRenderError, match="timed out"):
        Renderer(runner=timed_out).render(request(tmp_path / "timeout"))


def test_missing_runtime_and_baseline_failure_are_infrastructure_exclusions(
    tmp_path: Path,
) -> None:
    with pytest.raises(InfrastructureRenderError, match="executable"):
        Renderer(
            runner=RecordingRunner(missing_executable=True)
        ).render(request(tmp_path))

    failed = RecordingRunner(
        ProcessResult(
            returncode=1,
            stdout="",
            stderr="runtime broke",
            timed_out=False,
        ),
        create_video=False,
    )
    with pytest.raises(InfrastructureRenderError, match="baseline"):
        Renderer(runner=failed).render(request(tmp_path, role="baseline"))


def test_success_without_video_is_infrastructure_error(tmp_path: Path) -> None:
    runner = RecordingRunner(create_video=False)
    with pytest.raises(InfrastructureRenderError, match="MP4"):
        Renderer(runner=runner).render(request(tmp_path))


def test_ffprobe_duration_parsing_is_strict() -> None:
    assert parse_ffprobe_duration(
        '{"format":{"duration":"8.125"}}'
    ) == pytest.approx(8.125)
    with pytest.raises(InfrastructureRenderError, match="ffprobe"):
        parse_ffprobe_duration('{"format":{"duration":"not-a-number"}}')


def test_atomic_json_write_replaces_completed_payload(tmp_path: Path) -> None:
    path = tmp_path / "evidence.json"
    write_json_atomic(path, {"status": "first"})
    write_json_atomic(path, {"status": "completed", "count": 2})

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "count": 2,
        "status": "completed",
    }
    assert not path.with_suffix(".json.tmp").exists()
