import ast
import json
from pathlib import Path

import pytest

from grok.charters import STAGES, load_charter
from grok.cli import build_parser, main
from grok.client import XAIClient, api_key_status, collect_text, user_content
from grok.harness import GrokHarness
from grok.models import ARTIFACT_NAMES, RunRequest, StageCallResult
from grok.offline import _OFFLINE_SCENE, reverse_tree_for
from grok.service import GrokService
from grok.validation import validate_reverse_tree, validate_run


GROK_DIR = Path("grok")


def test_offline_run_writes_complete_film_bundle(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="the heat equation", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["status"] == "completed"
    assert manifest["backend"] == "xai-responses"
    assert manifest["model"] == "offline"
    assert all((run_dir / name).is_file() for name in ARTIFACT_NAMES)
    assert (run_dir / "traces" / "cartographer.json").is_file()
    failures, scene_name, video_path = validate_run(run_dir, require_video=False)
    assert failures == []
    assert scene_name == "GrokOfflineStory"
    assert video_path is None


def test_offline_cartographer_is_a_reverse_tree():
    tree = reverse_tree_for("the heat equation")
    assert validate_reverse_tree(tree) == []
    target_ids = [node["id"] for node in tree["nodes"] if node["depth"] == 0]
    assert target_ids == ["claim"]
    assert tree["nodes"][0]["depth"] == 0 or any(node["depth"] == 0 for node in tree["nodes"])
    start = next(node for node in tree["nodes"] if node["id"] == tree["spine"][0])
    assert start["assumed"] is True
    for src, dst in tree["edges"]:
        depths = {node["id"]: node["depth"] for node in tree["nodes"]}
        assert depths[src] > depths[dst]


def test_homework_offline_tree_is_also_reverse():
    tree = reverse_tree_for(
        "A 3 kg cart at 4 m/s hits a spring k=200. How far does it compress?"
    )
    assert validate_reverse_tree(tree) == []
    assert tree["spine"][0]
    assert next(node for node in tree["nodes"] if node["id"] == tree["spine"][0])["assumed"] is True


def test_cli_help_and_image_flag():
    parser = build_parser()
    help_text = parser.format_help()
    assert "math-to-manim-grok" in help_text
    run_help = parser.parse_args(["run", "the heat equation", "--offline", "--image", "page.jpg"])
    assert run_help.command == "run"
    assert run_help.offline is True
    assert run_help.image == "page.jpg"
    doctor = parser.parse_args(["doctor"])
    assert doctor.command == "doctor"
    with pytest.raises(SystemExit):
        parser.parse_args(["serve"])
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


def test_cli_run_help_mentions_offline_and_image(capsys):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["run", "--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--offline" in output
    assert "--image" in output
    assert "--reasoning-effort" in output


def test_doctor_checks_key_without_printing_it(monkeypatch, capsys):
    secret = "xai-super-secret-value-do-not-leak"
    monkeypatch.setenv("XAI_API_KEY", secret)
    monkeypatch.setenv("XAI_MODEL", "grok-4.6")
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert secret not in output
    assert "XAI_API_KEY is set" in output
    assert "grok-4.6" in output
    monkeypatch.delenv("XAI_API_KEY")
    assert main(["doctor"]) == 1
    failure = capsys.readouterr().out
    assert "not ready" in failure
    assert secret not in failure


def test_api_key_status_never_returns_the_secret():
    ok, detail = api_key_status("xai-this-must-not-appear")
    assert ok is True
    assert "xai-this-must-not-appear" not in detail


def test_client_builds_responses_payload_without_network(tmp_path):
    client = XAIClient(api_key="xai-test-key", model="grok-4.6", reasoning_effort="xhigh")
    payload = client.build_payload(
        instructions="charter",
        text="solve this",
        tools=({"type": "code_interpreter"}, {"type": "web_search"}),
        image_path=None,
        tool_choice="required",
    )
    assert payload["model"] == "grok-4.6"
    assert payload["reasoning"]["effort"] == "xhigh"
    assert payload["input"][0]["role"] == "system"
    assert payload["tool_choice"] == "required"
    assert {"type": "code_interpreter"} in payload["tools"]


def test_client_attaches_homework_image(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    content = user_content("read this page", image)
    assert content[0]["type"] == "input_text"
    assert content[1]["type"] == "input_image"
    assert content[1]["image_url"].startswith("data:image/png;base64,")


def test_collect_text_reads_responses_output():
    text = collect_text(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"ok": true}'}],
                }
            ]
        }
    )
    assert text == '{"ok": true}'


