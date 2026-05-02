<p align="center">
  <a href="https://www.star-history.com/#HarleyCoops/Math-To-Manim&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" width="100%" />
    </picture>
  </a>
</p>

# Math-To-Manim

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE%200.19%2B-orange)](https://www.manim.community/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Claude Opus 4.7](https://img.shields.io/badge/Claude-Opus%204.7-blueviolet)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Turn one-line prompts into cinematic Manim animations with a multi-agent reverse knowledge tree pipeline.**

From calculus intuition to chaotic attractors, topology, spacetime, stochastic finance, and AI explainers — this repo is built to make math feel alive.

</div>

---

## Visual showcase

Math-To-Manim is not just text-to-code. It builds the prerequisite story, designs the visuals, writes Manim, validates the Python, and renders animations that teach.

These README previews are optimized clips generated from the larger GIFs in `public/`, `giffolder/`, and `media/videos/` so the page stays fast while still showing the good stuff.

<table>
  <tr>
    <td width="50%">
      <img src="public/readme-showcase/rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron animation" width="100%"><br>
      <b>Rhombicosidodecahedron</b><br>
      A vivid 3D Archimedean solid with layered orange/blue geometry, depth, and publish-ready mathematical spectacle.
    </td>
    <td width="50%">
      <img src="public/readme-showcase/cosmic-gravity-3d.gif" alt="Cosmic gravity spacetime animation" width="100%"><br>
      <b>CosmicGravity3D</b><br>
      A cinematic spacetime scene with stars, field equations, and the feeling of a physics documentary opener.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="public/readme-showcase/derivatives-as-slopes.gif" alt="Derivatives as slopes animation" width="100%"><br>
      <b>Derivatives as Slopes</b><br>
      The classic calculus aha moment: a secant line tightens into a tangent, turning local change into visible slope.
    </td>
    <td width="50%">
      <img src="public/readme-showcase/lorenz-attractor.gif" alt="Lorenz attractor animation" width="100%"><br>
      <b>Lorenz Attractor</b><br>
      Chaos theory made visual: evolving trajectories reveal the iconic butterfly-shaped strange attractor.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="public/readme-showcase/prolip-scene.gif" alt="ProLIP graph and neural network style animation" width="100%"><br>
      <b>ProLIP Scene</b><br>
      A modern graph/neural-network style explainer with glowing nodes, structured connections, and ML presentation energy.
    </td>
    <td width="50%">
      <img src="public/readme-showcase/grpo-explanation.gif" alt="Group Relative Policy Optimization animation" width="100%"><br>
      <b>GRPO Explanation</b><br>
      Reinforcement learning concepts turned into an animated visual narrative for Group Relative Policy Optimization.
    </td>
  </tr>
</table>

## More epic GIFs in the repo

<table>
  <tr>
    <td width="33%">
      <img src="public/readme-showcase/fourier-epicycles.gif" alt="Fourier epicycles animation" width="100%"><br>
      <b>Fourier Epicycles</b><br>
      Rotating circles combine to trace complex curves — Fourier analysis as moving geometry.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/hopf-fibration.gif" alt="Hopf fibration animation" width="100%"><br>
      <b>Hopf Fibration</b><br>
      A topology visualizer for stereographic projection from S³ into R³.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/teaching-hopf.gif" alt="Teaching Hopf fibration animation" width="100%"><br>
      <b>Teaching Hopf</b><br>
      A clean instructional walkthrough for one of topology's most beautiful constructions.
    </td>
  </tr>
  <tr>
    <td width="33%">
      <img src="public/readme-showcase/brownian-finance.gif" alt="Brownian motion finance animation" width="100%"><br>
      <b>Brownian Finance</b><br>
      Stochastic motion and financial uncertainty introduced through animated mathematical storytelling.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/radius-of-convergence.gif" alt="Radius of convergence animation" width="100%"><br>
      <b>Radius of Convergence</b><br>
      Power series behavior explained with number-line intuition and visual boundaries.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/whiskering-exchange.gif" alt="Whiskering exchange scene animation" width="100%"><br>
      <b>Whiskering Exchange</b><br>
      Abstract algebra/category-theory structure presented as a formal visual explainer.
    </td>
  </tr>
  <tr>
    <td width="33%">
      <img src="public/readme-showcase/derivative-visualization.gif" alt="Derivative visualization animation" width="100%"><br>
      <b>Derivative Visualization</b><br>
      A foundational calculus scene for local change, axes, curves, and slope intuition.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/cosmic-gravity-3d.gif" alt="Cosmic gravity animation" width="100%"><br>
      <b>Gravity + Geometry</b><br>
      Relativity-flavored visual language for connecting equations to curved spacetime.
    </td>
    <td width="33%">
      <img src="public/readme-showcase/lorenz-attractor.gif" alt="Lorenz attractor animation" width="100%"><br>
      <b>Dynamic Systems</b><br>
      Nonlinear motion and sensitive dependence on initial conditions in a compact visual loop.
    </td>
  </tr>
</table>

---

## What makes this different

Math-To-Manim does **not** just ask an LLM to "write a Manim script."

It first builds a **reverse knowledge tree**. For any requested concept, the system recursively asks:

> What must someone understand before they can understand this?

That produces a pedagogical dependency tree from foundations to the target idea. Later agents enrich that tree with equations, visual metaphors, scene structure, and finally executable Manim code.

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

The result is a path from **understanding** to **animation**, not just text-to-code.

---

## Example: tiny prompt to full animation

The derivative hero started as:

```text
Explain why derivatives are slopes
```

The system expanded it into a teachable concept chain:

```text
derivatives as slopes of tangent lines
  +- slope of a line
  +- functions and their graphs
  +- limits
  +- secant lines
  +- linear equations
```

Then Claude generated a 400+ line Manim scene with 100+ animations, and Manim rendered the final video/GIF.

---

## Quickstart

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
ANTHROPIC_API_KEY=***
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

The runner prints each stage, saves generated artifacts, infers the Manim scene class, and renders the MP4.

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

| Flag | Purpose |
|---|---|
| `--prompt` | Natural-language animation request. |
| `--depth` | Reverse knowledge tree depth. Use `1` or `2` for live demos. |
| `--model` | Claude model ID. Current default: `claude-opus-4-7`. |
| `--style` | `basic`, `cinematic`, or `experimental`. |
| `--quality` | Manim render quality: `l`, `m`, `h`, `p`, `k`. Default: `l`. |
| `--threejs` | Also generate an interactive Three.js artifact. |
| `--no-render` | Generate code and artifacts, but skip MP4 rendering. |

`cinematic` mode asks the code generator for a polished educational-video style: dark background, visual hierarchy, geometry before algebra, readable labels, and a clear aha moment.

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
  visual_designer.py          # colors, layout, timing, and transitions
  narrative_composer.py       # tree -> verbose production prompt
  threejs_code_generator.py   # optional interactive web output
```

### The six main stages

1. **ConceptAnalyzer** — extracts the core concept, domain, level, and learning goal.
2. **PrerequisiteExplorer** — recursively asks what must be understood before the target concept.
3. **MathematicalEnricher** — adds equations, definitions, examples, and interpretation.
4. **VisualDesigner** — adds visual elements, color palette, layout, timing, and transitions.
5. **NarrativeComposer** — walks the tree from prerequisites to target and produces the production prompt.
6. **CodeGenerator** — generates complete Manim CE Python code, validates syntax, and repairs malformed output.

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

## Rebuild the README derivative hero GIF

The derivative hero GIF is generated from the rendered derivative MP4 with FFmpeg:

```bash
MP4="media/videos/derivatives_as_slopes_of_tangent_lines_animation/480p15/DerivativesAsSlopes.mp4"

ffmpeg -y -ss 95 -t 24 -i "$MP4" \
  -vf "fps=12,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  public/readme-showcase/derivatives-as-slopes.gif
```

This keeps the README asset small while showing the secant-line-to-tangent-line payoff.

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

## Star history

If Math-To-Manim is useful, a star helps people find the project.

<a href="https://www.star-history.com/#HarleyCoops/Math-To-Manim&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date" />
  </picture>
</a>

---

## Troubleshooting

### `ANTHROPIC_API_KEY is not set`

Create `.env` in the repository root:

```bash
ANTHROPIC_API_KEY=***
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
