"""MCP server: tool registry and offline tool calls."""

import asyncio
import json
from pathlib import Path

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


def test_tools_expose_typed_mcp2_annotations():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    by_name = {tool.name: tool for tool in tools}

    create = by_name["m2m_create_animation"].annotations
    assert create is not None
    assert create.title == "Create Math Animation"
    assert create.read_only_hint is False
    assert create.open_world_hint is True

    charter = by_name["m2m_cinematic_charter"].annotations
    assert charter is not None
    assert charter.read_only_hint is True
    assert charter.idempotent_hint is True
    assert charter.open_world_hint is False


def test_tool_can_be_called_through_mcp2_server():
    result = asyncio.run(mcp_server.mcp.call_tool(
        "m2m_cinematic_charter", {}))
    assert result.is_error is False
    assert result.content[0].text.startswith("MYTHOS CINEMATIC CHARTER")


def test_mcp2_dependency_and_import_surface():
    root = Path(__file__).resolve().parents[1]
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    source = (root / "mythos/mcp_server.py").read_text(encoding="utf-8")

    assert project.count('"mcp>=2.0,<3"') == 2
    assert "from mcp.server import MCPServer" in source
    assert "mcp.server.fastmcp" not in source
    assert "FastMCP" not in source


def test_server_launches_supported_mcp2_transports(monkeypatch):
    calls = []
    monkeypatch.setattr(
        mcp_server.mcp,
        "run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    mcp_server.main()
    mcp_server.main(transport="streamable-http", port=9000)

    assert calls == [
        ((), {}),
        ((), {
            "transport": "streamable-http",
            "host": "127.0.0.1",
            "port": 9000,
        }),
    ]


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
