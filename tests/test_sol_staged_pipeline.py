import io
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from sol.agents import AGENT_STAGES, build_stage_prompt
from sol.cli import build_parser
from sol.client import CodexCli
from sol.harness import SolHarness
from sol.models import ARTIFACT_NAMES, RunRequest, StageRunResult
from sol.rendering import (
    RenderOutcome,
    build_manim_command,
    find_final_video,
    render_environment,
)
from sol.staged import StagedPipeline, stage_input_hash
from sol.validation import validate_run


def _completed_result() -> dict:
    return {
        "status": "completed",
        "scene_file": "sol_scene.py",
        "scene_name": "ExampleScene",
        "artifacts": list(ARTIFACT_NAMES),
        "rendered": False,
        "video_path": None,
        "checks": ["structured output"],
        "notes": [],
    }


def test_codex_resume_command_targets_existing_thread(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "/usr/bin/codex")

    command = CodexCli().build_command(
        cwd=tmp_path,
        schema_path=tmp_path / "schema.json",
        output_path=tmp_path / "result.json",
        session_id="thread-1038",
    )

    assert command[command.index("exec") + 1 : command.index("--model")] == [
        "resume",
        "thread-1038",
    ]


def test_codex_streams_jsonl_events_to_trace_and_sink(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "/usr/bin/codex")
    observed: dict = {}

    class FakeProcess:
        def __init__(self):
            self.stdin = io.StringIO()
            self.stdout = io.StringIO(
                '{"type":"thread.started","thread_id":"thread-1038"}\n'
                '{"type":"turn.completed","usage":{"input_tokens":12}}\n'
            )
            self.stderr = io.StringIO("startup warning\n")
            self.returncode = 0

        def wait(self, timeout=None):
            # CodexCli streams stdout to the trace from a daemon thread it only
            # joins after wait() returns, so nothing orders that thread against
            # this call. Poll instead of reading once: the point of the
            # assertion is that the trace fills during the run rather than
            # afterwards, and a bare read just races the reader thread.
            trace = tmp_path / "trace.jsonl"
            deadline = time.monotonic() + 10.0
            text = ""
            while time.monotonic() < deadline:
                if trace.is_file():
                    text = trace.read_text(encoding="utf-8")
                    if "thread.started" in text:
                        break
                time.sleep(0.01)
            observed["trace_during_wait"] = text
            return self.returncode

        def kill(self):
            self.returncode = -9

    def fake_popen(command, **kwargs):
        observed["command"] = command
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text(json.dumps(_completed_result()), encoding="utf-8")
        return FakeProcess()

    monkeypatch.setattr("sol.client.subprocess.Popen", fake_popen)
    events: list[dict] = []

    result = CodexCli().run(
        "make a film",
        cwd=tmp_path,
        schema_path=tmp_path / "schema.json",
        output_path=tmp_path / "result.json",
        trace_path=tmp_path / "trace.jsonl",
        event_sink=events.append,
    )

    assert result.status == "completed"
    assert [event["type"] for event in events] == [
        "thread.started",
        "turn.completed",
    ]
    assert "thread.started" in observed["trace_during_wait"]
    assert (tmp_path / "trace.jsonl").read_text(encoding="utf-8").count("\n") == 2


def test_six_sol_agents_have_explicit_artifacts_and_dependencies():
    assert [stage.name for stage in AGENT_STAGES] == [
        "intent",
        "cartographer",
        "curriculum",
        "math-director",
        "cinematographer",
        "scene-composer",
    ]
    by_name = {stage.name: stage for stage in AGENT_STAGES}
    assert by_name["intent"].artifacts == ("01_intent.json",)
    assert by_name["cartographer"].dependencies == ("intent",)
    assert by_name["curriculum"].dependencies == ("cartographer",)
    assert by_name["math-director"].dependencies == ("intent",)
    assert by_name["cinematographer"].dependencies == (
        "curriculum",
        "math-director",
    )
    assert by_name["scene-composer"].artifacts == (
        "06_scene_spec.json",
        "sol_scene.py",
    )

    all_writes = [
        artifact
        for stage in AGENT_STAGES
        for artifact in stage.artifacts
    ]
    assert len(all_writes) == len(set(all_writes))


