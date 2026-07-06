# Archive

Everything in this directory is **retired, kept for history**. Nothing here is
imported by the live package (`mythos/`), installed by `pip install`, or
exercised by CI. It is preserved because the reasoning traces, evals, and
provider experiments document how Math-To-Manim evolved from a one-shot R1
prompt into the Mythos chain.

| Directory | What it was |
|---|---|
| `codex-pipeline/` | The v1.0 typed pipeline: OpenAI Agents SDK stage agents (`math_to_manim/`), its unit tests, prompt evals, the Prime Intellect RL environment scaffolding, prompts, and tools. Superseded by the Mythos 6-agent chain in v1.1. |
| `hermes/` | The Hermes contributor/operator agent and its repo-local skills. Operator work now happens through Claude-native tooling (Claude Code / Cowork). |
| `papers/` | Reference papers that inspired animations. |
| `assets/` | Retired hero images. |
| `notes/` | Odds and ends from the early days. |
| `local/` | (gitignored) Local experiment output that never belonged in the repo. |

The original January 2025 repository — the R1-era one-shot prompt collection —
lives one level up in [`legacy/`](../legacy/), untouched, as it has since v1.0.

If you need the old CLI back:

```bash
git checkout v1.0.0
pip install -e ".[dev]"
python -m math_to_manim.cli --help
```
