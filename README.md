<div align="center">

<a href="https://www.star-history.com/#HarleyCoops/Math-To-Manim&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" width="100%" />
  </picture>
</a>

# Math to Manim

### Ask a question -> reverse reasoning -> Manim movie

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3b82f6)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE-f59e0b)](https://www.manim.community/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-111827)](https://openai.github.io/openai-agents-python/)
[![Hermes assisted](https://img.shields.io/badge/Hermes-agent%20assisted-8b5cf6)](#hermes-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

[Motion showcase](docs/showcase/README.md) · [Architecture](docs/ARCHITECTURE.md) · [Prime RL](docs/PRIME_INTELLECT_RL.md) · [Roadmap](docs/ROADMAP.md) · [Agent guide](AGENTS.md)

<br />

<p align="center">
  <img src="docs/showcase/assets/continuous-geometric-picture.gif" alt="GRPO semantic manifold: sibling completions become a geometric policy update across the full scene" width="48%" />
  <img src="docs/showcase/assets/qed-minkowski-epic-3d.gif" alt="QED and Minkowski spacetime: light cones, electromagnetic waves, gauge symmetry, and renormalization flow on an off-white 3D stage" width="48%" />
</p>

<br />

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/circle-area-3d-unwrapped.gif" alt="3D circle area derivation from annuli to unwrapped triangle" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/cosmic-gravity-3d.gif" alt="Cosmic gravity 3D animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/continuous-geometric-picture.gif" alt="Full GRPO semantic manifold animation" width="24%" /></a>
</p>

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/derivative-visualization.gif" alt="Derivative visualization animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/prolip-scene.gif" alt="ProLIP animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/lorenz-attractor.gif" alt="Lorenz attractor animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/hopf-fibration.gif" alt="Hopf fibration animation" width="24%" /></a>
</p>

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/fourier-epicycles.gif" alt="Fourier epicycles animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/teaching-hopf.gif" alt="Teaching Hopf animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/brownian-finance.gif" alt="Brownian finance animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/radius-of-convergence.gif" alt="Radius of convergence animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/whiskering-exchange.gif" alt="Whiskering exchange animation" width="24%" /></a>
</p>

**Math-To-Manim turns short prompts into reverse-reasoned lesson plans, typed pipeline artifacts, generated Manim code, and reusable visual explanations.**

[**Browse the local GIF gallery →**](docs/showcase/README.md)

<br />

<img src="docs/assets/reverse-reasoning-pipeline.svg" alt="Reverse reasoning pipeline diagram showing the actual Math-To-Manim stage agents, artifacts, validation gate, render path, review, package, and manifest" width="100%" />

<br />

<em>Code-grounded workflow: every run stays inspectable from prompt to artifacts to render.</em>

</div>

---

## What this is

**Math to Manim** is for the moment when a learner asks, “Can you show me why?” A teacher, tutor, parent, or guardian can type a question and get back a visual explanation plan: the concept, the missing prerequisites, the order of ideas, the screen beats, the generated Manim code, and optionally the rendered video.

The input can be short, but the product is the explanation: what the learner needs to understand, what should appear first, where the aha moment lives, and which visual metaphor makes the idea feel inevitable.

Math-To-Manim proves that calculus, topology, chaos, spacetime, stochastic finance, and ML concepts can become useful mathematical motion when agents plan the explanation before they write code.

This repo turns that idea into a durable agent pipeline:

- a prerequisite-story pipeline inspired by the original reverse knowledge tree;
- typed Pydantic artifacts between every stage;
- OpenAI Agents SDK-compatible adapters for planning and generation;
- optional Codex CLI-backed codegen for subscription-authenticated iteration;
- a reproducible `runs/<run_id>/` bundle for every generation;
- static validation, render metadata, review artifacts, and manifests that are easy to inspect in CI or by another agent.

The design principle is simple: **story before symbols, geometry before algebra, artifacts before side effects.**

---

## Reverse reasoning pipeline

A normal text-to-code demo jumps from request to Python. Math-To-Manim takes the long way on purpose: it reasons backward from the final concept to the prerequisites, then walks forward through a teachable visual sequence.

The code path is explicit in [`math_to_manim/pipeline/runner.py`](math_to_manim/pipeline/runner.py). `AnimationPipeline.generate()` runs a fixed stage chain: `IntentAgent`, `PrerequisiteGraphAgent`, `CurriculumAgent`, `MathAgent`, `StoryboardAgent`, `SceneSpecAgent`, `ManimCodeAgent`, `StaticReviewAgent`, `RenderAgent`, `VideoReviewAgent`, and `PublisherAgent`.

| Stage | Why it exists | Artifact |
| --- | --- | --- |
| Intent | Clarify what the learner is really asking. | `intent.json` |
| Reverse prerequisites | Build the knowledge graph needed before the target idea. | `knowledge_graph.json` |
| Curriculum | Turn the graph into a teachable order. | `curriculum.json` |
| Math packet | Select definitions, equations, assumptions, and examples. | `math_packet.json` |
| Storyboard | Decide the screen beats before code exists. | `storyboard.json` |
| Scene spec | Compile the visual plan into Manim objects, animations, timing, and camera notes. | `scene_spec.json` |
| Code, validation, render, review | Generate runnable Manim, gate it with static checks, render when allowed, and package the evidence. | `generated_scene.py`, reports, manifest |

<p align="center">
  <img src="docs/assets/render-repair-loop.svg" alt="Render validation and bounded repair loop diagram showing static review, render skip, Manim subprocess, repair from frozen scene spec, video review, and publisher package" width="100%" />
</p>

That gives every run a memory: JSON contracts, generated code, render results, review notes, and a manifest. The output is not just a video; it is an inspectable path from **question** to **understanding** to **animation**.

For current editable-video status and the planned prompt/spec/code edit loop, see the [roadmap](docs/ROADMAP.md).

---

## Prime Intellect RL repair loop

Math-To-Manim is also becoming a Prime Intellect reinforcement-learning environment. The first RL target is not "make the whole video in one shot." It is the repair move that matters most when generated animation code fails: take the typed scene plan, the broken `generated_scene.py`, and validation/render evidence, then return corrected Manim Python that is safe, sparse, and more likely to render.

<p align="center">
  <img src="docs/assets/prime-intellect/primeintellect-logo.svg" alt="Prime Intellect logo" width="220" />
</p>

<p align="center">
  <img src="docs/assets/prime-intellect/m2m2-prime-rl-loop.svg" alt="Diagram of the Math-To-Manim Prime Intellect RL repair loop from generated Manim code through static reward checks back to corrected renderable Manim Python" width="100%" />
</p>

<table>
<tr>
<td width="33%"><img src="docs/assets/prime-intellect/primeintellect-lab.png" alt="Prime Intellect lab field visual, used here to represent the environment task space" /></td>
<td width="33%"><img src="docs/assets/prime-intellect/primeintellect-reward-hacking-cover.png" alt="Prime Intellect reward hacking visual, used here to represent reward design pressure" /></td>
<td width="33%"><img src="docs/assets/prime-intellect/primeintellect-compute-bg.png" alt="Prime Intellect compute corridor visual, used here to represent hosted training and inference" /></td>
</tr>
<tr>
<td><b>Run bundle as environment</b></td>
<td><b>Reward function as critic</b></td>
<td><b>Policy update as repair engine</b></td>
</tr>
</table>

The current hub environment is `harleycooper/math-to-manim`. A repair task carries the original prompt, typed `scene_spec`, generated Manim Python, static-validation report, and render/recovery evidence when available. The model must return one strict `GeneratedCode` JSON block. The Verifiers reward checks whether the proposed code parses, defines the expected Manim scene, avoids unsafe imports and calls, preserves expected math terms, and reduces obvious text/layout crowding hazards.

```text
generated_scene.py + scene_spec + validation/render evidence
  -> Prime Intellect Verifiers environment
  -> model proposes corrected GeneratedCode JSON
  -> static reward checks parseability, scene shape, safety, terms, layout
  -> hosted RL updates the repair policy
  -> corrected, renderable Manim Python flows back into M2M2 recovery
```

That keeps the fast RL loop text-and-AST based while the slower Manim renderer remains the audit gate. The intended result is a model that learns the house style of this repo: cinematic but readable scenes, sparse formulas, staged captions, safe Manim code, and scripts that are much more likely to render on the first recovery attempt.

Current hosted-training status: the environment action passes on Prime, the hub package is published as `harleycooper/math-to-manim@0.1.1`, a 1-step smoke completed, and a 25-step W&B-enabled pilot has been launched on `Qwen/Qwen3.5-35B-A3B`.

See the full integration notes in [`docs/PRIME_INTELLECT_RL.md`](docs/PRIME_INTELLECT_RL.md).

---

## Clone and run

### 1. Clone

Windows PowerShell:

```powershell
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest
```

macOS / Linux / WSL:

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest
```

### 2. Run a no-API smoke test

This proves the CLI, artifact contracts, and validators are wired before you spend model or render time:

```bash
math-to-manim generate "Explain why derivatives are slopes" --deterministic --no-render
```

Equivalent module form:

```bash
python -m math_to_manim.cli generate "Explain why derivatives are slopes" --deterministic --no-render
```

### 3. Generate with model calls

Set an OpenAI key and choose a model if desired:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4.1"
math-to-manim generate "Explain Fourier epicycles as rotating vectors" --no-render
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_MODEL = "gpt-4.1"
math-to-manim generate "Explain Fourier epicycles as rotating vectors" --no-render
```

### 4. Install render extras when you want MP4 output

Python render dependency:

```bash
python -m pip install -e ".[dev,render]"
```

System render dependencies are also needed for real Manim output, especially FFmpeg and LaTeX for `MathTex`. On Debian/Ubuntu/WSL:

```bash
./scripts/bootstrap-render.sh
```

The package list lives in [`requirements-system.txt`](requirements-system.txt).

---

## Codex CLI codegen path

Math-To-Manim can keep the typed planning pipeline while sending the Manim codegen and repair loop through a locally authenticated Codex CLI session.

Check Codex first:

```bash
codex --version
codex exec "Say ready from inside this repo"
```

Then route codegen through Codex:

```bash
math-to-manim generate "Explain derivatives as slopes with a cinematic tangent-line reveal" \
  --codegen-provider codex-cli \
  --codex-full-auto \
  --style cinematic \
  --quality l
```

Earlier planning stages remain on the typed adapters; only the generated-code and repair stages move first. That makes the migration incremental instead of all-or-nothing.

---

## What lands on disk

A generation writes a self-contained run bundle:

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
  recovery_manifest.json  # after recover-render
  draft_review/
    draft_review.md
    contact_sheet.png
    frames/
  animation_package.json
  manifest.json
```

After editing `generated_scene.py` inside a run bundle, rerun the recovery path:

```bash
math-to-manim recover-render runs/<run_id> --quality l
```

That command refreshes validation, render, review, draft-review assets, and
`recovery_manifest.json` without regenerating upstream planning artifacts.

Package layout:

```text
math_to_manim/
  agents/      # stage adapters
  schemas/     # versioned artifact contracts
  tools/       # graph, validation, rendering, video, artifact helpers
  pipeline/    # orchestration, tracing, repair loop
  rendering/   # Manim and FFmpeg wrappers
  review/      # static and visual review scoring
```

---

## Hermes Agent

Hermes is the contributor/operator agent around this repository. It is not imported by Math-To-Manim and is not a runtime dependency; it uses the repo the way a developer would: read files, search code, patch docs and code, run terminal checks, inspect generated artifacts, review frames or GIFs, track todos, delegate larger work, and preserve stable context through skills.

That makes Hermes useful for maintaining the reverse-reasoning pipeline without becoming part of it. A Hermes session can inspect `AGENTS.md`, `pyproject.toml`, schemas, tests, and `runs/<run_id>/` bundles; run `pytest`, CLI smoke commands, Manim, FFmpeg, and git checks; then verify that docs, code, and showcase media still match the artifact contracts.

Repo-local Hermes skills live under [`hermes/skills/`](hermes/skills/). The old Claude `./skill` path is historical; current contributor guidance is in [`AGENTS.md`](AGENTS.md), with launch notes in [`docs/HERMES_LEARNS_MANIM.md`](docs/HERMES_LEARNS_MANIM.md).

---

## Motion showcase

Sixteen curated GIFs are tracked under [`docs/showcase/assets/`](docs/showcase/assets/) as the **art direction target** for Math-To-Manim's visual explanations.

<table>
<tr>
<td width="33%"><a href="docs/showcase/README.md"><img src="docs/showcase/assets/rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron" /></a></td>
<td width="33%"><a href="docs/showcase/README.md"><img src="docs/showcase/assets/hopf-fibration.gif" alt="Hopf fibration" /></a></td>
<td width="33%"><a href="docs/showcase/README.md"><img src="docs/showcase/assets/lorenz-attractor.gif" alt="Lorenz attractor" /></a></td>
</tr>
<tr>
<td><b>Geometry as spectacle</b></td>
<td><b>Topology as choreography</b></td>
<td><b>Chaos as intuition</b></td>
</tr>
</table>

See the full gallery with descriptions: **[`docs/showcase/README.md`](docs/showcase/README.md)**.

### Make a README-sized GIF from a render

```bash
MP4="media/videos/your_scene/480p15/YourScene.mp4"

ffmpeg -y -ss 95 -t 24 -i "$MP4" \
  -vf "fps=12,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  docs/showcase/assets/your-clip.gif
```

Adjust `-ss` and `-t` to capture the teaching beat you want.

---

## License

MIT.
