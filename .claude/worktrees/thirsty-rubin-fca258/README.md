<p align="center">
  <img src="public/derivatives-as-slopes-hero.gif" alt="Math-To-Manim derivative animation hero" width="100%">
</p>

# Math-To-Manim

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE%200.19%2B-orange)](https://www.manim.community/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Claude Opus 4.7](https://img.shields.io/badge/Claude-Opus%204.7-blueviolet)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Turn a one-line math prompt into a rendered Manim video with a multi-agent reverse knowledge tree pipeline.**

</div>

---

## What just happened in the hero GIF?

The prompt was tiny:

```text
Explain why derivatives are slopes
```

Math-To-Manim expanded it into a full agent pipeline:

```text
simple prompt
  -> ConceptAnalyzer
  -> PrerequisiteExplorer: "What must I understand BEFORE this?"
  -> MathematicalEnricher
  -> VisualDesigner
  -> NarrativeComposer
  -> Manim CodeGenerator
  -> Python syntax validation / repair
  -> Manim render
  -> MP4 / GIF
```

The generated derivative demo built this concept chain:

```text
derivatives as slopes of tangent lines
  +- slope of a line
  +- functions and their graphs
  +- limits
  +- secant lines
  +- linear equations
```

Then Claude generated a 400+ line Manim scene with 100+ animations, and Manim rendered the final MP4.

---

## Why this project is different

Math-To-Manim does **not** just ask an LLM to "write a Manim script."

It first builds a **reverse knowledge tree**. For any requested concept, the system recursively asks:

> What must someone understand before they can understand this?

That produces a pedagogical dependency tree from foundations to the target idea. Later agents enrich that tree with equations, visual metaphors, scene structure, and finally executable Manim code.

The result is a path from **understanding** to **animation**, not just text-to-code.

---

## Current best demo: 10-minute multi-agent run

This is the recommended live demo because it shows the agents working in the terminal and ends with a real rendered MP4.

### 1. Install

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev,claude,web]"
```

System dependencies:

```bash
ffmpeg -version
python -m manim --version
latex --version
```

Add your Anthropic key to `.env`:

```bash
ANTHROPIC_API_KEY=your_key_here
```

### 2. Run the cinematic derivative demo

```bash
python scripts/demo_10_minute_pipeline.py \
  --prompt "Explain why derivatives are slopes" \
  --depth 1 \
  --style cinematic \
  --model claude-opus-4-7
```

On Windows PowerShell:

```powershell
python scripts\demo_10_minute_pipeline.py `
  --prompt "Explain why derivatives are slopes" `
  --depth 1 `
  --style cinematic `
  --model claude-opus-4-7
```

The runner prints each stage, saves the generated artifacts, infers the Manim scene class, and renders the MP4.

Typical final video path:

```text
media/videos/derivatives_as_slopes_of_tangent_lines_animation/480p15/DerivativesAsSlopes.mp4
```

### 3. Faster code-only run

If you want to show the multi-agent process without waiting for Manim to render:

```bash
python scripts/demo_10_minute_pipeline.py \
  --prompt "Explain why derivatives are slopes" \
  --depth 1 \
  --style cinematic \
  --model claude-opus-4-7 \
  --no-render
```

---

## Demo runner options

```bash
python scripts/demo_10_minute_pipeline.py --help
```

Important flags:

| Flag | Purpose |
|---|---|
| `--prompt` | Natural-language animation request. |
| `--depth` | Reverse knowledge tree depth. Use `1` or `2` for live demos. |
| `--model` | Claude model ID. Current default: `claude-opus-4-7`. |
| `--style` | `basic`, `cinematic`, or `experimental`. |
| `--quality` | Manim render quality: `l`, `m`, `h`, `p`, `k`. Default: `l`. |
| `--threejs` | Also generate an interactive Three.js artifact. |
| `--no-render` | Generate code and artifacts, but skip MP4 rendering. |

`cinematic` mode asks the code generator for a more polished educational-video style: dark background, visual hierarchy, geometry before algebra, readable labels, and a clear aha moment.

`experimental` mode asks for a more creative metaphor while still trying to stay renderable with standard Manim CE primitives.

---

## Generated artifacts

Each demo run writes files under:

```text
output/demo_10_minute/
```

Typical files:

```text
<concept>_tree.json       # reverse knowledge tree
<concept>_prompt.txt      # verbose production prompt
<concept>_animation.py    # generated Manim scene
<concept>_result.json     # metadata and combined outputs
```

Rendered videos are written by Manim under:

```text
media/videos/
```

`output/` and `media/videos/` are generated artifacts and are intentionally gitignored.

---

## Architecture

The default Claude pipeline lives in `src/agents/`.

```text
src/agents/
  orchestrator.py             # coordinates the full pipeline
  prerequisite_explorer.py    # reverse knowledge tree core
  llm_client.py               # Anthropic / DeepSeek / Kimi client abstraction
  mathematical_enricher.py    # equations, definitions, examples
  visual_designer.py          # colors, layout, animation ideas
  narrative_composer.py       # tree -> verbose production prompt
  threejs_code_generator.py   # optional interactive web output
