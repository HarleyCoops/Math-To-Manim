# GLM-5.3-Flash Silo

The `glm/` package is the provider-native Math-To-Manim silo for
**GLM-5.3-Flash** (Z.ai). It talks only to Z.ai's OpenAI-compatible Coding
Plan endpoint and never routes through, or imports from, `mythos/`, `sol/`,
or `grok/`.

## Wire contract

- **Endpoint** — `POST https://api.z.ai/api/coding/paas/v4/chat/completions`
- **Model** — `glm-5.3-flash` (override with `GLM_MODEL`)
- **Thinking** — always `{"type": "enabled"}`; every call in this silo keeps
  the thinking block on. GLM surfaces reasoning as `reasoning_content`, which
  the client captures into stage traces.
- **Reasoning effort** — `low | high | max`. The chat/completions body has no
  effort enum, so effort maps to sampling latitude plus a token budget:
  temperature `{0.15, 0.65, 0.9}` and max tokens `{2048, 6144, 12288}`
  (`glm/models.py`).
- **Auth** — key resolved from `ZHIPU_API_KEY`, then `ZAI_API_KEY`, then an
  OpenCode `auth.json` entry named `zai-coding-plan`
  (`~/.local/share/opencode/auth.json`). The key is never printed, logged, or
  echoed in errors (`redact_secret` scrubs any response body that might
  contain it).

## Pipeline (live)

```
intent → cartographer → curriculum → math-director → cinematographer → composer → verify → optional render
```

Each stage reads its charter from `glm/agents/*.md`, receives upstream
artifacts in the user turn, and must answer with one JSON object. The chat/
completions tool surface exposes exactly one local function,
`verify_scene(source)`; the composer calls it on its own output and repairs
until it passes. Server-side abilities (web research, sandbox) stay advisory
prompt text so runs remain reproducible from artifacts alone.

Artifacts land in `runs/glm/<timestamp>-<slug>/`:

| File | Stage |
|---|---|
| `01_intent.json` | intent |
| `02_knowledge_map.json` | cartographer (reverse tree: depth 0 target, prerequisite edges, assumed spine start) |
| `03_curriculum.json` | curriculum |
| `04_math_dossier.json` | math-director |
| `05_shot_list.json` | cinematographer |
| `06_scene_spec.json` + `glm_scene.py` | composer |
| `validation.json`, `review.json`, `manifest.json`, `traces/` | harness |

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
calls. Validation runs identically on offline bundles.

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

## Flagship film

`examples/glm/glm_flash_magnetic_monopole.py` — **The Lone Pole**: Dirac's
quantization argument told geometrically with 3D StreamLines, TexturedSurface,
SurfaceMesh, and composite prism flux tubes on the paper stage.
