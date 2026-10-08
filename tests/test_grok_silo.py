import ast
import json
import re
import subprocess
import time
from pathlib import Path

import pytest

from grok.charters import STAGES, load_charter
from grok.cli import build_parser, main
from grok.client import (
    XAIClient,
    XAIClientError,
    api_key_status,
    collect_function_calls,
    collect_text,
    user_content,
)
from grok.harness import GrokHarness
from grok.jsonutil import extract_json_object, extract_python_block, extract_scene_source
from grok.models import ARTIFACT_NAMES, RunRequest, StageCallResult
from grok.offline import _OFFLINE_SCENE, reverse_tree_for
from grok.service import GrokService, Job
from grok.tools import verify_scene
from grok.validation import normalize_reverse_tree, validate_reverse_tree, validate_run


GROK_DIR = Path("grok")


def _marker(index: int) -> str:
    """Neutral stand-in. Joined at runtime so the source has no credential literal."""
    return "SENTINEL_VALUE_" + str(index)


def test_offline_run_writes_complete_film_bundle(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="the heat equation", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["status"] == "completed"
    assert manifest["backend"] == "offline"
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
    claim = next(node for node in tree["nodes"] if node["id"] == "claim")
    assert claim["depth"] == 0
    assert claim["assumed"] is False
    start = next(node for node in tree["nodes"] if node["id"] == tree["spine"][0])
    assert start["assumed"] is True
    assert tree["spine"][-1] == "claim"
    depths = {node["id"]: node["depth"] for node in tree["nodes"]}
    spine_depths = [depths[node_id] for node_id in tree["spine"]]
    assert spine_depths == sorted(spine_depths, reverse=True)
    for src, dst in tree["edges"]:
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
    secret = _marker(1)
    monkeypatch.setenv("XAI_API_KEY", secret)
    monkeypatch.setenv("XAI_MODEL", "grok-4.6")
    monkeypatch.setattr(
        XAIClient,
        "ping",
        lambda self: (True, "XAI_API_KEY is set; live ping succeeded"),
    )
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert secret not in output
    assert "XAI_API_KEY is set" in output
    assert "live ping succeeded" in output
    assert "grok-4.6" in output
    monkeypatch.delenv("XAI_API_KEY")
    assert main(["doctor"]) == 1
    failure = capsys.readouterr().out
    assert "not ready" in failure
    assert secret not in failure


def test_doctor_fails_on_rejected_key_without_printing_it(monkeypatch, capsys):
    secret = _marker(2)
    monkeypatch.setenv("XAI_API_KEY", secret)

    def fake_post(self, payload, previous_response_id=None):
        raise XAIClientError("xAI Responses API failed (401): invalid api key")

    monkeypatch.setattr(XAIClient, "post", fake_post)
    assert main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert secret not in output
    assert "not ready" in output
    assert "key rejected" in output


def test_doctor_does_not_ping_when_key_missing(monkeypatch, capsys):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    called = []
    monkeypatch.setattr(XAIClient, "ping", lambda self: called.append(True) or (True, "should not run"))
    assert main(["doctor"]) == 1
    assert called == []
    assert "not ready" in capsys.readouterr().out


def test_api_key_status_never_returns_the_secret():
    marker = _marker(3)
    ok, detail = api_key_status(marker)
    assert ok is True
    assert marker not in detail


def test_client_builds_responses_payload_without_network(tmp_path):
    client = XAIClient(api_key=_marker(1), model="grok-4.6", reasoning_effort="xhigh")
    payload = client.build_payload(
        instructions="charter",
        text="solve this",
        tools=({"type": "code_interpreter"}, {"type": "web_search"}),
        image_path=None,
        tool_choice="required",
    )
    assert payload["model"] == "grok-4.6"
    assert payload["reasoning"]["effort"] == "xhigh"
    assert payload["instructions"] == "charter"
    assert payload["input"][0]["role"] == "user"
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
            if kwargs.get("schema_name") == "assessment":
                text = kwargs.get("text") or ""
                files = re.findall(r"[\w.-]+\.(?:json|py|png)", text)
                frames = [name for name in files if name.startswith("frame_")]
                evidence = [frames[0]] if frames else (files[:1] or ["01_intent.json"])
                body = {
                    "verdict": "pass",
                    "evidence": evidence,
                    "repair_stage": "composer",
                    "feedback": "ok",
                    "defects": [],
                }
                return StageCallResult(text=json.dumps(body), payload=body, raw={"id": "audit"})
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

    monkeypatch.setenv("XAI_API_KEY", _marker(1))
    harness = GrokHarness(runs_dir=tmp_path, client=FakeClient(api_key=_marker(1)))
    manifest = harness.run(RunRequest(prompt="the heat equation", offline=False))
    assert manifest["status"] == "completed"
    stage_calls = [item for item in calls if item.get("schema_name") != "assessment"]
    audit_calls = [item for item in calls if item.get("schema_name") == "assessment"]
    assert len(stage_calls) == len(STAGES)
    assert len(audit_calls) == len(STAGES)
    assert stage_calls[0]["prompt_cache_key"].endswith(":intent")
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


def test_service_submit_offline_job(tmp_path):
    import time

    service = GrokService(runs_dir=tmp_path)
    job = service.submit(RunRequest(prompt="the heat equation", offline=True))
    assert isinstance(job, Job)
    for _ in range(100):
        polled = service.get_job(job.id)
        if polled.status in {"completed", "failed"}:
            break
        time.sleep(0.1)
    assert polled.status == "completed"
    bundle = service.inspect_run(polled.run_id)
    assert "grok_scene.py" in bundle["artifacts"]
    assert "class GrokOfflineStory" in service.read_scene_code(polled.run_id)


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
    forbidden = ("mythos", "sol", "astra", "glm", "mimo")
    for path in GROK_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(forbidden)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(forbidden)


def test_offline_scene_obeys_camera_rule(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="camera check", offline=True)
    )
    source = (tmp_path / manifest["run_id"] / "grok_scene.py").read_text(encoding="utf-8")
    assert "self.camera.animate" not in source
    assert "move_camera" in source or "set_camera_orientation" in source
    failures, scene_name, _ = validate_run(tmp_path / manifest["run_id"], require_video=False)
    assert failures == []
    assert scene_name == "GrokOfflineStory"


