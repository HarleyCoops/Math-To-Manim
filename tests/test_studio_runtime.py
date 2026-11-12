"""Studio agent runtime: agent files, SDK options and result handling, with a fake SDK."""

import json
from types import SimpleNamespace

import pytest

from studio import agent_check
from studio.runtime import (
    AgentSpec,
    LocalSdkRuntime,
    RuntimeUnavailable,
    get_runtime,
    load_agent_file,
)


def fake_query(messages, seen=None):
    async def query_fn(*, prompt, options):
        if seen is not None:
            seen.update(prompt=prompt, options=options)
        for message in messages:
            yield message

    return query_fn


def result_message(**overrides):
    values = dict(structured_output={"os": "Linux"}, result="done", session_id="s1",
                  num_turns=3, total_cost_usd=0.01, is_error=False, errors=None,
                  subtype="success", permission_denials=[])
    values.update(overrides)
    return SimpleNamespace(**values)


def test_agent_file_gives_name_model_and_system(tmp_path):
    path = tmp_path / "scout.md"
    path.write_text("---\nname: Story Scout\nmodel: claude-fable-5-2\ntools:\n  - x\n---\n\n"
                    "Find the paper.\n", encoding="utf-8")
    spec = load_agent_file(path, tools=("WebSearch",))
    assert (spec.name, spec.model, spec.system) == (
        "Story Scout", "claude-fable-5-2", "Find the paper.")
    assert spec.tools == ("WebSearch",)


def test_shipped_doctor_agent_loads():
    spec = load_agent_file(agent_check.AGENTS_DIR / "studio-doctor.md")
    assert spec.name == "Studio Doctor"
    assert "one JSON object" in spec.system


def test_local_runtime_is_hermetic_and_denies_unlisted_tools(tmp_path):
    seen = {}
    runtime = LocalSdkRuntime(query_fn=fake_query([result_message()], seen),
                              config_dir="C:/logins/personal")
    spec = AgentSpec(name="a", system="sys", tools=("Bash",), schema={"type": "object"})
    result = runtime.run(spec, "go", cwd=tmp_path)

    options = seen["options"]
    assert options["allowed_tools"] == ["Bash"]
    assert options["permission_mode"] == "dontAsk"
    assert options["setting_sources"] == []
    assert options["model"] == "claude-fable-5-2"
    assert options["output_format"] == {"type": "json_schema", "schema": {"type": "object"}}
    assert options["env"] == {"CLAUDE_CONFIG_DIR": "C:/logins/personal"}
    assert result.ok and result.output == {"os": "Linux"}
    assert (result.session_id, result.turns, result.runtime) == ("s1", 3, "local-sdk")


def test_local_runtime_reports_errors_instead_of_raising(tmp_path):
    spec = AgentSpec(name="a", system="sys", schema={"type": "object"})

    missing = LocalSdkRuntime(query_fn=fake_query(
        [result_message(structured_output=None)])).run(spec, "go", cwd=tmp_path)
    assert not missing.ok and "no structured output" in missing.error

    failed = LocalSdkRuntime(query_fn=fake_query(
        [result_message(is_error=True, errors=["rate limited"])])).run(
            spec, "go", cwd=tmp_path)
    assert not failed.ok and "rate limited" in failed.error

    async def broken(*, prompt, options):
        raise OSError("claude CLI not found")
        yield  # pragma: no cover

    crashed = LocalSdkRuntime(query_fn=broken).run(spec, "go", cwd=tmp_path)
    assert not crashed.ok and "claude CLI not found" in crashed.error

    silent = LocalSdkRuntime(query_fn=fake_query([])).run(
        AgentSpec(name="a", system="sys"), "go", cwd=tmp_path)
    assert not silent.ok and "no result message" in silent.error


def test_runtime_selection(monkeypatch):
    monkeypatch.delenv("STUDIO_RUNTIME", raising=False)
    assert get_runtime().name == "local-sdk"
    with pytest.raises(RuntimeUnavailable, match="no API credit"):
        get_runtime("managed-agents")
    with pytest.raises(ValueError):
        get_runtime("somewhere-else")


def test_agent_check_writes_its_record(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    report = {key: None for key in agent_check.DOCTOR_SCHEMA["required"]}
    runtime = LocalSdkRuntime(query_fn=fake_query(
        [result_message(structured_output=report)]))
    lines = []
    assert agent_check.run_agent_check(runtime=runtime, log=lines.append) == 0
    record = json.loads(
        (tmp_path / "studio" / "doctor" / "agent-check.json").read_text(encoding="utf-8"))
    assert record["ok"] is True and record["output"] == report
    assert set(agent_check.DOCTOR_SCHEMA["properties"]) == set(report)
