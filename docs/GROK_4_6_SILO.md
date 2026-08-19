# Grok 4.6: xAI-native film silo

## Boundary

Math-To-Manim contains three deliberately independent production systems.
The public README features only Grok. Mythos and Sol remain supported in
code and keep their own CLIs.

| Silo | Native runtime | Entry point |
|---|---|---|
| `grok/` | xAI Responses API, model `grok-4.6` | `math-to-manim-grok` |
| `mythos/` | Anthropic charter chain | `math-to-manim` |
| `sol/` | Codex CLI + GPT-5.6 Sol | `math-to-manim-sol` |

The Grok silo imports no Mythos prompt, backend, or harness, and no Sol
client. It is not routed through `mythos/harness.py`.

## Why the stages are cut this way

Reverse thinking is preserved. The chain does not flatten into one "think
then write Manim" prompt.

Grok's tools change the job of later stages, not the teaching method:

| Stage | Tools | Why this hop exists |
|---|---|---|
| intent | image input (vision), no tools | A photographed page is a claim, not a topic name. Vision belongs here. |
| cartographer | optional `web_search` | Reverse tree. Search only for canonical names. |
| curriculum | none | First forward pass. Curiosity segues. Tools would invite more facts. |
| math-director | required `code_interpreter`, optional cited `web_search` | Homework numbers come from the sandbox. This is Grok's unique cut. |
| cinematographer | `image_generation` (1 to 3 stills), optional `x_search` | Stills and visual seeds are native Grok tools, not a Claude shot list. |
| composer | local `verify_scene` function | Spec and source live together because Grok can compile mid-turn. |

Composer is not a seventh "codegen" charter. Mythos splits spec from
codegen because that hop cannot execute local checks. Grok can, so the
loop closes here.

## Runtime

```text
math-to-manim-grok run <request> [--image PATH]
  -> create isolated runs/grok/<timestamp>-<slug>/ ledger
  -> for each stage, POST https://api.x.ai/v1/responses
       model grok-4.6
       reasoning.effort from XAI_REASONING_EFFORT
       stage-scoped tools
  -> persist thinking traces and tool calls under traces/
  -> save generated stills under stills/
  -> local reverse-tree, AST, camera, and compile checks
  -> optional manim render
  -> final manifest
```

## Authentication and environment

| Variable | Default | Purpose |
|---|---|---|
| `XAI_API_KEY` | unset | Required for live runs. Doctor checks it without printing it. |
| `XAI_MODEL` | `grok-4.6` | Responses API model name |
| `XAI_REASONING_EFFORT` | `high` | `low`, `medium`, `high`, or `xhigh` |
| `XAI_BASE_URL` | `https://api.x.ai/v1` | Override only for tests |
| `XAI_TIMEOUT` | `900` | Seconds for one Responses call |

```bash
export XAI_API_KEY=...
math-to-manim-grok doctor
math-to-manim-grok run "the heat equation"
math-to-manim-grok run "A 3 kg cart at 4 m/s hits a spring k=200. How far does it compress?"
math-to-manim-grok run "solve this worksheet" --image homework.jpg
```

Doctor checks that the key is set, then makes a tiny live Responses ping
when the key is present. A present-but-invalid key is a failure. It never
prints the key.

## Offline versus live

`--offline` writes the same artifact shape with zero xAI calls. Use it in
CI and plumbing checks.

Live `run` calls Grok when `XAI_API_KEY` is present. Pytest never calls
xAI. Tests mock the client or stay on `--offline`.

## Reverse thinking rules

- Depth 0 is the target claim.
- Depth increases toward foundations the learner already owns.
- Edges are prerequisites: `[from_id, to_id]` means `from_id` is needed
  before `to_id`.
- The spine starts at an assumed foundation and ends at depth 0.
- Cartographer must not write a forward lesson plan or search "how to
  explain X".
- Curriculum is the first forward pass.
- Solved numbers come from `code_interpreter`.
- Camera: `move_camera()` / `set_camera_orientation()` only.

## Artifact contract

Every run contains:

| Artifact | Purpose |
|---|---|
| `01_intent.json` | audience, core claim, scope, big zoom, optional image read |
| `02_knowledge_map.json` | reverse prerequisite graph |
| `03_curriculum.json` | forward teaching sequence |
| `04_math_dossier.json` | formulas, sandbox numbers, checks, sources |
| `05_shot_list.json` | cinematic beats and still references |
| `06_scene_spec.json` | ThreeDScene contract |
| `grok_scene.py` | one self-contained Manim CE scene |
| `validation.json` | compile, AST, and camera evidence |
| `review.json` | limitations and render note |
| `traces/<stage>.json` | thinking summaries and tool calls |
| `manifest.json` | wrapper-owned status |

## Custom bot

Edit `grok/agents/*.md`. Those charters are the product: thinking contract,
allowed tools, JSON keys, forbidden moves. A custom bot for Manim explainer
videos is a charter edit, not a new application.

## References

- https://docs.x.ai/developers/models/grok-4.6
- https://docs.x.ai/developers/tools/overview