```

### The six main stages

1. **ConceptAnalyzer**
   - Extracts the core concept, domain, level, and learning goal.

2. **PrerequisiteExplorer**
   - Recursively asks what must be understood before the target concept.
   - Builds a tree from foundations to the requested idea.

3. **MathematicalEnricher**
   - Adds equations, definitions, examples, and interpretation.

4. **VisualDesigner**
   - Adds visual elements, color palette, layout, timing, and transitions.

5. **NarrativeComposer**
   - Walks the tree from prerequisites to target.
   - Produces a long, structured prompt for code generation.

6. **CodeGenerator**
   - Generates complete Manim Community Edition Python code.
   - Validates syntax and asks the model to repair malformed code before saving.

---

## Python API example

```python
from dotenv import load_dotenv
from src.agents.orchestrator import ReverseKnowledgeTreeOrchestrator

load_dotenv()

orchestrator = ReverseKnowledgeTreeOrchestrator(
    model="claude-opus-4-7",
    max_tree_depth=1,
    enable_code_generation=True,
    enable_threejs_generation=False,
    creative_brief="Make this cinematic: geometry before algebra, dark palette, clear aha moment.",
)

result = orchestrator.process(
    user_input="Explain why derivatives are slopes",
    output_dir="output/demo_10_minute",
)

print(result.target_concept)
print(result.verbose_prompt[:1000])
```

---

## Render generated Manim manually

If you already have a generated file and scene class:

```bash
python -m manim -ql output/demo_10_minute/derivatives_as_slopes_of_tangent_lines_animation.py DerivativesAsSlopes
```

Use higher quality when you are ready to publish:

```bash
python -m manim -qm output/demo_10_minute/derivatives_as_slopes_of_tangent_lines_animation.py DerivativesAsSlopes
python -m manim -qh output/demo_10_minute/derivatives_as_slopes_of_tangent_lines_animation.py DerivativesAsSlopes
```

---

## Rebuild the README hero GIF

The hero GIF is generated from the rendered derivative MP4 with FFmpeg:

```bash
MP4="media/videos/derivatives_as_slopes_of_tangent_lines_animation/480p15/DerivativesAsSlopes.mp4"

ffmpeg -y -ss 95 -t 24 -i "$MP4" \
  -vf "fps=12,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  public/derivatives-as-slopes-hero.gif