def test_live_run_uses_client_and_never_hits_network(tmp_path, monkeypatch):
    calls = []

    class FakeClient(XAIClient):
        def complete(self, **kwargs):
            calls.append(kwargs)
            stage_tools = [tool.get("type") for tool in kwargs.get("tools") or ()]
            body = {
                "offline": False,
                "core_claim": "test",
                "audience": "tester",
                "emotional_arc": ["a"],
                "scope": {"in": ["x"], "out": []},
                "duration_seconds": 90,
                "title_options": ["A", "B", "C"],
                "the_big_zoom": "z",
                "image_read": None,
                "target": "claim",
                "nodes": reverse_tree_for("the heat equation")["nodes"],
                "edges": reverse_tree_for("the heat equation")["edges"],
                "spine": reverse_tree_for("the heat equation")["spine"],
                "sources": [],
                "acts": [{"act_number": 1, "title": "t", "opening_question": "q",
                          "teaches": "foundations", "narrative": "n", "headline": "h",
                          "payoff": "p", "estimated_seconds": 10}],
                "through_line": "forward",
                "formulas": [{"id": "F1", "act_number": 1, "latex_parts": ["E"],
                              "term_glossary": [], "derivation_or_motivation": "d",
                              "common_misreading": "m"}],
                "color_identity": {},
                "numbers": [],
                "checks": ["sandbox"],
                "shots": [{"beat": 1, "verb": "HEADLINE"}],
                "camera_score": "hold",
                "stills": [],
                "visual_seeds": [],
                "scene_name": "GrokOfflineStory",
                "scene_class": "ThreeDScene",
                "palette": {},
                "objects": [],
                "timeline": [],
                "constraints": [],
                "acceptance": [],
                "source": _OFFLINE_SCENE,
            }
            return StageCallResult(text=json.dumps(body), payload=body, raw={"id": "resp"})

    monkeypatch.setenv("XAI_API_KEY", "xai-test-key")
    harness = GrokHarness(runs_dir=tmp_path, client=FakeClient(api_key="xai-test-key"))
    manifest = harness.run(RunRequest(prompt="the heat equation", offline=False))
    assert manifest["status"] == "completed"
    assert len(calls) == len(STAGES)
    math_call = next(item for item in calls if "code_interpreter" in {
        tool.get("type") for tool in item.get("tools") or ()
    })
    assert math_call["tool_choice"] == "required"
    assert any(
        tool.get("type") == "image_generation"
        for item in calls
        for tool in item.get("tools") or ()
    )


def test_service_reads_run_ledger(tmp_path):
    service = GrokService(runs_dir=tmp_path)
    manifest = service.run(RunRequest(prompt="visualize curvature", offline=True))
    assert service.get_run(manifest["run_id"]).status == "completed"
    assert service.list_runs(limit=1)[0].run_id == manifest["run_id"]
    with pytest.raises(ValueError):
        service.get_run("../escape")


def test_charters_ship_and_name_tools():
    expected = {
        "intent": [],
        "cartographer": ["web_search"],
        "curriculum": [],
        "math-director": ["code_interpreter", "web_search"],
        "cinematographer": ["image_generation", "x_search"],
        "composer": ["function"],
    }
    for stage in STAGES:
        text = load_charter(stage.charter_file)
        assert len(text) > 200
        assert "THINKING CONTRACT" in text
        assert "FORBIDDEN MOVES" in text
        kinds = [tool.get("type") for tool in stage.tools]
        assert kinds == expected[stage.name]


def test_grok_silo_does_not_import_mythos_or_sol():
    for path in GROK_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("mythos")
                    assert not alias.name.startswith("sol")
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("mythos")
                assert not node.module.startswith("sol")


def test_offline_scene_obeys_camera_rule(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="camera check", offline=True)
    )
    source = (tmp_path / manifest["run_id"] / "grok_scene.py").read_text(encoding="utf-8")
    assert "self.camera.animate" not in source
    assert "move_camera" in source or "set_camera_orientation" in source
