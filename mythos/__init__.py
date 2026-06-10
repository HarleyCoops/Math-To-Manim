"""Mythos layer: Claude Mythos-driven cinematic Manim generation.

Additive layer on top of the Math-To-Manim typed pipeline. Nothing here
modifies the legacy codex flow; it provides:

- ``mythos.cinematography``: the visual grammar (zooms, headlines, term tours)
- ``mythos.harness``: a 6-stage reasoning chain driven through the Claude CLI
"""

__version__ = "0.1.0"
