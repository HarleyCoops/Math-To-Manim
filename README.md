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

[![Grok 4.6](https://img.shields.io/badge/Grok-4.6-1d9bf0)](#make-your-first-explainer)
[![Python 3.10](https://img.shields.io/badge/Python-3.10%2B-3b82f6)](https://www.python.org/)
[![Manim CE](https://img.shields.io/badge/Manim-CE-f59e0b)](https://www.manim.community/)
[![License MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

[Featured explainers](#featured-visual-explainers) ·
[What you can ask](#what-can-i-ask) ·
[How the reasoning works](#how-the-reasoning-pipeline-works) ·
[First run](#make-your-first-explainer) ·
[Custom bot](#make-a-custom-bot) ·
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

<p align="center"><em><a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">Watch the complete 79 second visual explainer</a> · <a href="docs/prompts/erdos-1038-off-white-3d.md">Read the complete production prompt</a></em></p>

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

<p align="center"><em><a href="docs/showcase/assets/olin-off-white-3d-space.mp4">Watch the complete Olin visual explainer</a> · <a href="docs/prompts/olin-off-white-3d-space.md">Read the complete production prompt</a> · <a href="examples/mythos/olin_off_white_3d_space.py">Inspect the Manim scene</a></em></p>

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

The public way to run that process is Grok 4.6 through the xAI Responses API.
Grok reads a question or a photographed homework page, works backward from
the core claim, then walks forward into a Manim film.

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

A photographed worksheet is also enough. Pass `--image` and Grok reads the
page, then treats it as a film about one claim.

## How The Reasoning Pipeline Works

The method is reverse thinking. Grok starts from the solved insight and walks
back to what the learner already knows. Only then does it walk forward into
the film. The stages below are that story with Grok names and xAI tools.

1. **Understand the learner.** The `intent` stage names the audience, the
   core claim, the scope, and the one big zoom. If a homework photo is
   attached, Grok uses vision. No code is written here.
2. **Find the missing prerequisites.** The `cartographer` builds a reverse
   knowledge tree. Depth 0 is the target claim. Edges are prerequisites.
   The spine starts at assumed foundations. Optional web search is allowed
   only for a canonical name, never for a lesson plan.
3. **Build the teaching sequence.** The `curriculum` stage is the first
   forward pass. Each act teaches one idea and hands a question to the next.
   This stage uses no tools.
4. **Choose the mathematics.** The `math-director` must use the code
   interpreter to solve homework and physics numbers, check units, and
   verify LaTeX. Web search is allowed only for a cited constant.
5. **Plan the visuals.** The `cinematographer` writes the shot list and
   generates one to three art direction stills. X search is only a visual
   seed, never a source for the math.
6. **Compose the Manim scene.** The `composer` writes a `ThreeDScene`
   contract and the Python file. Camera moves use `move_camera` or
   `set_camera_orientation` only. Grok calls a local verify function
   before the file is trusted.
7. **Validate the result.** The harness checks the reverse tree, code
   structure, and camera rules.
8. **Render, inspect, and repair.** Produce the explainer, review the
   evidence, and correct visible defects.

A worksheet is a film about one claim. Solved numbers come from the sandbox.
Use 3D when space is the idea.

## Make Your First Explainer

```bash
python -m venv .venv
pip install -e ".[dev,grok,render]"
export XAI_API_KEY=your_xai_key
math-to-manim-grok doctor
```

Doctor checks that `XAI_API_KEY` is set. It never prints the key. It also
reports the model (`grok-4.6` by default) and the reasoning effort.

A login free rehearsal of the same path writes a full run with zero xAI
calls. Use this in CI:

```bash
math-to-manim-grok run "the heat equation" --offline
```

That writes `runs/grok/<timestamp>-the-heat-equation/grok_scene.py`,
`validation.json`, `traces/`, and `manifest.json`.

A live run actually calls Grok:

```bash
math-to-manim-grok run "the heat equation"
math-to-manim-grok run "A 3 kg cart at 4 m/s hits a spring k=200. How far does it compress?"
math-to-manim-grok run "solve the problem on this page" --image homework.jpg
```

Add `--render -q l` after `pip install -e ".[render]"` if you want the MP4
inside that same run directory.

Get an API key from [xAI](https://docs.x.ai/developers/models/grok-4.6).
Optional environment variables are `XAI_MODEL` and `XAI_REASONING_EFFORT`
(`low`, `medium`, `high`, or `xhigh`).

## Make A Custom Bot

The product is the stage charters in `grok/agents`. Edit those markdown
files to change what the film argues, how reverse thinking works, which
xAI tools a stage may call, and the JSON each stage must emit.

A custom bot just for Manim explainer videos is a charter edit, not a new
application. Keep reverse thinking intact: cartography stays reverse,
curriculum stays the first forward pass, and the sandbox still owns the
numbers. Then run `math-to-manim-grok` as usual.

Read the [Grok 4.6 silo contract](docs/GROK_4_6_SILO.md) for the tool map,
artifact list, and forbidden moves.

---

## Installation

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv
pip install -e ".[dev,grok,render]"
python -m pytest -q
```

Run `math-to-manim-grok doctor` before a live request so a missing key
appears immediately.

Static checks parse `MathTex` and `Tex` fragments in process. If `chktex`
is on `PATH`, the verifier also consults it. If `M2M_LATEX_DEEP_CHECK` is
set and `lualatex` is on `PATH`, fragments are compiled with
`lualatex --halt-on-error --interaction=nonstopmode`. Both tools are
optional and not required for `pytest`.

## Run Artifacts

Every run keeps its reasoning, scene source, validation evidence, thinking
traces, tool calls, and manifest inside the repository. Grok writes to
`runs/grok/`. Open the intermediate JSON when you want to understand or
revise how the explainer was built.

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

## Configuration

Grok reads configuration from the environment or a local `.env` file.

| Variable | Default | Purpose |
|---|---|---|
| `XAI_API_KEY` | unset | Authenticates live Responses API calls |
| `XAI_MODEL` | `grok-4.6` | Selects the Grok model |
| `XAI_REASONING_EFFORT` | `high` | Sets thinking depth (`low` `medium` `high` `xhigh`) |
| `XAI_BASE_URL` | `https://api.x.ai/v1` | Selects the xAI endpoint |
| `XAI_TIMEOUT` | `900` | Sets the model call budget in seconds |

## Testing

```bash
python -m pytest -q
math-to-manim-grok run "the heat equation" --offline
```

Offline runs validate the complete artifact shape without model calls or an
expensive render. Pytest never calls xAI.

## More From The Project

The [motion showcase](docs/showcase/README.md) preserves every visual study and
older animation. The [Prime Intellect notes](docs/PRIME_INTELLECT_RL.md)
describe reinforcement learning work for visual repair. The
[roadmap](docs/ROADMAP.md) tracks future work. The [agent guide](AGENTS.md)
defines repository boundaries and verification rules. Related work on a
different architecture lives at [Kimi K3 Manim](https://github.com/HarleyCoops/KimiK3Manim).

## Repository Layout

```text
grok/              Grok 4.6 reasoning chain, xAI client, and CLI
grok/agents/       Stage charters: thinking, tools, JSON, forbidden moves
docs/GROK_4_6_SILO.md
docs/showcase/     Complete visual archive
tests/             Offline repository tests
runs/              Local reasoning and render artifacts
```

## License

[MIT](LICENSE).
