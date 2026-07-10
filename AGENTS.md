# Agent guide

Guidance for AI agents (and humans) working in this repository.

## What this repo is

Math-To-Manim contains provider-native silos. The established `mythos/` product
is the Anthropic-native six-agent chain driven by Claude Fable 5. The parallel
`sol/` product is a GPT-5.6 Sol-native calculator using the Responses API,
hosted Python, a strict typed result, and deterministic Manim compilation.
Do not route one provider through the other provider's orchestration layer.

## Layout

| Path | Role |
|---|---|
| `sol/` | Independent GPT-5.6 Sol silo: client, contracts, fallback, compiler, service, API, CLI |
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
| `archive/`, `legacy/` | Retired code. Do not import from it; do not "fix" it. |

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

## Quick verification

```bash
pip install -e ".[dev]"
pytest                                        # 29 tests, offline
math-to-manim run "the heat equation" --offline
math-to-manim serve-api &  curl localhost:8642/health
```
