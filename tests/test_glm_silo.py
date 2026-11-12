"""Behavioural tests for the GLM silo (src/glm).

Every test runs offline: the Z.ai wire is replaced by a fake transport injected
through ``GlmClient(transport=...)``. Nothing here reaches the network, the
user's environment, or the OpenCode auth file.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glm import cli
from glm.client import (
    GlmClient,
    GlmClientError,
    GlmSettings,
    api_key_status,
    resolve_api_key,
    user_content,
)
from glm.harness import GlmHarness
from glm.jsonutil import extract_json_object, extract_scene_source
from glm.models import RunRequest
from glm.offline import reverse_tree_for
from glm.service import GlmService
from glm.stages import BUNDLE_FILES, STAGES, stage_prompt
from glm.tools import VERIFY_SCENE, verify_scene
from glm.validation import validate_reverse_tree, verify_scene_report

VERIFY_SCENE_TOOL = VERIFY_SCENE.schema()

KEY = "k" * 32
STAGE_NAMES = ["intent", "cartographer", "curriculum", "math-director", "cinematographer", "composer"]
STAGE_ARTIFACTS = [
    "01_intent.json",
    "02_knowledge_map.json",
    "03_curriculum.json",
    "04_math_dossier.json",
    "05_shot_list.json",
    "06_scene_spec.json",
]
TOOLS_REQUESTED = {
    "intent": [],
    "cartographer": ["web_search"],
    "curriculum": [],
    "math-director": ["code_interpreter", "web_search"],
    "cinematographer": ["web_search"],
    "composer": ["verify_scene"],
}

GOOD_SCENE = '''from manim import *


class LivePole(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#f3ecd8"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.play(FadeIn(Text("pole")))
'''

BAD_SCENE = GOOD_SCENE.replace(
    "self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)",
    "self.play(self.camera.animate.set_phi(1))",
)


def reply(content, *, tool_calls=None, reasoning=None) -> dict:
    message: dict = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    if reasoning is not None:
        message["reasoning_content"] = reasoning
    return {"choices": [{"message": message}]}


def verify_call(source: str, call_id: str = "call-1") -> dict:
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": "verify_scene", "arguments": json.dumps({"source": source})},
    }


class FakeTransport:
    """Scripted Z.ai: returns replies in order and records every request."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls: list[dict] = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": headers, "body": body, "timeout": timeout})
        if not self.replies:
            raise AssertionError("fake Z.ai ran out of scripted replies")
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def user_texts(self) -> list[str]:
        out = []
        for call in self.calls:
            user = [m for m in call["body"]["messages"] if m["role"] == "user"][0]
            content = user["content"]
            out.append(content if isinstance(content, str) else content[0]["text"])
        return out


def stage_replies(scene_source: str = GOOD_SCENE) -> list[dict]:
    tree = reverse_tree_for("Explain the magnetic monopole")
    return [
        reply(json.dumps({"core_claim": "poles"}), reasoning="think-intent"),
        reply(json.dumps(tree)),
        reply(json.dumps({"acts": []})),
        reply(json.dumps({"formulas": []})),
        reply(json.dumps({"shots": []})),
        reply(json.dumps({"scene_name": "LivePole", "source": scene_source})),
    ]


def live_harness(tmp_path: Path, replies) -> tuple[GlmHarness, FakeTransport, list[str]]:
    transport = FakeTransport(replies)
    progress: list[str] = []
    client = GlmClient(api_key=KEY, model="glm-test", transport=transport)
    harness = GlmHarness(runs_dir=tmp_path / "runs", client=client, progress=progress.append)
    return harness, transport, progress


