"""OpenAI-compatible Sakana Fugu API helpers.

Secrets are read from environment variables only and are never stamped into
artifacts or error messages.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from math_to_manim.config import load_env_file

FUGU_DEFAULT_BASE_URL = "https://api.sakana.ai/v1"
FUGU_API_KEY_ENV_CANDIDATES = (
    "FUGU_API_KEY",
    "SAKANA_API_KEY",
    "SAKAA_API_KEY",
)


def fugu_api_key_from_env() -> tuple[str | None, str | None]:
    """Return (api_key, env_name) for the first configured Fugu key."""

    load_env_file()
    for name in FUGU_API_KEY_ENV_CANDIDATES:
        value = os.getenv(name)
        if value:
            return value, name
    return None, None


def fugu_base_url_from_env(default: str = FUGU_DEFAULT_BASE_URL) -> str:
    """Return the configured OpenAI-compatible Fugu base URL."""

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
    """Call a Sakana Fugu/OpenAI-compatible chat completion endpoint."""

    api_key, env_name = fugu_api_key_from_env()
    if not api_key:
        names = ", ".join(FUGU_API_KEY_ENV_CANDIDATES)
        raise RuntimeError(f"No Fugu API key found. Set one of: {names}.")

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
    }

    url = _chat_completions_url(base_url)
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
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
            f"endpoint: {url}\n"
            f"model: {model}\n"
            f"api_key_env: {env_name}\n"
            f"status: {exc.code}\n"
            f"body:\n{detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Fugu API call failed before a response was received\n"
            f"endpoint: {url}\n"
            f"model: {model}\n"
            f"api_key_env: {env_name}\n"
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
        # Some OpenAI-compatible gateways return Responses-API-shaped output.
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
