# GPT-5.6 Sol: Codex CLI-native film silo

## Boundary

Math-To-Manim has two deliberately independent production systems:

| Silo | Native runtime | Entry point |
|---|---|---|
| `mythos/` | Anthropic charter chain | `math-to-manim` |
| `sol/` | One long-horizon Codex CLI run using GPT-5.6 Sol | `math-to-manim-sol` |

The Sol silo is not a calculator, web API, or adapter around Mythos. It is a
parallel implementation of the complete Math-To-Manim outcome. It imports no
Mythos prompt, backend, or orchestrator.

## Runtime architecture

```text
math-to-manim-sol run <request>
  -> create isolated runs/sol/<timestamp>-<slug>/ ledger
  -> codex exec --model gpt-5.6-sol --sandbox workspace-write
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
checks, and the repair budget. Sol owns the film. This keeps model reasoning in
one coherent context while retaining a deterministic trust boundary around the
generated Python and artifacts.

## Authentication

The child process removes `OPENAI_API_KEY` from its environment. Authentication
therefore comes only from the Codex CLI's cached ChatGPT session:

```bash
npm install -g @openai/codex
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
