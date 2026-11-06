"""Environment-driven settings and API-key handling for the Argon silo.

Nothing here imports the Google SDKs, so offline runs, the run ledger and the
operator script work without ``google-adk`` installed.
"""

from __future__ import annotations

import os

# Environment variables consulted, in order, for the Gemini API key.
API_KEY_ENV_VARS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ARGON_API_KEY")

# Removed from the environment of any subprocess that executes model-written
# code (the Manim render). Our own key variables plus other providers' keys
# that may be set on a developer machine.
SCRUBBED_ENV_VARS = API_KEY_ENV_VARS + ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")

MISSING_KEY_MESSAGE = "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set"


def default_model() -> str:
    return os.getenv("ARGON_MODEL", "gemini-2.5-pro")


def default_reasoning_effort() -> str:
    return os.getenv("ARGON_REASONING_EFFORT", "high")


def resolve_api_key(explicit: str | None = None) -> tuple[str, str]:
    """Return (key, source) where source is "explicit" or the env var name."""
    if explicit is not None and explicit.strip():
        return explicit.strip(), "explicit"
    for name in API_KEY_ENV_VARS:
        val = os.getenv(name, "").strip()
        if val:
            return val, name
    return "", API_KEY_ENV_VARS[0]


def api_key_status(key: str | None = None) -> tuple[bool, str]:
    """Check whether a Gemini/Google API key is configured without returning its value."""
    value, source = resolve_api_key(key)
    if not value:
        return False, MISSING_KEY_MESSAGE
    if len(value) < 8:
        return False, f"{source} is present but too short to be valid"
    return True, f"{source} is set"


def redact_secret(text: str, secret: str | None) -> str:
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")