```

This keeps the README asset small while showing the secant-line-to-tangent-line payoff.

---

## Gallery

Each GIF below was rendered from a Manim scene in `examples/` (or `Gemini3/`). The descriptions are inferred from the source files. Click into the linked source for the full scene.

### Calculus and analysis

<p align="center">
  <img src="giffolder/DerivativeVisualization.gif" alt="Derivative visualization" width="80%">
</p>

**DerivativeVisualization** — Companion clip for the hero demo. A function graph with a moving secant line collapsing to the tangent, illustrating why the derivative is the slope of the tangent at a point. Generated by the Claude pipeline from the prompt *"Explain why derivatives are slopes."*

<p align="center">
  <img src="giffolder/RadiusOfConvergence.gif" alt="Radius of convergence" width="80%">
</p>

**RadiusOfConvergence** — Taylor series approximations on a deep slate background, with the cyan "true function" curve, gold partial-sum approximations, and a red region marking where the series diverges outside the radius of convergence. Source: [`Gemini3/taylor_scene.py`](Gemini3/taylor_scene.py).

<p align="center">
  <img src="giffolder/FourierEpicycles.gif" alt="Fourier epicycles" width="80%">
</p>

**FourierEpicycles** — A chain of rotating circles (epicycles) whose tip traces out a target curve, visualizing how a Fourier series reconstructs a signal as a sum of complex exponentials. Source: [`examples/mathematics/fourier/fourier_epicycles.py`](examples/mathematics/fourier/fourier_epicycles.py).

<p align="center">
  <img src="giffolder/LorenzAttractor.gif" alt="Lorenz attractor" width="80%">
</p>

**LorenzAttractor** — The Lorenz system integrated as a 3D trajectory, showing the iconic two-lobed strange attractor and sensitivity to initial conditions. Source: [`examples/mathematics/analysis/lorenz_attractor_symphony.py`](examples/mathematics/analysis/lorenz_attractor_symphony.py).

### Geometry and topology

<p align="center">
  <img src="giffolder/HopfFibrationAnimation.gif" alt="Hopf fibration" width="80%">
</p>

**HopfFibrationEpic** — A cinematic rendering of the Hopf fibration: linked circles in 3-space that together cover S^3, color-coded by their base point on S^2. Source: [`examples/misc/epic_hopf.py`](examples/misc/epic_hopf.py).

<p align="center">
  <img src="giffolder/TeachingHopf.gif" alt="Teaching the Hopf fibration" width="80%">
</p>

**TeachingHopf** — A pedagogical walkthrough of the same fibration, building it up fiber by fiber rather than presenting the finished bundle. Source: [`examples/misc/teaching_hopf.py`](examples/misc/teaching_hopf.py).

<p align="center">
  <img src="giffolder/Rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron" width="80%">
</p>

**Rhombicosidodecahedron** — A 62-faced Archimedean solid rotating in 3D, with squares, triangles, and pentagons highlighted by face type. Source: [`examples/mathematics/geometry/rhombicosidodecahedron_flythrough.py`](examples/mathematics/geometry/rhombicosidodecahedron_flythrough.py) and [`rhombicosidodecahedron_bouncing.py`](examples/mathematics/geometry/rhombicosidodecahedron_bouncing.py).

<p align="center">
  <img src="giffolder/WhiskeringExchangeScene.gif" alt="Whiskering exchange law" width="80%">
</p>

**WhiskeringExchangeScene** — A 2-category theory diagram illustrating the whiskering exchange law: horizontal and vertical composition of 2-morphisms (blue and orange) commute. Source: [`Gemini3/whiskering_scene.py`](Gemini3/whiskering_scene.py).

### Physics and cosmology

<p align="center">
  <img src="giffolder/CosmicGravity3D.gif" alt="Cosmic gravity well" width="80%">
</p>

**CosmicGravity3D** — A 3D gravitational well embedded in a starfield, showing the curvature of space induced by a massive body. Source: `CosmicGravity3D` in [`examples/misc/visual_styles_showcase.py`](examples/misc/visual_styles_showcase.py).

<p align="center">
  <img src="giffolder/BrownianFinance.gif" alt="Brownian motion to Einstein" width="80%">
</p>

**BrownianFinance / BrownToEinstein** — Brownian motion of a pollen grain visualized as a random walk, then connected to Einstein's diffusion equation — the same mathematical object that underlies stochastic models in finance. Source: [`examples/mathematics/statistics/brown_einstein.py`](examples/mathematics/statistics/brown_einstein.py).

### Machine learning

<p align="center">
  <img src="giffolder/GRPO_Explanation.gif" alt="GRPO explanation" width="80%">
</p>

**GRPOAnimation** — Group Relative Policy Optimization (the RL algorithm behind DeepSeek-R1) explained scene-by-scene: traditional RL setup, group sampling, and the relative-advantage update. Source: [`examples/computer_science/machine_learning/GRPO.py`](examples/computer_science/machine_learning/GRPO.py).

<p align="center">
  <img src="media/videos/GRPO2/480p15/GRPOArtisticExplanationOnly_ManimCE_v0.19.0.gif" alt="GRPO artistic explanation" width="80%">
</p>

**GRPOArtisticExplanationOnly** — A second, more stylized take on GRPO that focuses purely on the visual narrative of the policy update without the textbook framing. Source: [`examples/computer_science/machine_learning/GRPO2.py`](examples/computer_science/machine_learning/GRPO2.py).

<p align="center">
  <img src="giffolder/ProLIPScene.gif" alt="ProLIP scene" width="80%">
</p>

**ProLIPScene** — Probabilistic Language-Image Pretraining: image and text encoders project into a shared embedding space, with dashed-arrow probabilistic mappings replacing the deterministic CLIP arrows. Source: [`examples/computer_science/algorithms/prolip.py`](examples/computer_science/algorithms/prolip.py).

<p align="center">
  <img src="media/videos/prolip/480p15/ProLIPScene_preview.gif" alt="ProLIP scene preview" width="80%">
</p>

**ProLIPScene (preview render)** — Low-resolution preview render of the ProLIP scene above, produced directly by `manim -pql` during development.

---

## Other pipelines in the repo

Math-To-Manim also contains experimental and alternative pipelines:

| Pipeline | Location | Notes |
|---|---|---|
| Claude / Anthropic | `src/` | Default maintained path for the 10-minute demo. |
| Gemini 3 / Google ADK | `Gemini3/` | Experimental Google-agent pipeline. |
| Kimi K2.5 / Moonshot | `KimiK2.5Swarm/` | Experimental swarm-style pipeline. |

The root quickstart currently focuses on the Claude pipeline because it has the most reliable end-to-end prompt-to-MP4 demo path.

---

## Useful docs

| Doc | Purpose |
|---|---|
| `docs/10_MINUTE_MULTI_AGENT_DEMO.md` | Presenter runbook for the live demo. |
| `docs/REVERSE_KNOWLEDGE_TREE.md` | Core algorithm explanation. |
| `docs/ARCHITECTURE.md` | System design details. |
| `docs/EXAMPLES.md` | Existing generated animations. |
| `docs/ROADMAP.md` | Project direction. |

---

## Troubleshooting

### `ANTHROPIC_API_KEY is not set`

Create `.env` in the repository root:

```bash
ANTHROPIC_API_KEY=your_key_here
```

Do not commit `.env`.

### `Missing Python dependency: dotenv`

Your active Python environment does not have the project dependencies installed. Run:

```bash
pip install -e ".[dev,claude,web]"
```

### `manim` command not found

Use the module form; it works even when the console script is not on PATH:

```bash
python -m manim --version
python -m manim -ql generated_file.py SceneName
```

### Windows and WSL environments are separate

Installing dependencies in Windows Python does not install them into WSL Python. If you run from WSL, create and activate a WSL venv and install the project there.

---

## License

MIT. See `LICENSE`.
