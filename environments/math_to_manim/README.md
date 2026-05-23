# Math-To-Manim Visual Repair

Prime Intellect Verifiers environment for training models to repair generated
Manim code from Math-To-Manim run bundles.

## Environment

- Hub ID: `harleycooper/math-to-manim`
- Package: `math-to-manim`
- Import package: `m2m2_visual_repair`
- Task: single-turn generated-code repair

The model receives an M2M2 prompt, scene spec, current generated code, and
validation/render/review evidence. It must return exactly one
`<generated_code>...</generated_code>` block containing JSON with at least
`scene_name` and `code`.

The default dataset includes a QED/Minkowski layout-repair task from the README
GIF. Its reward includes static text-crowding checks for long formulas without
`scale_to_fit_width`, dense text grouping, and excessive fixed-frame overlays.
Full rendering remains an eval/audit step, not the per-rollout reward.

## Local Use

```bash
uv pip install -e environments/math_to_manim
uv run python -c "from verifiers import load_environment; env = load_environment('math-to-manim'); print(len(env.dataset))"
uv run vf-eval math-to-manim -n 2
```

## Export M2M2 Runs

From the Math-To-Manim repo:

```bash
python -m math_to_manim.cli pi-export-runs \
  --runs-dir runs \
  --output environments/math_to_manim/m2m2_visual_repair/data/repair_tasks.jsonl
```

## Publish

Run from an authenticated Prime environment:

```bash
prime env push --path environments/math_to_manim --name math-to-manim --visibility PUBLIC
```

## Training Templates

Config snippets are bundled under `m2m2_visual_repair/configs/`.

- Smoke: `Qwen/Qwen3.5-0.8B`
- Practical repair: `Qwen/Qwen3.5-35B-A3B`
- Follow-up: `Qwen/Qwen3.5-397B-A17B`
