"""Codex CLI-native GPT-6 Astra Math-To-Manim silo."""

__version__ = "0.2.0"

from sol.harness import SolHarness
from sol.models import RunManifest, RunRequest

__all__ = ["RunManifest", "RunRequest", "SolHarness"]
