"""Model backends for the Mythos chain.

Three ways to reach a reasoning model, one call signature:

- ``claude`` (default): the Claude CLI, ``claude -p --model claude-fable-5-2``
- ``codex``: the Codex CLI, ``codex exec --model <model> -``
- ``fugu-api``: any OpenAI-compatible chat endpoint (Sakana Fugu Ultra)

Configuration lives in :mod:`mythos.settings`. Secrets are read from
environment variables only and are never stamped into artifacts or error
messages.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from mythos.settings import (
    DEFAULT_COMMAND,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    FUGU_API_KEY_ENV_CANDIDATES,
    fugu_api_key_from_env,
    fugu_base_url_from_env,
)

FUGU_API_COMMANDS = {"fugu-api", "sakana-api", "sakaa-api"}


def backend_kind(command: str) -> str:
    """``"fugu"``, ``"codex"`` or ``"claude"`` for a configured M2M_COMMAND."""
    if command in FUGU_API_COMMANDS:
        return "fugu"
    if "codex" in Path(command).name.lower():
        return "codex"
    return "claude"


def is_claude_cli_command(command: str) -> bool:
    """True when `command` dispatches to the Claude CLI (subscription login).

    Model fallback only applies here: the codex and fugu-api backends have
    their own model namespaces and are explicit choices, never fallbacks.
    """
    return backend_kind(command) == "claude"


class BackendAuthError(RuntimeError):
    """The model backend is reachable but refuses our credentials."""


#: Substrings that mark an authentication failure in CLI output.
_AUTH_MARKERS = (
    "not logged in",
    "please run /login",
    "failed to authenticate",
    "invalid authentication credentials",
    "authentication_error",
    "api error: 401",
    "http 401",
    "401 unauthorized",
)

#: Access-violation exit codes from a flaky Windows CLI, worth retrying.
_CRASH_EXIT_CODES = {3221225477, -1073741819}
_CLI_CRASH_RETRIES = 3


# --------------------------------------------------------------------- #
# Locating the CLI executable (Windows npm shims)                         #
# --------------------------------------------------------------------- #

#: Where ``npm install -g @anthropic-ai/claude-code`` puts the native binary,
#: relative to the directory holding its ``claude.cmd`` shim.
_CLAUDE_NATIVE_EXE = ("node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe")

#: Windows command-line limits. A ``.cmd``/``.bat`` shim runs through
#: cmd.exe, whose line tops out at 8191 characters; a native executable gets
#: CreateProcess's ~32k. Leave headroom for quoting.
_CMD_SHIM_LINE_LIMIT = 8191
_CREATE_PROCESS_LINE_LIMIT = 32767
_LINE_HEADROOM = 512


def _is_cmd_shim(executable: str) -> bool:
    return executable.lower().endswith((".cmd", ".bat"))


def resolve_command(
    command: str,
    *,
    which: Callable[[str], str | None] = shutil.which,
    os_name: str = os.name,
) -> str:
    """Resolve a CLI executable, tolerating Windows .cmd shims.

    On Windows the npm shim ``claude.cmd`` is what PATH finds; when the native
    ``claude.exe`` sits beside it, prefer that (it is not bound by cmd.exe's
    8191-character command line).
    """
    found = which(command)
    if not found and os_name == "nt" and not _is_cmd_shim(command):
        found = which(command + ".cmd")
    if not found:
        return command
    if os_name == "nt" and _is_cmd_shim(found) and Path(found).stem.lower() == "claude":
        native = Path(found).parent.joinpath(*_CLAUDE_NATIVE_EXE)
        if native.is_file():
            return str(native)
    return found


def command_line_limit(executable: str) -> int:
    """Longest command line the OS will hand to ``executable`` (Windows)."""
    if _is_cmd_shim(executable):
        return _CMD_SHIM_LINE_LIMIT
    return _CREATE_PROCESS_LINE_LIMIT


def claude_cli_command(
    executable: str,
    *,
    model: str,
    system_extra: str | None,
    prompt: str,
    os_name: str = os.name,
) -> tuple[list[str], str | None]:
    """Build the ``claude -p`` argv and decide how the prompt travels.

    Returns ``(argv, stdin_text)``. The Windows Claude CLI can crash reading
    piped stdin, so on Windows the prompt rides in argv whenever the whole
    command line fits the limit of the resolved executable; otherwise (and
    always off Windows) it goes through stdin.
    """
    cmd = [executable, "-p", "--output-format", "text", "--model", model]
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]
    if os_name != "nt":
        return cmd, prompt
    with_prompt = cmd[:2] + [prompt] + cmd[2:]
    # Each argument is quoted and space-separated on the command line.
    line_length = sum(len(arg) + 3 for arg in with_prompt)
    if line_length <= command_line_limit(executable) - _LINE_HEADROOM:
        return with_prompt, None
    return cmd, prompt


# --------------------------------------------------------------------- #
# One call, any backend                                                  #
# --------------------------------------------------------------------- #

def run_model(
    prompt: str,
    *,
    system_extra: str | None = None,
    command: str = DEFAULT_COMMAND,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Send one prompt to the configured backend and return raw text output."""
    kind = backend_kind(command)
    if kind == "fugu":
        return call_fugu_chat(
            prompt,
            system_prompt=system_extra,
            model=model,
            base_url=fugu_base_url_from_env(),
            timeout=timeout,
        )
    executable = resolve_command(command)
    if kind == "codex":
        return _run_codex(executable, prompt, system_extra=system_extra,
                          model=model, timeout=timeout)
    return _run_claude(executable, prompt, system_extra=system_extra,
                       model=model, timeout=timeout)


