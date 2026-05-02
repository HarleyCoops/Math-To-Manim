# Math-To-Manim Codex Refactor

This repository is the clean Codex/OpenAI Agents SDK spine for Math-To-Manim.
It turns a compact prompt into typed pipeline artifacts, Manim code, render
metadata, review reports, and a reproducible run directory.

The first target command is:

```bash
math-to-manim generate "Explain why derivatives are slopes" --style cinematic --quality low
```

That command writes a run folder containing:

```text
runs/<run_id>/
  request.json
  intent.json
  knowledge_graph.json
  curriculum.json
  math_packet.json
  storyboard.json
  scene_spec.json
  generated_code.json
  generated_scene.py
  validation_report.json
  render_result.json
  review_report.json
  animation_package.json
  manifest.json
```

The package is deliberately structured around strict artifacts and local tools:

```text
math_to_manim/
  agents/      # OpenAI Agents SDK-compatible stage adapters
  schemas/     # versioned Pydantic artifact contracts
  tools/       # graph, validation, rendering, video, artifact, eval helpers
  pipeline/    # orchestration, tracing, repair loop
  rendering/   # Manim and FFmpeg wrappers
  review/      # static and visual review scoring
  app/         # optional API/UI entrypoints
```

The public `HarleyCoops/Math-To-Manim` repository remains the migration source
for examples and legacy Claude/Kimi/Gemini experiments. This repo starts by
building a new vertical slice beside that legacy architecture instead of copying
the older layering forward.

## Local Use

```bash
python -m pip install -e ".[dev]"
python -m math_to_manim.cli generate "Explain why derivatives are slopes" --no-render
python -m pytest
```

Rendering is optional during development. If Manim or FFmpeg are not installed,
the pipeline records a structured skip/failure report instead of crashing.