def test_stage_prompt_is_sol_native_and_limits_writes(tmp_path):
    stage = next(stage for stage in AGENT_STAGES if stage.name == "cinematographer")
    prompt = build_stage_prompt(
        stage,
        RunRequest(prompt="explain a theorem"),
        run_dir=tmp_path,
    )

    assert "GPT-5.6 Sol" in prompt
    assert "05_shot_list.json" in prompt
    assert "03_curriculum.json" in prompt
    assert "04_math_dossier.json" in prompt
    assert "Do not write any other file" in prompt
    assert "Mythos" not in prompt
    assert all("Mythos" not in item.charter for item in AGENT_STAGES)


def test_stage_result_schema_is_strict():
    schema = StageRunResult.model_json_schema()

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])


def test_offline_run_records_all_six_stages(tmp_path):
    manifest = SolHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="explain a theorem", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]

    assert manifest["execution_mode"] == "staged"
    assert manifest["stage_records"] == [
        f"stages/{index:02d}-{stage.name}.json"
        for index, stage in enumerate(AGENT_STAGES, start=1)
    ]
    for relative in manifest["stage_records"]:
        record = json.loads((run_dir / relative).read_text(encoding="utf-8"))
        assert record["status"] == "completed"
        assert record["input_hash"]
        assert record["artifact_hashes"]
        assert record["thread_id"] is None


def test_stage_hash_changes_with_upstream_artifact():
    request = RunRequest(prompt="explain a theorem")
    stage = next(item for item in AGENT_STAGES if item.name == "curriculum")

    first = stage_input_hash(stage, request, {"02_knowledge_map.json": "aaa"})
    second = stage_input_hash(stage, request, {"02_knowledge_map.json": "bbb"})

    assert first != second
    assert first == stage_input_hash(
        stage,
        request,
        {"02_knowledge_map.json": "aaa"},
    )


class FakeStageClient:
    model = "gpt-5.6-sol"

    def __init__(self):
        self.calls: list[tuple[str, str | None]] = []
        self.prompts: list[str] = []

    def run(
        self,
        prompt,
        *,
        cwd,
        schema_path,
        output_path,
        trace_path,
        event_sink=None,
        session_id=None,
        reasoning_effort=None,
        result_model=None,
    ):
        role = next(
            stage.name
            for stage in AGENT_STAGES
            if f"You are the {stage.name} specialist" in prompt
        )
        stage = next(stage for stage in AGENT_STAGES if stage.name == role)
        self.calls.append((role, session_id))
        self.prompts.append(prompt)
        if event_sink:
            event_sink(
                {
                    "type": "thread.started",
                    "thread_id": session_id or f"thread-{role}",
                }
            )
        for artifact in stage.artifacts:
            path = cwd / artifact
            if artifact.endswith(".json"):
                path.write_text(
                    json.dumps({"role": role, "content": ["checked"]}),
                    encoding="utf-8",
                )
            else:
                path.write_text(
                    "from manim import *\n\nclass ExampleScene(Scene):\n    pass\n",
                    encoding="utf-8",
                )
        result = StageRunResult(
            status="completed",
            role=role,
            artifacts=list(stage.artifacts),
            summary=f"{role} complete",
            checks=["artifact written"],
            notes=[],
        )
        output_path.write_text(result.model_dump_json(), encoding="utf-8")
        trace_path.touch(exist_ok=True)
        return result


def test_staged_pipeline_caches_completed_agents_and_resumes_from_named_stage(tmp_path):
    client = FakeStageClient()
    request = RunRequest(prompt="explain a theorem")
    pipeline = StagedPipeline(client=client)

    pipeline.run(tmp_path, request)
    assert {role for role, _ in client.calls} == {
        stage.name for stage in AGENT_STAGES
    }
    assert all(
        json.loads(path.read_text(encoding="utf-8"))["thread_id"]
        for path in (tmp_path / "stages").glob("[0-9][0-9]-*.json")
        if not path.name.endswith("-result.json")
    )

    initial_call_count = len(client.calls)
    pipeline.run(tmp_path, request)
    assert len(client.calls) == initial_call_count

    pipeline.run(tmp_path, request, from_stage="cinematographer")
    resumed = client.calls[initial_call_count:]
    assert [role for role, _ in resumed] == [
        "cinematographer",
        "scene-composer",
    ]
    assert resumed[0][1] == "thread-cinematographer"
    assert resumed[1][1] == "thread-scene-composer"