# --------------------------------------------------------------------------
# Offline bundle
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt",
    ["Explain the magnetic monopole", "Why Fourier solves the heat equation", "Count the primes"],
)
def test_offline_run_writes_the_complete_bundle(tmp_path, prompt):
    harness = GlmHarness(runs_dir=tmp_path, client=GlmClient(api_key=KEY))
    manifest = harness.run(RunRequest(prompt=prompt, offline=True))
    run_dir = tmp_path / manifest["run_id"]

    assert manifest["status"] == "completed"
    assert manifest["offline"] is True
    assert manifest["model"] == "offline"
    assert manifest["key_source"] is None
    assert manifest["scene_file"] == "glm_scene.py"
    assert manifest["scene_name"] == "GlmOfflineStory"
    assert manifest["video_path"] is None
    assert manifest["attempts"] == [{"attempt": 0, "mode": "offline", "status": "completed"}]
    assert manifest["status_detail"] == {"validation": "complete"}
    assert manifest["artifacts"] == {name: name for name in BUNDLE_FILES}
    assert list(BUNDLE_FILES) == STAGE_ARTIFACTS + ["glm_scene.py", "validation.json", "review.json"]
    assert json.loads((run_dir / "manifest.json").read_text()) == manifest

    for name in BUNDLE_FILES:
        assert (run_dir / name).is_file(), name
    for name in STAGE_ARTIFACTS:
        payload = json.loads((run_dir / name).read_text())
        assert isinstance(payload, dict) and payload
        assert payload["offline"] is True
    assert json.loads((run_dir / "request.json").read_text())["prompt"] == prompt

    tree = json.loads((run_dir / "02_knowledge_map.json").read_text())
    assert validate_reverse_tree(tree) == []

    spec = json.loads((run_dir / "06_scene_spec.json").read_text())
    assert spec["scene_name"] == "GlmOfflineStory"
    assert spec["palette"]["background"] == "#f3ecd8"

    scene = (run_dir / "glm_scene.py").read_text()
    assert "class GlmOfflineStory(ThreeDScene)" in scene
    assert '"#f3ecd8"' in scene
    assert json.loads((run_dir / "validation.json").read_text()) == {
        "passed": True,
        "scene_name": "GlmOfflineStory",
        "errors": [],
    }

    review = json.loads((run_dir / "review.json").read_text())
    assert review["offline"] is True
    assert review["checks"] == ["artifact contract", "reverse tree", "python compilation"]
    assert review["rendered"] is False
    assert review["limitations"] == ["deterministic rehearsal; no Z.ai call"]


def test_offline_traces_name_each_stage_and_its_abilities(tmp_path):
    harness = GlmHarness(runs_dir=tmp_path, client=GlmClient(api_key=KEY))
    manifest = harness.run(RunRequest(prompt="Explain the magnetic monopole", offline=True))
    traces = tmp_path / manifest["run_id"] / "traces"
    assert sorted(p.name for p in traces.iterdir()) == sorted(f"{s}.json" for s in STAGE_NAMES)
    for stage in STAGE_NAMES:
        trace = json.loads((traces / f"{stage}.json").read_text())
        assert trace["stage"] == stage
        assert trace["offline"] is True
        assert trace["model"] == "offline"
        assert trace["tools_requested"] == TOOLS_REQUESTED[stage]
        assert trace["tool_calls"] == []


def test_offline_run_records_an_image_path_without_reading_it(tmp_path):
    harness = GlmHarness(runs_dir=tmp_path, client=GlmClient(api_key=KEY))
    manifest = harness.run(
        RunRequest(prompt="Explain the magnetic monopole", offline=True, image="/nowhere/page.png")
    )
    intent = json.loads((tmp_path / manifest["run_id"] / "01_intent.json").read_text())
    assert intent["image_read"]["path"] == "/nowhere/page.png"
    assert manifest["image"] == "/nowhere/page.png"


def test_run_dirs_are_slugged_and_never_collide(tmp_path):
    harness = GlmHarness(runs_dir=tmp_path, client=GlmClient(api_key=KEY))
    first = harness.run(RunRequest(prompt="Explain the magnetic monopole!!", offline=True))
    second = harness.run(RunRequest(prompt="Explain the magnetic monopole!!", offline=True))
    assert first["run_id"].endswith("-explain-the-magnetic-monopole")
    assert first["run_id"] != second["run_id"]


# --------------------------------------------------------------------------
# Stage table and prompts
# --------------------------------------------------------------------------


def test_stage_table_order_and_artifacts():
    assert [stage.name for stage in STAGES] == STAGE_NAMES
    assert [stage.artifact for stage in STAGES] == STAGE_ARTIFACTS
    for stage in STAGES:
        charter = Path(__file__).resolve().parents[1] / "src" / "glm" / "agents" / stage.charter_file
        assert charter.is_file(), stage.charter_file


def test_stage_prompts_carry_request_role_and_upstream_artifacts():
    prior = {"01_intent.json": {"core_claim": "poles"}}
    for stage in STAGES:
        text = stage_prompt(stage, "Explain X", prior)
        assert text.startswith("User request:\nExplain X\n")
        assert f"You are the {stage.name} stage of the GLM chain." in text
        assert "Return one JSON object with exactly the keys the charter names." in text
        assert json.dumps(prior, indent=2) in text


