import io
import json
import subprocess
import threading
from pathlib import Path

import pytest

from sol.agents import AGENT_STAGES, build_stage_prompt
from sol.cli import build_parser
from sol.client import CodexCli
from sol.harness import SolHarness
from sol.models import ARTIFACT_NAMES, RunRequest, StageRunResult
from sol.staged import StagedPipeline, stage_input_hash


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
            observed["trace_during_wait"] = (
                tmp_path / "trace.jsonl"
            ).read_text(encoding="utf-8")
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
