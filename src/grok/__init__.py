"""Grok-native Math-To-Manim silo.

This package is independent of every other silo under ``src/``. It talks to
the xAI Responses API, reads charters from ``src/grok/agents/``, and writes
inspectable runs under ``runs/grok/`` (see ``harness.default_runs_dir``).
"""

__version__ = "0.1.0"

from grok.harness import GrokHarness
from grok.models import RunManifest, RunRequest
from grok.service import GrokService

__all__ = ["GrokHarness", "GrokService", "RunManifest", "RunRequest", "__version__"]