def test_stage_prompts_name_platform_abilities_only_where_they_exist():
    prompts = {s.name: stage_prompt(s, "P", {}) for s in STAGES}
    assert "Platform abilities this stage may reference conceptually: web_search." in prompts["cartographer"]
    assert (
        "Platform abilities this stage may reference conceptually: code_interpreter, web_search."
        in prompts["math-director"]
    )
    assert "Platform abilities this stage may reference conceptually: web_search." in prompts["cinematographer"]
    assert "Platform abilities" not in prompts["composer"]
    # BUG (fixed by the refactor): a fake "note" tool used to leak into these.
    assert "Platform abilities" not in prompts["intent"]
    assert "Platform abilities" not in prompts["curriculum"]
    assert "note" not in prompts["intent"].split("Upstream artifacts")[0].replace("Thinking is on", "")


# --------------------------------------------------------------------------
# Client: key resolution, request body, tool loop, ping
# --------------------------------------------------------------------------


def test_resolve_api_key_prefers_zhipu_then_zai(tmp_path):
    both = {"ZHIPU_API_KEY": " " + KEY + " ", "ZAI_API_KEY": "b" * 16}
    assert resolve_api_key(both) == (KEY, "ZHIPU_API_KEY")
    assert resolve_api_key({"ZAI_API_KEY": "b" * 16}) == ("b" * 16, "ZAI_API_KEY")
    absent = {"ZHIPU_API_KEY": "   ", "OPENCODE_AUTH_JSON": str(tmp_path / "absent.json")}
    assert resolve_api_key(absent) == (None, None)


def test_resolve_api_key_falls_back_to_the_opencode_entry(tmp_path):
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({"zai-coding-plan": {"type": "api", "key": "opencode-" + "c" * 16}}))
    env = {"OPENCODE_AUTH_JSON": str(auth)}
    assert resolve_api_key(env) == ("opencode-" + "c" * 16, "opencode:auth.json:zai-coding-plan")

    auth.write_text(json.dumps({"other-provider": {"key": "x" * 20}}))
    assert resolve_api_key(env) == (None, None)
    auth.write_text("not json")
    assert resolve_api_key(env) == (None, None)

    home = {"HOME": str(tmp_path)}
    (tmp_path / ".local" / "share" / "opencode").mkdir(parents=True)
    (tmp_path / ".local" / "share" / "opencode" / "auth.json").write_text(
        json.dumps({"zai-coding-plan": {"token": "t" * 16}})
    )
    assert resolve_api_key(home) == ("t" * 16, "opencode:auth.json:zai-coding-plan")


def test_api_key_status_never_reveals_the_key(tmp_path):
    ok, detail = api_key_status({"OPENCODE_AUTH_JSON": str(tmp_path / "absent.json")})
    assert ok is False
    assert detail == (
        "no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY, or log in via OpenCode (zai-coding-plan)"
    )
    assert api_key_status({"ZAI_API_KEY": "short"}) == (False, "a GLM key is present but too short to be valid")
    ok, detail = api_key_status({"ZHIPU_API_KEY": KEY})
    assert ok is True
    assert detail == "a GLM key is set (source: ZHIPU_API_KEY)"
    assert KEY not in detail


def test_explicit_api_key_wins_and_is_marked_explicit():
    client = GlmClient(api_key="  " + KEY + " ")
    assert client.api_key == KEY
    assert client.key_source == "explicit"
    assert client.endpoint == "https://api.z.ai/api/coding/paas/v4/chat/completions"
    assert GlmClient(api_key=None).key_source is None


def test_settings_are_read_from_the_given_environment_at_call_time(tmp_path):
    env = {
        "GLM_MODEL": "glm-next",
        "GLM_BASE_URL": "https://example.test/v4/",
        "GLM_REASONING_EFFORT": "max",
        "GLM_TIMEOUT": "12.5",
        "ZAI_API_KEY": KEY,
    }
    settings = GlmSettings.from_env(env)
    assert (settings.model, settings.base_url, settings.reasoning_effort, settings.timeout) == (
        "glm-next",
        "https://example.test/v4/",
        "max",
        12.5,
    )
    assert (settings.api_key, settings.key_source) == (KEY, "ZAI_API_KEY")
    client = GlmClient.from_env(env)
    assert client.endpoint == "https://example.test/v4/chat/completions"
    assert client.model == "glm-next" and client.timeout == 12.5
    assert (client.api_key, client.key_source) == (KEY, "ZAI_API_KEY")

    bare = GlmSettings.from_env({"OPENCODE_AUTH_JSON": str(tmp_path / "absent.json")})
    assert bare.model == "glm-5.3-flash" and bare.reasoning_effort == "high"
    assert bare.api_key is None and bare.key_source is None
    with pytest.raises(GlmClientError, match="GLM_REASONING_EFFORT"):
        GlmSettings.from_env({"GLM_REASONING_EFFORT": "ultra"})


