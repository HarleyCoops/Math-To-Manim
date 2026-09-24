# GPT-6 Astra: Codex CLI-native film silo

## Boundary

The Codex-native chain runs independently of the other provider pipelines:

| Silo | Native runtime | Entry point |
|---|---|---|
| `mythos/` | Anthropic charter chain | `math-to-manim` |
| `sol/` | Six durable Codex specialist sessions using GPT-6 Astra | `math-to-manim-sol` |

The Sol silo is not a calculator, web API, or adapter around Mythos. It is a
parallel implementation of the complete Math-To-Manim outcome. It imports no
Mythos prompt, backend, or orchestrator.

## Runtime architecture

```text
math-to-manim-sol run <request>
  -> create isolated runs/sol/<timestamp>-<slug>/ ledger
  -> codex exec --model gpt-6-astra --sandbox workspace-write
     -> infer intent and learner altitude
     -> reverse-map prerequisites
     -> build curriculum and checked math dossier
     -> storyboard the visual argument
     -> author one self-contained Manim CE scene
     -> compile, optionally render, inspect evidence, and repair
  -> application-side artifact, AST, compilation, and render validation
  -> bounded Codex repair pass when validation fails
  -> final manifest
```

The wrapper owns isolation, the output schema, the run ledger, final static
checks, and the repair budget. Each specialist session owns its declared
artifacts. After intent, the curriculum lane and math director can run in
parallel; cinematography joins their outputs before scene composition.
The optional independent Jev session scores the rendered candidate and sends
rejections back through a bounded repair loop. Static validation and the CLI
sandbox reduce risk; they are not a formal security boundary.

## Authentication

The child process removes `OPENAI_API_KEY` from its environment. Authentication
therefore comes only from the Codex CLI's cached ChatGPT session:

```bash
npm ci
# Uses the repository-pinned Codex runtime (0.156.1).
codex login
math-to-manim-sol doctor
```

No API key is accepted or required by the Sol package.

## Reproducible installation

On Ubuntu, Debian, or WSL, one bootstrap command installs the native
Cairo/Pango build headers, TeX and `dvisvgm`, FFmpeg, the complete Python
environment, and the repository-pinned Codex CLI:

```bash
./scripts/bootstrap-sol.sh
.venv/bin/codex login
.venv/bin/math-to-manim-sol doctor
```

The dependency layers are explicit and independently inspectable:

- `requirements-system.txt`: native build and render packages
- `requirements.txt`: core development and offline tests
- `requirements-render.txt`: development plus Manim
- `requirements-sol.txt`: complete Python side of the Sol pipeline
- `package.json` and `package-lock.json`: exact Codex CLI runtime

The bootstrap script uses the local `.venv` and `node_modules` trees and links
the pinned `codex` executable into `.venv/bin`, so activating the environment
makes both `manim` and `codex` discoverable by the Sol harness.

## Run it

```bash
./scripts/bootstrap-sol.sh
source .venv/bin/activate

# Full live production through Codex CLI
math-to-manim-sol run \
  "build a visual proof of why Fourier modes solve the heat equation"

# Ask the same run to render and inspect the film
math-to-manim-sol run \
  "explain parallel transport and holonomy on a sphere" \
  --render -q l --reasoning-effort high --max-repairs 2

# Deterministic contract rehearsal: no model call and no render
math-to-manim-sol run "rehearse the Sol pipeline" --offline

# Inspect the local ledger
math-to-manim-sol runs
```

## Artifact contract

Every run contains:

| Artifact | Purpose |
|---|---|
| `01_intent.json` | audience, scope, desired learning outcome |
| `02_knowledge_map.json` | reverse prerequisite graph |
| `03_curriculum.json` | forward teaching sequence |
| `04_math_dossier.json` | definitions, derivations, examples, checks, sources |
| `05_shot_list.json` | cinematic beats and visual transitions |
| `06_scene_spec.json` | implementable scene contract |
| `sol_scene.py` | one self-contained Manim CE scene |
| `review.json` | validation, render evidence, repairs, limitations |
| `manifest.json` | wrapper-owned status and attempt ledger |

`--offline` writes the same shape so plumbing and release checks never need a
model login, network request, or render installation.

## Why this split

Provider-native silos can evolve independently. The Anthropic path can retain
its explicit agent charters while Sol can exploit the Codex CLI's long-horizon
tool loop and workspace execution. Shared abstractions are limited to the final
product expectation—an inspectable Manim film bundle—not the provider control
plane.

## Independent Astra review

Use `--render --evaluator astra_review` for a fresh, read-only GPT-6 Astra
review of mathematics and sampled presentation evidence. This legacy option was
previously mislabeled Jev; it does not call TypeSafe. The new primary Astra
pipeline uses [real TypeSafe Jev](JEV.md) at every checkpoint.
