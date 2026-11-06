"""Math-To-Manim: ask a question -> get a freakin' movie.

The Mythos engine turns one sentence into a cinematic Manim film through a
6-agent reasoning chain driven by Claude Fable 5:

- ``mythos.harness``: the chain runner (intent -> ... -> scene-composer ->
  codegen -> verify -> render -> repair)
- ``mythos.cinematography``: the visual grammar (headlines, term zooms,
  pull-backs, glows — the Mythos house style)
- ``mythos.charter``: the Cinematic Charter and shared parsing utilities
- ``mythos.backends``: model backends (Claude CLI, Codex CLI, OpenAI-compatible)
- ``mythos.service``: job orchestration shared by every front door
- ``mythos.api``: the REST API (FastAPI)
- ``mythos.mcp_server``: the official MCP Python SDK 2.x server
- ``mythos.cli``: the ``math-to-manim`` command
"""

__version__ = "1.1.0"
