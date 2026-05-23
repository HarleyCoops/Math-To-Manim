"""Codex/OpenAI Agents SDK spine for Math-To-Manim."""

from __future__ import annotations

__all__ = ["__version__", "load_environment"]

__version__ = "0.1.0"


def load_environment(*args, **kwargs):
    """Load the optional Prime Intellect repair environment when installed."""

    try:
        from m2m2_visual_repair import load_environment as _load_environment
    except ImportError as exc:  # pragma: no cover - exercised only by external Verifiers loader
        raise RuntimeError(
            "The Prime Intellect environment is not installed. "
            "Install it with `uv pip install -e environments/math_to_manim`."
        ) from exc
    return _load_environment(*args, **kwargs)