def test_cli_offline_homework_run(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("grok.cli.GrokService", lambda: GrokService(runs_dir=tmp_path))
    prompt = "A 3 kg cart at 4 m/s hits a spring k=200. How far does it compress?"
    assert main(["run", prompt, "--offline"]) == 0
    printed = json.loads(capsys.readouterr().out)
    run_dir = tmp_path / printed["run_id"]
    failures, scene_name, _ = validate_run(run_dir, require_video=False)
    assert failures == []
    assert scene_name == "GrokOfflineStory"
    tree = json.loads((run_dir / "02_knowledge_map.json").read_text(encoding="utf-8"))
    assert validate_reverse_tree(tree) == []
    source = (run_dir / "grok_scene.py").read_text(encoding="utf-8")
    compile(source, str(run_dir / "grok_scene.py"), "exec")


def test_reverse_tree_rejects_a_forward_lesson_plan():
    forward = {
        "target": "springs",
        "nodes": [
            {"id": "intro", "depth": 0, "assumed": True, "name": "start here"},
            {"id": "claim", "depth": 1, "assumed": False, "name": "later"},
        ],
        "edges": [["intro", "claim"]],
        "spine": ["intro", "claim"],
    }
    failures = validate_reverse_tree(forward)
    assert any("depth 0" in item or "assumed" in item or "prerequisite" in item for item in failures)


def test_reverse_tree_rejects_missing_depth_zero():
    tree = reverse_tree_for("the heat equation")
    for node in tree["nodes"]:
        if node["depth"] == 0:
            node["depth"] = 1
    failures = validate_reverse_tree(tree)
    assert any("depth 0" in item for item in failures)


def test_normalize_live_cartographer_shapes():
    messy = {
        "nodes": [
            {"id": "claim", "name": "energy balance", "depth": "0", "assumed": "false"},
            {"id": "energy", "name": "KE = PE", "depth": "1", "assumed": "false"},
            {"id": "symbols", "name": "givens", "depth": "2", "assumed": "true"},
        ],
        "edges": [
            {"from": "energy", "to": "claim"},
            {"from_id": "symbols", "to_id": "energy"},
        ],
        "spine": "symbols energy claim",
    }
    cleaned = normalize_reverse_tree(messy)
    assert validate_reverse_tree(cleaned) == []
    assert cleaned["nodes"][0]["depth"] == 0
    assert cleaned["nodes"][0]["assumed"] is False
    assert cleaned["edges"][0] == ["energy", "claim"]
    assert cleaned["spine"] == ["symbols", "energy", "claim"]
    assert "energy balance" in cleaned["target"]


def test_extract_json_object_reads_nested_fenced_json():
    text = 'Here you go:\n```json\n{"a": {"b": [1, 2]}, "s": "x{y}"}\n```\n'
    assert extract_json_object(text) == {"a": {"b": [1, 2]}, "s": "x{y}"}


def test_extract_json_object_reads_source_field_with_braces():
    scene = "from manim import *\n\nclass Demo(ThreeDScene):\n    def construct(self):\n        x = {1, 2}\n"
    blob = json.dumps({"scene_name": "Demo", "source": scene})
    parsed = extract_json_object(f"```json\n{blob}\n```")
    assert parsed["scene_name"] == "Demo"
    assert "class Demo" in parsed["source"]


def test_extract_python_block_ignores_json_fence():
    scene = "from manim import *\n\nclass Demo(ThreeDScene):\n    def construct(self):\n        self.wait()\n"
    text = f"```json\n{{\"scene_name\": \"Demo\"}}\n```\n\n```python\n{scene}```\n"
    assert "class Demo" in extract_python_block(text)
    with pytest.raises(ValueError):
        extract_python_block('```json\n{"scene_name": "Demo"}\n```\n')


def test_extract_scene_source_from_verify_scene_args():
    source = extract_scene_source(
        {"scene_name": "Demo"},
        "no python here",
        [{"name": "verify_scene", "arguments": json.dumps({"source": _OFFLINE_SCENE})}],
    )
    assert "class GrokOfflineStory" in source


def test_validate_run_rejects_uncompilable_scene(tmp_path):
    bundle = GrokHarness(runs_dir=tmp_path).run(RunRequest(prompt="the heat equation", offline=True))
    run_dir = tmp_path / bundle["run_id"]
    (run_dir / "grok_scene.py").write_text("class Broken(ThreeDScene)\n    pass\n", encoding="utf-8")
    failures, scene_name, _ = validate_run(run_dir, require_video=False)
    assert scene_name is None
    assert any("compilation" in item or "syntax" in item for item in failures)


def test_client_function_loop_returns_final_json(monkeypatch):
    scene_json = json.dumps({"scene_name": "GrokOfflineStory", "source": _OFFLINE_SCENE})
    responses = [
        {
            "id": "resp-1",
            "status": "completed",
            "output": [
                {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "verify_scene",
                    "arguments": json.dumps({"source": _OFFLINE_SCENE}),
                }
            ],
        },
        {
            "id": "resp-2",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": scene_json}],
                }
            ],
        },
    ]
    posted = []

    def fake_post(self, payload, previous_response_id=None):
        posted.append({"payload": payload, "previous": previous_response_id})
        return responses[len(posted) - 1]

    monkeypatch.setattr(XAIClient, "post", fake_post)
    client = XAIClient(api_key=_marker(1))
    result = client.complete(
        instructions="composer",
        text="write the scene",
        tools=({"type": "function", "name": "verify_scene"},),
        function_handlers={"verify_scene": verify_scene},
    )
    assert result.payload["scene_name"] == "GrokOfflineStory"
    assert "class GrokOfflineStory" in result.payload["source"]
    assert posted[1]["previous"] == "resp-1"
    assert posted[1]["payload"]["input"][0]["type"] == "function_call_output"
    assert posted[1]["payload"]["input"][0]["call_id"] == "call-1"
    output = json.loads(posted[1]["payload"]["input"][0]["output"])
    assert output["passed"] is True