def _run_codex(executable: str, prompt: str, *, system_extra: str | None,
               model: str, timeout: float) -> str:
    """Codex OAuth backend: prompt on stdin, system extra folded in."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False,
        prefix="mythos-codex-", suffix=".txt",
    ) as output_file:
        output_path = Path(output_file.name)
    cmd = [
        executable,
        "-c", 'service_tier="fast"',
        "exec",
        "--model", model,
        "--output-last-message", str(output_path),
        "-",
    ]
    payload = f"{system_extra}\n\n{prompt}" if system_extra else prompt
    try:
        completed = subprocess.run(
            cmd, input=payload, text=True, capture_output=True,
            encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
        _raise_for_failure(completed, cmd)
        if output_path.exists():
            return output_path.read_text(encoding="utf-8")
        return completed.stdout
    finally:
        output_path.unlink(missing_ok=True)


def _run_claude(executable: str, prompt: str, *, system_extra: str | None,
                model: str, timeout: float) -> str:
    cmd, stdin_prompt = claude_cli_command(
        executable, model=model, system_extra=system_extra, prompt=prompt)
    # This repo runs the chain on the Claude CLI's subscription login.
    # A stray ANTHROPIC_API_KEY in the environment would silently
    # override that login (and 401 if stale), so scrub it.
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    # The Windows Claude CLI intermittently dies with an access
    # violation (0xC0000005); retry those crashes a few times.
    for attempt in range(_CLI_CRASH_RETRIES + 1):
        completed = subprocess.run(
            cmd, input=stdin_prompt, text=True, capture_output=True,
            encoding="utf-8", errors="replace", env=env,
            timeout=timeout, check=False,
        )
        if completed.returncode not in _CRASH_EXIT_CODES:
            break
        time.sleep(1.5 * (attempt + 1))
    _raise_for_failure(completed, cmd)
    stripped = (completed.stdout or "").strip().lower()
    if stripped.startswith("not logged in"):
        raise BackendAuthError(
            f"The {Path(cmd[0]).stem!r} backend is not logged in. "
            "Run `claude /login` (or `codex login`), or set "
            "M2M_COMMAND/M2M_MODEL to a configured backend."
        )
    return completed.stdout


def _raise_for_failure(completed: subprocess.CompletedProcess, cmd: list[str]) -> None:
    if completed.returncode == 0:
        return
    combined = f"{completed.stdout}\n{completed.stderr}".lower()
    if any(marker in combined for marker in _AUTH_MARKERS):
        raise BackendAuthError(
            f"The {Path(cmd[0]).stem!r} backend rejected our credentials.\n"
            "Fix one of:\n"
            "  - Claude CLI: run `claude /login` (the chain uses the CLI's "
            "subscription login; a stale ANTHROPIC_API_KEY is scrubbed on "
            "purpose)\n"
            "  - Codex CLI:  run `codex login`\n"
            "  - Or point M2M_COMMAND / M2M_MODEL at a backend that is "
            "logged in.\n"
            f"backend output (tail):\n{combined[-1200:]}"
        )
    raise RuntimeError(
        f"Mythos model command failed (exit {completed.returncode})\n"
        f"command: {cmd[0]}\n"
        f"stderr:\n{completed.stderr[-4000:]}"
    )


# --------------------------------------------------------------------- #
# Fugu / OpenAI-compatible HTTP backend                                  #
# --------------------------------------------------------------------- #

def call_fugu_chat(
    prompt: str,
    *,
    system_prompt: str | None,
    model: str,
    base_url: str,
    timeout: float,
) -> str:
    """Call an OpenAI-compatible chat completion endpoint with Fugu keys."""
    api_key, env_name = fugu_api_key_from_env()
    if not api_key:
        names = ", ".join(FUGU_API_KEY_ENV_CANDIDATES)
        raise RuntimeError(f"No Fugu API key found. Set one of: {names}.")
    return _call_openai_compatible(
        prompt,
        system_prompt=system_prompt,
        model=model,
        base_url=base_url,
        timeout=timeout,
        api_key=api_key,
        key_env_name=env_name or "FUGU_API_KEY",
    )


def _call_openai_compatible(
    prompt: str,
    *,
    system_prompt: str | None,
    model: str,
    base_url: str,
    timeout: float,
    api_key: str,
    key_env_name: str,
) -> str:
    """POST to any OpenAI-compatible /chat/completions endpoint."""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    url = _chat_completions_url(base_url)
    request = Request(
        url,
        data=json.dumps({"model": model, "messages": messages}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-4000:]
        raise RuntimeError(
            "Fugu API call failed\n"
            f"endpoint: {url}\nmodel: {model}\napi_key_env: {key_env_name}\n"
            f"status: {exc.code}\nbody:\n{detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Fugu API call failed before a response was received\n"
            f"endpoint: {url}\nmodel: {model}\napi_key_env: {key_env_name}\n"
            f"reason: {exc.reason}"
        ) from exc

    return _extract_openai_compatible_text(raw)


def _chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _extract_openai_compatible_text(raw: str) -> str:
    try:
        payload: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Fugu API returned non-JSON response:\n{raw[:1000]}") from exc

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        text = _extract_responses_text(payload)
        if text is not None:
            return text
        raise RuntimeError(
            "Fugu API response did not include choices[0].message.content. "
            f"Response keys: {sorted(payload)}"
        ) from exc
    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        return "".join(parts)
    if not isinstance(content, str):
        raise RuntimeError("Fugu API response content was not text")
    return content


def _extract_responses_text(payload: dict[str, Any]) -> str | None:
    output = payload.get("output")
    if not isinstance(output, list):
        return None
    chunks: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        for part in item.get("content", []):
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "".join(chunks) if chunks else None
