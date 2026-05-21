# Eval Strategy

M2M2 evals should measure the whole path from prompt to useful animation, while
keeping failures attributable to a single stage.

## Eval Layers

| Layer | Question | Gate |
| --- | --- | --- |
| Prompt eval | Did the pipeline infer the right educational intent? | Required before code generation |
| Schema eval | Are artifacts valid and complete? | Required at every stage |
| Pedagogy eval | Does the concept order move from foundations to target? | Required before narrative approval |
| Visual feasibility eval | Can the visual plan be built in Manim CE? | Required before code generation |
| Static code eval | Does generated Python parse and define the expected Scene? | Required before render |
| Render eval | Does Manim produce media without errors? | Required before shipping |
| Regression eval | Did a changed prompt or stage degrade known cases? | Required in CI once package code exists |

## Initial YAML Suite

`evals/prompt_suite.yaml` is the starter prompt-level suite. It is deliberately
runner-neutral: package owners can bind it to OpenAI Evals, pytest, Inspect, or a
custom runner later.

Each case has:

- `input.prompt`: the natural-language request.
- `expected`: key concepts, artifact requirements, and disallowed shortcuts.
- `rubric`: weighted checks that a grader can apply to stage artifacts.

## Suggested Execution Flow

1. Run prompt cases through the stage pipeline through `scene_spec`.
2. Validate each artifact against the schema docs or generated JSON Schema when
   that exists.
3. Grade pedagogy and visual feasibility using deterministic checks first.
4. Use a judge model only for subjective criteria such as explanation quality,
   and store the full judge prompt/version in the `eval_record`.
5. Run static Python checks before invoking Manim.
6. Render at low quality for routine CI, then use higher quality only for release
   candidates or golden examples.

## Local Runner

Run the deterministic structural suite without Manim:

```bash
./.venv/bin/python -m math_to_manim.cli eval-suite evals/prompt_suite.yaml --runs-dir /tmp/m2m2-evals
```

Add `--render --quality l` when render dependencies are installed and the eval
should require Manim output. The runner writes normal run bundles and checks
artifact completeness, scene-name sanity, generated Python parsing, static
validation, render status, and optional `expected.acceptance_terms`.

## Minimum CI Gates

Minimum gates should be:

- All YAML suites parse.
- Every generated artifact has a valid shared envelope.
- Every generated `scene_spec` names one scene class.
- Generated Manim files parse with `python -m py_compile`.
- Reference examples render with `python -m manim -ql`.

## Grading Guidance

Use separate scores rather than one blended pass/fail score. A scene can be
mathematically correct but visually impractical, or renderable but pedagogically
thin.

Recommended score fields:

- `schema_valid`: 0 or 1.
- `concept_coverage`: 0 to 1.
- `prerequisite_ordering`: 0 to 1.
- `visual_feasibility`: 0 to 1.
- `narrative_alignment`: 0 to 1.
- `manim_static`: 0 or 1.
- `render`: 0 or 1.

Shipping threshold: all binary checks pass, no critical failures, and average
subjective score is at least 0.8.

## OpenAI Eval Alignment

OpenAI's agent eval guidance emphasizes reproducible evals for agent workflows
and trace-level grading for workflow errors. M2M2 should store run traces and
artifact IDs together so a failed grade can be mapped back to the responsible
agent stage.

Source: https://platform.openai.com/docs/guides/agent-evals
