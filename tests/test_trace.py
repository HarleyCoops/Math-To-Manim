"""The run trace writer and its scrubber."""

from __future__ import annotations

import json

import pytest

from mythos import backends, trace
from mythos.trace import EVENT_FIELDS, Scrubber, TraceWriter


def _scrubber() -> Scrubber:
    return Scrubber(home_dirs=(r"C:\Users\alice", "/home/alice"),
                    user_names=("alice", "Alice Example"),
                    secrets=("supersecretvalue-1234567890",))


@pytest.mark.parametrize("raw", [
    "key sk-ant-api03-AbCdEfGhIjKlMnOpQrStUv here",
    "openai sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX12345",
    "github ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "hf hf_ABCDEFGHIJKLMNOPQRSTUVWXYZabcd",
    "aws AKIAABCDEFGHIJKLMNOP",
    "Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345",
    'ANTHROPIC_API_KEY="abcdef0123456789abcdef"',
    "password=hunter2hunter2",
    "token eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop",
    "env value supersecretvalue-1234567890 leaked",
])
def test_scrubber_removes_keys_and_tokens(raw):
    cleaned = _scrubber().text(raw)
    assert "<secret>" in cleaned
    for fragment in ("sk-ant-api03", "sk-proj-ABC", "ghp_ABC", "hf_ABC", "AKIAABC",
                     "abcdefghijklmnopqrstuvwxyz012345", "abcdef0123456789abcdef",
                     "hunter2", "eyJhbGci", "supersecretvalue"):
        assert fragment not in cleaned


def test_scrubber_removes_home_paths_names_and_emails():
    s = _scrubber()
    text = (r"C:\Users\alice\Math-To-Manim\runs\x.mp4 and C:/Users/bob/file "
            r"and C:\\Users\\carol\\y and /home/alice/repo and /Users/dave/z "
            "by Alice Example (alice) <alice.example@mail.com>")
    cleaned = s.text(text)
    for leaked in ("alice", "Alice", "bob", "carol", "dave", "@mail.com", "Users"):
        assert leaked not in cleaned, (leaked, cleaned)
    assert r"~\Math-To-Manim\runs\x.mp4" in cleaned
    assert "<email>" in cleaned and "<user>" in cleaned


def test_scrubber_keeps_ordinary_text_and_code():
    s = _scrubber()
    text = 'Text("Free CDN for All", color="#6A4DFF")  # Alicegate is not a name match'
    assert s.text(text) == text


def test_scrubber_walks_nested_values():
    s = _scrubber()
    cleaned = s.value({"a": ["/home/alice/x", {"k": "alice@x.org"}], "n": 3, "b": None})
    assert cleaned == {"a": ["~/x", {"k": "<email>"}], "n": 3, "b": None}


def test_trace_writer_schema_sequence_and_scrubbing(tmp_path):
    writer = TraceWriter(tmp_path / "events.jsonl", run_id="r1", task_id="Benefits_01",
                         profile="motion", model="m", scrubber=_scrubber())
    first = writer.emit("agent_call", stage="brief_parser", input="prompt text",
                        output={"text": "from /home/alice/x"}, tokens_in=10, tokens_out=5,
                        latency_ms=12.345)
    second = writer.emit("tool_call", stage="scene_coder", input={"tool": "Read"},
                         output="ok", parent_seq=first)
    events = writer.read()
    assert [e["seq"] for e in events] == [1, 2] and second == 2
    for event in events:
        assert tuple(event) == EVENT_FIELDS
        assert event["run_id"] == "r1" and event["task_id"] == "Benefits_01"
        assert event["profile"] == "motion"
    assert events[0]["prompt_sha"] and len(events[0]["prompt_sha"]) == 64
    assert events[0]["output"] == {"text": "from ~/x"}
    assert events[1]["parent_seq"] == 1
    assert writer.tokens_in == 10 and writer.tokens_out == 5
    with pytest.raises(ValueError):
        writer.emit("not_an_event", stage="x")


def test_run_model_records_an_agent_call_when_bound(tmp_path, monkeypatch):
    envelope = json.dumps({"type": "result", "is_error": False, "result": '{"ok": 1}',
                           "usage": {"input_tokens": 7, "cache_read_input_tokens": 3,
                                     "output_tokens": 4},
                           "modelUsage": {"claude-fable-5-2": {}}})
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        import subprocess
        return subprocess.CompletedProcess(cmd, 0, stdout=envelope, stderr="")

    monkeypatch.setattr(backends, "resolve_command", lambda command: "/opt/claude")
    monkeypatch.setattr(backends.subprocess, "run", fake_run)
    writer = TraceWriter(tmp_path / "e.jsonl", run_id="r", profile="motion",
                         scrubber=_scrubber())
    with trace.bind(writer, "brief_parser"):
        reply = backends.run_model("hi", system_extra="sys", command="claude", model="m",
                                   timeout=1.0)
    assert reply == '{"ok": 1}'
    assert "json" in seen["cmd"]
    (event,) = writer.read()
    assert event["event_type"] == "agent_call" and event["stage"] == "brief_parser"
    assert event["tokens_in"] == 10 and event["tokens_out"] == 4
    assert event["model"] == "claude-fable-5-2"
    assert event["input"]["system"] == "sys" and event["output"] == {"text": '{"ok": 1}'}
    assert trace.current() is None


def test_run_model_unbound_keeps_text_output(monkeypatch):
    import subprocess

    monkeypatch.setattr(backends, "resolve_command", lambda command: "/opt/claude")
    monkeypatch.setattr(backends.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "plain", ""))
    assert backends.run_model("hi", command="claude", model="m", timeout=1.0) == "plain"
