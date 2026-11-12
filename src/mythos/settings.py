"""Mythos configuration: every environment variable the silo reads.

Values come from the process environment or from a local (gitignored)
``.env`` in the current directory, which is loaded once when this module is
imported (existing environment variables win). Nothing else in the silo
calls ``os.getenv``.

    M2M_MODEL                 baseline model id            default claude-fable-5-2
    M2M_COMMAND               backend: claude | codex | fugu-api | <cli path>
                                                           default claude
    M2M_TIMEOUT               seconds per model call       default 900
    M2M_MODEL_FALLBACKS       comma-separated Anthropic models tried, in order,
                              when the primary fails on the Claude CLI
                              (''= disabled)                default claude-opus-4-8,claude-sonnet-5
    M2M_RENDER_TIMEOUT        render wall-clock seconds    default 1800
    M2M_RUNS_DIR              parent of the run ledger     default <checkout>/runs, or ./runs for a wheel install  (runs land in <dir>/mythos)
    M2M_MANIM                 manim launcher override      default: active interpreter's manim
    M2M_PREREQ_CACHE_TTL_DAYS prerequisite cache TTL       default 30
    M2M_LATEX_DEEP_CHECK      1/true/yes/on: also compile MathTex fragments with lualatex
    FUGU_API_KEY | SAKANA_API_KEY | SAKAA_API_KEY       key for the fugu-api backend
    FUGU_BASE_URL | SAKANA_BASE_URL | SAKAA_BASE_URL    OpenAI-compatible endpoint
                                                           default https://api.sakana.ai/v1

The archived pipeline's ``M2M2_*`` variables are deliberately not read: they
configured a different engine, and silently retargeting this one would be a
footgun. ``doctor`` points that out when it sees ``M2M2_MYTHOS_MODEL``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ENV_FILE = Path(".env")


def load_env_file(path: Path | None = None) -> None:
    """Load simple KEY=VALUE lines from a .env file into os.environ (no override)."""
    env_path = path or ENV_FILE
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

DEFAULT_MODEL = os.getenv("M2M_MODEL") or "claude-fable-5-2"
DEFAULT_COMMAND = os.getenv("M2M_COMMAND", "claude")
#: Where the defaults above came from, for ``doctor``'s configuration report.
SETTING_SOURCES = {
    "model": "M2M_MODEL" if os.getenv("M2M_MODEL") else "default",
    "command": "M2M_COMMAND" if os.getenv("M2M_COMMAND") else "default",
}
DEFAULT_TIMEOUT = float(os.getenv("M2M_TIMEOUT", "900"))
DEFAULT_RENDER_TIMEOUT = float(os.getenv("M2M_RENDER_TIMEOUT", "1800"))
MANIM_COMMAND_OVERRIDE = os.getenv("M2M_MANIM") or None

#: Anthropic models tried, in order, when the primary fails for a
#: model-specific reason (overload, not-found, 5xx). All of them run through
#: the same Claude CLI subscription login — no API key involved. Haiku is
#: deliberately absent: it is below the quality bar for reasoning stages.
_FALLBACKS_DEFAULT = "claude-opus-4-8,claude-sonnet-5"

FUGU_DEFAULT_BASE_URL = "https://api.sakana.ai/v1"
FUGU_API_KEY_ENV_CANDIDATES = ("FUGU_API_KEY", "SAKANA_API_KEY", "SAKAA_API_KEY")
_FUGU_BASE_URL_ENV_CANDIDATES = ("FUGU_BASE_URL", "SAKANA_BASE_URL", "SAKAA_BASE_URL")

DEFAULT_PREREQ_CACHE_TTL_DAYS = 30


def model_fallbacks_from_env() -> tuple[str, ...]:
    """Fallback model ids from M2M_MODEL_FALLBACKS; empty string disables."""
    raw = os.getenv("M2M_MODEL_FALLBACKS")
    if raw is None:
        raw = _FALLBACKS_DEFAULT
    return tuple(m.strip() for m in raw.split(",") if m.strip())


def fugu_api_key_from_env() -> tuple[str | None, str | None]:
    """Return (api_key, env_name) for the first configured Fugu key."""
    for name in FUGU_API_KEY_ENV_CANDIDATES:
        value = os.getenv(name)
        if value:
            return value, name
    return None, None


def fugu_base_url_from_env() -> str:
    """Return the configured OpenAI-compatible base URL, without a trailing slash."""
    for name in _FUGU_BASE_URL_ENV_CANDIDATES:
        value = os.getenv(name)
        if value:
            return value.rstrip("/")
    return FUGU_DEFAULT_BASE_URL


def ignored_legacy_vars() -> tuple[str, ...]:
    """Archived-pipeline variables present in the environment (never read)."""
    return tuple(name for name in ("M2M2_MYTHOS_MODEL",) if os.getenv(name))


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/mythos``; else ``runs/mythos`` in the source checkout this
    package runs from; else ``./runs/mythos`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "mythos"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "mythos"


@dataclass(frozen=True)
class PipelineSettings:
    """Operator-tunable static-check and cache settings, read at call time."""

    prereq_cache_ttl_days: int = DEFAULT_PREREQ_CACHE_TTL_DAYS
    latex_deep_check: bool = False

    @classmethod
    def from_env(cls) -> "PipelineSettings":
        raw_ttl = os.getenv("M2M_PREREQ_CACHE_TTL_DAYS", str(DEFAULT_PREREQ_CACHE_TTL_DAYS))
        try:
            ttl = max(1, int(raw_ttl))
        except ValueError:
            ttl = DEFAULT_PREREQ_CACHE_TTL_DAYS
        deep = os.getenv("M2M_LATEX_DEEP_CHECK", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return cls(prereq_cache_ttl_days=ttl, latex_deep_check=deep)
