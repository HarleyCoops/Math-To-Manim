# AGENTS.md

Best-practice instructions for AI coding agents working in this repository. Treat this as the repo-specific companion to `README.md`: humans get the product story there; agents get the operating contract here.

## Project overview

M2M2 is a rewrite of Math-To-Manim: short educational prompts become typed planning artifacts, generated Manim code, optional renders, review outputs, and a reproducible run bundle.

Core promise: story before symbols, geometry before algebra, artifacts before side effects.

Primary package: `math_to_manim`.
Primary CLI entry points: `m2m2` and `math-to-manim`.
Primary runtime path: `math_to_manim/pipeline/runner.py`.
Architecture reference: `docs/ARCHITECTURE.md`.
Human-facing landing page: `README.md`.

## Agent operating principles

Follow these Karpathy-inspired rules in every change:

1. Think before coding.
   - Do not silently assume requirements, architecture, file ownership, or command behavior.
   - Surface ambiguity when it changes implementation choices.
   - Ask for clarification only when genuinely blocked; otherwise choose the smallest safe interpretation and state the assumption.
   - Present tradeoffs when a request has meaningful complexity, safety, or product implications.

2. Simplicity first.
   - Prefer the smallest maintainable change that satisfies the request.
   - Do not add speculative abstractions, broad configurability, background services, new frameworks, or “future-proofing” unless asked.
   - If a solution grows large, stop and look for a smaller cut before continuing.

3. Surgical changes.
   - Touch only files and lines required for the task.
   - Do not opportunistically rewrite comments, formatting, docs, or adjacent code.
   - Match existing style in the file you are editing.
   - Remove imports/functions/files only when your change made them unused, or when the user explicitly asked for cleanup.
   - Mention unrelated dead code in your final notes instead of deleting it.

4. Goal-driven execution.
   - Define success criteria before editing.
   - For bugs, reproduce the failure or add a failing test first when practical.
   - For features, add or update tests around the changed behavior when practical.
   - Verify with exact commands before final response.

## Repository layout

- `math_to_manim/agents/` — stage adapters for intent, graph, curriculum, math, storyboard, scene spec, codegen, static review, render, video review, and publishing.
- `math_to_manim/schemas/` — Pydantic artifact contracts. Treat these as public pipeline interfaces.
- `math_to_manim/pipeline/` — orchestration, tracing, state, and repair loop behavior.
- `math_to_manim/tools/` — deterministic helpers for graph work, AST/static validation, scene discovery, and artifact storage.
- `math_to_manim/rendering/` — Manim, FFmpeg, and render command wrappers.
- `math_to_manim/providers/` — provider-specific integrations such as the Codex CLI bridge.
- `math_to_manim/app/` — optional API/UI surfaces.
- `tests/unit/` — current automated test suite.
- `docs/` — architecture, docs index, showcase, and visual documentation assets.
- `docs/showcase/assets/` — intentionally tracked legacy showcase GIFs used as art-direction targets.
- `scripts/` — operational helper scripts such as render dependency bootstrap.
- `runs/` — generated run bundles; ignored and normally not committed.

## Setup commands

Use the existing local virtual environment when present:

```bash
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Fresh checkout on macOS/Linux/WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Fresh checkout on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Install render extras only when the task requires real Manim rendering:

```bash
python -m pip install -e ".[dev,render]"
./scripts/bootstrap-render.sh  # Debian/Ubuntu/WSL system deps: FFmpeg, LaTeX, etc.
```

## Verification commands

Run the fastest relevant checks before finishing. Prefer the venv-qualified form so results are independent of shell activation:

```bash
./.venv/bin/python -m pytest
./.venv/bin/python -m math_to_manim.cli --help
./.venv/bin/python -m math_to_manim.cli generate --help
./.venv/bin/python -m math_to_manim.cli generate "Explain why derivatives are slopes" --deterministic --no-render --runs-dir /tmp/m2m2-smoke
```

If the CLI entry points are installed in the active environment, these equivalents should also work:

```bash
m2m2 generate "Explain why derivatives are slopes" --deterministic --no-render
math-to-manim generate "Explain why derivatives are slopes" --deterministic --no-render
```

For codegen-provider work, verify Codex separately before blaming M2M2:

```bash
codex --version
codex exec "Say ready from inside this repo"
```

For render work, run a small render-quality smoke only after render dependencies are installed. If a full render is too slow or unavailable, run deterministic no-render plus the relevant unit tests and clearly report the skipped render with the reason.

## Pipeline contracts

A normal generation writes a run bundle under `runs/<run_id>/` with artifacts such as:

- `request.json`
- `intent.json`
- `knowledge_graph.json`
- `curriculum.json`
- `math_packet.json`
- `storyboard.json`
- `scene_spec.json`
- `generated_code.json`
- `generated_scene.py`
- `validation_report.json`
- `render_result.json`
- `review_report.json`
- `animation_package.json`
- `manifest.json`

Rules:

- Preserve artifact names unless the task is explicitly a schema/pipeline migration.
- If you change a schema, update all producers, consumers, tests, and docs that depend on it.
- Deterministic mode must remain offline and reproducible.
- Rendering must stay gated by static validation; failed validation should not invoke Manim.
- Repair loops should operate on the frozen upstream `scene_spec` and recorded stderr/stdout, not rerun all planning.

## Code style and architecture

- Python 3.10+.
- Use Pydantic models for artifact boundaries.
- Keep provider-specific behavior behind stage runners/providers; do not leak OpenAI, Anthropic, Gemini, Kimi, or Codex assumptions into schemas.
- Prefer pure functions and deterministic helpers for validation, graph operations, filesystem packaging, and command construction.
- Keep stage outputs inspectable as JSON.
- Make errors actionable: include command, artifact path, stderr summary, and stage when available.
- Avoid hidden parallelism in the pipeline runner; the documented runtime shape is single-threaded and ordered.
- Do not bypass static review to make rendering “work.” Fix the generated code or the validator contract.

## Testing guidance

- Add or update tests for behavior changes in `tests/unit/`.
- For schema changes, test serialization/validation and at least one pipeline consumer.
- For CLI changes, test argument parsing or run a CLI smoke command.
- For provider changes, mock subprocess/network boundaries where possible; do not require real subscription credentials in unit tests.
- For render changes, isolate command construction and result parsing from actual Manim execution where practical.

## Generated files and assets policy

Do not commit by default:

- `.venv/`, `venv/`
- `.env`, `.env.*`
- `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`
- `runs/`, `.tmp-runs/`
- `media/`, `output/`, `artifacts/`
- generated `*.mp4`, logs, temporary contact sheets, or ad hoc generated GIFs/PNGs

Intentionally tracked exceptions:

- `docs/showcase/assets/*.gif` — curated legacy showcase GIFs from the original Math-To-Manim repo. These are art-direction targets, not current rewrite outputs.
- `docs/assets/pipeline-at-a-glance.svg` — pipeline overview diagram (docs asset).

When touching showcase media:

- Validate the asset exists locally and is not a blank/broken placeholder.
- Prefer visual inspection or representative frame/contact-sheet inspection for new images/GIFs.
- Keep filenames stable when README/showcase links already point to them.
- Update both `README.md` and `docs/showcase/README.md` when changing gallery membership.

## Security and secrets

- Never commit credentials, tokens, API keys, auth headers, `.env` contents, or connection strings.
- Do not print secret values in logs, docs, commits, PR bodies, or final responses.
- Use placeholder examples such as `OPENAI_API_KEY="***"` in documentation.
- If a command needs local credentials, rely on the existing user environment and report values as redacted.
- Generated Manim code should not read arbitrary local files, shell out unexpectedly, access network resources, or write outside its run directory unless explicitly designed and reviewed.

## Hermes skill workflow

This repo is intended for skill-driven Hermes/Codex work. Hermes is contributor tooling, not an M2M2 runtime dependency. Use it to inspect, plan, test, debug, review, and coordinate changes while preserving typed pipeline contracts.

### Install and verify Hermes

Linux/macOS/WSL2:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup
hermes doctor
hermes tools list --summary
hermes skills list
```

Native Windows is not the preferred path for Hermes repo work. Use WSL2 when working on this checkout from Windows.

### Start Hermes for M2M2 work

Preload the smallest skill set that matches the task:

```bash
# General repo inspection / docs accuracy.
hermes --skills codebase-inspection

# Agent instructions and launch docs.
hermes --skills agents-md,codebase-inspection

# Animation concepting, render/GIF work, and visual quality review.
hermes --skills manim-video,systematic-debugging,codebase-inspection

# Larger pipeline or schema work.
hermes --skills writing-plans,test-driven-development,codebase-inspection

# Debugging CLI, schema, provider, render, or generated-code failures.
hermes --skills systematic-debugging,codebase-inspection

# Coordinated multi-agent implementation.
hermes --worktree --skills subagent-driven-development,writing-plans

# Pre-commit review for risky changes.
hermes --skills requesting-code-review,codebase-inspection
```

Single-shot form for scripted checks:

```bash
hermes -z "Inspect this M2M2 repo and verify the README, AGENTS.md, pyproject entry points, and CLI smoke command agree." \
  --skills codebase-inspection,agents-md
```

### Skill map for this repository

- `agents-md` — update this file or other agent operating instructions.
- `manim-video` — design, critique, harden, render, and GIF-export Manim explanations.
- `codebase-inspection` — verify claims against `pyproject.toml`, CLI help, tests, docs, and actual files.
- `writing-plans` — plan feature work, schema migrations, provider changes, render behavior changes, and docs restructures.
- `test-driven-development` — add behavior around stage adapters, schemas, CLI flags, static validation, and repair loops.
- `systematic-debugging` — diagnose failures in deterministic runs, model-backed runs, Codex CLI provider calls, Manim renders, and artifact handoffs.
- `subagent-driven-development` — split larger tasks across file-boundary-safe workers, e.g. one for schemas/tests, one for CLI, one for docs.
- `requesting-code-review` — request review before committing schema/provider/security/render changes.
- `github-pr-workflow` — commit, push, create/update PRs, and verify remote state when the user asks.
- `codex` — use when working specifically on the Codex CLI-backed codegen provider or Codex developer workflow.

### If a skill is missing

Check and inspect before installing anything new:

```bash
hermes skills list
hermes skills search <query>
hermes skills inspect <identifier>
hermes skills install <identifier>
hermes skills audit
```

Do not vendor Hermes skills into this repo unless the user explicitly asks. Do not commit local skill caches or session-only plans.

### Hermes-specific pitfalls

- Do not use `--ignore-rules` for normal repo work; it skips `AGENTS.md` and can bypass this operating contract.
- Avoid `--yolo` unless the user explicitly accepts the risk; it bypasses dangerous-command approval prompts.
- Prefer `--worktree` for parallel agents that may edit overlapping files.
- Hermes credentials live outside the repo, usually under `~/.hermes/`; never copy them into `.env`, docs, commits, logs, or PR text.
- M2M2 model credentials such as `OPENAI_API_KEY` should be shown only as redacted placeholders.
- Generated `runs/`, Manim `media/`, temporary renders, contact sheets, and ad hoc GIFs/PNGs should not be committed unless the user explicitly requests a curated docs asset.
- Do not conflate Hermes skills with M2M2 runtime dependencies. The package dependencies are defined in `pyproject.toml`; Hermes should not be imported by M2M2 code.

### Hermes planning files

Hermes planning files may live under `.hermes/plans/` when explicitly useful. A plan should include task scope, skills used, expected file changes, artifact/schema contracts affected, acceptance criteria, verification commands, known risks, and rollback notes.

Do not commit stale or session-only plans unless the user asks to preserve them.

## Documentation rules

- Keep `README.md` polished and human-facing.
- Keep `AGENTS.md` operational and agent-facing.
- Keep `docs/ARCHITECTURE.md` aligned with actual runtime behavior.
- Keep `docs/showcase/README.md` aligned with local showcase assets.
- If commands in README and AGENTS diverge, inspect the code/config and resolve the mismatch rather than guessing.

## Git and PR guidance

- Work on a focused branch.
- Keep commits scoped to the request.
- Use conventional commit messages such as `docs: add agent operating guide` or `fix: repair deterministic pipeline smoke`.
- Before committing, run relevant checks and inspect:

```bash
git status --short
git diff --check
git diff --stat
```

- For GitHub-visible README/docs/assets changes, push and verify the remote branch/PR when requested.
- Report final status with exact commands run, changed files, and any skipped checks with reasons.

## Stop conditions

Stop and ask or escalate if:

- Requirements conflict with existing pipeline contracts.
- A change would require committing secrets, large generated media, or local-only artifacts.
- Tests fail for reasons unrelated to your change and fixing them would require broad refactoring.
- You cannot verify a requested render or media change because required local dependencies are missing.