def test_complete_without_a_key_raises_before_any_request():
    transport = FakeTransport([])
    client = GlmClient(api_key="", transport=transport)
    assert client.api_key in (None, "")
    with pytest.raises(GlmClientError, match="no GLM key found"):
        client.complete(instructions="s", text="u")
    assert transport.calls == []


def test_user_content_embeds_an_image_as_a_data_uri(tmp_path):
    png = tmp_path / "page.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    assert user_content("hello") == "hello"
    content = user_content("hello", png)
    assert content[0] == {"type": "text", "text": "hello"}
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_complete_runs_the_verify_scene_tool_loop(monkeypatch):
    transport = FakeTransport(
        [
            reply("", tool_calls=[verify_call(GOOD_SCENE)], reasoning="checking"),
            reply(json.dumps({"scene_name": "LivePole", "source": GOOD_SCENE}), reasoning="done"),
        ]
    )
    client = GlmClient(api_key=KEY, model="glm-test", transport=transport)
    result = client.complete(
        instructions="composer charter",
        text="write the scene",
        reasoning_effort="low",
        tools=(VERIFY_SCENE,),
    )

    assert len(transport.calls) == 2
    first = transport.calls[0]
    assert first["url"] == client.endpoint
    assert first["headers"]["Authorization"] == f"Bearer {KEY}"
    assert first["timeout"] == 600.0
    body = first["body"]
    assert body["model"] == "glm-test"
    assert body["thinking"] == {"type": "enabled"}
    assert body["temperature"] == 0.15 and body["max_tokens"] == 2048
    assert body["tools"] == [VERIFY_SCENE_TOOL]
    assert body["messages"][0] == {"role": "system", "content": "composer charter"}
    assert body["messages"][1] == {"role": "user", "content": "write the scene"}

    second = transport.calls[1]["body"]["messages"]
    assert second[2]["role"] == "assistant"
    assert second[2]["tool_calls"] == [verify_call(GOOD_SCENE)]
    assert second[3]["role"] == "tool"
    assert second[3]["tool_call_id"] == "call-1"
    assert second[3]["name"] == "verify_scene"
    assert json.loads(second[3]["content"]) == {"passed": True, "scene_name": "LivePole", "errors": []}

    assert result.text == json.dumps({"scene_name": "LivePole", "source": GOOD_SCENE})
    assert result.tool_calls == [
        {"id": "call-1", "name": "verify_scene", "arguments": json.dumps({"source": GOOD_SCENE})}
    ]
    assert result.thinking == ["checking", "done"]
    assert result.raw == reply(json.dumps({"scene_name": "LivePole", "source": GOOD_SCENE}), reasoning="done")


def test_tool_loop_reports_handler_errors_to_the_model_instead_of_crashing():
    unknown = {"id": "c2", "type": "function", "function": {"name": "launch", "arguments": "{}"}}
    empty = {"id": "c3", "type": "function", "function": {"name": "verify_scene", "arguments": "not json"}}
    transport = FakeTransport([reply("", tool_calls=[unknown, empty]), reply('{"ok": true}')])
    client = GlmClient(api_key=KEY, transport=transport)
    result = client.complete(instructions="s", text="u", tools=(VERIFY_SCENE,))
    tool_messages = [m for m in transport.calls[1]["body"]["messages"] if m["role"] == "tool"]
    assert json.loads(tool_messages[0]["content"]) == {"error": "no local handler for launch"}
    assert json.loads(tool_messages[1]["content"])["passed"] is False
    assert json.loads(tool_messages[1]["content"])["errors"] == ["source was empty"]
    assert [c["name"] for c in result.tool_calls] == ["launch", "verify_scene"]
    assert result.text == '{"ok": true}'