def test_client_continues_incomplete_response(monkeypatch):
    responses = [
        {"id": "resp-1", "status": "incomplete", "output": []},
        {
            "id": "resp-2",
            "status": "completed",
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": '{"ok": true}'}]}
            ],
        },
    ]
    posted = []

    def fake_post(self, payload, previous_response_id=None):
        posted.append(previous_response_id)
        return responses[len(posted) - 1]

    monkeypatch.setattr(XAIClient, "post", fake_post)
    result = XAIClient(api_key=_marker(1)).complete(instructions="intent", text="go")
    assert result.payload == {"ok": True}
    assert posted == [None, "resp-1"]


def test_collect_function_calls_reads_nested_tool_call():
    calls = collect_function_calls(
        {
            "output": [
                {
                    "type": "tool_call",
                    "id": "tc-1",
                    "function": {"name": "verify_scene", "arguments": '{"source": "x"}'},
                }
            ]
        }
    )
    assert calls[0]["name"] == "verify_scene"
    assert calls[0]["call_id"] == "tc-1"


def test_client_ping_payload_is_tiny():
    payload = XAIClient(api_key=_marker(1)).ping_payload()
    assert payload["input"] == "Reply with the single word pong."
    assert payload["max_output_tokens"] == 16
    assert payload["reasoning"]["effort"] == "low"


