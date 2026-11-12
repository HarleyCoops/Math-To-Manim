"""Google Agent SDK (google-adk + google-genai) reasoning chain for Gemini 4 Argon."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("math-to-manim")
except PackageNotFoundError:  # running from a checkout that is not installed
    __version__ = "0.0.0"
