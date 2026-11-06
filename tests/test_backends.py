"""Backend error handling, CLI resolution and the Windows command-line limit."""

import subprocess
from urllib.error import HTTPError, URLError

import pytest

from mythos import backends
from mythos.backends import claude_cli_command, resolve_command

CHARTER = "x" * 2500          # the Cinematic Charter rides in argv too
LONG_PROMPT = "p" * 11_700    # a real production prompt that broke claude.cmd
SHORT_PROMPT = "p" * 2_000


def test_openai_compatible_urlerror_reports_key_env(monkeypatch):
    def raise_urlerror(*args, **kwargs):
        raise URLError("network down")

    monkeypatch.setattr(backends, "urlopen", raise_urlerror)

    with pytest.raises(RuntimeError) as exc:
        backends._call_openai_compatible(
            "hello",
            system_prompt=None,
            model="fugu-ultra",
            base_url="https://example.test/v1",
            timeout=1.0,
            api_key="secret",
            key_env_name="FUGU_API_KEY",
        )

    message = str(exc.value)
    assert "api_key_env: FUGU_API_KEY" in message
    assert "network down" in message


def test_openai_compatible_httperror_reports_key_env(monkeypatch):
    class ResponseBody:
        def read(self):
            return b'{"error":"bad auth"}'

    def raise_httperror(*args, **kwargs):
        raise HTTPError(
            url="https://example.test/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=ResponseBody(),
        )

    monkeypatch.setattr(backends, "urlopen", raise_httperror)

    with pytest.raises(RuntimeError) as exc:
        backends._call_openai_compatible(
            "hello",
            system_prompt=None,
            model="fugu-ultra",
            base_url="https://example.test/v1",
            timeout=1.0,
            api_key="secret",
            key_env_name="FUGU_API_KEY",
        )

    message = str(exc.value)
    assert "api_key_env: FUGU_API_KEY" in message
    assert "status: 401" in message
    assert "bad auth" in message


def test_codex_backend_reads_output_last_message(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["input"] = kwargs["input"]
        output_path = cmd[cmd.index("--output-last-message") + 1]
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write('{"ok": true}')
        return subprocess.CompletedProcess(cmd, 0, stdout="banner", stderr="")

    monkeypatch.setattr(backends, "resolve_command", lambda command: command)
    monkeypatch.setattr(backends.subprocess, "run", fake_run)

    result = backends.run_model(
        "return json",
        system_extra="system",
        command="codex",
        model="gpt-5.5",
        timeout=1.0,
    )

    assert result == '{"ok": true}'
    assert captured["cmd"][:3] == ["codex", "-c", 'service_tier="fast"']
    assert "--output-last-message" in captured["cmd"]
    assert captured["input"] == "system\n\nreturn json"


# --------------------------------------------------------------------- #
# Windows: npm shim vs native exe, argv vs stdin                         #
# --------------------------------------------------------------------- #

def _npm_prefix(tmp_path, *, with_native: bool):
    shim = tmp_path / "claude.cmd"
    shim.write_text("@echo off\n", encoding="utf-8")
    if with_native:
        native = tmp_path / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        native.parent.mkdir(parents=True)
        native.write_bytes(b"MZ")
    return shim


def test_resolve_command_prefers_native_claude_exe_beside_the_npm_shim(tmp_path):
    shim = _npm_prefix(tmp_path, with_native=True)
    resolved = resolve_command("claude", which=lambda name: str(shim), os_name="nt")
    assert resolved.endswith("claude.exe")
    assert "node_modules" in resolved


def test_resolve_command_keeps_the_shim_when_no_native_exe(tmp_path):
    shim = _npm_prefix(tmp_path, with_native=False)
    resolved = resolve_command("claude", which=lambda name: str(shim), os_name="nt")
    assert resolved == str(shim)


def test_resolve_command_tries_cmd_suffix_on_windows(tmp_path):
    shim = _npm_prefix(tmp_path, with_native=False)
    lookups = {"claude.cmd": str(shim)}
    resolved = resolve_command("claude", which=lookups.get, os_name="nt")
    assert resolved == str(shim)
    assert resolve_command("claude", which=lambda name: None, os_name="nt") == "claude"


def test_resolve_command_on_posix_is_plain_which():
    assert resolve_command("claude", which=lambda name: "/usr/bin/claude", os_name="posix") == "/usr/bin/claude"
    assert resolve_command("claude", which=lambda name: None, os_name="posix") == "claude"


def test_long_prompt_goes_through_stdin_for_a_cmd_shim():
    cmd, stdin = claude_cli_command(r"C:\\Users\\me\\AppData\\Roaming\\npm\\claude.CMD",
                                    model="claude-fable-5", system_extra=CHARTER,
                                    prompt=LONG_PROMPT, os_name="nt")
    assert stdin == LONG_PROMPT
    assert LONG_PROMPT not in cmd
    assert sum(len(a) + 3 for a in cmd) < 8191


def test_long_prompt_rides_argv_for_the_native_exe():
    cmd, stdin = claude_cli_command(r"C:\\npm\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe",
                                    model="claude-fable-5", system_extra=CHARTER,
                                    prompt=LONG_PROMPT, os_name="nt")
    assert stdin is None
    assert cmd[:3] == [cmd[0], "-p", LONG_PROMPT]


def test_short_prompt_rides_argv_even_for_a_cmd_shim():
    cmd, stdin = claude_cli_command(r"C:\\npm\\claude.cmd", model="claude-fable-5",
                                    system_extra=CHARTER, prompt=SHORT_PROMPT, os_name="nt")
    assert stdin is None and SHORT_PROMPT in cmd


def test_argv_decision_counts_the_whole_command_line():
    # Prompt alone fits a shim, prompt + charter does not.
    prompt = "p" * 7_000
    _, stdin = claude_cli_command(r"C:\\npm\\claude.cmd", model="m", system_extra=CHARTER,
                                  prompt=prompt, os_name="nt")
    assert stdin == prompt
    _, stdin = claude_cli_command(r"C:\\npm\\claude.cmd", model="m", system_extra=None,
                                  prompt=prompt, os_name="nt")
    assert stdin is None


def test_prompt_always_goes_through_stdin_off_windows():
    cmd, stdin = claude_cli_command("/usr/bin/claude", model="m", system_extra=CHARTER,
                                    prompt=SHORT_PROMPT, os_name="posix")
    assert stdin == SHORT_PROMPT
    assert cmd == ["/usr/bin/claude", "-p", "--output-format", "text", "--model", "m",
                   "--append-system-prompt", CHARTER]


def test_claude_backend_runs_resolved_executable(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["input"] = kwargs["input"]
        captured["env"] = kwargs["env"]
        return subprocess.CompletedProcess(cmd, 0, stdout="answer", stderr="")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "stale")
    monkeypatch.setattr(backends, "resolve_command", lambda command: "/opt/claude")
    monkeypatch.setattr(backends.subprocess, "run", fake_run)
    assert backends.run_model("hi", system_extra="sys", command="claude", model="m",
                              timeout=1.0) == "answer"
    assert captured["cmd"][0] == "/opt/claude"
    assert captured["input"] == "hi" or "hi" in captured["cmd"]  # stdin off Windows, argv on it
    assert "ANTHROPIC_API_KEY" not in captured["env"]