def test_default_model_is_grok_4_7(monkeypatch):
    monkeypatch.delenv("XAI_MODEL", raising=False)
    assert XAIClient(api_key=_marker(1)).model == "grok-4.7"


def test_payload_sends_prompt_cache_key_and_strict_schema():
    client = XAIClient(api_key=_marker(1), model="grok-4.7")
    schema = {"type": "object", "properties": {"core_claim": {"type": "string"}}, "required": ["core_claim"]}
    payload = client.build_payload(
        instructions="charter",
        text="the heat equation",
        schema=schema,
        schema_name_value="intent",
        prompt_cache_key="run-1:intent",
    )
    assert payload["prompt_cache_key"] == "run-1:intent"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["text"]["format"]["name"] == "intent"
    assert payload["text"]["format"]["schema"] == schema
    assert payload["reasoning"]["effort"] == "high"


def test_structured_outputs_can_be_disabled(monkeypatch):
    monkeypatch.setenv("GROK_STRUCTURED_OUTPUTS", "0")
    client = XAIClient(api_key=_marker(1), model="grok-4.7")
    payload = client.build_payload(
        instructions="charter",
        text="go",
        schema={"type": "object"},
        schema_name_value="intent",
    )
    assert "text" not in payload


def test_code_model_omits_server_tools_until_configured():
    client = XAIClient(api_key=_marker(1), model="grok-build-0.1", reasoning_effort="high")
    payload = client.build_payload(
        instructions="charter",
        text="go",
        tools=({"type": "web_search"}, {"type": "function", "name": "verify_scene"}),
    )
    kinds = [tool["type"] for tool in payload["tools"]]
    assert kinds == ["function"]
    assert any("web_search" in warning for warning in client.capability_warnings)


