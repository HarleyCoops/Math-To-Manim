"""Anthropic model fallback ladder: same Claude CLI login, no API key.

Contract under test:
- model-specific failures walk M2M_MODEL_FALLBACKS in order and stick with
  the first model that answers (recorded in the manifest)
- auth failures never fall back: a broken login is broken for every model
- non-Claude backends (codex, fugu-api) never fall back
"""

from __future__ import annotations

import pytest

import mythos.harness as harness_mod
from mythos.backends import (
    BackendAuthError,
    is_claude_cli_command,
    model_fallbacks_from_env,
)
from mythos.harness import MythosHarness


# --------------------------------------------------------------------- #
# Config parsing                                                         #
# --------------------------------------------------------------------- #

def test_default_fallback_chain_is_anthropic_no_haiku(monkeypatch):
    monkeypatch.delenv("M2M_MODEL_FALLBACKS", raising=False)
    chain = model_fallbacks_from_env()
    assert chain == ("claude-opus-4-8", "claude-sonnet-5")
    assert not any("haiku" in m for m in chain)


def test_fallbacks_disabled_by_empty_string(monkeypatch):
    monkeypatch.setenv("M2M_MODEL_FALLBACKS", "")
    assert model_fallbacks_from_env() == ()


def test_fallbacks_custom_list(monkeypatch):
    monkeypatch.setenv("M2M_MODEL_FALLBACKS", " claude-sonnet-5 , claude-opus-4-8 ")
    assert model_fallbacks_from_env() == ("claude-sonnet-5", "claude-opus-4-8")


def test_claude_cli_detection():
    assert is_claude_cli_command("claude")
    assert is_claude_cli_command(r"C:\Users\someone\bin\claude.cmd")
    assert not is_claude_cli_command("codex")
    assert not is_claude_cli_command("fugu-api")


# --------------------------------------------------------------------- #
# The ladder itself                                                      #
# --------------------------------------------------------------------- #

def _harness(tmp_path, **kwargs):
    return MythosHarness(runs_dir=tmp_path, command="claude",
                         model="claude-fable-5",
                         model_fallbacks=("claude-opus-4-8",
                                          "claude-sonnet-5"),
                         **kwargs)


def test_fallback_walks_ladder_and_sticks(tmp_path, monkeypatch):
    harness = _harness(tmp_path)
    calls = []

    def fake_run_model(prompt, *, system_extra=None, command, model, timeout):
        calls.append(model)
        if model == "claude-fable-5":
            raise RuntimeError("Mythos model command failed (exit 1)\n529 overloaded")
        return f"answer from {model}"

    monkeypatch.setattr(harness_mod, "run_model", fake_run_model)
    out = harness._model("hello")
    assert out == "answer from claude-opus-4-8"
    assert harness.model == "claude-opus-4-8"          # sticky
    assert harness.fallbacks_used[0]["from"] == "claude-fable-5"
    assert harness.fallbacks_used[0]["to"] == "claude-opus-4-8"

    # the next call goes straight to the survivor — no wasted primary call
    harness._model("again")
    assert calls == ["claude-fable-5", "claude-opus-4-8", "claude-opus-4-8"]


def test_fallback_exhaustion_reports_every_model_tried(tmp_path, monkeypatch):
    harness = _harness(tmp_path)

    def always_fail(prompt, *, system_extra=None, command, model, timeout):
        raise RuntimeError(f"model {model} unavailable")

    monkeypatch.setattr(harness_mod, "run_model", always_fail)
    with pytest.raises(RuntimeError) as excinfo:
        harness._model("hello")
    message = str(excinfo.value)
    for model in ("claude-fable-5", "claude-opus-4-8", "claude-sonnet-5"):
        assert model in message


def test_auth_error_never_falls_back(tmp_path, monkeypatch):
    harness = _harness(tmp_path)
    calls = []

    def auth_fail(prompt, *, system_extra=None, command, model, timeout):
        calls.append(model)
        raise BackendAuthError("run `claude /login`")

    monkeypatch.setattr(harness_mod, "run_model", auth_fail)
    with pytest.raises(BackendAuthError):
        harness._model("hello")
    assert calls == ["claude-fable-5"]                 # exactly one attempt
    assert harness.fallbacks_used == []


def test_codex_backend_never_falls_back(tmp_path, monkeypatch):
    harness = MythosHarness(runs_dir=tmp_path, command="codex",
                            model="gpt-5.5",
                            model_fallbacks=("claude-opus-4-8",))
    calls = []

    def fail(prompt, *, system_extra=None, command, model, timeout):
        calls.append(model)
        raise RuntimeError("codex exploded")

    monkeypatch.setattr(harness_mod, "run_model", fail)
    with pytest.raises(RuntimeError, match="codex exploded"):
        harness._model("hello")
    assert calls == ["gpt-5.5"]


def test_manifest_records_fallback(tmp_path, monkeypatch):
    harness = _harness(tmp_path)

    def flaky(prompt, *, system_extra=None, command, model, timeout):
        if model == "claude-fable-5":
            raise RuntimeError("529 overloaded")
        return '{"stage": "x", "content": "' + "y" * 400 + '"}'

    monkeypatch.setattr(harness_mod, "run_model", flaky)
    monkeypatch.setattr(harness, "load_charter", lambda f: "CHARTER")
    monkeypatch.setattr(
        harness_mod.MythosHarness, "_codegen",
        lambda self, run_dir, prompt, spec, manifest: (
            run_dir / "mythos_scene.py", "FakeScene"))
    monkeypatch.setattr(
        harness_mod.MythosHarness, "_verify",
        staticmethod(lambda code_path, prompt=None: (True, None)))
    # make every stage's artifact pass validation
    monkeypatch.setattr(harness_mod, "validate_stage_artifact",
                        lambda slug, artifact: None)
    manifest = harness.run("test the ladder")
    assert manifest["model"] == "claude-opus-4-8"
    assert manifest["model_fallbacks"][0]["from"] == "claude-fable-5"
