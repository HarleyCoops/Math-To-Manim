import io
import json
import subprocess
from pathlib import Path

from sol.agents import AGENT_STAGES, build_stage_prompt
from sol.client import CodexCli
from sol.models import ARTIFACT_NAMES, RunRequest, StageRunResult


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
