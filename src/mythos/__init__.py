"""Math-To-Manim: ask a question -> get a freakin' movie.

The Mythos engine turns one sentence into a cinematic Manim film through a
6-agent reasoning chain driven by Claude Fable 5.2:

- ``mythos.stages``: the stage table (charters, artifacts, reply checks)
- ``mythos.harness``: the chain runner (intent -> ... -> scene-composer ->
  codegen -> verify -> render -> repair)
- ``mythos.layout``: the run-bundle layout and its atomic writer
- ``mythos.cinematography``: the visual grammar (headlines, term zooms,
  pull-backs, glows — the Mythos house style)
- ``mythos.charter``: the Cinematic Charter and model-output parsing
- ``mythos.backends``: model backends (Claude CLI, Codex CLI, OpenAI-compatible)
- ``mythos.settings``: every environment variable the silo reads
- ``mythos.service``: job orchestration shared by every front door
- ``mythos.api``: the REST API (FastAPI)
- ``mythos.lifecycle``: job and run states, and the legal moves between them
- ``mythos.mcp_server``: the MCP server (``serve-mcp``) over the Mythos service
- ``mythos.cli``: the ``math-to-manim-mythos`` command
"""

__version__ = "1.1.0"