def test_tool_loop_stops_after_the_round_limit():
    endless = [reply("", tool_calls=[verify_call(GOOD_SCENE)]) for _ in range(20)]
    transport = FakeTransport(endless)
    client = GlmClient(api_key=KEY, transport=transport)
    client.complete(instructions="s", text="u", tools=(VERIFY_SCENE,))
    assert len(transport.calls) == 7  # MAX_TOOL_ROUNDS + 1


def test_tool_calls_without_tools_end_the_turn():
    transport = FakeTransport([reply("plain", tool_calls=[verify_call(GOOD_SCENE)])])
    client = GlmClient(api_key=KEY, transport=transport)
    result = client.complete(instructions="s", text="u")
    assert len(transport.calls) == 1
    assert "tools" not in transport.calls[0]["body"]
    assert result.text == "plain"


def test_complete_rejects_a_reply_without_an_assistant_message():
    client = GlmClient(api_key=KEY, transport=FakeTransport([{"choices": []}]))
    with pytest.raises(GlmClientError, match="no assistant message"):
        client.complete(instructions="s", text="u")


def test_transport_errors_are_redacted():
    boom = GlmClientError(f"Z.ai returned HTTP 500: leaked {KEY} here")
    client = GlmClient(api_key=KEY, transport=FakeTransport([boom]))
    with pytest.raises(GlmClientError) as info:
        client.complete(instructions="s", text="u")
    assert KEY not in str(info.value)
    assert "[redacted]" in str(info.value)


def test_ping_expects_pong():
    transport = FakeTransport([reply("Pong!")])
    client = GlmClient(api_key=KEY, model="glm-test", transport=transport)
    assert client.ping() == (True, "pong from glm-test")
    body = transport.calls[0]["body"]
    assert body["temperature"] == 0.0 and body["max_tokens"] == 1024
    assert transport.calls[0]["timeout"] == 45.0

    client = GlmClient(api_key=KEY, transport=FakeTransport([reply("hello there")]))
    assert client.ping() == (False, "expected pong, got: 'hello there'")

    assert GlmClient(api_key="", transport=FakeTransport([])).ping() == (
        False,
        "no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY",
    )


def test_ping_reports_a_failure_after_one_attempt():
    # BUG (fixed by the refactor): ping used to sleep and retry even on 401/403.
    transport = FakeTransport([GlmClientError("Z.ai returned HTTP 401: bad key")])
    client = GlmClient(api_key=KEY, transport=transport)
    assert client.ping() == (False, "Z.ai returned HTTP 401: bad key")
    assert len(transport.calls) == 1


# --------------------------------------------------------------------------
# Live chain through the harness (fake transport)
# --------------------------------------------------------------------------


def test_live_run_writes_every_artifact_and_trace(tmp_path, capsys):
    harness, transport, progress = live_harness(tmp_path, stage_replies())
    manifest = harness.run(
        RunRequest(prompt="Explain the magnetic monopole", reasoning_effort="max", max_repairs=1)
    )
    run_dir = tmp_path / "runs" / manifest["run_id"]

    assert manifest["status"] == "completed"
    assert manifest["model"] == "glm-test"
    assert manifest["key_source"] == "explicit"
    assert manifest["scene_name"] == "LivePole"
    assert manifest["artifacts"] == {name: name for name in BUNDLE_FILES}
    assert [s["stage"] for s in manifest["stages"]] == STAGE_NAMES
    assert [s["artifact"] for s in manifest["stages"]] == STAGE_ARTIFACTS
    assert manifest["attempts"] == [
        {"attempt": 0, "mode": "zai-chat-completions", "status": "completed"}
    ]
    for name in BUNDLE_FILES:
        assert (run_dir / name).is_file(), name
    assert (run_dir / "glm_scene.py").read_text() == GOOD_SCENE
    assert json.loads((run_dir / "validation.json").read_text()) == {
        "passed": True,
        "scene_name": "LivePole",
        "errors": [],
    }
    review = json.loads((run_dir / "review.json").read_text())
    assert review["offline"] is False
    assert review["model"] == "glm-test"
    assert review["checks"] == ["artifact contract", "reverse tree", "python compilation"]
    assert review["rendered"] is False

    assert len(transport.calls) == 6
    user_texts = transport.user_texts()
    for index, stage in enumerate(STAGE_NAMES):
        assert f"You are the {stage} stage" in user_texts[index]
    assert '"core_claim": "poles"' in user_texts[1]
    system_prompts = [c["body"]["messages"][0]["content"] for c in transport.calls]
    assert all(s.strip() for s in system_prompts)
    assert "tools" not in transport.calls[0]["body"]
    assert transport.calls[5]["body"]["tools"] == [VERIFY_SCENE_TOOL]
    # per-run effort: every call uses the request's effort
    assert all(c["body"]["temperature"] == 0.9 for c in transport.calls)
    assert all(c["body"]["max_tokens"] == 12288 for c in transport.calls)

    for stage in STAGE_NAMES:
        trace = json.loads((run_dir / "traces" / f"{stage}.json").read_text())
        assert trace["stage"] == stage
        assert trace["model"] == "glm-test"
        assert trace["reasoning_effort"] == "max"
        assert trace["thinking_enabled"] is True
        assert trace["tools_requested"] == TOOLS_REQUESTED[stage]  # BUG fixed: intent had ["note"]
        assert (run_dir / "traces" / f"{stage}.raw.json").is_file()
    assert json.loads((run_dir / "traces" / "intent.json").read_text())["thinking"] == ["think-intent"]

    # BUG fixed: progress used to go to stdout, corrupting CLI JSON.
    assert capsys.readouterr().out == ""
    assert len(progress) == 6
    assert "intent" in progress[0] and "01_intent.json" in progress[0]


