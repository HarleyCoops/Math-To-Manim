# Prime Intellect RL Integration

Math-To-Manim can become a Prime Intellect RL environment by treating each run
bundle as a verifiable repair task.

## What Prime Runs

Prime's RL stack separates the job into three pieces:

- **Environment**: a Verifiers package that serves tasks and scores completions.
- **Orchestrator**: samples rollouts from the model, calls the environment, and
  turns rewards into training batches.
- **Trainer/inference**: updates the policy model and serves the latest weights.

For M2M2, the environment is `harleycooper/math-to-manim`. The first task is
not full video generation. It is generated-code repair:

```text
M2M2 run bundle
  -> prompt + scene_spec + generated_code + failure evidence
  -> model returns GeneratedCode JSON
  -> fast static reward
  -> Prime RL update
```

## Environment Contract

The standalone package lives at `environments/math_to_manim/`.

- Package name: `math-to-manim`
- Import package: `m2m2_visual_repair`
- Hub ID: `harleycooper/math-to-manim`
- Entry point: `from m2m2_visual_repair import load_environment`

Verifiers resolves `math-to-manim` by importing `math_to_manim`, so the
standalone environment package includes a small `math_to_manim` compatibility
shim. The main repo package also exposes a lazy `load_environment()` function
when `m2m2_visual_repair` is installed.

The model must return exactly one tagged JSON block:

```text
<generated_code>{"scene_name":"...","language":"python","code":"..."}</generated_code>
```

The reward uses static checks by default:

- output has the required tag;
- JSON matches the required `GeneratedCode` shape;
- generated Python parses;
- expected Manim scene class has a `construct` method;
- unsafe imports/calls are absent;
- expected math terms appear in the code;
- static layout checks estimate text-crowding risk without rendering.

The layout reward is a proxy, not a visual oracle. It inspects returned Manim
source for long high-font `Text`/`MathTex`, missing `scale_to_fit_width`, dense
text-group buffers, and too many fixed-frame overlays. This is designed to make
crowded scripts less likely during RL rollouts while keeping full renders as the
slower audit step.

Rendering and video review are intentionally not in the default reward loop
because Manim renders are slow and expensive for RL rollouts.

## Export Tasks

Create a JSONL dataset from existing M2M2 run bundles:

```bash
python -m math_to_manim.cli pi-export-runs \
  --runs-dir runs \
  --output environments/math_to_manim/m2m2_visual_repair/data/repair_tasks.jsonl
```

The exporter skips incomplete run bundles and writes only text artifacts. It does
not copy videos, media folders, credentials, or `.env` files.

## Local Verification

```bash
uv pip install -e environments/math_to_manim
uv run python -c "from verifiers import load_environment; env = load_environment('math-to-manim'); print(len(env.dataset))"
uv run vf-eval math-to-manim -n 2
```

For the current text-crowding target, the bundled default dataset includes a
layout-repair task built from the QED/Minkowski README GIF run. It asks the model
to preserve the QED educational arc while making captions and formulas sparse,
staged, scaled, and readable.

## Publish From Prime RL Box

The local Windows Prime CLI may be unauthenticated. Use the logged-in remote
Prime RL box when needed:

```bash
scp -r environments/math_to_manim ubuntu@69.19.136.157:~/math_to_manim_env
ssh ubuntu@69.19.136.157
cd ~/math_to_manim_env
uv pip install -e .
uv run python -c "from verifiers import load_environment; env = load_environment('math-to-manim'); print(len(env.dataset))"
uv run vf-eval math-to-manim -n 2
prime env push --path . --name math-to-manim --visibility PUBLIC
```

## Training Templates

Bundled templates live in
`environments/math_to_manim/m2m2_visual_repair/configs/`.

- Smoke: `Qwen/Qwen3.5-0.8B`
- Practical repair: `Qwen/Qwen3.5-35B-A3B`
- Follow-up: `Qwen/Qwen3.5-397B-A17B`

Use the smoke model to verify the environment and reward wiring. Use the 35B
repair model for the first serious Manim-code repair run. Use the 397B follow-up
only after reward curves are stable and the environment has a clean eval signal.
