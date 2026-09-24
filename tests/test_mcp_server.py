"""MCP server: tool registry and offline Grok tool calls."""

import asyncio
import json
import time
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from grok.mcp_server import DEFAULT_MCP_MODEL  # noqa: E402
from grok.models import ARTIFACT_NAMES  # noqa: E402
from grok.service import GrokService  # noqa: E402
from grok.validation import validate_reverse_tree  # noqa: E402
from mythos import mcp_server  # noqa: E402

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
    service = GrokService(runs_dir=tmp_path / "runs")
    monkeypatch.setattr("grok.mcp_server._service", service)
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
    assert charter.title == "Get the Grok Cinematic Contract"


def test_tool_can_be_called_through_mcp2_server():
    result = asyncio.run(mcp_server.mcp.call_tool(
        "m2m_cinematic_charter", {}))
    assert result.is_error is False
    text = result.content[0].text
    assert text.startswith("GROK CINEMATIC CONTRACT")
    assert "grok_scene.py" in text


def test_mcp2_dependency_and_import_surface():
    root = Path(__file__).resolve().parents[1]
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    source = (root / "grok/mcp_server.py").read_text(encoding="utf-8")
    shim = (root / "mythos/mcp_server.py").read_text(encoding="utf-8")

    assert project.count('"mcp>=2.0,<3"') == 2
    assert "from mcp.server import MCPServer" in source
    assert "GrokService" in source
    assert "MythosService" not in source
    assert "mcp.server.fastmcp" not in source
    assert "FastMCP" not in source
    assert "from grok.mcp_server import" in shim


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


def _wait_for_job(job_id: str) -> dict:
    polled = {}
    for _ in range(100):
        polled = json.loads(mcp_server.m2m_get_job(job_id))
        if polled["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)
    return polled


def test_create_and_inspect_animation_offline(isolated_service):
    raw = mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(
            prompt="explain euler's identity", offline=True))
    job = json.loads(raw)
    assert job["status"] in {"running", "completed"}
    assert job["options"]["offline"] is True

    polled = _wait_for_job(job["id"])
    assert polled["status"] == "completed"

    run_id = polled["run_id"]
    runs = json.loads(mcp_server.m2m_list_runs(mcp_server.ListRunsInput()))
    assert runs[0]["run_id"] == run_id

    detail = json.loads(mcp_server.m2m_get_run(
        mcp_server.RunIdInput(run_id=run_id)))
    assert "grok_scene.py" in detail["artifacts"]
    assert "mythos_scene.py" not in detail["artifacts"]
    for name in ARTIFACT_NAMES:
        assert name in detail["artifacts"]

    tree = json.loads(
        mcp_server.m2m_get_artifact(
            mcp_server.ArtifactInput(run_id=run_id, artifact_name="02_knowledge_map.json")
        )
    )
    assert validate_reverse_tree(tree) == []

    code = mcp_server.m2m_get_scene_code(mcp_server.RunIdInput(run_id=run_id))
    assert "ThreeDScene" in code
    assert "class GrokOfflineStory" in code
    assert "self.camera.animate" not in code


def test_create_animation_default_model_is_grok():
    fields = mcp_server.CreateAnimationInput.model_fields
    assert fields["model"].default == DEFAULT_MCP_MODEL == "grok-4.6"
    parsed = mcp_server.CreateAnimationInput(prompt="the heat equation")
    assert parsed.model == "grok-4.6"
    assert parsed.command is None
    assert parsed.image is None


def test_create_animation_accepts_image_and_ignores_command(isolated_service):
    raw = mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(
            prompt="solve this worksheet",
            offline=True,
            image="homework.jpg",
            command="claude",
        )
    )
    job = json.loads(raw)
    polled = _wait_for_job(job["id"])
    assert polled["status"] == "completed"
    assert polled["options"]["image"] == "homework.jpg"
    intent = json.loads(
        mcp_server.m2m_get_artifact(
            mcp_server.ArtifactInput(
                run_id=polled["run_id"],
                artifact_name="01_intent.json",
            )
        )
    )
    assert intent["image_read"]["path"] == "homework.jpg"


def test_scene_code_prefers_grok_then_mythos(isolated_service):
    run_dir = isolated_service.runs_dir / "legacy-mythos-run"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (run_dir / "mythos_scene.py").write_text(
        "from manim import *\n\nclass OldStory(ThreeDScene):\n    def construct(self):\n        self.wait()\n",
        encoding="utf-8",
    )
    code = mcp_server.m2m_get_scene_code(
        mcp_server.RunIdInput(run_id="legacy-mythos-run")
    )
    assert "class OldStory" in code

    (run_dir / "grok_scene.py").write_text(
        "from manim import *\n\nclass GrokStory(ThreeDScene):\n    def construct(self):\n        self.wait()\n",
        encoding="utf-8",
    )
    preferred = mcp_server.m2m_get_scene_code(
        mcp_server.RunIdInput(run_id="legacy-mythos-run")
    )
    assert "class GrokStory" in preferred


def test_charter_tool():
    charter = mcp_server.m2m_cinematic_charter()
    assert charter.startswith("GROK CINEMATIC CONTRACT")
    assert "CAMERA IS THE NARRATOR" in charter
    assert "grok_scene.py" in charter
    assert "move_camera" in charter


def test_error_paths_return_actionable_messages():
    assert mcp_server.m2m_get_job("nope").startswith("Error:")
    missing = mcp_server.m2m_get_run(mcp_server.RunIdInput(run_id="ghost"))
    assert missing.startswith("Error:")


def test_cli_serve_mcp_help_names_grok():
    from mythos.cli import build_parser

    help_text = build_parser().format_help()
    assert "serve-mcp" in help_text
    assert "Grok" in help_text
