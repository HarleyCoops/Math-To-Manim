# M2M2 Refactor Docs

This directory captures the documentation owned by Worker C for the Codex/OpenAI
Agents SDK refactor.

## Documents

- [Architecture](ARCHITECTURE.md) describes the target agent pipeline and worker
  boundaries.
- [Roadmap](ROADMAP.md) answers current editable-workflow status and the planned
  prompt/spec/code iteration loop.
- [Showcase](showcase/README.md) presents local copies of legacy Math-To-Manim
  GIFs and the visual bar for generated scenes.
- [Artifact schemas](ARTIFACT_SCHEMAS.md) defines the JSON/YAML contracts passed
  between planning, generation, render, and eval stages.
- [Eval strategy](EVAL_STRATEGY.md) explains how prompt, artifact, code, and
  render checks fit together.
- [Migration notes](MIGRATION_NOTES.md) summarizes the move from public
  Math-To-Manim into this refactor.

## Current Fixtures

- `evals/prompt_suite.yaml` contains the initial prompt-level eval suite.
- `examples/reference/limit_tangent_reference.py` is a small Manim CE reference
  scene for renderer and style sanity checks.