def test_capability_fallback_strips_rejected_schema(monkeypatch):
    calls = []

    def fake_once(self, payload, previous_response_id=None):
        calls.append(payload)
        if len(calls) == 1:
            raise XAIClientError(
                'xAI Responses API failed (400): {"error":"unsupported parameter: text.format"}'
            )
        return {
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": '{"ok": true}'}]}
            ]
        }

    monkeypatch.setattr(XAIClient, "_post_once", fake_once)
    result = XAIClient(api_key=_marker(1), model="grok-4.7").complete(
        instructions="intent",
        text="go",
        schema={"type": "object"},
        schema_name="intent",
        prompt_cache_key="run:intent",
    )
    assert result.payload == {"ok": True}
    assert "text" not in calls[1]
    assert calls[1]["prompt_cache_key"] == "run:intent"
    assert any("text.format" in warning for warning in result.warnings)


def test_clean_environment_strips_xai_key(monkeypatch):
    from grok.rendering import clean_environment

    xai_value = _marker(4)
    monkeypatch.setenv("XAI_API_KEY", xai_value)
    monkeypatch.setenv("GH_TOKEN", _marker(5))
    monkeypatch.setenv("APP_SECRET", _marker(6))
    monkeypatch.setenv("DB_PASSWORD", _marker(7))
    env = clean_environment()
    assert "XAI_API_KEY" not in env
    assert "GH_TOKEN" not in env
    assert "APP_SECRET" not in env
    assert "DB_PASSWORD" not in env
    assert "PATH" in env
    assert xai_value not in env.values()


def test_render_uses_timeout_and_clean_env(monkeypatch, tmp_path):
    from grok.rendering import render

    render_value = _marker(8)
    monkeypatch.setenv("XAI_API_KEY", render_value)
    seen = {}

    def runner(args, **kwargs):
        seen["env"] = kwargs["env"]
        seen["timeout"] = kwargs["timeout"]
        raise RuntimeError("stop-after-inspect")

    with pytest.raises(RuntimeError, match="stop-after-inspect"):
        render(tmp_path, _OFFLINE_SCENE, "l", 1, timeout=321, runner=runner)
    assert seen["timeout"] == 321
    assert "XAI_API_KEY" not in seen["env"]
    assert render_value not in seen["env"].values()


def test_render_duration_gate_and_twelve_frames(tmp_path):
    from grok.rendering import render

    calls = []

    def runner(args, **kwargs):
        calls.append(list(args))
        if "render_worker.py" in args[1]:
            media = Path(args[3])
            video = media / "videos" / "GrokOfflineStory.mp4"
            video.parent.mkdir(parents=True, exist_ok=True)
            video.write_bytes(b"x" * 2048)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ffprobe":
            body = json.dumps({"format": {"duration": "36.0"}, "streams": []})
            return subprocess.CompletedProcess(args, 0, body, "")
        if args[0] == "ffmpeg":
            Path(args[-1]).write_bytes(b"\x89PNG\r\n")
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError(args)

    def sheet(folder, frames, duration):
        assert len(frames) == 12
        assert duration == 36.0
        target = folder / "contact_sheet.png"
        target.write_bytes(b"\x89PNG\r\n")
        return target

    video, frames, contact = render(
        tmp_path,
        _OFFLINE_SCENE,
        "l",
        1,
        timeout=50,
        min_duration=20,
        max_duration=240,
        runner=runner,
        contact_sheet=sheet,
    )
    assert video.name == "GrokOfflineStory.mp4"
    assert len(frames) == 12
    assert contact.name == "contact_sheet.png"
    assert sum(1 for args in calls if args[0] == "ffmpeg") == 12
    assert any(args[0] == "ffprobe" for args in calls)


