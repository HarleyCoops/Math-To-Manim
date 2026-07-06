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
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from mythos.charter import load_env_file, resolve_command

DEFAULT_MODEL = "claude-fable-5"
DEFAULT_COMMAND = "claude"
DEFAULT_TIMEOUT = 900.0

FUGU_DEFAULT_BASE_URL = "https://api.sakana.ai/v1"
FUGU_API_COMMANDS = {"fugu-api", "sakana-api", "sakaa-api"}
FUGU_API_KEY_ENV_CANDIDATES = ("FUGU_API_KEY", "SAKANA_API_KEY", "SAKAA_API_KEY")


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
        cmd = [resolved, "exec", "--model", model, "-"]
        payload = f"{system_extra}\n\n{prompt}" if system_extra else prompt
        completed = subprocess.run(
            cmd, input=payload, text=True, capture_output=True,
            timeout=timeout, check=False,
        )
    else:
        cmd = [resolved, "-p", "--output-format", "text", "--model", model]
        if system_extra:
            cmd += ["--append-system-prompt", system_extra]
        completed = subprocess.run(
            cmd, input=prompt, text=True, capture_output=True,
            timeout=timeout, check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Mythos model command failed (exit {completed.returncode})\n"
            f"command: {cmd[0]}\n"
            f"stderr:\n{completed.stderr[-4000:]}"
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
    """Call an OpenAI-compatible chat completion endpoint."""
    api_key, env_name = fugu_api_key_from_env()
    if not api_key:
        names = ", ".join(FUGU_API_KEY_ENV_CANDIDATES)
        raise RuntimeError(f"No Fugu API key found. Set one of: {names}.")

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
            f"endpoint: {url}\nmodel: {model}\napi_key_env: {env_name}\n"
            f"status: {exc.code}\nbody:\n{detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Fugu API call failed before a response was received\n"
            f"endpoint: {url}\nmodel: {model}\napi_key_env: {env_name}\n"
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
