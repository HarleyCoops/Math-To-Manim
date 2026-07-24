<div align="center">

<a href="https://www.star-history.com/?repos=HarleyCoops%2FMath-To-Manim&type=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&theme=dark&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" width="100%" />
  </picture>
</a>

# Math to Manim

### Ask a question. Get a visual explainer.

[![v1.1](https://img.shields.io/badge/Release-v1.1.0-d97757)](#whats-new-in-v11)
[![Claude Fable 5](https://img.shields.io/badge/Claude-Fable%205%20baseline-d97757)](#the-mythos-engine)
[![GPT-5.6 Sol](https://img.shields.io/badge/Codex-GPT--5.6%20Sol-10a37f)](docs/SOL_5_6_SILO.md)
[![REST API](https://img.shields.io/badge/REST-API-6a9bcc)](#the-api)
[![MCP server](https://img.shields.io/badge/MCP-server-788c5d)](#the-mcp-server)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3b82f6)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE-f59e0b)](https://www.manim.community/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

[Mythos engine](#the-mythos-engine) · [Reverse reasoning](#the-reverse-reasoning-tree) · [API](#the-api) · [MCP server](#the-mcp-server) · [Motion showcase](docs/showcase/README.md) · [Prime RL](docs/PRIME_INTELLECT_RL.md) · [Roadmap](docs/ROADMAP.md) · [Agent guide](AGENTS.md)

<br />

> *This page is the drafting room for two native film engines: the six-agent **Claude Fable 5** Mythos chain and the independent **GPT-5.6 Sol** Codex CLI silo. Every moving plate below was generated, rendered, inspected, and published from one of those pipelines. [The story of how the series began in the middle →](docs/showcase/THE-PLATES.md)*

<br />

<p align="center">
  <a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">
    <img src="docs/showcase/assets/erdos-1038-potential-landscape.gif" alt="Erdős Problem 1038 shown as an archival off-white three-dimensional landscape: a certified valley narrows to the lower limit, endpoint root towers reveal the upper limit, and the final tableau compares both answers" width="90%" />
  </a>
</p>

<p align="center"><strong>ERDŐS 1038: THE POTENTIAL LANDSCAPE</strong></p>

A polynomial is usually introduced as a line of symbols, but it can also be
seen as a landscape made by its roots. Imagine every root pressing into a
flexible sheet stretched above the number line. Taken together, the roots
raise and lower that sheet. The transparent plane in the explainer marks zero:
wherever the landscape falls beneath it, the polynomial has size less than
one. The footprint under the plane is therefore the exact set whose width the
problem asks us to measure.

That turns the question into something physical: how should the roots be
arranged to make the submerged footprint as narrow as possible, or as wide as
possible? For the narrow side, clusters of roots can be gathered toward their
centres without making the footprint larger. Repeating that idea leads toward
an increasingly fine, one-sided distribution of roots. No finite polynomial
quite reaches the limiting shape, but a sequence of them gets arbitrarily
close. Its width is **1.834430475762661…**—the certified floor shown by the
curved 3D valley.

The widest case is beautifully simpler. Put the roots at the two endpoints,
−1 and +1, in equal numbers. This produces the family
**f(x) = (x² − 1)ᵐ**, and the region where the polynomial is smaller than one
runs from −√2 to +√2. Its width is therefore **2√2**. So the film ends by
contrasting two different kinds of extreme: a lower value that can be
approached forever but never attained by a finite polynomial, and an upper
value reached exactly by piling the roots at the endpoints.

<p align="center"><em><a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">Watch the complete 79 second visual explainer</a> · <a href="docs/prompts/erdos-1038-off-white-3d.md">Read the complete Sol production prompt</a></em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/jacobian-conjecture-3d.gif" alt="THE JACOBIAN CONJECTURE — LOCAL CERTAINTY, GLOBAL QUESTION: a complete 3D Manim film zooming through a deformed polynomial coordinate lattice, isolating a tangent plane, turning Jacobian columns into colored basis arrows, comparing a tiny cube with its image parallelepiped, and pulling back from local invertibility to the global polynomial-inverse question" width="85%" />
</p>

<p align="center"><em><strong>THE JACOBIAN CONJECTURE.</strong> This explainer separates local certainty from global truth. A small cube becomes a parallelepiped, making the Jacobian determinant visible as local volume change. The camera then pulls back to show why a map can be reversible nearby without being reversible everywhere.</em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/traitor-axis.gif" alt="THE TRAITOR AXIS: a coral-and-steel T-handle tumbling against ink-black space — spun about its middle axis it somersaults every 8.2 seconds while the angular-momentum sphere reveals why: polhode loops in blue and gold, the coral separatrix crossing at the saddle, and the simulated spin creeping then sprinting along it" width="85%" />
</p>

<p align="center"><em><strong>THE TRAITOR AXIS.</strong> This explainer teaches why two ways of spinning an object remain steady while the middle axis flips. A computed handle and its momentum sphere move together, letting the learner connect each somersault to the unstable path in the equations. <a href="examples/physics/classical_mechanics/dzhanibekov_traitor_axis.py">Explore the source scene.</a></em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/vortex-leapfrog.gif" alt="Two glowing vortex rings pass through each other while tracer particles reveal the surrounding flow" width="85%" />
</p>

<p align="center"><em><strong>VORTEX LEAPFROG.</strong> This explainer teaches how one vortex ring can pass through another. The rings contract, accelerate, pass, and expand under a computed velocity field while tracer particles make the invisible flow visible.</em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/the-valley.gif" alt="The valley of nuclear stability appears as a three dimensional energy landscape" width="85%" />
</p>

<p align="center"><em><strong>THE VALLEY OF STABILITY.</strong> This explainer turns nuclear binding energy into terrain. Fusion and fission begin on opposite sides, then both move toward the same stable basin near iron, making two difficult processes feel like one geometric idea.</em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/exceptional-point-monodromy.gif" alt="A loop around an exceptional point moves between two sheets of a square root surface" width="85%" />
</p>

<p align="center"><em><strong>EXCEPTIONAL POINT MONODROMY.</strong> This explainer shows why one loop around a branch point swaps two eigenvalues. The path lifts onto a two sheeted square root surface, so the learner can watch one branch become the other.</em></p>

<br />

<p align="center"><strong><a href="docs/showcase/README.md">Explore every visual explainer in the motion showcase</a></strong></p>

</div>

---

## What's new in v1.1

v1.1 is the release where the Mythos chain stops being a layer and becomes **the** pipeline.

| Change | What it means |
|---|---|
| **One engine** | The 6-agent Mythos chain (`mythos/`) is now the single pipeline. The v1.0 Codex/OpenAI typed pipeline, its tests, evals, and the Hermes operator agent are preserved under [`archive/`](archive/) — nothing deleted, nothing imported. |
| **REST API** | `math-to-manim serve-api` starts a FastAPI service: `POST /v1/runs` with one sentence, poll the job, download every artifact. [Details.](#the-api) |
| **MCP server** | `math-to-manim serve-mcp` exposes the chain to any MCP client (Claude Desktop, Claude Code, Cowork) as seven tools. Your assistant can now *make films*. [Details.](#the-mcp-server) |
| **One clean package** | `pip install -e .` gives you `mythos/` and two commands: `math-to-manim` and its short alias `m2m`. Core dependency: pydantic. Everything else is an extra (`[api]`, `[mcp]`, `[render]`). |
| **Offline everything** | The entire chain, the API, and every MCP tool run deterministically with `--offline` — zero model calls, zero render deps. CI proves it on every push. |
| **New showcase films** | The reverse reasoning tree and the grammar reel, written in the engine's own cinematography grammar and rendered to the GIFs at the top of this page. |

### The hardening update (July 2026)

Every entry below encodes a failure observed in a real run, then fixed:

| Change | What it means |
|---|---|
| **Fable-first, with an Anthropic ladder** | `claude-fable-5` is the baseline for every reasoning stage. If it fails for a *model* reason (overload, not-found, 5xx), the chain walks `M2M_MODEL_FALLBACKS` — `claude-opus-4-8`, then `claude-sonnet-5` — through the **same Claude CLI subscription login, never an API key**. The first model that answers sticks for the rest of the run, and the manifest records the switch. |
| **Auth fails fast** | A logged-out CLI used to die opaquely mid-chain. Now it raises immediately with the fix (`claude /login`) — and never wastes fallback attempts, because a broken login is broken for every model. |
| **Self-defending chain** | Degenerate stage output (a 48-byte math dossier once storyboarded an *empty film*) is rejected, retried once with a corrective nudge, and aborts loudly on the second offense. |
| **Truthful, live manifests** | Manifests are written atomically after every stage (Windows-safe), so `m2m_get_job` and `GET /v1/jobs/{id}` stream real per-stage progress instead of silence until the end. |
| **Render budget** | Renders get their own `M2M_RENDER_TIMEOUT` (default 1800 s); a timeout no longer kills the job or burns model-repair attempts on a budget problem. |
| **`math-to-manim doctor`** | Preflight before you spend 30 minutes: configuration and where each value came from, backend login (`--ping` walks the whole model ladder with 1-line calls), manim/ffmpeg/latex, runs-dir writability. |
| **`math-to-manim gif`** | One command from a run id (or any `.mp4`) to a palette-optimized showcase GIF — the exact recipe behind every GIF on this page. |
| **Config from env, never from code** | All knobs live in the environment or a gitignored `.env` (see [Configuration](#quickstart)); the audit removed the last hardcoded personal path. |

---

## The morning it started

Math-To-Manim began on the morning of Donald Trump's inauguration — **January 20, 2025 — the day the reasoning models arrived.** I do not think it was an accident that the Chinese decided to release the R1 model on that day.

I was awake, saw the model hit Hugging Face, and quickly built a `.ipynb` to load the model and run it.

I created this repo at `2025-01-20T11:04:50Z` / `04:04:50 MST`.

Within a couple of minutes I realized what this meant. If the Chinese, via GRPO, had reasoning on a chip, recursive reasoning was not far behind. In my tweet I wrote "Wrap it up, its over" and I still believe it.

```text
09a2f22  2025-01-20T04:24:50-07:00  updated
A        DeepSeek_R1_zero.ipynb
A        Readme.md
```

Three hours later, the first Manim file landed: `pythagorean.py` at `2025-01-20T07:18:12-07:00`.

<p align="center">
  <a href="https://x.com/christiancooper/status/1881335734256492605?s=20"><img src="docs/assets/r1-pythagorean-tweet.gif" alt="The original R1 Pythagorean theorem Manim animation from the viral January 20, 2025 tweet" width="80%" /></a>
</p>

> "I asked #R1 to visually explain to me the Pythagorean theorem. This was done in one shot with no errors in less than 30 seconds. Wrap it up, its over: #DeepSeek #R1"
>
> — [Christian H. Cooper, January 20, 2025](https://x.com/christiancooper/status/1881335734256492605?s=20)

What R1 proved that morning is that a reasoning model was already good at Manim out of the box. What this repo became is the thesis taken seriously: **if one shot of reasoning gets you a clean Pythagorean proof, a chain of recursive reasoning gets you a film.** Six planning agents now reason over your prompt — backward, then forward — before a single line of scene code is generated, validated, rendered, and reviewed.

-christian

---

## The reverse reasoning tree

Every text-to-code demo you have seen jumps straight from request to Python. Math-To-Manim takes the long way on purpose, and the long way is the product.

<p align="center">
  <img src="docs/showcase/assets/reverse-reasoning-tree.gif" alt="Animated reverse reasoning tree: the question decomposes backward through special relativity and quantum mechanics down to known ground, then a gold pulse walks it forward as a curriculum" width="85%" />
</p>

The pipeline's first move is not "write code" — it is a question: **what would a mind need to already hold for this idea to land?** Then it asks that question again, of each answer, recursively, until it bottoms out at things the viewer already knows. That is the reverse reasoning tree:

```text
                     "Explain quantum field theory"
                                  │
                                  ▼  what must you already know?
                 ┌────────────────┴────────────────┐
        special relativity                 quantum mechanics
                 │                                  │
        ┌────────┴────────┐                ┌────────┴─────────┐
   spacetime          Lorentz         wavefunctions       operators
   intervals        invariance             │                  │
        │                │            superposition     commutation
        ▼                ▼                 ▼                  ▼
   ─────────────  the tree bottoms out at known ground  ─────────────
                                  │
                                  ▼  now walk it FORWARD
      known ground → prerequisites → target concept → the film
```

The tree is built backward from the target and then **walked forward as a curriculum**: the film teaches the leaves first, so that by the time the camera reaches the QED Lagrangian, every symbol on screen has already been earned. That single design decision is why the output feels like teaching instead of decoration.

The tree is not a metaphor — it is a file. Every run writes it to disk as `02_knowledge_map.json`, an artifact you can open, inspect, and edit before any code exists.

---

## One engine, every altitude

The reverse reasoning tree has a property that no template system has: **it bottoms out at whatever the asker already knows.** That makes the same six agents serve two people who will never sit in the same classroom:

> *"I'm a single parent and my 6th grader is struggling with greatest common factors and order of operations. She's a visual learner — show it to her."*

The tree bottoms out at multiplication. The film that comes back builds factor trees out of manipulatives, zooms into the shared factor of 12 and 18, color-codes PEMDAS, and ends with two parent check questions on screen. (That's a real run — it's in the ledger as `StructureFirstJourney`.) A photo of the actual textbook problem works too: any MCP client that can see images — Claude Desktop, Cowork — transcribes the problem and hands the sentence to `m2m_create_animation`.

> *"I'm working on my PhD in topology — help me actually see why one loop around the exceptional point swaps the eigenvalue branches."*

Same engine, same charter. The tree now bottoms out at complex multiplication and covering spaces, and the film draws the two-sheeted square-root surface and lets monodromy happen to the camera. (Also a real run — the exceptional point film is three plates up this page.)

Between those two altitudes sit the rest of the plates: derivatives for a first calculus course, the circle-area unwrapping for geometry class, Fourier epicycles for engineers, GRPO policy geometry for ML researchers, the traitor axis for anyone who has ever thrown a tennis racket. The recursion is the teaching tool: **decompose the question backward until it touches what you know, then film the walk forward — and when a step still doesn't land, ask again from that step, and the engine builds the next film one level deeper.**

---

## The Mythos engine

<p align="center">
  <img src="docs/assets/mythos-learns-math-to-manim.png" alt="Mythos Learns Math-to-Manim" width="92%" />
</p>

**This repo is built around Claude Fable 5.** The six agents are Claude Code subagents; the harness drives them headlessly through the Claude CLI with `claude-fable-5` as the baseline; every frame is written with the camera as narrator — plain-language headlines before symbols, flights into the exact term being explained, pull-backs to restore context, true-3D set pieces.

Behind Fable stands an all-Anthropic ladder on the same CLI subscription login: if the baseline fails for a model-specific reason, the chain quietly steps down to `claude-opus-4-8`, then `claude-sonnet-5`, sticks with the first model that answers, and writes the switch into the run's manifest. No API key is involved at any rung — and a logged-out CLI fails fast with the fix instead of failing slow with a mystery.

The chain: **intent → cartographer → curriculum → math-director → cinematographer → scene-composer**, then codegen → static checks → render → self-repair.

| Agent | Question it answers | Artifact |
|---|---|---|
| **Intent** | What is the learner really asking, and at what level? | `01_intent.json` |
| **Cartographer** | What is the reverse reasoning tree beneath the target? | `02_knowledge_map.json` |
| **Curriculum** | In what order does the tree become teachable? | `03_curriculum.json` |
| **Math-director** | Which definitions, equations, and examples carry the load? | `04_math_dossier.json` |
| **Cinematographer** | What does the camera do, beat by beat? | `05_shot_list.json` |
| **Scene-composer** | How does the shot list compile into Manim objects and timing? | `06_scene_spec.json` |

| Piece | Where | What it does |
|---|---|---|
| Agent charters | [`mythos/agents/`](mythos/agents/) (mirror to `.claude/agents/` for native Claude Code use) | The six minds of the chain, one markdown charter each — the single source of truth |
| Harness | [`mythos/harness.py`](mythos/harness.py) | Runs the whole chain via `claude -p --model claude-fable-5`; artifacts land in `runs/mythos/<ts>/`; `--offline` rehearsal mode needs no login |
| Camera grammar | [`mythos/cinematography.py`](mythos/cinematography.py) | `headline`, `zoom_to`, `pull_back`, `term_tour`, `tilt_to_3d`, glows — the Mythos house style, Anthropic palette |
| Cinematic Charter | [`mythos/charter.py`](mythos/charter.py) | The visual contract injected into every generation |
| Service core | [`mythos/service.py`](mythos/service.py) | Job orchestration shared by the CLI, the API, and the MCP server |
| Backends | [`mythos/backends.py`](mythos/backends.py) | Claude CLI (default, with the Anthropic fallback ladder) · Codex CLI · any OpenAI-compatible endpoint — the last two are explicit choices, never fallbacks |
| Preflight | [`mythos/doctor.py`](mythos/doctor.py) | `math-to-manim doctor --ping`: config provenance, login, the model ladder, render toolchain |
| Flagship films | [`examples/mythos/`](examples/mythos/) | QED in 8 acts, the Sound of Spacetime, the reverse reasoning tree, the grammar reel |

```bash
pip install -e ".[dev]"

# the whole chain, one line, Fable 5 as the baseline
math-to-manim run "explain quantum field theory" --render -q m

# or render a flagship directly
manim -qh examples/mythos/qft_cinematic.py QFTCinematicJourney
```

The model backend is a seam, not a marriage: `--model` overrides the baseline, `--fallbacks "a,b"` reshapes the Anthropic ladder (empty disables it), `--command fugu-api` routes the same chain through an OpenAI-compatible endpoint, and `--command codex` uses the Codex CLI. Codex and fugu are escape hatches you choose on purpose — the chain never falls back across backends on its own. The v1.0 typed pipeline that these seams grew out of is preserved in [`archive/codex-pipeline/`](archive/).

<p align="center">
  <img src="docs/assets/mythos-qft-term-tour.png" alt="Camera inside the QED Lagrangian: the Dirac term spotlit with a plain-language caption" width="49%" />
  <img src="docs/assets/mythos-qft-vertex.png" alt="The electron-photon vertex with the fine-structure constant resolving to 1/137" width="49%" />
</p>

<p align="center"><em>Stills from the Mythos cut of the QED journey: the camera inside the Lagrangian (left); the e⁻e⁻γ vertex as α resolves to 1/137 (right).</em></p>

### The grammar, in thirty seconds

<p align="center">
  <img src="docs/showcase/assets/mythos-grammar-reel.gif" alt="Grammar reel: full-screen headline, E=mc2 built from addressable terms, camera zooming into E then m then c squared with captions, then a 3D energy surface set piece" width="85%" />
</p>

Headline before symbols. Camera into the exact term. Caption everything. Tilt into 3D only when the idea itself is 3D. That is the whole contract — [`mythos/charter.py`](mythos/charter.py) spells it out, the static verifier enforces the camera rules, and every agent in the chain writes toward it.

---

## Quickstart

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv && source .venv/bin/activate     # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                                                # 29 tests, all offline
```

**Prove the plumbing with zero model calls** — the offline mode runs the entire chain with deterministic artifacts:

```bash
math-to-manim run "the heat equation" --offline
math-to-manim runs        # inspect the on-disk ledger
```

**Make a real film** — needs only a logged-in Claude CLI; the defaults already point at `claude-fable-5`:

```bash
math-to-manim doctor --ping   # preflight: config, login, the model ladder, manim, ffmpeg, latex
math-to-manim run "Show why the quantum harmonic oscillator only allows discrete energies: start with a springy potential well, zoom into the wavefunctions, then reveal the ladder of allowed energy levels." --render -q l
math-to-manim gif <run-id>    # palette-optimized showcase GIF from that run's render
```

**Configuration** lives in the environment (or a local, gitignored `.env`) — nothing personal is hardcoded:

| Variable | Default | What it does |
|---|---|---|
| `M2M_MODEL` | `claude-fable-5` | Baseline model for every reasoning stage |
| `M2M_MODEL_FALLBACKS` | `claude-opus-4-8,claude-sonnet-5` | Anthropic models tried in order when the baseline fails (overload, not-found, 5xx) — all through the same Claude CLI subscription login, never an API key. Auth failures don't fall back; they fail fast with the fix. Set empty to disable. |
| `M2M_COMMAND` | `claude` | Backend: `claude` (Claude CLI login), `codex` (Codex CLI), `fugu-api` (OpenAI-compatible HTTP) |
| `M2M_TIMEOUT` | `900` | Seconds per model call |
| `M2M_RENDER_TIMEOUT` | `1800` | Wall-clock budget for one manim render |
| `M2M_RUNS_DIR` | `runs/` | Where run bundles land (legacy alias: `M2M2_RUNS_DIR`) |
| `M2M_MANIM` | auto | Manim executable override; otherwise the active env's manim wins over PATH |
| `FUGU_API_KEY` / `FUGU_BASE_URL` | — | Only for the HTTP backend; keys are read from env, never stamped into artifacts |

Fable is the house baseline; `codex` and `fugu-api` are explicit escape hatches, never silently chosen. If the Claude CLI is logged out the chain now fails fast with the fix (`claude /login`) instead of dying mid-run.

**Render extras** (FFmpeg + LaTeX are system deps; on Debian/Ubuntu/WSL run [`./scripts/bootstrap-render.sh`](scripts/bootstrap-render.sh)):

```bash
pip install -e ".[dev,render]"
```

Every run writes a self-contained bundle:

```text
runs/mythos/<timestamp>-<slug>/
  01_intent.json           what the learner is really asking
  02_knowledge_map.json    the reverse reasoning tree
  03_curriculum.json       the tree, walked forward
  04_math_dossier.json     the formulas that carry the load
  05_shot_list.json        what the camera does, beat by beat
  06_scene_spec.json       the compiled visual plan
  *.raw.txt                full model traces for every stage
  mythos_scene.py          the film, as runnable Manim CE
  manifest.json            stages, timing, checks, renders
```

The chain reasons in JSON so the artifacts stay legible: prune a branch of `02_knowledge_map.json` mid-run and the rest of the chain inherits your edit; render failures feed a bounded repair loop instead of crashing the run. Degenerate stage output (an empty math dossier, a five-beat shot list) is rejected and retried once with a corrective nudge — and if it happens twice the chain aborts loudly rather than filming an empty story. Manifests are written atomically after every stage, so polling clients always see valid JSON and live progress.

<p align="center">
  <img src="docs/assets/render-repair-loop.svg" alt="Render validation and bounded repair loop diagram showing static review, render, repair from evidence, and packaged output" width="100%" />
</p>

---

## The API

New in v1.1: the engine as a service. Start it:

```bash
pip install -e ".[api]"
math-to-manim serve-api            # http://127.0.0.1:8642 · OpenAPI docs at /docs
```

| Method | Route | What it does |
|---|---|---|
| `GET` | `/health` | Liveness + version |
| `POST` | `/v1/runs` | Submit a prompt; returns a job record immediately (202) |
| `GET` | `/v1/jobs/{job_id}` | Poll a job: `queued → running → completed \| failed` |
| `GET` | `/v1/runs` | The on-disk run ledger, newest first |
| `GET` | `/v1/runs/{run_id}` | Full manifest + artifact listing for one run |
| `GET` | `/v1/runs/{run_id}/artifacts/{name}` | One artifact's content (JSON or Python) |

```bash
# one sentence in…
curl -s -X POST localhost:8642/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "explain fourier epicycles as rotating vectors", "render": false}'

# …poll the job, then read the film
curl -s localhost:8642/v1/jobs/<job_id>
curl -s localhost:8642/v1/runs/<run_id>/artifacts/mythos_scene.py
```

The API is a thin wrapper over [`mythos/service.py`](mythos/service.py) — the same core the CLI and MCP server use, so behavior never forks between front doors. Try the whole loop without a model login by adding `"offline": true` to the POST body.

---

## The MCP server

Also new in v1.1: any MCP client can drive the engine. Claude Desktop, Claude Code, and Cowork can turn a sentence in a conversation into a rendered film and then read back every reasoning artifact that produced it.

```bash
pip install -e ".[mcp]"
math-to-manim serve-mcp                                    # stdio
math-to-manim serve-mcp --transport streamable-http       # remote, :8643
```

Claude Desktop / Claude Code config:

```json
{
  "mcpServers": {
    "math-to-manim": {
      "command": "math-to-manim",
      "args": ["serve-mcp"]
    }
  }
}
```

| Tool | What it does |
|---|---|
| `m2m_create_animation` | One sentence in; starts the 6-agent chain as a background job (model/backend default to the server's env — Fable with the Anthropic ladder) |
| `m2m_get_job` | Poll a job — now reports **live per-stage progress** from the atomically-written manifest, not silence until the end |
| `m2m_list_runs` | The on-disk run ledger, newest first |
| `m2m_get_run` | Full manifest + artifact listing for one run |
| `m2m_get_artifact` | Read any artifact: the reverse reasoning tree, the shot list, … |
| `m2m_get_scene_code` | The generated Manim scene, ready to render |
| `m2m_cinematic_charter` | The house-style contract, so an assistant can write scenes directly |

Need a headless client instead of a chat window? [`scripts/drive_mcp_pipeline.py`](scripts/drive_mcp_pipeline.py) is the reference: it spawns `serve-mcp` over stdio, submits one prompt, polls to completion, and logs JSONL you can tail from another terminal:

```bash
python scripts/drive_mcp_pipeline.py "why does a spinning T-handle flip itself?" --render -q l --log runs/drive.log
```

That last tool is the quiet superpower: an MCP client that already writes code can pull the Cinematic Charter and the [cinematography grammar](mythos/cinematography.py) and compose Mythos-style scenes itself, using the chain only when it wants the full reasoning treatment.

---

## Prime Intellect RL repair loop

Math-To-Manim is also becoming a Prime Intellect reinforcement-learning environment. The first RL target is not "make the whole video in one shot." It is the edit move that matters after a base model produces a plausible but flawed scene: text overlaps formulas, equations are too small, the camera angle hides the point, or the zoom never lands on the symbol the learner needs to read.

The experiment: give the model the scene plan, the generated Python, validation/render evidence, and a human request such as "fix the overlap" or "zoom into the formulas before the narration moves on." The policy should return a sparse code edit that preserves the scene while making the movie more readable.

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

The hub environment is `harleycooper/math-to-manim` (published at `0.1.1`; a 25-step W&B pilot ran on `Qwen/Qwen3.5-35B-A3B`). The v1.0 environment scaffolding now lives in [`archive/codex-pipeline/environments/`](archive/); integration notes in [`docs/PRIME_INTELLECT_RL.md`](docs/PRIME_INTELLECT_RL.md).

---

## Motion showcase

Sixteen-plus curated GIFs are tracked under [`docs/showcase/assets/`](docs/showcase/assets/) as the **art direction target** for Math-To-Manim's visual explanations.

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

Adjust `-ss` and `-t` to capture the teaching beat you want. That is exactly how every GIF on this page was made.

---

## Repository layout

```text
mythos/            the engine: harness, charter, backends, service, api, mcp_server, cli
mythos/agents/     the six agent charters (markdown — the single source of truth)
examples/mythos/   flagship hand-finished films
tests/             offline test suite (no model calls, no render deps)
docs/              showcase gallery, roadmap, RL notes, assets
scripts/           render bootstrap for Debian/Ubuntu/WSL
archive/           v1.0 typed pipeline, Hermes agent, papers — retired, kept for history
legacy/            the original January 2025 repo, untouched
```

## License

MIT.
