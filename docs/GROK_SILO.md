# Grok silo

`grok/` is the xAI-native Math-To-Manim chain. It does not import Astra,
Mythos, Sol, GLM, or MiMo. The default model for every stage is `grok-4.7`.
Change it with `XAI_MODEL` or `--model`. There is no separate composer model.

Pricing and model limits change. Check the live pages rather than this file:

- https://docs.x.ai/docs/models/grok-4.7
- https://docs.x.ai/docs/guides/tools/overview

## Entry points

| Command | What it does |
|---|---|
| `math-to-manim-grok run` | brief through scene, then optional render |
| `math-to-manim-grok resume <run-id>` | reuse accepted stages whose hashes still match |
| `math-to-manim-grok render-existing <run-id>` | render a saved scene with zero model calls |
| `math-to-manim-grok login` | run `grok login` (add `--device-auth` when there is no browser) |
| `math-to-manim-grok doctor` | report the auth source; never print a key or token |
| `math-to-manim-grok serve-mcp` | stdio or HTTP MCP on port 8643 |

`math-to-manim serve-mcp` is the Astra server. The older Mythos command
`math-to-manim-mythos serve-mcp` still re-exports this Grok server.

```bash
math-to-manim-grok run "the heat equation" --backend xai-api
math-to-manim-grok run "Pythagorean theorem" --backend offline
math-to-manim-grok serve-mcp --transport http --port 8643
```

## Authentication

Two paths, and no custom OAuth client:

| Path | Backend | Credential |
|---|---|---|
| xAI API key | `--backend xai-api` (default) | `XAI_API_KEY` in the environment or a local `.env` |
| Grok login | `--backend grok-build` | cached `grok login` session (`~/.grok/auth.json` is detected, never read aloud) |

On the Grok Build backend, a missing session falls back to `XAI_API_KEY`,
which is the CLI's own precedence. The key is never placed on the command
line. `doctor` prints `auth_source=xai-api-key` or `auth_source=grok-login`.

## Evidence loop

Each stage returns JSON. The client asks the Responses API for
`text.format` json_schema when `GROK_STRUCTURED_OUTPUTS` is on (the default).
The reply is always checked against a pydantic schema. A bad reply gets one
corrective retry. If the API rejects a parameter or tool with HTTP 400, that
parameter or tool is removed and the call is retried once. The trace records
the warning.

After each stage an independent Grok audit returns `{verdict, evidence,
repair_stage}`. `--review advisory` (the default) keeps the audit and does
not regenerate. `--review gated` sends a failure back to the earliest
responsible stage, at most `--max-revisions` times (default 2). `--review off`
skips the auditor and is labeled `not_reviewed`.

Accepted stages are SHA-256 bound in `ledger.json`. `resume` calls the model
only for stale stages. `render-existing` does not call the model.

Rendering, when requested:

1. AST allowlist: imports are only `manim`, `numpy`, and `math`; one
   `ThreeDScene` whose name ends in `Journey` or `Story` (or `GROK_SCENE_CLASS`).
2. Final-frame probe.
3. Full render with `--render-timeout` (default 2 hours). The child
   environment drops every variable whose name contains `API_KEY`, `SECRET`,
   `TOKEN`, or `PASSWORD`, so `XAI_API_KEY` never reaches Manim.
4. ffprobe duration check, default 20–240 seconds (`--min-duration`,
   `--max-duration`).
5. Twelve frames and a contact sheet.
6. A Grok vision review that must cite those frame filenames.

Static screening is not a sandbox. It only rejects a short list of imports
and calls before a local process runs the scene.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `XAI_API_KEY` | unset | API-key auth. Never printed. Never passed to Manim. |
| `XAI_MODEL` | `grok-4.7` | Model for every stage |
| `XAI_REASONING_EFFORT` | `high` | `low`, `medium`, `high`, or `xhigh` when the model allows it |
| `XAI_BASE_URL` | `https://api.x.ai/v1` | Responses API origin |
| `XAI_TIMEOUT` | `900` | Seconds for one model call |
| `GROK_STRUCTURED_OUTPUTS` | on | Send `text.format` json_schema |
| `GROK_SCENE_CLASS` | unset | Require this scene class name instead of the Journey/Story suffix |
| `GROK_AUTH_FILE` | `~/.grok/auth.json` | Login file to detect, not to print |
| `M2M_RUNS_DIR` | unset | Parent of `grok/` run directories. Unset uses `./runs/grok` from the working directory |

Runs are not written under the repository root unless that is the working
directory. `prompt_cache_key` is `<run-id>:<stage>`.

## MCP

`math-to-manim-grok serve-mcp` exposes the existing seven tools plus
`m2m_resume_run` and `m2m_render_existing`. Job records are JSON files under
the runs directory, so `m2m_get_job` still works after a restart.

## Offline

`--backend offline` or `--offline` writes the artifact bundle with zero model
calls. Pytest and CI use that path. Nothing in the test suite calls xAI or
the `grok` CLI.
