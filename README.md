# Math-To-Manim Codex Refactor

This repository is the clean Codex/OpenAI Agents SDK spine for Math-To-Manim.
It turns a compact prompt into typed pipeline artifacts, Manim code, render
metadata, review reports, and a reproducible run directory.

## Current Showcase

![Star-Chart Statistics generated Manim preview](docs/assets/star_chart_statistics.gif)

Generated from the Star-Chart Statistics prompt: data scatter becomes standard
deviation, Brownian paths, diffusion, Black-Scholes geometry, and an implied
volatility surface.

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
  draft_review/
    draft_review.md
    contact_sheet.png
    frames/
  animation_package.json
  manifest.json
```

Successful renders are treated as drafts. The review stage writes a second-pass
handoff in `draft_review/` with the rendered video path, contact sheet, sampled
frames, and an improvement checklist. Full visual scoring and automatic visual
repair are the next loop; the current review only proves the video rendered and
creates assets for an editor or vision model to inspect.

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

## Codex subscription-backed codegen

M2M2 can keep the typed planning pipeline while routing Manim code generation
and render repair through a locally authenticated Codex CLI session instead of
direct OpenAI API calls for those stages.

First make sure Codex is installed and logged in:

```bash
codex --version
codex exec "Say ready from inside this repo"
```

Then run M2M2 with the Codex codegen provider:

```bash
m2m2 generate "Explain derivatives as slopes with a cinematic tangent-line reveal" \
  --codegen-provider codex-cli \
  --codex-full-auto \
  --style cinematic \
  --quality l
```

Useful environment equivalents:

```bash
export M2M2_CODEGEN_PROVIDER=codex-cli
export M2M2_CODEX_FULL_AUTO=1
export M2M2_CODEX_COMMAND=codex
export M2M2_CODEX_TIMEOUT_SECONDS=900
```

The Codex path currently owns the `GeneratedCode` stage and render-repair loop.
Earlier planning artifacts still use the existing deterministic/OpenAI Agents SDK
adapters, so this is intentionally a staged migration rather than a risky full
provider swap.
