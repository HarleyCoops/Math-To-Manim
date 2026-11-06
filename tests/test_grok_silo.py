import json

import pytest

from grok.cli import build_parser, main
from grok.client import (
    XAIClient,
    XAIClientError,
    api_key_status,
    collect_function_calls,
    collect_text,
    user_content,
)
from grok.harness import GrokHarness, default_runs_dir
from grok.jsonutil import extract_json_object, extract_python_block, extract_scene_source
from grok.models import RunRequest, StageCallResult
from grok.offline import _OFFLINE_SCENE, reverse_tree_for
from grok.service import GrokService, Job
from grok.stages import ARTIFACT_NAMES, STAGES, load_charter, tool_labels, validate_run
from grok.tools import verify_scene
from grok.validation import normalize_reverse_tree, validate_reverse_tree


def test_offline_run_writes_complete_film_bundle(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="the heat equation", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["status"] == "completed"
    assert manifest["backend"] == "xai-responses"
    assert manifest["model"] == "offline"
    assert manifest["video_path"] is None
    assert all((run_dir / name).is_file() for name in ARTIFACT_NAMES)
    for stage in STAGES:
        trace = json.loads((run_dir / "traces" / f"{stage.name}.json").read_text(encoding="utf-8"))
        assert trace["tools_requested"] == tool_labels(stage)
    failures, scene_name = validate_run(run_dir)
    assert failures == []
    assert scene_name == "GrokOfflineStory"
    validation = json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation == {"passed": True, "scene_name": "GrokOfflineStory", "errors": []}
    review = json.loads((run_dir / "review.json").read_text(encoding="utf-8"))
    assert review["offline"] is True
    assert review["rendered"] is False


def test_default_runs_dir_follows_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert default_runs_dir() == tmp_path / "runs" / "grok"


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
    secret = "xai-super-secret-value-do-not-leak"
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
    secret = "xai-invalid-key-must-stay-hidden"
    monkeypatch.setenv("XAI_API_KEY", secret)

    def fake_post(self, payload, previous_response_id=None, **kwargs):
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


def _fake_stage_body() -> dict:
    tree = reverse_tree_for("the heat equation")
    return {
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
        "nodes": tree["nodes"],
        "edges": tree["edges"],
        "spine": tree["spine"],
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


class RecordingClient(XAIClient):
    """Answers every stage with one complete payload and records the calls."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls: list[dict] = []

    def complete(self, **kwargs):
        self.calls.append(kwargs)
        body = _fake_stage_body()
        return StageCallResult(text=json.dumps(body), payload=body, raw={"id": "resp"})


def test_live_run_uses_client_and_never_hits_network(tmp_path, capsys):
    client = RecordingClient(api_key="xai-test-key", model="grok-4.6", reasoning_effort="high")
    lines: list[str] = []
    harness = GrokHarness(runs_dir=tmp_path, client=client, log=lines.append)
    started: list[str] = []
    manifest = harness.run(
        RunRequest(prompt="the heat equation", model="grok-4.6-fast", reasoning_effort="low"),
        on_start=started.append,
    )
    assert manifest["status"] == "completed"
    assert manifest["model"] == "grok-4.6-fast"
    assert started == [manifest["run_id"]]
    assert len(client.calls) == len(STAGES)
    assert len(lines) == len(STAGES)

    # Per-run settings travel with every call; the shared client is untouched.
    assert {call["model"] for call in client.calls} == {"grok-4.6-fast"}
    assert {call["reasoning_effort"] for call in client.calls} == {"low"}
    assert (client.model, client.reasoning_effort) == ("grok-4.6", "high")

    by_stage = dict(zip([stage.name for stage in STAGES], client.calls))
    assert by_stage["math-director"]["tool_choice"] == "required"
    assert by_stage["intent"]["tool_choice"] is None
    assert any(tool.get("type") == "image_generation" for tool in by_stage["cinematographer"]["tools"])
    assert by_stage["composer"]["function_handlers"] == {"verify_scene": verify_scene}
    assert by_stage["intent"]["function_handlers"] is None
    assert "source field" in by_stage["composer"]["text"]
    assert "source field" not in by_stage["intent"]["text"]

    run_dir = tmp_path / manifest["run_id"]
    trace = json.loads((run_dir / "traces" / "composer.json").read_text(encoding="utf-8"))
    assert (trace["model"], trace["reasoning_effort"]) == ("grok-4.6-fast", "low")
    review = json.loads((run_dir / "review.json").read_text(encoding="utf-8"))
    assert review["model"] == "grok-4.6-fast"
    assert review["offline"] is False
    # stdout stays clean for CLI JSON and MCP stdio.
    assert capsys.readouterr().out == ""


def test_live_run_defaults_to_client_settings(tmp_path):
    client = RecordingClient(api_key="xai-test-key", model="grok-4.6", reasoning_effort="xhigh")
    manifest = GrokHarness(runs_dir=tmp_path, client=client, log=lambda _: None).run(
        RunRequest(prompt="the heat equation")
    )
    assert manifest["model"] == "grok-4.6"
    assert {call["reasoning_effort"] for call in client.calls} == {"xhigh"}


def test_live_run_repairs_then_records_validation(tmp_path):
    broken = _OFFLINE_SCENE.replace("self.move_camera(", "self.camera.animate.x(")

    class RepairingClient(RecordingClient):
        def complete(self, **kwargs):
            self.calls.append(kwargs)
            body = _fake_stage_body()
            if len(self.calls) <= len(STAGES):
                body["source"] = broken
            else:
                body = {"scene_name": "GrokOfflineStory", "source": _OFFLINE_SCENE}
            return StageCallResult(text=json.dumps(body), payload=body, raw={"id": "resp"})

    client = RepairingClient(api_key="xai-test-key")
    manifest = GrokHarness(runs_dir=tmp_path, client=client, log=lambda _: None).run(
        RunRequest(prompt="the heat equation", max_repairs=2)
    )
    assert manifest["status"] == "completed"
    assert len(client.calls) == len(STAGES) + 1
    run_dir = tmp_path / manifest["run_id"]
    assert (run_dir / "traces" / "repair-1.json").is_file()
    assert [attempt["mode"] for attempt in manifest["attempts"]] == ["xai-responses", "composer-repair"]
    assert "camera" in manifest["attempts"][1]["input_failures"][0]
    validation = json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["passed"] is True


def test_live_run_failure_leaves_validation_evidence(tmp_path):
    class NoJsonClient(RecordingClient):
        def complete(self, **kwargs):
            self.calls.append(kwargs)
            return StageCallResult(text="I cannot.", payload=None, raw={"id": "resp"})

    harness = GrokHarness(runs_dir=tmp_path, client=NoJsonClient(api_key="xai-test-key"), log=lambda _: None)
    with pytest.raises(XAIClientError, match="stage intent did not return JSON"):
        harness.run(RunRequest(prompt="the heat equation"))
    manifest = json.loads(next(tmp_path.glob("*/manifest.json")).read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert "intent did not return JSON" in manifest["error"]


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
        "composer": ["verify_scene"],
    }
    assert [stage.name for stage in STAGES] == list(expected)
    for stage in STAGES:
        text = load_charter(stage.charter_file)
        assert len(text) > 200
        assert "THINKING CONTRACT" in text
        assert "FORBIDDEN MOVES" in text
        assert tool_labels(stage) == expected[stage.name]
    assert [stage.name for stage in STAGES if stage.tool_choice == "required"] == ["math-director"]
    assert [stage.name for stage in STAGES if stage.takes_image] == ["intent"]
    assert [stage.name for stage in STAGES if stage.writes_scene] == ["composer"]
    assert [stage.name for stage in STAGES if stage.normalize] == ["cartographer"]


def test_offline_scene_obeys_camera_rule(tmp_path):
    manifest = GrokHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="camera check", offline=True)
    )
    source = (tmp_path / manifest["run_id"] / "grok_scene.py").read_text(encoding="utf-8")
    assert "self.camera.animate" not in source
    assert "move_camera" in source or "set_camera_orientation" in source
    failures, scene_name = validate_run(tmp_path / manifest["run_id"])
    assert failures == []
    assert scene_name == "GrokOfflineStory"


def test_cli_offline_homework_run(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("grok.cli.GrokService", lambda: GrokService(runs_dir=tmp_path))
    prompt = "A 3 kg cart at 4 m/s hits a spring k=200. How far does it compress?"
    assert main(["run", prompt, "--offline"]) == 0
    printed = json.loads(capsys.readouterr().out)
    run_dir = tmp_path / printed["run_id"]
    failures, scene_name = validate_run(run_dir)
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
    failures, scene_name = validate_run(run_dir)
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

    def fake_post(self, payload, previous_response_id=None, **kwargs):
        posted.append({"payload": payload, "previous": previous_response_id})
        return responses[len(posted) - 1]

    monkeypatch.setattr(XAIClient, "post", fake_post)
    client = XAIClient(api_key="xai-test-key")
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

    def fake_post(self, payload, previous_response_id=None, **kwargs):
        posted.append(previous_response_id)
        return responses[len(posted) - 1]

    monkeypatch.setattr(XAIClient, "post", fake_post)
    result = XAIClient(api_key="xai-test-key").complete(instructions="intent", text="go")
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
    payload = XAIClient(api_key="xai-test-key").ping_payload()
    assert payload["input"] == "Reply with the single word pong."
    assert payload["max_output_tokens"] == 16
    assert payload["reasoning"]["effort"] == "low"
