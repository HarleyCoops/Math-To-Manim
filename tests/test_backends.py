"""Backend error handling for model providers."""

import subprocess
from urllib.error import HTTPError, URLError

import pytest

from mythos import backends


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

        def close(self):
            # HTTPError wraps fp in a finalizer that calls close() on GC. Without
            # this, the AttributeError surfaces as an unraisable exception inside
            # whatever unrelated test happens to be running when the collector
            # gets to it.
            pass

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
