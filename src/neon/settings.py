"""Environment settings and secret-handling helpers for the Neon silo."""

from __future__ import annotations

import os
import shutil

from neon import DEFAULT_MODEL

API_KEY_ENV_VARS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "NEON_API_KEY")
SCRUBBED_ENV_VARS = API_KEY_ENV_VARS + ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def default_model() -> str:
    return os.getenv("NEON_MODEL", DEFAULT_MODEL)


def default_backend() -> str:
    return os.getenv("NEON_BACKEND", "auto")


def default_thinking_budget() -> int:
    raw = os.getenv("NEON_THINKING_BUDGET", "8192")
    try:
        return max(0, int(raw))
    except ValueError:
        return 8192


def resolve_api_key(explicit: str | None = None) -> tuple[str, str]:
    """Return ``(key, source)`` without logging or exposing the secret."""
    if explicit and explicit.strip():
        return explicit.strip(), "explicit"
    for name in API_KEY_ENV_VARS:
        val = os.getenv(name, "").strip()
        if val:
            return val, name
    return "", API_KEY_ENV_VARS[0]


def has_gemini_api_cli() -> bool:
    return shutil.which("gemini-api") is not None


def scrubbed_env() -> dict[str, str]:
    """Environment copy with all provider API keys removed for Manim execution."""
    env = dict(os.environ)
    for var in SCRUBBED_ENV_VARS:
        env.pop(var, None)
    return env


def redact_secret(text: str, secret: str | None) -> str:
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")
