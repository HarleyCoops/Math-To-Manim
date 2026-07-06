"""MCP server: tool registry and offline tool calls."""

import asyncio
import json

import pytest

pytest.importorskip("mcp")

from mythos import mcp_server  # noqa: E402
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
def isolated_service(tmp_path, monkeypatch):
    service = MythosService(runs_dir=tmp_path / "runs")
    monkeypatch.setattr(mcp_server, "_service", service)
    return service


def test_all_tools_registered():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    names = {tool.name for tool in tools}
    assert EXPECTED_TOOLS <= names
    for tool in tools:
        assert tool.description, f"{tool.name} has no description"


def test_create_and_inspect_animation_offline(isolated_service):
    raw = mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(
            prompt="explain euler's identity", offline=True))
    job = json.loads(raw)
    assert job["status"] in {"running", "completed"}

    for _ in range(100):
        polled = json.loads(mcp_server.m2m_get_job(job["id"]))
        if polled["status"] in {"completed", "failed"}:
            break
        import time
        time.sleep(0.1)
    assert polled["status"] == "completed"

    run_id = polled["run_id"]
    runs = json.loads(mcp_server.m2m_list_runs(mcp_server.ListRunsInput()))
    assert runs[0]["run_id"] == run_id

    detail = json.loads(mcp_server.m2m_get_run(
        mcp_server.RunIdInput(run_id=run_id)))
    assert "mythos_scene.py" in detail["artifacts"]

    code = mcp_server.m2m_get_scene_code(mcp_server.RunIdInput(run_id=run_id))
    assert "ThreeDScene" in code


def test_charter_tool():
    charter = mcp_server.m2m_cinematic_charter()
    assert "CAMERA IS THE NARRATOR" in charter


def test_error_paths_return_actionable_messages():
    assert mcp_server.m2m_get_job("nope").startswith("Error:")
    missing = mcp_server.m2m_get_run(mcp_server.RunIdInput(run_id="ghost"))
    assert missing.startswith("Error:")