def test_staged_pipeline_runs_independent_branches_in_parallel(tmp_path):
    class ParallelClient(FakeStageClient):
        def __init__(self):
            super().__init__()
            self.branch_barrier = threading.Barrier(2)

        def run(self, prompt, **kwargs):
            role = next(
                stage.name
                for stage in AGENT_STAGES
                if f"You are the {stage.name} specialist" in prompt
            )
            if role in {"cartographer", "math-director"}:
                self.branch_barrier.wait(timeout=2)
            return super().run(prompt, **kwargs)

    client = ParallelClient()

    StagedPipeline(client=client).run(
        tmp_path,
        RunRequest(prompt="explain a theorem"),
    )

    assert client.branch_barrier.n_waiting == 0


def test_cli_parses_resume_and_status_commands():
    parser = build_parser()

    resume = parser.parse_args(
        ["resume", "20260723-example", "--from", "cinematographer"]
    )
    status = parser.parse_args(["status", "20260723-example"])

    assert resume.command == "resume"
    assert resume.from_stage == "cinematographer"
    assert status.command == "status"
    with pytest.raises(SystemExit):
        parser.parse_args(["resume", "run", "--from", "unknown"])


def test_manim_command_uses_active_python_and_run_local_media(tmp_path):
    command = build_manim_command(
        tmp_path,
        scene_name="ErdosScene",
        quality="l",
    )

    assert command[:3] == [sys.executable, "-m", "manim"]
    assert "-ql" in command
    assert command[command.index("--media_dir") + 1] == str(tmp_path / "media")
    assert command[-2:] == ["sol_scene.py", "ErdosScene"]


def test_render_environment_keeps_miktex_writes_inside_run(tmp_path):
    env = render_environment(tmp_path, {"PATH": "example"})

    assert env["PATH"] == "example"
    assert env["MIKTEX_USERCONFIG"].startswith(str(tmp_path))
    assert env["MIKTEX_USERDATA"].startswith(str(tmp_path))
    assert env["MIKTEX_USERINSTALL"].startswith(str(tmp_path))


def test_final_video_selection_ignores_partial_movie_fragments(tmp_path):
    partial = (
        tmp_path
        / "media"
        / "videos"
        / "scene"
        / "480p15"
        / "partial_movie_files"
        / "Example"
        / "fragment.mp4"
    )
    final = tmp_path / "media" / "videos" / "scene" / "480p15" / "Example.mp4"
    partial.parent.mkdir(parents=True)
    final.parent.mkdir(parents=True, exist_ok=True)
    partial.write_bytes(b"x" * 2048)
    final.write_bytes(b"y" * 4096)

    assert find_final_video(tmp_path) == final


def test_run_validator_reports_final_video_not_partial_fragment(tmp_path):
    for name in ARTIFACT_NAMES:
        path = tmp_path / name
        if name == "sol_scene.py":
            path.write_text(
                "from manim import *\n\nclass ExampleScene(Scene):\n    pass\n",
                encoding="utf-8",
            )
        else:
            path.write_text('{"ok": true}', encoding="utf-8")
    partial = (
        tmp_path
        / "media"
        / "videos"
        / "scene"
        / "480p15"
        / "partial_movie_files"
        / "ExampleScene"
        / "fragment.mp4"
    )
    final = tmp_path / "media" / "videos" / "scene" / "480p15" / "ExampleScene.mp4"
    partial.parent.mkdir(parents=True)
    final.parent.mkdir(parents=True, exist_ok=True)
    partial.write_bytes(b"x" * 2048)
    final.write_bytes(b"y" * 4096)

    failures, _, video_path = validate_run(tmp_path, require_video=True)

    assert failures == []
    assert video_path == "media/videos/scene/480p15/ExampleScene.mp4"


def test_scene_repair_prompt_reuses_thread_and_includes_render_evidence(tmp_path):
    client = FakeStageClient()
    request = RunRequest(prompt="explain a theorem")
    pipeline = StagedPipeline(client=client)
    pipeline.run(tmp_path, request)
    initial = len(client.calls)

    pipeline.run(
        tmp_path,
        request,
        from_stage="scene-composer",
        feedback={"scene-composer": "MathTex failed at line 81"},
    )

    assert client.calls[initial:] == [
        ("scene-composer", "thread-scene-composer")
    ]
    assert "MathTex failed at line 81" in client.prompts[-1]