def test_short_film_fails_duration_check(tmp_path):
    from grok.rendering import render

    def runner(args, **kwargs):
        if "render_worker.py" in args[1]:
            video = Path(args[3]) / "videos" / "GrokOfflineStory.mp4"
            video.parent.mkdir(parents=True, exist_ok=True)
            video.write_bytes(b"x" * 2048)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ffprobe":
            body = json.dumps({"format": {"duration": "1.5"}})
            return subprocess.CompletedProcess(args, 0, body, "")
        raise AssertionError(args)

    with pytest.raises(RuntimeError, match="duration"):
        render(tmp_path, _OFFLINE_SCENE, "l", 1, runner=runner)


def test_allowlist_rejects_os_eval_and_dunder():
    from grok.validation import validate_scene_source

    source = (
        "import os\n"
        "from manim import *\n\n"
        "class SecretStory(ThreeDScene):\n"
        "    def construct(self):\n"
        "        eval('1')\n"
        "        self.__dict__\n"
    )
    failures, scene_name = validate_scene_source(source)
    assert scene_name is None
    assert any("manim, numpy, or math" in item for item in failures)
    assert any("eval" in item for item in failures)
    assert any("dunder" in item for item in failures)


def test_scene_name_must_end_in_journey_or_story():
    from grok.validation import validate_scene_source

    source = "from manim import *\n\nclass HeatFilm(ThreeDScene):\n    def construct(self):\n        self.wait()\n"
    failures, scene_name = validate_scene_source(source)
    assert scene_name is None
    assert any("Journey or Story" in item for item in failures)


def test_grok_build_argv_is_headless_and_does_not_embed_the_key(monkeypatch):
    from grok.backends.grok_build import GrokBuildBackend, build_grok_argv

    argv = build_grok_argv(
        binary="grok",
        prompt="explain curvature",
        model="grok-4.7",
        effort="high",
        system_prompt="charter",
        cwd="/tmp/run",
    )
    assert argv[:2] == ["grok", "-p"]
    assert "--output-format" in argv and "json" in argv
    assert "--sandbox" in argv and "read-only" in argv
    assert "--no-auto-update" in argv
    assert "--disable-web-search" in argv
    key_value = _marker(9)
    assert key_value not in argv

    monkeypatch.setenv("XAI_API_KEY", key_value)
    captured = {}

    def runner(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs.get("env")
        return subprocess.CompletedProcess(command, 0, '{"core": "claim"}', "")

    backend = GrokBuildBackend(model="grok-4.7", binary="grok", runner=runner, api_key=key_value)
    monkeypatch.setattr("grok.backends.grok_build.cached_login_present", lambda path=None: True)
    result = backend.complete(instructions="charter", text="go", cwd=Path("/tmp"))
    assert key_value not in result.text
    assert key_value not in captured["command"]
    assert result.payload == {"core": "claim"}


def test_login_wraps_grok_login(monkeypatch):
    from grok.backends.grok_build import login_command

    monkeypatch.setattr("grok.backends.grok_build.grok_binary", lambda: "/usr/bin/grok")
    assert login_command(device_auth=False) == ["/usr/bin/grok", "login"]
    assert login_command(device_auth=True) == ["/usr/bin/grok", "login", "--device-auth"]
    calls = []
    monkeypatch.setattr("grok.cli.login_command", lambda device_auth=False: calls.append(device_auth) or ["grok", "login"])
    monkeypatch.setattr("grok.cli.subprocess.call", lambda command: 0)
    assert main(["login", "--device-auth"]) == 0
    assert calls == [True]


def test_doctor_reports_grok_login_without_printing_the_token(monkeypatch, tmp_path, capsys):
    token = _marker(10)
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({"token": token}), encoding="utf-8")
    monkeypatch.setenv("GROK_AUTH_FILE", str(auth))
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert main(["doctor", "--backend", "grok-build"]) == 0
    output = capsys.readouterr().out
    assert token not in output
    assert "auth_source=grok-login" in output
    assert "ready" in output


