"""Grok MCP server: tool registry and offline Grok tool calls.

The Mythos MCP server has its own tests in test_mythos_mcp_server.py.
"""

import asyncio
import json
import time
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from grok import mcp_server  # noqa: E402
from grok.client import XAIClient  # noqa: E402
from grok.harness import GrokHarness  # noqa: E402
from grok.service import GrokService  # noqa: E402
from grok.stages import ARTIFACT_NAMES  # noqa: E402
from grok.validation import validate_reverse_tree  # noqa: E402

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
    client = XAIClient(api_key="xai-test-key", model="grok-4.6", reasoning_effort="high")
    harness = GrokHarness(runs_dir=tmp_path / "runs", client=client, log=lambda _: None)
    service = GrokService(harness=harness)
    mcp_server.set_service(service)
    yield service
    mcp_server.set_service(None)


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
    source = (root / "src/grok/mcp_server.py").read_text(encoding="utf-8")

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    extras = tomllib.loads(project)['project']['optional-dependencies']
    for name in ('astra', 'dev', 'mcp'):
        assert 'mcp>=2.0,<3' in extras[name]
    assert "from mcp.server import MCPServer" in source
    assert "GrokService" in source
    assert "MythosService" not in source
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


def test_create_animation_defaults_to_server_model(isolated_service):
    parsed = mcp_server.CreateAnimationInput(prompt="the heat equation")
    assert parsed.model is None
    assert parsed.reasoning_effort is None
    assert parsed.command is None
    assert parsed.image is None
    job = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(prompt="the heat equation", offline=True)))
    polled = _wait_for_job(job["id"])
    assert polled["status"] == "completed"
    assert polled["options"]["model"] is None
    assert isolated_service.harness.client.model == "grok-4.6"


def test_create_animation_model_is_per_job_not_per_client(isolated_service):
    client = isolated_service.harness.client
    seen = []

    def fake_complete(**kwargs):
        seen.append((kwargs["model"], kwargs["reasoning_effort"]))
        raise RuntimeError("stop here")

    client.complete = fake_complete
    job = json.loads(mcp_server.m2m_create_animation(
        mcp_server.CreateAnimationInput(
            prompt="the heat equation", model="grok-4.6-fast", reasoning_effort="low")))
    polled = _wait_for_job(job["id"])
    assert polled["status"] == "failed"
    assert polled["run_id"]
    assert seen == [("grok-4.6-fast", "low")]
    assert (client.model, client.reasoning_effort) == ("grok-4.6", "high")


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


def test_scene_code_reads_grok_scene_only(isolated_service):
    run_dir = isolated_service.runs_dir / "some-run"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
    missing = mcp_server.m2m_get_scene_code(mcp_server.RunIdInput(run_id="some-run"))
    assert missing.startswith("Error:")
    assert "grok_scene.py" in missing
    (run_dir / "grok_scene.py").write_text(
        "from manim import *\n\nclass GrokStory(ThreeDScene):\n    def construct(self):\n        self.wait()\n",
        encoding="utf-8",
    )
    assert "class GrokStory" in mcp_server.m2m_get_scene_code(mcp_server.RunIdInput(run_id="some-run"))


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
    from grok.cli import build_parser

    help_text = build_parser().format_help()
    assert "serve-mcp" in help_text
    assert "Grok" in help_text
