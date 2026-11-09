"""Mythos MCP server: the tools run the Mythos chain and return the Mythos job."""

import asyncio
import json
import time
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from mythos import mcp_server  # noqa: E402
from mythos.harness import MythosHarness  # noqa: E402
from mythos.service import MythosService  # noqa: E402

EXPECTED_TOOLS = {
    "m2m_create_animation",
    "m2m_get_job",
    "m2m_list_runs",
    "m2m_get_run",
    "m2m_get_artifact",
    "m2m_get_scene_code",
    "m2m_cinematic_charter",
}


@pytest.fixture(autouse=True)
def isolated_service(tmp_path):
    service = MythosService(runs_dir=tmp_path / "runs")
    mcp_server.set_service(service)
    yield service
    mcp_server.set_service(None)


def _wait_for_job(job_id: str) -> dict:
    polled = {}
    for _ in range(100):
        polled = json.loads(mcp_server.m2m_get_job(job_id))
        if polled["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)
    return polled


def test_all_tools_registered_with_descriptions():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    for tool in tools:
        assert tool.description, f"{tool.name} has no description"


def test_server_is_mythos_native():
    source = (Path(__file__).resolve().parents[1]
              / "src/mythos/mcp_server.py").read_text(encoding="utf-8")
    assert "MythosService" in source
    assert "import grok" not in source
    assert "from grok" not in source


def test_create_and_inspect_animation_offline():
    job = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(prompt="explain euler's identity", offline=True)))
    assert job["status"] in {"running", "completed"}
    assert {"stage", "outcome"} <= set(job)

    polled = _wait_for_job(job["id"])
    assert polled["status"] == "completed"
    assert polled["stage"] is None
    assert polled["outcome"] == "scene_ready"

    run_id = polled["run_id"]
    runs = json.loads(mcp_server.m2m_list_runs(mcp_server.ListRunsInput()))
    assert runs[0]["run_id"] == run_id
    assert runs[0]["status"] == "completed"
    assert runs[0]["outcome"] == "scene_ready"

    detail = json.loads(mcp_server.m2m_get_run(mcp_server.RunIdInput(run_id=run_id)))
    assert "mythos_scene.py" in detail["artifacts"]
    assert detail["manifest"]["status"]["run"] == "completed"

    shots = json.loads(mcp_server.m2m_get_artifact(
        mcp_server.ArtifactInput(run_id=run_id, artifact_name="05_shot_list.json")))
    assert shots["offline"] is True

    code = mcp_server.m2m_get_scene_code(mcp_server.RunIdInput(run_id=run_id))
    assert "ThreeDScene" in code


def test_failed_job_names_the_stage_that_failed(tmp_path, monkeypatch):
    harness = MythosHarness(offline=True, runs_dir=tmp_path / "runs",
                            log=lambda _: None)
    monkeypatch.setattr(
        harness, "_codegen",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no scene")))
    mcp_server.set_service(MythosService(
        runs_dir=harness.runs_dir, harness_factory=lambda **kwargs: harness))

    job = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(prompt="crash in codegen", offline=True)))
    polled = _wait_for_job(job["id"])
    assert polled["status"] == "failed"
    assert polled["stage"] == "codegen"
    assert polled["outcome"] == "chain_failed"
    assert "no scene" in polled["error"]


def test_model_and_command_pass_through_only_when_given():
    defaults = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(prompt="the heat equation", offline=True)))
    assert "model" not in defaults["options"]
    assert "command" not in defaults["options"]
    chosen = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(
            prompt="the heat equation", offline=True,
            model="claude-opus-4-8", command="claude", max_repairs=1)))
    assert chosen["options"]["model"] == "claude-opus-4-8"
    assert chosen["options"]["command"] == "claude"
    assert chosen["options"]["max_repairs"] == 1
    _wait_for_job(defaults["id"])
    _wait_for_job(chosen["id"])


def test_grok_only_fields_are_rejected():
    with pytest.raises(ValueError):
        mcp_server.CreateAnimationInput(prompt="solve this page", image="page.jpg")


def test_charter_and_error_paths():
    charter = asyncio.run(mcp_server.mcp.call_tool("m2m_cinematic_charter", {}))
    assert charter.is_error is False
    assert charter.content[0].text == mcp_server.CINEMATIC_CHARTER
    assert mcp_server.m2m_get_job("nope").startswith("Error:")
    assert mcp_server.m2m_get_run(
        mcp_server.RunIdInput(run_id="ghost")).startswith("Error:")
    assert mcp_server.m2m_get_scene_code(
        mcp_server.RunIdInput(run_id="ghost")).startswith("Error:")


def test_cli_serve_mcp_help_names_mythos():
    from mythos.cli import build_parser

    help_text = build_parser().format_help()
    assert "serve-mcp" in help_text
    assert "Mythos MCP server" in help_text