def test_resume_reuses_hashed_stages_with_zero_new_model_calls(tmp_path, monkeypatch):
    calls = {"n": 0}

    class FakeClient(XAIClient):
        def complete(self, **kwargs):
            calls["n"] += 1
            if kwargs.get("schema_name") == "assessment":
                text = kwargs.get("text") or ""
                files = re.findall(r"[\w.-]+\.(?:json|py|png)", text)
                body = {
                    "verdict": "pass",
                    "evidence": files[:1] or ["01_intent.json"],
                    "repair_stage": "composer",
                    "feedback": "ok",
                    "defects": [],
                }
                return StageCallResult(text=json.dumps(body), payload=body, raw={})
            body = _live_body()
            return StageCallResult(text=json.dumps(body), payload=body, raw={})

    monkeypatch.setenv("XAI_API_KEY", _marker(1))
    harness = GrokHarness(runs_dir=tmp_path, client=FakeClient(api_key=_marker(1)))
    first = harness.run(RunRequest(prompt="the heat equation", offline=False, review="advisory"))
    spent = calls["n"]
    assert spent > 0
    second = harness.resume(first["run_id"])
    assert second["status"] == "completed"
    assert calls["n"] == spent


def test_render_existing_makes_zero_model_calls(tmp_path):
    harness = GrokHarness(runs_dir=tmp_path)
    first = harness.run(RunRequest(prompt="the heat equation", offline=True))

    def boom(**kwargs):
        raise AssertionError("model call")

    harness.client.complete = boom

    def renderer(run_dir, source, quality, attempt, **kwargs):
        folder = Path(run_dir) / f"renders/{attempt:03d}"
        folder.mkdir(parents=True)
        video = folder / "GrokOfflineStory.mp4"
        video.write_bytes(b"x" * 2048)
        frames = []
        for index in range(12):
            frame = folder / f"frame_{index:02d}.png"
            frame.write_bytes(b"\x89PNG\r\n")
            frames.append(frame)
        sheet = folder / "contact_sheet.png"
        sheet.write_bytes(b"\x89PNG\r\n")
        return video, frames, sheet

    harness.renderer = renderer
    manifest = harness.render_existing(first["run_id"], quality="l")
    assert manifest["review_status"] == "not_reviewed"
    assert manifest["video_path"].endswith(".mp4")
    review = json.loads((tmp_path / first["run_id"] / "review.json").read_text(encoding="utf-8"))
    assert review["local_render"]["model_calls"] == 0


def test_gated_review_routes_to_repair_stage(tmp_path, monkeypatch):
    calls = []

    class FakeClient(XAIClient):
        def complete(self, **kwargs):
            calls.append(kwargs.get("schema_name"))
            if kwargs.get("schema_name") == "assessment":
                text = kwargs.get("text") or ""
                if text.startswith("STAGE: curriculum") and not any(
                    item == "assessment" and calls.count("curriculum") > 1 for item in calls
                ):
                    # Fail the first curriculum audit only.
                    if calls.count("assessment") == 3:
                        body = {
                            "verdict": "fail",
                            "evidence": ["03_curriculum.json"],
                            "repair_stage": "intent",
                            "feedback": "audience is vague",
                            "defects": ["audience"],
                        }
                        return StageCallResult(text=json.dumps(body), payload=body, raw={})
                files = re.findall(r"[\w.-]+\.(?:json|py|png)", text)
                body = {
                    "verdict": "pass",
                    "evidence": files[:1] or ["01_intent.json"],
                    "repair_stage": "composer",
                    "feedback": "ok",
                    "defects": [],
                }
                return StageCallResult(text=json.dumps(body), payload=body, raw={})
            return StageCallResult(text="{}", payload=_live_body(), raw={})

    monkeypatch.setenv("XAI_API_KEY", _marker(1))
    harness = GrokHarness(runs_dir=tmp_path, client=FakeClient(api_key=_marker(1)))
    manifest = harness.run(
        RunRequest(prompt="the heat equation", offline=False, review="gated", max_revisions=2)
    )
    assert manifest["status"] == "completed"
    assert manifest["review_status"] == "approved"
    assert calls.count("intent") >= 2


