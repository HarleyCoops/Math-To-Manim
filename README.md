<div align="center">

# Math to Manim

### Hermes learns Manim: prompt → prerequisite story → typed artifacts → cinematic mathematical motion

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3b82f6)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE-f59e0b)](https://www.manim.community/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-111827)](https://openai.github.io/openai-agents-python/)
[![Hermes assisted](https://img.shields.io/badge/Hermes-learns%20Manim-8b5cf6)](#hermes-learns-manim)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

[Motion showcase](docs/showcase/README.md) · [Architecture](docs/ARCHITECTURE.md) · [Launch plan](docs/HERMES_LEARNS_MANIM.md) · [Agent guide](AGENTS.md) · [Legacy Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim)

<br />

<img src="Hero.jpg" alt="Hermes learns Manim hero: mathematical motion, equations, and agentic animation" width="760" />

<br />

<a href="docs/showcase/README.md">
  <img src="docs/showcase/assets/derivatives-as-slopes.gif" alt="Derivatives as slopes: a secant line becomes a tangent" width="760" />
</a>

*Classic calculus beat from the original pipeline: secant tension resolving into a tangent.*

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/cosmic-gravity-3d.gif" alt="Cosmic gravity 3D animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/grpo-explanation.gif" alt="GRPO explanation animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/derivative-visualization.gif" alt="Derivative visualization animation" width="24%" /></a>
</p>

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/prolip-scene.gif" alt="ProLIP animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/lorenz-attractor.gif" alt="Lorenz attractor animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/hopf-fibration.gif" alt="Hopf fibration animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/fourier-epicycles.gif" alt="Fourier epicycles animation" width="24%" /></a>
</p>

<p align="center">
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/teaching-hopf.gif" alt="Teaching Hopf animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/brownian-finance.gif" alt="Brownian finance animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/radius-of-convergence.gif" alt="Radius of convergence animation" width="24%" /></a>
  <a href="docs/showcase/README.md"><img src="docs/showcase/assets/whiskering-exchange.gif" alt="Whiskering exchange animation" width="24%" /></a>
</p>

**The rewrite keeps the visual ambition of the original project, but gives the pipeline contracts, traces, and repeatable run folders.**

[**Browse the local GIF gallery →**](docs/showcase/README.md)

</div>

---

## Start here: Hermes + M2M2 setup

This repo is meant to be operated by **Hermes Agent** while M2M2 provides the Manim animation pipeline. The split is intentional:

- **Hermes** is the repo operator: skills, file/search/patch tools, terminal checks, vision review, todos, delegation, memory, and GitHub verification.
- **M2M2** is the Python package: typed curriculum/storyboard artifacts, Manim code generation, validation, render/review bundles, and showcase assets.

Fastest path for a new checkout:

```bash
git clone https://github.com/HarleyCoops/M2M2.git
cd M2M2

# 1. Install and verify the Python package.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest

# 2. Install and verify Hermes.
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup
hermes doctor
hermes tools list --summary
hermes skills list

# 3. Start Hermes with the repo skills that matter here.
hermes --skills agents-md,codebase-inspection,manim-video,systematic-debugging
```

Once Hermes is inside this repo, the expected workflow is concrete: read `AGENTS.md`, inspect `pyproject.toml` and CLI help, run deterministic smoke generations, open the `runs/<run_id>/` artifact bundle, visually inspect frames/GIFs when media changes, then commit/push only verified docs/code/assets.

See [How Hermes uses this repo](#hermes-learns-manim) for the detailed tool map.

---

## What this is

**Math to Manim** turns one-line prompts into cinematic Manim animations with an agentic teaching pipeline. It is not just “LLM writes a script.” The system first builds the lesson: what the viewer needs to understand, what should appear first, where the aha moment lives, and which visual metaphor makes the math feel inevitable.

The original [Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim) proved that this works: calculus, topology, chaos, spacetime, stochastic finance, and ML concepts can become publishable mathematical motion when agents plan the explanation before they write code.

This repo is the rewrite of that idea around a cleaner spine:

- a prerequisite-story pipeline inspired by the original reverse knowledge tree;
- typed Pydantic artifacts between every stage;
- OpenAI Agents SDK-compatible adapters for planning and generation;
- optional Codex CLI-backed codegen for subscription-authenticated iteration;
- a reproducible `runs/<run_id>/` bundle for every generation;
- static validation, render metadata, review artifacts, and manifests that are easy to inspect in CI, by Hermes, or by another agent.

The design principle is simple: **story before symbols, geometry before algebra, artifacts before side effects.**

---

## What makes this different

A normal text-to-code demo jumps from prompt straight to Python. Math to Manim takes the long way on purpose:

```text
short prompt
  → intent: what should this teach?
  → prerequisite graph: what must be understood first?
  → curriculum: what order makes the idea click?
  → math packet: which definitions/equations matter?
  → storyboard: what should move on screen?
  → scene spec: what Manim objects and beats are needed?
  → generated_scene.py
  → static validation / repair
  → Manim render
  → review artifacts / showcase GIF
```

That gives every run a memory: JSON contracts, generated code, render results, review notes, and a manifest. The output is not just a video; it is an inspectable path from **understanding** to **animation**.

---

## Clone and run

### 1. Clone

Windows PowerShell:

```powershell
git clone https://github.com/HarleyCoops/M2M2.git
cd M2M2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest
```

macOS / Linux / WSL:

```bash
git clone https://github.com/HarleyCoops/M2M2.git
cd M2M2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest
```

### 2. Run a no-API smoke test

This proves the CLI, artifact contracts, and validators are wired before you spend model or render time:

```bash
m2m2 generate "Explain why derivatives are slopes" --deterministic --no-render
```

Equivalent module form:

```bash
python -m math_to_manim.cli generate "Explain why derivatives are slopes" --deterministic --no-render
```

### 3. Generate with model calls

Set an OpenAI key and choose a model if desired:

```bash
export OPENAI_API_KEY="sk-..."
export M2M2_MODEL="gpt-4.1"
m2m2 generate "Explain Fourier epicycles as rotating vectors" --no-render
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:M2M2_MODEL = "gpt-4.1"
m2m2 generate "Explain Fourier epicycles as rotating vectors" --no-render
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

M2M2 can keep the typed planning pipeline while sending the Manim codegen and repair loop through a locally authenticated Codex CLI session.

Check Codex first:

```bash
codex --version
codex exec "Say ready from inside this repo"
```

Then route codegen through Codex:

```bash
m2m2 generate "Explain derivatives as slopes with a cinematic tangent-line reveal" \
  --codegen-provider codex-cli \
  --codex-full-auto \
  --style cinematic \
  --quality l
```

Environment equivalents:

```bash
export M2M2_CODEGEN_PROVIDER=codex-cli
export M2M2_CODEX_FULL_AUTO=1
export M2M2_CODEX_COMMAND=codex
export M2M2_CODEX_TIMEOUT_SECONDS=900
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
  draft_review/
    draft_review.md
    contact_sheet.png
    frames/
  animation_package.json
  manifest.json
```

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

## Motion showcase

Thirteen curated GIFs from the legacy repo's [`public/readme-showcase/`](https://github.com/HarleyCoops/Math-To-Manim/tree/main/public/readme-showcase) directory are copied into this repo under [`docs/showcase/assets/`](docs/showcase/assets/). They are not outputs from the rewrite yet; they are the **art direction target**.

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

## Hermes learns Manim

This repo is also a live **Hermes Agent workspace**. Hermes is not imported by M2M2 and is not a runtime dependency; it is the contributor/operator layer that uses the repo the way a developer would: read files, search code, patch docs and code, run terminal checks, inspect generated artifacts, review media with vision, delegate larger work, track todos, and preserve useful context through skills and memory.

| Hermes-native capability | How it is used in M2M2 |
| --- | --- |
| File + search tools | Read `README.md`, `AGENTS.md`, `pyproject.toml`, schemas, tests, docs, and generated run artifacts before making claims. |
| Patch tool | Make surgical edits to docs, schemas, tests, pipeline code, and launch copy while preserving repo style and typed contracts. |
| Terminal tool | Run `pytest`, CLI help, deterministic smoke generations, Codex checks, Manim, FFmpeg, link validators, git, and GitHub verification. |
| Vision/media review | Inspect screenshots, contact sheets, frames, and GIFs so showcase media is judged visually, not trusted because filenames exist. |
| Delegation + todos | Split larger work across focused agents, track acceptance criteria, and keep implementation/review/checklist state explicit. |
| Session search + memory | Recover prior repo decisions and preserve stable conventions without storing secrets or temporary run noise. |
| Skills | Load procedures such as `agents-md`, `codebase-inspection`, `manim-video`, `systematic-debugging`, `writing-plans`, `test-driven-development`, and `subagent-driven-development`. |

The M2M2 side gives Hermes concrete things to operate: the `m2m2` / `math-to-manim` CLI, deterministic helpers in `math_to_manim/tools/`, typed stages in `math_to_manim/agents/` and `math_to_manim/pipeline/`, schemas in `math_to_manim/schemas/`, render/review helpers, and reproducible `runs/<run_id>/` bundles containing JSON contracts, `generated_scene.py`, validation/render/review reports, contact sheets, frames, and `manifest.json`.

Start a repo-aware Hermes session:

```bash
# Install/configure Hermes if needed.
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup
hermes doctor

# From the repo root, preload skills for this repo.
hermes --skills agents-md,manim-video,codebase-inspection,systematic-debugging
```

See [`AGENTS.md`](AGENTS.md) for the full operating contract and [`docs/HERMES_LEARNS_MANIM.md`](docs/HERMES_LEARNS_MANIM.md) for the launch/thread plan and new animation slate.

---

## Relationship to the classic repo

Use [HarleyCoops/Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim) for historical Claude / Gemini / Kimi experiments, examples, and the original orchestration experiments. Use **M2M2** for the refactor focused on typed artifacts, tracing, staged provider migration, and repeatable agent workflows.

---

## License

MIT. Showcase GIFs originate from the upstream Math-To-Manim project and are duplicated locally here for documentation and art-direction continuity.
