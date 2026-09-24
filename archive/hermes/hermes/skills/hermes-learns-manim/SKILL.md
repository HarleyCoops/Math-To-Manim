---
name: hermes-learns-manim
description: "Operate Math-To-Manim with Hermes: inspect artifacts, run deterministic checks, use Codex-backed codegen, render/review Manim outputs, and avoid committing generated media."
version: 1.0.0
author: HarleyCoops + Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [math-to-manim, manim, m2m2, hermes, codex, animation, artifacts]
---

# Hermes Learns Manim

Use this skill when operating the Math-To-Manim repo with Hermes to inspect,
generate, validate, render, or review educational Manim animations.

## Operating Contract

- Read `README.md` and `AGENTS.md` before editing.
- Treat Hermes as contributor tooling, not a Python runtime dependency.
- Keep M2M2 artifacts inspectable under `runs/<run_id>/`.
- Keep user-visible render/demo outputs in repo-local `runs/`; use `.tmp-runs/`
  only for disposable smoke checks, and do not send user-facing movies to `/tmp`.
- Preserve the pipeline contract: story before symbols, geometry before algebra,
  artifacts before side effects.
- Prefer deterministic no-render checks before model-backed or render-heavy runs.
- Do not commit generated `runs/`, `media/`, temporary renders, secrets, or local caches.
- For showcase/media changes, visually inspect representative frames/GIFs before
  claiming success.

## Quick Verification

From the repo root:

```bash
./.venv/bin/python -m math_to_manim.cli --help
./.venv/bin/python -m math_to_manim.cli generate --help
./.venv/bin/python -m math_to_manim.cli generate "Explain why derivatives are slopes" --deterministic --no-render --runs-dir .tmp-runs/m2m2-smoke
```

If the venv is not installed yet:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e ".[dev]"
```

For Codex-backed code generation, first verify the local Codex CLI:

```bash
codex --version
codex exec "Say ready from inside this repo"
```

## Starter Workflow

1. Inspect `pyproject.toml`, `math_to_manim/cli.py`, and
   `math_to_manim/pipeline/runner.py`.
2. Run CLI help or a deterministic smoke command before changing behavior.
3. Open the generated `runs/<run_id>/` bundle and inspect JSON artifacts before
   changing downstream code.
4. For media work, render only after static validation passes and inspect the
   output visually.
5. Report exact commands, run bundle paths, skipped checks, and changed files.

## Status

This skill is archived. It is not a supported generate path. The live
first animation flow is in the repository `README.md` (Mythos CLI, Sol
CLI, or `math-to-manim serve-mcp`). There is no `hermes/skills/` directory
at the repo root. If you still have a local Hermes install and want to
load this archived skill for inspection only:

```bash
hermes config set skills.external_dirs "$(pwd)/archive/hermes/hermes/skills"
hermes skills list --source local
hermes --skills hermes-learns-manim
```

Do not expect `initialize_run_workspace` or `output/<run>/scene.py`. Live
runs write `runs/mythos/<run>/mythos_scene.py` and seed
`runs/mythos/<run>/validation.json` as the canonical validation artifact.

Env vars are documented in the README Configuration table (`M2M_MODEL`,
`M2M_COMMAND`, `M2M_TIMEOUT`, `M2M_RENDER_TIMEOUT`, `M2M_RUNS_DIR`,
`M2M_MANIM`, `M2M_PREREQ_CACHE_TTL_DAYS`, `M2M_LATEX_DEEP_CHECK`). There
is no Hermes `config.py` in this repository.

For full repo instructions, see `README.md` and `AGENTS.md`.