def test_live_run_does_not_mutate_the_shared_client(tmp_path):
    transport = FakeTransport(stage_replies())
    client = GlmClient(api_key=KEY, model="glm-test", transport=transport)
    harness = GlmHarness(runs_dir=tmp_path, client=client, progress=lambda line: None)
    harness.run(RunRequest(prompt="Explain the magnetic monopole", reasoning_effort="max"))
    assert all(c["body"]["temperature"] == 0.9 for c in transport.calls)
    assert not hasattr(client, "reasoning_effort")
    assert vars(client) == vars(GlmClient(api_key=KEY, model="glm-test", transport=transport))


def test_live_intent_stage_receives_the_image(tmp_path):
    png = tmp_path / "page.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    harness, transport, _ = live_harness(tmp_path, stage_replies())
    harness.run(RunRequest(prompt="Explain the magnetic monopole", image=str(png)))
    first_user = [m for m in transport.calls[0]["body"]["messages"] if m["role"] == "user"][0]
    assert isinstance(first_user["content"], list) and first_user["content"][1]["type"] == "image_url"
    for call in transport.calls[1:]:
        user = [m for m in call["body"]["messages"] if m["role"] == "user"][0]
        assert isinstance(user["content"], str)


def test_live_run_fails_fast_on_a_missing_image(tmp_path):
    harness, transport, _ = live_harness(tmp_path, stage_replies())
    with pytest.raises(GlmClientError, match="image file not found"):
        harness.run(RunRequest(prompt="Explain the magnetic monopole", image=str(tmp_path / "no.png")))
    assert transport.calls == []


def test_live_run_repairs_a_failing_scene(tmp_path):
    replies = stage_replies(BAD_SCENE) + [
        reply(json.dumps({"source": GOOD_SCENE}), reasoning="fixing")
    ]
    harness, transport, _ = live_harness(tmp_path, replies)
    manifest = harness.run(RunRequest(prompt="Explain the magnetic monopole", max_repairs=2))
    run_dir = tmp_path / "runs" / manifest["run_id"]

    assert manifest["status"] == "completed"
    assert len(transport.calls) == 7
    repair_text = transport.user_texts()[6]
    assert repair_text.startswith("Repair this Manim scene.")
    assert "never animate self.camera" in repair_text
    assert BAD_SCENE in repair_text
    assert transport.calls[6]["body"]["tools"] == [VERIFY_SCENE_TOOL]
    assert len(manifest["attempts"]) == 2
    assert manifest["attempts"][1]["attempt"] == 1
    assert manifest["attempts"][1]["mode"] == "composer-repair"
    assert any("never animate self.camera" in f for f in manifest["attempts"][1]["input_failures"])
    assert (run_dir / "glm_scene.py").read_text() == GOOD_SCENE
    assert json.loads((run_dir / "validation.json").read_text())["passed"] is True
    assert json.loads((run_dir / "traces" / "repair.json").read_text())["thinking"] == ["fixing"]


