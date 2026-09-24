"""Grok-native Math-To-Manim silo.

This package is independent of ``mythos/`` and ``sol/``. It talks to the
xAI Responses API, reads charters from ``grok/agents/``, and writes
inspectable runs under ``runs/grok/``.
"""

from grok.harness import GrokHarness
from grok.models import RunManifest, RunRequest
from grok.service import GrokService

__all__ = ["GrokHarness", "GrokService", "RunManifest", "RunRequest"]
__version__ = "0.1.0"