def test_schema_failure_retries_once(tmp_path, monkeypatch):
    attempts = {"intent": 0}

    class FakeClient(XAIClient):
        def complete(self, **kwargs):
            if kwargs.get("schema_name") == "assessment":
                text = kwargs.get("text") or ""
                files = re.findall(r"[\w.-]+\.(?:json|py|png)", text)
                body = {
                    "verdict": "pass",
                    "evidence": files[:1] or ["01_intent.json"],
                    "repair_stage": "composer",
                    "feedback": "ok",
                    "defects": [],
                }
                return StageCallResult(text=json.dumps(body), payload=body, raw={})
            if kwargs.get("schema_name") == "intent":
                attempts["intent"] += 1
                if attempts["intent"] == 1:
                    return StageCallResult(text="{}", payload={"raw_text": "nope"}, raw={})
            return StageCallResult(text="{}", payload=_live_body(), raw={})

    monkeypatch.setenv("XAI_API_KEY", _marker(1))
    harness = GrokHarness(runs_dir=tmp_path, client=FakeClient(api_key=_marker(1)))
    manifest = harness.run(RunRequest(prompt="the heat equation", offline=False, review="off"))
    assert manifest["status"] == "completed"
    assert attempts["intent"] == 2


def test_job_record_survives_a_new_service(tmp_path):
    service = GrokService(runs_dir=tmp_path)
    job = service.submit(RunRequest(prompt="the heat equation", offline=True))
    for _ in range(100):
        polled = service.get_job(job.id)
        if polled and polled.status in {"completed", "failed"}:
            break
        time.sleep(0.05)
    assert polled.status == "completed"
    restarted = GrokService(runs_dir=tmp_path)
    restored = restarted.get_job(job.id)
    assert restored is not None
    assert restored.status == "completed"
    assert restored.run_id == polled.run_id


def test_runs_dir_follows_cwd_or_env(monkeypatch, tmp_path):
    from grok.harness import default_runs_dir

    monkeypatch.delenv("M2M_RUNS_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    assert default_runs_dir() == tmp_path / "runs" / "grok"
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path / "custom"))
    assert default_runs_dir() == tmp_path / "custom" / "grok"


def test_mcp_tool_count_includes_resume_and_render(monkeypatch):
    pytest.importorskip("mcp")
    import asyncio

    from grok.mcp_server import mcp

    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert len(names) >= 9
    assert "m2m_resume_run" in names
    assert "m2m_render_existing" in names


def test_cli_serve_mcp_accepts_http_transport():
    args = build_parser().parse_args(["serve-mcp", "--transport", "http", "--port", "8643"])
    assert args.transport == "http"
    assert args.port == 8643


def _live_body() -> dict:
    tree = reverse_tree_for("the heat equation")
    return {
        "core_claim": "test",
        "audience": "tester",
        "emotional_arc": ["a"],
        "scope": {"in": ["x"], "out": []},
        "duration_seconds": 90,
        "title_options": ["A", "B", "C"],
        "the_big_zoom": "z",
        "image_read": None,
        "target": "claim",
        "nodes": tree["nodes"],
        "edges": tree["edges"],
        "spine": tree["spine"],
        "sources": [],
        "acts": [
            {
                "act_number": 1,
                "title": "t",
                "opening_question": "q",
                "teaches": "foundations",
                "narrative": "n",
                "headline": "h",
                "payoff": "p",
                "estimated_seconds": 10,
            }
        ],
        "through_line": "forward",
        "formulas": [
            {
                "id": "F1",
                "act_number": 1,
                "latex_parts": ["E"],
                "term_glossary": [],
                "derivation_or_motivation": "d",
                "common_misreading": "m",
            }
        ],
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
