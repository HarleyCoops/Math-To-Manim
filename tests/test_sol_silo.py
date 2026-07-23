import json
import os
import subprocess
from pathlib import Path

import pytest

from sol.cli import build_parser
from sol.client import CodexCli, CodexCliError
from sol.harness import SolHarness
from sol.models import ARTIFACT_NAMES, RunRequest
from sol.service import SolService
from sol.validation import validate_run


def test_offline_run_writes_complete_film_bundle(tmp_path):
    manifest = SolHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="explain the heat equation", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["status"] == "completed"
    assert manifest["backend"] == "codex-cli"
    assert all((run_dir / name).is_file() for name in ARTIFACT_NAMES)
    assert json.loads((run_dir / "02_knowledge_map.json").read_text())["topic"]
    failures, scene_name, video_path = validate_run(run_dir, require_video=False)
    assert failures == []
    assert scene_name == "SolOfflineScene"
    assert video_path is None


def test_codex_command_is_cli_native(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "/usr/bin/codex")
    client = CodexCli(model="gpt-5.6-sol", reasoning_effort="xhigh")
    command = client.build_command(
        cwd=tmp_path,
        schema_path=tmp_path / "schema.json",
        output_path=tmp_path / "result.json",
    )
    assert command[0] == "/usr/bin/codex"
    assert "exec" in command
    assert command[command.index("--model") + 1] == "gpt-5.6-sol"
    assert command[command.index("--sandbox") + 1] == "workspace-write"
    assert {"--json", "--output-schema", "--output-last-message", "--cd"} <= set(command)
    assert 'model_reasoning_effort="xhigh"' in command
    assert 'service_tier="fast"' in command


def test_doctor_overrides_invalid_global_service_tier(monkeypatch):
    observed = []

    monkeypatch.setattr("sol.cli.CodexCli.resolve", lambda self: "codex")

    def fake_run(command, **kwargs):
        observed.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr("sol.cli.subprocess.run", fake_run)

    from sol.cli import main

    assert main(["doctor"]) == 0
    login_command = next(command for command in observed if "login" in command)
    assert 'service_tier="fast"' in login_command


def test_codex_result_schema_is_strict_for_structured_outputs():
    from sol.models import CodexRunResult

    schema = CodexRunResult.model_json_schema()
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])


def test_codex_failure_preserves_stdout_error_when_stderr_has_warnings(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "/usr/bin/codex")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            1,
            stdout='{"type":"error","message":"invalid_json_schema"}\n',
            stderr="non-fatal startup warning\n",
        )

    monkeypatch.setattr("sol.client.subprocess.run", fake_run)
    with pytest.raises(CodexCliError, match="invalid_json_schema"):
        CodexCli().run(
            "make a film",
            cwd=tmp_path,
            schema_path=tmp_path / "schema.json",
            output_path=tmp_path / "result.json",
            trace_path=tmp_path / "trace.jsonl",
        )
    assert "invalid_json_schema" in (tmp_path / "trace.jsonl").read_text()


def test_codex_child_never_receives_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "/usr/bin/codex")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")
    observed = {}

    def fake_run(command, **kwargs):
        observed["env"] = kwargs["env"]
        output = Path(command[command.index("--output-last-message") + 1])
        output.write_text(json.dumps({
            "status": "completed",
            "scene_file": "sol_scene.py",
            "scene_name": "Example",
            "artifacts": list(ARTIFACT_NAMES),
            "rendered": False,
            "video_path": None,
            "checks": ["ok"],
            "notes": [],
        }))
        return subprocess.CompletedProcess(command, 0, stdout="{}\n", stderr="")

    monkeypatch.setattr("sol.client.subprocess.run", fake_run)
    CodexCli().run(
        "make a film",
        cwd=tmp_path,
        schema_path=tmp_path / "schema.json",
        output_path=tmp_path / "result.json",
        trace_path=tmp_path / "trace.jsonl",
    )
    assert "OPENAI_API_KEY" not in observed["env"]
    assert os.environ["OPENAI_API_KEY"] == "must-not-leak"


def test_validator_blocks_generated_code_with_process_access(tmp_path):
    for name in ARTIFACT_NAMES:
        path = tmp_path / name
        if name == "sol_scene.py":
            path.write_text("from manim import *\nimport subprocess\nclass Bad(Scene):\n    pass\n")
        else:
            path.write_text('{"ok": true}')
    failures, _, _ = validate_run(tmp_path, require_video=False)
    assert any("blocked import 'subprocess'" in failure for failure in failures)


def test_service_reads_run_ledger(tmp_path):
    service = SolService(runs_dir=tmp_path)
    manifest = service.run(RunRequest(prompt="visualize curvature", offline=True))
    assert service.get_run(manifest["run_id"]).status == "completed"
    assert service.list_runs(limit=1)[0].run_id == manifest["run_id"]
    with pytest.raises(ValueError):
        service.get_run("../escape")


def test_cli_surface_has_no_server_or_calculator_commands():
    parser = build_parser()
    args = parser.parse_args(["run", "explain eigenvectors", "--offline"])
    assert args.command == "run"
    assert args.offline is True
    with pytest.raises(SystemExit):
        parser.parse_args(["serve"])
    with pytest.raises(SystemExit):
        parser.parse_args(["calculate", "1+1"])
