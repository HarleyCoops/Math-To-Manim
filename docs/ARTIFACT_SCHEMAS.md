# Artifact Schemas

Artifacts are the contract between agents, tools, renderers, and evals. They
should be plain JSON-compatible objects, versioned, and persisted before the next
stage runs.

## Shared Envelope

Every artifact uses the same top-level metadata.

```yaml
schema_version: "m2m2.artifact.v1"
artifact_type: "scene_spec"
artifact_id: "2026-05-02T140000Z-derivative-scene"
created_at: "2026-05-02T14:00:00Z"
source_run_id: "run_..."
producer:
  stage: "visual_designer"
  model: "provider/model-or-local-tool"
  prompt_hash: "sha256:..."
```

Required rules:

- `schema_version` is bumped only for breaking changes.
- `artifact_type` is one of the types below.
- `artifact_id` is stable once written.
- `producer.model` may be `local-tool` for deterministic scripts.

## request_spec

Captures the normalized user request.

```yaml
artifact_type: "request_spec"
prompt: "Explain why derivatives are slopes"
audience: "high_school"
duration_seconds: 60
style: "clear"
quality_target: "preview"
constraints:
  render_engine: "manim-ce"
  max_scene_count: 1
  allowed_external_assets: false
```

## concept_plan

Defines the target concept and teaching objective.

```yaml
artifact_type: "concept_plan"
target_concept: "Derivative as slope of a tangent line"
learning_objectives:
  - "Connect average rate of change to secant slope."
  - "Show tangent slope as the secant limit."
misconceptions:
  - "A tangent line must touch a graph at only one point."
key_terms:
  - "secant line"
  - "tangent line"
  - "limit"
```

## knowledge_tree

Represents reverse prerequisite discovery.

```yaml
artifact_type: "knowledge_tree"
root:
  id: "derivative_slope"
  label: "Derivative as slope"
  prerequisites:
    - id: "line_slope"
      label: "Slope of a line"
      prerequisites: []
    - id: "secant_limit"
      label: "Secant lines approaching tangents"
      prerequisites:
        - id: "function_graph"
          label: "Functions and graphs"
          prerequisites: []
depth_limit: 2
ordering: "foundations_to_target"
```

## math_enrichment

Stores equations, invariants, and checks used by later stages.

```yaml
artifact_type: "math_enrichment"
definitions:
  derivative: "f'(a) = lim_{h -> 0} (f(a+h)-f(a))/h"
equations:
  - id: "difference_quotient"
    latex: "f'(a)=\\lim_{h\\to 0}\\frac{f(a+h)-f(a)}{h}"
    plain_language: "The derivative is the limiting secant slope."
assumptions:
  - "Function is differentiable at the highlighted point."
validation_notes:
  - "Use h values that approach zero from the right in the visual."
```

## visual_spec

Describes the visual plan without executable code.

```yaml
artifact_type: "visual_spec"
canvas:
  aspect_ratio: "16:9"
  background: "dark"
visual_elements:
  - id: "graph"
    type: "axes_plot"
    expression: "0.25*x**2 + 0.5"
  - id: "secant_line"
    type: "line"
    relation: "passes through graph at x=a and x=a+h"
beats:
  - id: "introduce_average_slope"
    duration_seconds: 12
    focus: ["graph", "secant_line"]
```

## narrative_spec

Defines narration, captions, and pacing.

```yaml
artifact_type: "narrative_spec"
tone: "precise"
beats:
  - id: "introduce_average_slope"
    narration: "Start with the slope between two nearby points."
    on_screen_text: "Average slope"
    math_refs: ["difference_quotient"]
```

## scene_spec

The final implementation-neutral contract before code generation.

```yaml
artifact_type: "scene_spec"
scene_id: "derivative_slope_intro"
scene_class_name: "DerivativeSlopeIntro"
manim_version_target: "CE >=0.18"
imports:
  - "from manim import *"
sections:
  - id: "setup"
    objective: "Show axes, graph, and secant line."
    required_mobjects: ["Axes", "MathTex", "Line", "Dot"]
  - id: "limit"
    objective: "Animate h decreasing until the secant appears tangent."
    required_animations: ["Create", "Transform", "FadeIn"]
acceptance_checks:
  - "One Scene subclass exists with the requested class name."
  - "No network or filesystem writes are used."
  - "MathTex strings are valid LaTeX fragments."
```

## manim_artifact

Stores generated code and static validation.

```yaml
artifact_type: "manim_artifact"
scene_class_name: "DerivativeSlopeIntro"
source_path: "generated/derivative_slope_intro.py"
code_hash: "sha256:..."
static_validation:
  syntax_ok: true
  forbidden_imports: []
  scene_classes: ["DerivativeSlopeIntro"]
```

## render_artifact

Stores render output metadata.

```yaml
artifact_type: "render_artifact"
command: "python -m manim -ql generated/derivative_slope_intro.py DerivativeSlopeIntro"
status: "passed"
media:
  video_path: "media/videos/derivative_slope_intro/480p15/DerivativeSlopeIntro.mp4"
  preview_image_path: "media/images/derivative_slope_intro.png"
duration_seconds: 58.4
stderr_summary: ""
```

## study_notes_artifact

Captures companion study material.

```yaml
artifact_type: "study_notes_artifact"
formats:
  markdown_path: "generated/derivative_slope_intro.md"
  latex_path: "generated/derivative_slope_intro.tex"
outline:
  - "Average slope"
  - "Limit of secants"
  - "Derivative notation"
```

## eval_record

Summarizes automated and human-reviewable quality signals.

```yaml
artifact_type: "eval_record"
suite: "m2m2_prompt_refactor_v1"
case_id: "derivative_slope_intro"
status: "passed"
scores:
  schema_valid: 1.0
  pedagogy: 0.86
  visual_feasibility: 0.92
  manim_static: 1.0
  render: 1.0
failures: []
```

## Compatibility Notes

- Artifacts should be serializable as JSON and readable as YAML fixtures.
- Generated Manim code is referenced by path and hash; it is not embedded in
  eval records unless a runner explicitly needs inline review.
- The schema avoids provider-specific prompt fields so that Anthropic, Gemini,
  Kimi, OpenAI, and local deterministic stages can all produce the same shape.