def test_live_run_gives_up_after_max_repairs(tmp_path):
    harness, transport, _ = live_harness(tmp_path, stage_replies(BAD_SCENE))
    with pytest.raises(RuntimeError, match="run bundle validation failed"):
        harness.run(RunRequest(prompt="Explain the magnetic monopole", max_repairs=0))
    assert len(transport.calls) == 6
    run_dir = next(p for p in (tmp_path / "runs").iterdir())
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["status"] == "failed"
    assert "never animate self.camera" in manifest["error"]
    assert manifest["completed_utc"]


def test_live_stage_that_returns_prose_fails_the_run(tmp_path):
    harness, transport, _ = live_harness(tmp_path, [reply("I would rather not.")])
    with pytest.raises(GlmClientError, match="stage intent did not return JSON"):
        harness.run(RunRequest(prompt="Explain the magnetic monopole"))
    run_dir = next(p for p in (tmp_path / "runs").iterdir())
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["status"] == "failed"
    assert manifest["error"] == "stage intent did not return JSON"
    assert manifest["stages"] == []


def test_live_cartographer_output_is_normalized(tmp_path):
    tree = reverse_tree_for("Explain the magnetic monopole")
    loose = dict(tree)
    loose["nodes"] = [dict(n, depth=str(n["depth"]), assumed="yes" if n["assumed"] else "no") for n in tree["nodes"]]
    loose["edges"] = [{"from": a, "to": b} for a, b in tree["edges"]]
    loose["spine"] = " ".join(tree["spine"])
    replies = stage_replies()
    replies[1] = reply(json.dumps(loose))
    harness, _, _ = live_harness(tmp_path, replies)
    manifest = harness.run(RunRequest(prompt="Explain the magnetic monopole"))
    saved = json.loads((tmp_path / "runs" / manifest["run_id"] / "02_knowledge_map.json").read_text())
    assert saved["nodes"] == tree["nodes"]
    assert saved["edges"] == tree["edges"]
    assert saved["spine"] == tree["spine"]


def test_live_invalid_knowledge_map_fails_at_the_cartographer(tmp_path):
    # BUG (fixed by the refactor): a bad map used to fall through to composer repairs.
    replies = stage_replies()
    replies[1] = reply(json.dumps({"target": "x", "nodes": [{"id": "a", "depth": 3, "assumed": True}]}))
    harness, transport, _ = live_harness(tmp_path, replies)
    with pytest.raises(GlmClientError, match="cartographer"):
        harness.run(RunRequest(prompt="Explain the magnetic monopole"))
    assert len(transport.calls) == 2


def test_live_composer_scene_may_arrive_in_a_fence_or_a_tool_call(tmp_path):
    fenced = stage_replies()
    fenced[5] = reply("```json\n{\"scene_name\": \"LivePole\"}\n```\n```python\n" + GOOD_SCENE + "```")
    harness, _, _ = live_harness(tmp_path, fenced)
    manifest = harness.run(RunRequest(prompt="Explain the magnetic monopole"))
    assert (tmp_path / "runs" / manifest["run_id"] / "glm_scene.py").read_text() == GOOD_SCENE

    via_tool = stage_replies()
    via_tool[5:] = [
        reply("", tool_calls=[verify_call(GOOD_SCENE)]),
        reply(json.dumps({"scene_name": "LivePole", "verified": True})),
    ]
    harness, transport, _ = live_harness(tmp_path, via_tool)
    manifest = harness.run(RunRequest(prompt="Explain the magnetic monopole"))
    run_dir = tmp_path / "runs" / manifest["run_id"]
    assert (run_dir / "glm_scene.py").read_text() == GOOD_SCENE
    assert manifest["stages"][5]["tool_calls"] == 1
    assert json.loads((run_dir / "traces" / "composer.json").read_text())["tool_calls"][0]["name"] == "verify_scene"


# --------------------------------------------------------------------------
# Service ledger and jsonutil
# --------------------------------------------------------------------------


def test_service_lists_and_reads_runs(tmp_path):
    service = GlmService(runs_dir=tmp_path, harness=GlmHarness(runs_dir=tmp_path, client=GlmClient(api_key=KEY)))
    first = service.run(RunRequest(prompt="Explain the magnetic monopole", offline=True))
    second = service.run(RunRequest(prompt="Why Fourier solves the heat equation", offline=True))
    listed = service.list_runs(limit=5)
    assert {m.run_id for m in listed} == {first["run_id"], second["run_id"]}
    assert service.list_runs(limit=1)[0].run_id == max(first["run_id"], second["run_id"])
    assert service.get_run(first["run_id"]).prompt == "Explain the magnetic monopole"
    with pytest.raises(FileNotFoundError):
        service.get_run("20000101-000000-nope")
    with pytest.raises(ValueError):
        service.get_run("../escape")
    assert GlmService(runs_dir=tmp_path / "empty").list_runs() == []


