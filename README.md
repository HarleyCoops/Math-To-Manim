<div align="center">

<a href="https://www.star-history.com/?repos=HarleyCoops%2FMath-To-Manim&type=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&theme=dark&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left&sealed_token=EjITEOSI8nKcGNkepdjUHZ8WTRNOw4dKGtyggkiM_yrNBnjxIr00U2Pgt5DqaUF8Qgx4-WIhM4WdOM2ipFiXTXOJxhJU87yp_iOKrGOHkaIBES1Wrpn1f7i_TMd8chdgnaa09DKge1DJ93Hwe4MmjX0YO1PpzSsDF9ebqWr0MDDTnpRzPNbPUvweMI00" width="100%" />
  </picture>
</a>

# Math To Manim

### Ask a question. Get a visual explainer.

[![Claude Fable 5](https://img.shields.io/badge/Claude-Fable%205%20Mythos-d97757)](#mythos)
[![GPT 5.6 Sol](https://img.shields.io/badge/Codex-GPT--5.6%20Sol-10a37f)](#sol)
[![MCP server](https://img.shields.io/badge/MCP-server-788c5d)](#make-your-first-explainer)
[![Python 3.10](https://img.shields.io/badge/Python-3.10%2B-3b82f6)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE-f59e0b)](https://www.manim.community/)
[![License MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

[Featured explainers](#featured-visual-explainers) ·
[What you can ask](#what-can-i-ask) ·
[How the reasoning works](#how-the-reasoning-pipeline-works) ·
[MCP setup](#make-your-first-explainer) ·
[Native pipelines](#choose-a-native-pipeline) ·
[Technical reference](#installation)

<br />

> *Math To Manim turns a math or physics question into a carefully reasoned
> visual explanation. It finds what the learner needs to know, teaches those
> ideas in order, checks the mathematics, and builds the explanation in Manim.*

<br />

## Featured Visual Explainers

<p align="center">
  <a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">
    <img src="docs/showcase/assets/erdos-1038-potential-landscape.gif" alt="Erdős Problem 1038 appears as an archival three dimensional landscape with a certified valley and endpoint roots" width="90%" />
  </a>
</p>

<p align="center"><strong>ERDŐS 1038: THE POTENTIAL LANDSCAPE</strong></p>

A polynomial is usually introduced as a line of symbols, but it can also be
seen as a landscape made by its roots. Imagine every root pressing into a
flexible sheet stretched above the number line. Taken together, the roots
raise and lower that sheet. The transparent plane in the explainer marks zero.
Wherever the landscape falls beneath it, the polynomial has size less than
one. The footprint under the plane is therefore the exact set whose width the
problem asks us to measure.

That turns the question into something physical. How should the roots be
arranged to make the submerged footprint as narrow as possible, or as wide as
possible? For the narrow side, clusters of roots can be gathered toward their
centres without making the footprint larger. Repeating that idea leads toward
an increasingly fine, one sided distribution of roots. No finite polynomial
quite reaches the limiting shape, but a sequence of them gets arbitrarily
close. Its width is **1.834430475762661…**. This is the certified floor shown
by the curved valley.

The widest case is beautifully simpler. Put the roots at the two endpoints,
−1 and +1, in equal numbers. This produces the family
**f(x) = (x² − 1)ᵐ**, and the region where the polynomial is smaller than one
runs from −√2 to +√2. Its width is therefore **2√2**. The explainer ends by
contrasting two different kinds of extreme: a lower value that can be
approached forever but never attained by a finite polynomial, and an upper
value reached exactly by piling the roots at the endpoints.

<p align="center"><em><a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">Watch the complete 79 second visual explainer</a> · <a href="docs/prompts/erdos-1038-off-white-3d.md">Read the complete Sol production prompt</a></em></p>

<br />

<p align="center">
  <a href="docs/showcase/assets/olin-off-white-3d-space.mp4">
    <img src="docs/showcase/assets/olin-off-white-3d-space.gif" alt="Ten thousand points rise from a flat generative drawing into an off white three dimensional space while preserving the original shadow" width="90%" />
  </a>
</p>

<p align="center"><strong>OLIN: THE SPACE INSIDE A TWEET</strong></p>

A tiny program draws ten thousand points by passing each one through five
linked quantities: \(k\), \(e\), \(d\), \(c\), and \(q\). The final screen
coordinates are only a flat pair,
\((u,v)=(q+40\cos c,\;q\sin c+35d)\). A picture with two coordinates does not
determine one unique object in three dimensions, so the film explores two
different ways to reveal the space suggested by the code.

The first construction is the exact lift
\(E(i,t)=(u,\;40\sin c,\;v)\). It adds a hidden depth coordinate while
leaving \(u\) and \(v\) untouched. Look straight down that hidden direction
and every point lands exactly on the original drawing. This makes \(E\) a
faithful spatial source for the flat shadow.

The film then explores
\(C(i,t)=((40+q)\cos c,\;(40+q)\sin c,\;35d)\). Here \(c\) turns each point
around a vertical axis, \(q\) changes its radius, and \(35d\) sets its height.
This is an alternate cylindrical interpretation, not another exact lift.
Its projection does not reproduce the original drawing. The distinction
matters: \(E\) preserves what the code drew, while \(C\) asks what other
spatial form the same ingredients can suggest.

<p align="center"><em><a href="docs/showcase/assets/olin-off-white-3d-space.mp4">Watch the complete Olin visual explainer</a> · <a href="docs/prompts/olin-off-white-3d-space.md">Read the corrected Mythos production prompt</a> · <a href="examples/mythos/olin_off_white_3d_space.py">Inspect the Manim scene</a></em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/jacobian-conjecture-3d.gif" alt="A deformed coordinate lattice reveals local volume change before the camera pulls back to the global map" width="85%" />
</p>

<p align="center"><em><strong>THE JACOBIAN CONJECTURE.</strong> This explainer separates local certainty from global truth. A small cube becomes a parallelepiped, making the Jacobian determinant visible as local volume change. The camera then pulls back to show why a map can be reversible nearby without being reversible everywhere.</em></p>

<br />

<p align="center"><strong><a href="docs/showcase/README.md">Explore every visual explainer in the motion showcase</a></strong></p>

</div>

---

## What Is Math To Manim

Math To Manim turns a math or physics question into a carefully reasoned visual explanation.
It works backward to identify what the learner needs to know, rebuilds those
ideas in teaching order, checks the mathematics, and animates the explanation
in Manim.

[Manim](https://docs.manim.community/en/stable/) is the open source animation
engine originally created by Grant Sanderson for 3Blue1Brown. It powers many
of the most recognizable math and physics animations online. This project
uses the edition maintained by the Manim community.

The reasoning process is the product. Math To Manim does not jump directly
from a sentence to Python. It first decides what must be understood, what must
be shown, and in what order each idea should appear.

## What Can I Ask

### Middle School Arithmetic

> Explain why a negative number times a negative number becomes positive to
> an eighth grade student. Use a number line, one everyday analogy, and one
> worked example.

### Geometry

> Show why the Pythagorean theorem works without assuming advanced algebra.
> Build the squares on all three sides and rearrange their areas.

### Introductory Algebra

> Teach slope using three ramps. Explain rise over run, compare steepness,
> then solve one line equation.

### High School Physics

> Explain conservation of momentum using two carts that collide. Show the
> momentum arrows before and after impact.

### University Mathematics

> Explain Fourier series as rotating vectors that rebuild a signal. Begin
> with a circle and add one frequency at a time.

### Research Mathematics

> Show why one loop around an exceptional point swaps the eigenvalue branches.
> Assume I know complex numbers but not covering spaces.

### A Useful Prompt Recipe

> Explain [topic] to [learner]. Assume they already know [starting point].
> Use [visual metaphor or physical model]. Work through [specific example].
> End with [summary or check question].

You can name the learner's age, prior knowledge, pace, preferred visual model,
worked example, notation level, and final comprehension check. A simple
homework question is enough. The pipeline expands it into a teaching plan.

## How The Reasoning Pipeline Works

1. **Understand the learner.** Identify the real question, the audience, and
   the intended depth.
2. **Find the missing prerequisites.** Work backward until every branch reaches
   ideas the learner already knows.
3. **Build the teaching sequence.** Walk those ideas forward in the order that
   makes the final concept feel earned.
4. **Choose the mathematics.** Select the definitions, equations, examples,
   and checks that carry the explanation.
5. **Plan the visuals.** Decide what appears on screen, what changes, and where
   the camera guides attention.
6. **Compose the Manim scene.** Turn the teaching plan into complete,
   addressable visual objects and timing.
7. **Validate the result.** Check code structure, mathematical presentation,
   readability, and camera rules.
8. **Render, inspect, and repair.** Produce the explainer, review the evidence,
   and correct visible defects.

## Make Your First Explainer

The easiest path is a conversation with an assistant that can use MCP.

```bash
pip install -e ".[mcp]"
math-to-manim serve-mcp
```

Add the server to your MCP client:

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

Once the server is connected, type this in your assistant:

> Use Math To Manim to create a visual explainer for my eighth grade student.
> Explain why solving an equation means doing the same thing to both sides.
> Use a balance scale, solve 3x + 5 = 20, and end with one practice question.

You do not need to memorize tool names. The assistant starts the explainer.
The assistant reports progress. The assistant can inspect every reasoning artifact.
The final scene and render remain in the local run directory.

## Choose A Native Pipeline

Math To Manim contains two complete and independent ways to create a visual
explainer. Choose the command line account you already use.
Neither pipeline routes through the other.

### Mythos

Mythos uses the Claude CLI and a six agent charter chain. It reasons through
learner intent, prerequisite mapping, curriculum, mathematics, camera
direction, and scene composition.

```bash
math-to-manim doctor --ping
math-to-manim run "Explain fractions with a folding paper model for a sixth grade learner." --render -q m
```

### Sol

Sol uses the logged in Codex CLI and durable specialist stages. Each role saves
its artifact and session so the run can be inspected, resumed, and repaired by
the responsible specialist.

```bash
math-to-manim-sol doctor
math-to-manim-sol run "Explain fractions with a folding paper model for a sixth grade learner."
```

Read the [complete Sol contract](docs/SOL_5_6_SILO.md).

### Kimi

Kimi uses an agent architecture that is different enough to warrant its own repository.
Explore [Kimi K3 Manim](https://github.com/HarleyCoops/KimiK3Manim).

---

## Installation

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv
pip install -e ".[dev,render,mcp,api]"
python -m pytest -q
```

Use `math-to-manim doctor --ping` for Mythos. Use
`math-to-manim-sol doctor` for Sol. Run the appropriate check before a live
request so login and rendering problems appear immediately.

## Run Artifacts

Every run keeps its reasoning, scene source, validation evidence, and manifest
inside the repository. Mythos writes to `runs/mythos/`. Sol writes to
`runs/sol/`. Open the intermediate JSON when you want to understand or revise
how the explainer was built.

The artifacts tell a readable story:

```text
learner intent
      ↓
prerequisite map
      ↓
teaching sequence
      ↓
mathematics and examples
      ↓
visual plan
      ↓
Manim scene
      ↓
validation, render, and repair evidence
```

## MCP Reference

These tools are available to assistants and integrations. A learner can simply
ask for an explainer in ordinary language.

| Tool | Purpose |
|---|---|
| `m2m_create_animation` | Starts the Mythos reasoning chain as a background job |
| `m2m_get_job` | Reports live progress for each reasoning stage |
| `m2m_list_runs` | Lists local runs with the newest first |
| `m2m_get_run` | Returns the manifest and artifact list for one run |
| `m2m_get_artifact` | Reads a reasoning artifact such as the prerequisite map |
| `m2m_get_scene_code` | Returns the generated Manim scene |
| `m2m_cinematic_charter` | Returns the visual composition contract |

For a headless client, use the reference driver:

```bash
python scripts/drive_mcp_pipeline.py "why does a spinning handle flip itself?" --render -q l --log runs/drive.log
```

## REST API

The REST API exposes Mythos for applications and background jobs.

```bash
pip install -e ".[api]"
math-to-manim serve-api
```

OpenAPI documentation is available at `http://127.0.0.1:8642/docs`.

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Reports service health and version |
| `POST` | `/v1/runs` | Submits a prompt and returns a job record |
| `GET` | `/v1/jobs/{job_id}` | Reports queued, running, completed, or failed state |
| `GET` | `/v1/runs` | Lists the local run ledger |
| `GET` | `/v1/runs/{run_id}` | Returns a manifest and artifact listing |
| `GET` | `/v1/runs/{run_id}/artifacts/{name}` | Returns one JSON or Python artifact |

```bash
curl -s -X POST localhost:8642/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "explain Fourier epicycles as rotating vectors", "render": false}'
```

## Configuration

Mythos reads configuration from the environment or a local `.env` file.

| Variable | Default | Purpose |
|---|---|---|
| `M2M_MODEL` | `claude-fable-5` | Selects the baseline model |
| `M2M_MODEL_FALLBACKS` | `claude-opus-4-8,claude-sonnet-5` | Lists models used when the baseline has a model failure |
| `M2M_COMMAND` | `claude` | Selects the explicit backend command |
| `M2M_TIMEOUT` | `900` | Sets the model call budget in seconds |
| `M2M_RENDER_TIMEOUT` | `1800` | Sets the render budget in seconds |
| `M2M_RUNS_DIR` | `runs/` | Selects the local run directory |
| `M2M_MANIM` | automatic | Overrides the Manim executable |

Read the [Sol contract](docs/SOL_5_6_SILO.md) for its Codex CLI login, staged
sessions, resume command, manifest, and environment.

## Testing

```bash
python -m pytest -q
math-to-manim run "the heat equation" --offline
math-to-manim-sol run "the heat equation" --offline
```

Offline runs validate the complete artifact shape without model calls or an
expensive render.

## More From The Project

The [motion showcase](docs/showcase/README.md) preserves every visual study and
older animation. The [Prime Intellect notes](docs/PRIME_INTELLECT_RL.md)
describe reinforcement learning work for visual repair. The
[roadmap](docs/ROADMAP.md) tracks future work. The [agent guide](AGENTS.md)
defines repository boundaries and verification rules.

## Repository Layout

```text
mythos/            Claude CLI reasoning chain, service, API, MCP, and CLI
sol/               Codex CLI specialist pipeline
examples/mythos/   Hand finished Mythos examples
docs/showcase/     Complete visual archive
tests/             Offline repository tests
runs/              Local reasoning and render artifacts
archive/           Retired implementations kept for history
legacy/            Original January 2025 repository material
```

## License

[MIT](LICENSE).
