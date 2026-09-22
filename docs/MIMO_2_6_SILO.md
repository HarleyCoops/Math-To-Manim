# MiMo 2.6: tool-calling film silo

## Boundary

| Silo | Native runtime | Entry point |
|---|---|---|
| `mythos/` | Anthropic charter chain | `math-to-manim` |
| `sol/` | Codex CLI / GPT-5.6 Sol | `math-to-manim-sol` |
| `grok/` | xAI Responses API | `math-to-manim-grok` |
| `glm/` | Z.ai chat/completions | `math-to-manim-glm` |
| `mimo/` | **MiMo 2.6 tool calling** | `math-to-manim-mimo` |

The MiMo silo is an independent implementation of the complete Math-To-Manim
outcome. It imports no Mythos prompt, backend, or orchestrator and does not
import Sol, Grok, or GLM clients.

**Product difference:** every specialist stage is a *tool-using* agent. It must
call `write_artifact` to persist outputs, `verify_scene` before declaring a
scene done, and `verify_geometry` before asserting twist parity, frame
orthonormality, or which loops shrink. Reverse thinking is a first-class
contract for the cartographer stage (reverse knowledge tree).

## Runtime architecture

```text
math-to-manim-mimo run <request>
  -> create isolated runs/mimo/<timestamp>-<slug>/ ledger
  -> for each stage: OpenAI-compatible chat/completions with tools
     intent -> cartographer (reverse tree) -> curriculum
                 \\-> math-director -/
                      cinematographer -> scene-composer
     each stage: tool loop (write_artifact / read_artifact / verify_*)
  -> application-side artifact + AST validation
  -> bounded scene-composer repair when validation fails
  -> optional wrapper-owned manim render
  -> final manifest
```

## Tool surface (MiMo 2.6 capability multiplier)

| Tool | Purpose |
|---|---|
| `write_artifact` | Persist JSON/Python into the run directory (sandboxed) |
| `read_artifact` | Load upstream artifacts |
| `list_artifacts` | Inspect the run ledger |
| `record_decision` | Append design decisions to `decisions.json` |
| `verify_geometry` | Sample ribbon/frame/twist constraints; return parity + diagnostics |
| `verify_scene` | AST + compile check of Manim source (camera rule enforced) |

Handlers never use the network. Path writes are confined to the run directory.

## Authentication

```bash
export MIMO_API_KEY=...          # or MIMO_CODE_API_KEY
export MIMO_BASE_URL=http://127.0.0.1:8642/v1   # MiMoCode OpenAI-compatible
export MIMO_MODEL=mimo-2.6
math-to-manim-mimo doctor
```

Keys are never printed. Offline mode needs no key:

```bash
math-to-manim-mimo run "rehearse the MiMo pipeline" --offline
```

## Flagship creative exercise

`examples/mimo/the_second_turn.py` is the first MiMo-native 3-space film:

- **Concept:** clamped belt / spinor double cover / π₁(SO(3)) ≅ ℤ/2  
- **Method:** reverse knowledge tree (see `docs/prompts/the-second-turn-mimo26.md`)  
- **Novelty:** pure room-geometry 3D; not present in prior showcase material  
- **Scene class:** `TheSecondTurn` (`ThreeDScene`)

```bash
manim -ql examples/mimo/the_second_turn.py TheSecondTurn
```

## Run it

```bash
pip install -e ".[dev,render]"
math-to-manim-mimo doctor
math-to-manim-mimo run \
  "In a dark studio, show that a clamped belt is stuck after 360° and free after 720°" \
  --reasoning-effort max

math-to-manim-mimo run "..." --render -q l --max-repairs 2
math-to-manim-mimo runs
```

## Artifact contract

Every run contains `01_intent.json` … `06_scene_spec.json`, `mimo_scene.py`,
`validation.json`, `manifest.json`, and stage traces under `stages/` including
tool-call logs.
