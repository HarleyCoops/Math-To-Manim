"""GLM-native Math-To-Manim silo.

This package is independent of ``src/mythos/``, ``src/sol/``, and ``src/grok/``. It talks
to the Z.ai Coding Plan chat/completions endpoint with glm-5.3-flash, keeps
thinking enabled on every call, reads charters from ``src/glm/agents/``, and
writes inspectable runs under ``runs/glm/`` (see ``harness.default_runs_dir``).
"""

__version__ = "0.1.0"

from glm.harness import GlmHarness
from glm.models import RunManifest, RunRequest
from glm.service import GlmService

__all__ = ["GlmHarness", "GlmService", "RunManifest", "RunRequest"]
