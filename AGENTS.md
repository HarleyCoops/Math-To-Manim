# Agent guide

Guidance for AI agents (and humans) working in this repository.

## What this repo is

Math-To-Manim turns a natural-language prompt into a rendered Manim film through a
six-role reasoning chain, and carries the RL and evaluation substrate used to
improve that chain over time.

Math-To-Manim contains provider-native silos. The established `mythos/` product
is the Anthropic-native six-agent chain driven by Claude Fable 5. The parallel
`sol/` product is a complete GPT-5.6 Sol-native film pipeline driven only by
the Codex CLI and its cached ChatGPT login. It does not use an API key, an HTTP
model endpoint, or Mythos orchestration.
Do not route one provider through the other provider's orchestration layer.

## Layout

| Path | Role |
|---|---|
| `sol/` | Independent GPT-5.6 Sol silo: Codex CLI driver, film contract, harness, validation, run ledger |
| `docs/SOL_5_6_SILO.md` | Sol architecture and deployment contract |
| `mythos/agents/*.md` | The six agent charters (single source of truth; mirror to `.claude/agents/` for native Claude Code use) |
| `mythos/harness.py` | Chain runner: intent → cartographer → curriculum → math-director → cinematographer → scene-composer → codegen → verify → render → repair |
| `mythos/charter.py` | The Cinematic Charter + parsing utilities |
| `mythos/backends.py` | Model backends: Claude CLI (default), Codex CLI, OpenAI-compatible HTTP |
| `mythos/cinematography.py` | The visual grammar library scenes import |
| `mythos/service.py` | Job orchestration shared by all front doors |
| `mythos/api.py` | REST API (FastAPI) — `math-to-manim serve-api` |
| `mythos/mcp_server.py` | MCP server (FastMCP) — `math-to-manim serve-mcp` |
| `mythos/cli.py` | The `math-to-manim` command |
| `examples/mythos/` | Flagship hand-finished films (QFT, Sound of Spacetime) |
| `docs/showcase/` | Curated GIF gallery — the art-direction target |
| `tests/` | Offline test suite (no model calls, no render needed) |
| `archive/codex-pipeline/` | Prime Intellect Verifiers RL environment, static reward scoring, and prompt eval suite |
| `archive/paper_visualizations/` | Rendered paper-to-film corpora used as reference and eval material |
| `legacy/Math-To-Manim/` | Prior-generation pipelines (KimiK2.5Swarm, Gemini3) kept for RL and comparison work |

## Archive and legacy

`archive/` and `legacy/` are not dead weight. They hold the reinforcement-learning
and evaluation substrate for this project, plus the prior-generation pipelines the
current silos are measured against:

| Path | What it holds |
|---|---|
| `archive/codex-pipeline/environments/math_to_manim/` | `m2m2_visual_repair`, a Verifiers RL environment: `environment.py`, `scoring.py` (weighted static reward over format, schema, parse, static validation, safety, acceptance terms, and layout risk), training/inference/orchestration configs, and `data/repair_tasks.jsonl` |
| `archive/codex-pipeline/evals/prompt_suite.yaml` | Rubric-scored prompt eval cases (concept coverage, prerequisite ordering, visual feasibility, narrative alignment, artifact contract) |
| `archive/codex-pipeline/prompts/`, `math_to_manim/` | The staged artifact schemas and prompts those evals score against |
| `archive/paper_visualizations/` | Rendered film corpora — reference output and eval material |
| `legacy/Math-To-Manim/` | Earlier provider pipelines retained for RL baselines and cross-generation comparison |

Rules for working in them:

1. **Do not import `archive/` or `legacy/` from `mythos/` or `sol/`.** The runtime
   path stays clean; the RL and eval code depends on the silos, never the reverse.
2. **Do not casually refactor them.** Reward functions and task datasets are
   experiment inputs — changing scoring silently invalidates prior runs. Version
   the schema instead of editing in place.
3. **Their artifact schemas have drifted** from what `mythos/` and `sol/` emit
   today. Treat that gap as real work to be done deliberately, not a bug to patch
   on the way past.

## Working rules

1. **Runs are cheap, renders are not.** `--offline` exercises the whole chain
   deterministically with zero model calls; use it for plumbing changes.
2. **Charters are the product.** Behavior changes in the chain usually belong
   in `mythos/agents/*.md`, not in harness code.
3. **ThreeDScene camera rule:** `move_camera()` / `set_camera_orientation()`,
   never `.animate` on `self.camera`. The static verifier enforces this.
4. **Artifacts land in `runs/mythos/<ts>-<slug>/`** — keep them repo-local
   (never `/tmp`) so humans can inspect them.
5. **Tests must pass offline:** `pip install -e ".[dev]" && pytest`.
6. **Keep the README's showcase GIFs and star chart intact** in any docs work.
7. **Keep provider silos native.** `sol/` must not import Mythos prompts,
   backends, or orchestration; `mythos/` must not import the Sol client.
8. **Sol is CLI-only.** Do not add an HTTP API, Responses API client, API-key
   fallback, or calculator-specific compiler to `sol/`.

## Quick verification

```bash
pip install -e ".[dev]"
pytest                                        # 29 tests, offline
math-to-manim run "the heat equation" --offline
math-to-manim serve-api &  curl localhost:8642/health
math-to-manim-sol run "why Fourier modes solve the heat equation" --offline
math-to-manim-sol doctor
```
