# GLM-5.3-Flash Silo

The `src/glm/` package is the provider-native Math-To-Manim silo for
**GLM-5.3-Flash** (Z.ai). It talks only to Z.ai's OpenAI-compatible Coding
Plan endpoint and never routes through, or imports from, `src/mythos/`, `src/sol/`,
or `src/grok/`.

## Wire contract

- **Endpoint** — `POST https://api.z.ai/api/coding/paas/v4/chat/completions`
- **Model** — `glm-5.3-flash` (override with `GLM_MODEL`)
- **Thinking** — always `{"type": "enabled"}`; every call in this silo keeps
  the thinking block on. GLM surfaces reasoning as `reasoning_content`, which
  the client captures into stage traces.
- **Reasoning effort** — `low | high | max`, chosen per run (`--reasoning-effort`,
  default from `GLM_REASONING_EFFORT`, else `high`). The chat/completions body
  has no effort enum, so effort maps to sampling latitude plus a token budget:
  temperature `{0.15, 0.65, 0.9}` and max tokens `{2048, 6144, 12288}`
  (`src/glm/models.py`). One client serves any number of runs; nothing on it
  is mutated per request.
- **Auth** — key resolved from `ZHIPU_API_KEY`, then `ZAI_API_KEY`, then an
  OpenCode `auth.json` entry named `zai-coding-plan`
  (`~/.local/share/opencode/auth.json`, override with `OPENCODE_AUTH_JSON`).
  A client built with an explicit `api_key` reads neither. The key is never
  printed, logged, or echoed in errors (`redact_secret` scrubs any response
  body that might contain it).
- **Environment** — read in one place, `GlmSettings.from_env()`, at call
  time: `GLM_MODEL`, `GLM_BASE_URL`, `GLM_REASONING_EFFORT`, `GLM_TIMEOUT`
  (seconds, default 600) and the key variables above.

## Pipeline (live)

```
intent → cartographer → curriculum → math-director → cinematographer → composer → verify → optional render
```

The stage table `STAGES` in `src/glm/stages.py` is the single source of
stage order and behaviour: each `Stage` names its charter file under
`src/glm/agents/`, the artifact it writes, the server-side abilities its
prompt may mention (`web_search`, `code_interpreter`; advisory text only, so
runs remain reproducible from artifacts alone), the local function tools it
may call, whether it receives the attached image (intent), how its JSON is
normalized and checked before it is saved (cartographer: reverse-tree
contract, failing the run on the spot), and whether it must also hand back
the scene (composer). The bundle contract, prompts and traces all derive
from this table.

Each stage receives upstream artifacts in the user turn and must answer with
one JSON object. The chat/completions tool surface exposes exactly one local
function, `verify_scene(source)` (`src/glm/tools.py`, schema and handler
together); the composer calls it on its own output. After the chain the
harness verifies `glm_scene.py` itself and, while it fails and repairs
remain (`--max-repairs`, default 2), asks the composer to repair it.

Artifacts land in `runs/glm/<timestamp>-<slug>/` under the current working
directory (`GlmHarness(runs_dir=...)` to choose another place):

| File | Stage |
|---|---|
| `01_intent.json` | intent |
| `02_knowledge_map.json` | cartographer (reverse tree: depth 0 target, prerequisite edges, assumed spine start) |
| `03_curriculum.json` | curriculum |
| `04_math_dossier.json` | math-director |
| `05_shot_list.json` | cinematographer |
| `06_scene_spec.json` + `glm_scene.py` | composer |
| `request.json`, `manifest.json`, `traces/<stage>.json` (+ `.raw.json` live), `traces/repair.json` | harness, as the run proceeds |
| `validation.json` (the final `verify_scene` report), `review.json` | harness, once, when the bundle is complete (validation.json also on failure) |

Progress lines go to stderr; stdout carries only the CLI's output (the run
manifest as JSON).

## Scene contract

- One `ThreeDScene` subclass per file.
- Camera via `set_camera_orientation()` / `move_camera()` only;
  `self.camera.animate` fails validation.
- Paper stage `#f3ecd8`, ink text.
- No `os/subprocess/socket/urllib/requests/httpx/shutil` imports, no
  `eval/exec/open/__import__`.

## Offline path

`m2m-glm run "..." --offline` rehearses the entire chain deterministically —
all six artifacts plus a working `GlmOfflineStory` scene — with zero network
calls (`src/glm/offline.py`). The harness verifies, reviews and manifests an
offline bundle exactly as it does a live one.

## CLI

```
pip install -e '.[render]'
math-to-manim-glm run "explain the magnetic monopole" --offline
math-to-manim-glm run "..." --render -qh --reasoning-effort max
math-to-manim-glm runs --limit 5
math-to-manim-glm status <run_id>
math-to-manim-glm doctor        # live ping; expects pong, never prints the key
m2m-glm ...                     # alias
```

## Module layout

Least volatile first; each module imports only what sits above it.

| Module | Owns |
|---|---|
| `models.py` | `RunRequest`, `RunManifest`, bundle file names, effort tables, paper colour |
| `jsonutil.py` | JSON and scene-source extraction from model text |
| `validation.py` | reverse-tree and scene-source checks (pure functions) |
| `client.py` | `GlmSettings`, `GlmClient` (per-call effort, injectable transport, tool loop), `FunctionTool`, `StageReply` |
| `tools.py` | the `verify_scene` tool |
| `stages.py` | the `STAGES` table, charters, `stage_prompt`, `BUNDLE_FILES` |
| `offline.py` | the deterministic bundle |
| `harness.py` | one run: stages, repairs, render, manifest, validation/review |
| `service.py` | run ledger (`run`, `get_run`, `list_runs`) |
| `cli.py` | `math-to-manim-glm` / `m2m-glm` |

Tests: `tests/test_glm_silo.py` drives the whole chain through a fake
transport (`GlmClient(transport=...)`); nothing touches the network.

## Flagship film

`examples/glm/glm_flash_magnetic_monopole.py` — **The Lone Pole**: Dirac's
quantization argument told geometrically with 3D StreamLines, TexturedSurface,
SurfaceMesh, and composite prism flux tubes on the paper stage.