def test_render_review_returns_to_saved_cinematographer_thread(tmp_path):
    class ReviewClient(FakeStageClient):
        def run(self, prompt, **kwargs):
            if "render-review continuation" not in prompt:
                return super().run(prompt, **kwargs)
            session_id = kwargs["session_id"]
            self.calls.append(("cinematographer-review", session_id))
            self.prompts.append(prompt)
            if kwargs["event_sink"]:
                kwargs["event_sink"](
                    {
                        "type": "thread.started",
                        "thread_id": session_id,
                    }
                )
            review = {
                "status": "approved",
                "defects": [],
                "observations": ["off-white 3D composition is readable"],
                "evidence": ["review_frames/contact_sheet.png"],
            }
            (kwargs["cwd"] / "review.json").write_text(
                json.dumps(review),
                encoding="utf-8",
            )
            result = StageRunResult(
                status="completed",
                role="cinematographer",
                artifacts=["review.json"],
                summary="render approved",
                checks=["contact sheet inspected"],
                notes=[],
            )
            kwargs["output_path"].write_text(
                result.model_dump_json(),
                encoding="utf-8",
            )
            kwargs["trace_path"].touch(exist_ok=True)
            return result

    client = ReviewClient()
    request = RunRequest(prompt="explain a theorem", render=True)
    pipeline = StagedPipeline(client=client)
    pipeline.run(tmp_path, request)
    review_dir = tmp_path / "review_frames"
    review_dir.mkdir()
    contact_sheet = review_dir / "contact_sheet.png"
    contact_sheet.write_bytes(b"image")

    review = pipeline.review_render(
        tmp_path,
        request,
        evidence_paths=[contact_sheet],
    )

    assert review["status"] == "approved"
    assert client.calls[-1] == (
        "cinematographer-review",
        "thread-cinematographer",
    )


def test_harness_renders_then_reviews_with_saved_cinematographer(
    monkeypatch,
    tmp_path,
):
    class ReviewClient(FakeStageClient):
        def run(self, prompt, **kwargs):
            if "render-review continuation" not in prompt:
                return super().run(prompt, **kwargs)
            self.calls.append(("cinematographer-review", kwargs["session_id"]))
            self.prompts.append(prompt)
            (kwargs["cwd"] / "review.json").write_text(
                json.dumps(
                    {
                        "status": "approved",
                        "defects": [],
                        "observations": ["accepted"],
                        "evidence": ["review_frames/contact_sheet.png"],
                    }
                ),
                encoding="utf-8",
            )
            result = StageRunResult(
                status="completed",
                role="cinematographer",
                artifacts=["review.json"],
                summary="approved",
                checks=["visual review"],
                notes=[],
            )
            kwargs["output_path"].write_text(result.model_dump_json(), encoding="utf-8")
            kwargs["trace_path"].touch(exist_ok=True)
            return result

    calls: list[str] = []

    def fake_preflight():
        calls.append("preflight")
        return ["Manim: test"]

    def fake_render(run_dir, *, scene_name, quality):
        calls.append(f"render:{scene_name}:{quality}")
        video = run_dir / "media" / "videos" / "scene" / "480p15" / "ExampleScene.mp4"
        video.parent.mkdir(parents=True)
        video.write_bytes(b"v" * 4096)
        review_dir = run_dir / "review_frames"
        review_dir.mkdir()
        frame = review_dir / "frame_01.png"
        sheet = review_dir / "contact_sheet.png"
        frame.write_bytes(b"frame")
        sheet.write_bytes(b"sheet")
        return RenderOutcome(
            video_path=video,
            stdout_path=run_dir / "render_stdout.log",
            stderr_path=run_dir / "render_stderr.log",
            frame_paths=(frame,),
            contact_sheet_path=sheet,
        )

    monkeypatch.setattr("sol.harness.preflight_render", fake_preflight, raising=False)
    monkeypatch.setattr("sol.harness.render_scene", fake_render, raising=False)
    client = ReviewClient()

    manifest = SolHarness(runs_dir=tmp_path, client=client).run(
        RunRequest(
            prompt="explain a theorem",
            render=True,
            max_repairs=1,
        )
    )

    assert manifest["status"] == "completed"
    assert manifest["video_path"].endswith("ExampleScene.mp4")
    assert calls == ["preflight", "render:ExampleScene:l"]
    assert client.calls[-1] == (
        "cinematographer-review",
        "thread-cinematographer",
    )
