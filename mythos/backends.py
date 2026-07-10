"""Model backends for the Mythos chain.

Three ways to reach a reasoning model, one call signature:

- ``claude`` (default): the Claude CLI, ``claude -p --model claude-fable-5``
- ``codex``: the Codex CLI, ``codex exec --model <model> -``
- ``fugu-api``: any OpenAI-compatible chat endpoint (Sakana Fugu Ultra)

Secrets are read from environment variables only and are never stamped into
artifacts or error messages.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from mythos.charter import load_env_file, resolve_command

# ----------------------------------------------------------------------- #
# Configuration: environment first, sane defaults second.                  #
#                                                                          #
#   M2M_MODEL           baseline model id      (default: claude-fable-5)   #
#   M2M_COMMAND         backend                (default: claude)           #
#   M2M_TIMEOUT         per-model-call seconds (default: 900)              #
#                                                                          #
# Values may live in the environment or in a local (gitignored) .env.      #
# (The archived pipeline's M2M2_MYTHOS_MODEL is deliberately NOT read:     #
# it configured a different engine and silently retargeting this one       #
# to a non-Claude model with the claude backend would be a footgun.)       #
# ----------------------------------------------------------------------- #
load_env_file()

DEFAULT_MODEL = os.getenv("M2M_MODEL") or "claude-fable-5"
DEFAULT_COMMAND = os.getenv("M2M_COMMAND", "claude")
DEFAULT_TIMEOUT = float(os.getenv("M2M_TIMEOUT", "900"))


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

FUGU_DEFAULT_BASE_URL = "https://api.sakana.ai/v1"
FUGU_API_COMMANDS = {"fugu-api", "sakana-api", "sakaa-api"}
FUGU_API_KEY_ENV_CANDIDATES = ("FUGU_API_KEY", "SAKANA_API_KEY", "SAKAA_API_KEY")

#: Windows CreateProcess command lines top out near 32k chars; leave headroom.
_ARGV_PROMPT_LIMIT = 28000

#: Access-violation exit codes from a flaky Windows CLI, worth retrying.
_CRASH_EXIT_CODES = {3221225477, -1073741819}
_CLI_CRASH_RETRIES = 3


def run_model(
    prompt: str,
    *,
    system_extra: str | None = None,
    command: str = DEFAULT_COMMAND,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Send one prompt to the configured backend and return raw text output."""
    if command in FUGU_API_COMMANDS:
        return call_fugu_chat(
            prompt,
            system_prompt=system_extra,
            model=model,
            base_url=fugu_base_url_from_env(),
            timeout=timeout,
        )
    resolved = resolve_command(command)
    if "codex" in Path(command).name.lower():
        # Codex OAuth backend: prompt on stdin, system extra folded in.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False,
            prefix="mythos-codex-", suffix=".txt",
        ) as output_file:
            output_path = Path(output_file.name)
        cmd = [
            resolved,
            "-c", 'service_tier="fast"',
            "exec",
            "--model", model,
            "--output-last-message", str(output_path),
            "-",
        ]
        payload = f"{system_extra}\n\n{prompt}" if system_extra else prompt
        completed = subprocess.run(
            cmd, input=payload, text=True, capture_output=True,
            encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
        if completed.returncode == 0 and output_path.exists():
            try:
                return output_path.read_text(encoding="utf-8")
            finally:
                output_path.unlink(missing_ok=True)
    else:
        cmd = [resolved, "-p", "--output-format", "text", "--model", model]
        if system_extra:
            cmd += ["--append-system-prompt", system_extra]
        stdin_prompt: str | None = prompt
        if os.name == "nt" and len(prompt) < _ARGV_PROMPT_LIMIT:
            # The Windows Claude CLI can crash reading piped stdin; pass the
            # prompt as an argument when it fits in the command line.
            cmd.insert(2, prompt)
            stdin_prompt = None
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
    if completed.returncode != 0:
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
    stripped = (completed.stdout or "").strip().lower()
    if stripped.startswith("not logged in"):
        raise BackendAuthError(
            f"The {Path(cmd[0]).stem!r} backend is not logged in. "
            "Run `claude /login` (or `codex login`), or set "
            "M2M_COMMAND/M2M_MODEL to a configured backend."
        )
    return completed.stdout


# --------------------------------------------------------------------- #
# Fugu / OpenAI-compatible HTTP backend                                  #
# --------------------------------------------------------------------- #

def fugu_api_key_from_env() -> tuple[str | None, str | None]:
    """Return (api_key, env_name) for the first configured Fugu key."""
    load_env_file()
    for name in FUGU_API_KEY_ENV_CANDIDATES:
        value = os.getenv(name)
        if value:
            return value, name
    return None, None


def fugu_base_url_from_env(default: str = FUGU_DEFAULT_BASE_URL) -> str:
    """Return the configured OpenAI-compatible base URL."""
    load_env_file()
    return (
        os.getenv("FUGU_BASE_URL")
        or os.getenv("SAKANA_BASE_URL")
        or os.getenv("SAKAA_BASE_URL")
        or default
    ).rstrip("/")


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