def test_extract_json_object_handles_fences_and_nesting():
    assert extract_json_object('```json\n{"a": {"b": 1}}\n```') == {"a": {"b": 1}}
    assert extract_json_object('prose {"a": "}"} trailing') == {"a": "}"}
    with pytest.raises(ValueError):
        extract_json_object("no braces here")


def test_extract_scene_source_prefers_the_last_candidate():
    text = json.dumps({"scene_name": "LivePole", "source": GOOD_SCENE})
    assert extract_scene_source(text, []) == GOOD_SCENE
    fenced = "```json\n" + text + "\n```"
    assert extract_scene_source(fenced) == GOOD_SCENE
    tool_call = {"name": "verify_scene", "arguments": json.dumps({"source": GOOD_SCENE})}
    assert extract_scene_source("all done", [tool_call]) == GOOD_SCENE
    later = GOOD_SCENE.replace("pole", "later")
    assert extract_scene_source(text, [dict(tool_call, arguments=json.dumps({"source": later}))]) == later
    with pytest.raises(ValueError):
        extract_scene_source("all done", [])
    with pytest.raises(ValueError):
        extract_scene_source('{"scene_name": "x"}')


def test_verify_scene_report_flags_the_house_rules():
    assert verify_scene_report(GOOD_SCENE) == {"passed": True, "scene_name": "LivePole", "errors": []}
    bad = verify_scene_report(BAD_SCENE)
    assert bad["passed"] is False and bad["scene_name"] == "LivePole"
    assert any("never animate self.camera" in e for e in bad["errors"])
    blocked = verify_scene_report("import os\n" + GOOD_SCENE + "\nopen('x')\n")
    assert any("blocked import 'os'" in e for e in blocked["errors"])
    assert any("blocked call open()" in e for e in blocked["errors"])
    broken = verify_scene_report("def (:\n")
    assert broken["passed"] is False and broken["scene_name"] is None
    assert any("compilation failed" in e for e in broken["errors"])
    assert verify_scene(source="") == {"passed": False, "scene_name": None, "errors": ["source was empty"]}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_cli_offline_run_prints_only_the_manifest_json(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENCODE_AUTH_JSON", str(tmp_path / "absent.json"))
    for name in ("ZHIPU_API_KEY", "ZAI_API_KEY", "GLM_REASONING_EFFORT"):
        monkeypatch.delenv(name, raising=False)
    assert cli.main(["run", "Explain the magnetic monopole", "--offline"]) == 0
    out = capsys.readouterr().out
    manifest = json.loads(out)
    assert manifest["status"] == "completed"
    assert (tmp_path / "runs" / "glm" / manifest["run_id"] / "glm_scene.py").is_file()

    assert cli.main(["runs", "--limit", "5"]) == 0
    assert capsys.readouterr().out.startswith(manifest["run_id"] + "\tcompleted\t")
    assert cli.main(["status", manifest["run_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["run_id"] == manifest["run_id"]


def test_cli_defaults_follow_the_request_contract():
    parser = cli.build_parser()
    args = parser.parse_args(["run", "p"])
    assert (args.quality, args.max_repairs, args.reasoning_effort, args.offline) == ("l", 2, None, False)
    args = parser.parse_args(["run", "p", "-qh", "--max-repairs", "5", "--reasoning-effort", "low"])
    assert (args.quality, args.max_repairs, args.reasoning_effort) == ("h", 5, "low")
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "p", "--max-repairs", "6"])
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "p", "-qz"])


def test_cli_doctor_reports_a_missing_key_without_pinging(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENCODE_AUTH_JSON", str(tmp_path / "absent.json"))
    for name in ("ZHIPU_API_KEY", "ZAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GLM_MODEL", "glm-doc")
    assert cli.main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "model=glm-doc" in out
    assert "not ready: no GLM key found" in out

    assert str(tmp_path / "absent.json") in out


def test_cli_version_does_not_read_glm_settings(monkeypatch, capsys):
    monkeypatch.setenv("GLM_REASONING_EFFORT", "not-a-level")
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.startswith("math-to-manim-glm ")
