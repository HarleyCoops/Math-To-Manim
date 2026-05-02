# Migration Notes from Public Math-To-Manim

These notes describe how M2M2 should migrate ideas from the public
HarleyCoops/Math-To-Manim project without copying its provider-specific shape.

## Baseline Observed

The public project describes a pipeline that starts with a small prompt, builds a
reverse knowledge tree, enriches the math, designs visuals, writes narrative,
generates Manim code, validates or repairs syntax, renders with Manim, and emits
video or GIF artifacts.

The public README also lists multiple experimental provider paths: a maintained
Claude/Anthropic pipeline, a Gemini/Google ADK pipeline, and a Kimi/Moonshot
swarm-style pipeline.

Source: https://github.com/HarleyCoops/Math-To-Manim

## What Carries Forward

- Reverse prerequisite discovery remains the core pedagogy pattern.
- The output should include both animation code and study notes.
- Generated Manim must be validated before render.
- Demo prompts should remain small enough to show the pipeline expanding intent.
- Examples should prioritize mathematical clarity over visual excess.

## What Changes

- Stage outputs become versioned artifacts instead of implicit in-memory state.
- Provider-specific agents move behind a common stage-runner interface.
- OpenAI Agents SDK primitives can model specialist agents, deterministic tools,
  handoffs, guardrails, sessions, and tracing.
- Evals become first-class fixtures instead of manual demo inspection.
- Generated media paths are metadata in `render_artifact`, not the primary
  source of truth.

## Proposed Migration Map

| Public Math-To-Manim idea | M2M2 artifact or stage |
| --- | --- |
| Simple prompt | `request_spec` |
| ConceptAnalyzer | `concept_plan` |
| PrerequisiteExplorer | `knowledge_tree` |
| MathematicalEnricher | `math_enrichment` |
| VisualDesigner | `visual_spec` |
| NarrativeComposer | `narrative_spec` |
| Manim CodeGenerator | `scene_spec` then `manim_artifact` |
| Syntax validation and repair | `static_validation` inside `manim_artifact` |
| Manim render | `render_artifact` |
| Study notes | `study_notes_artifact` |
| Demo inspection | `eval_record` |

## Compatibility Risks

- Public examples may assume local folder names such as `src/`, `media/`, or
  provider-specific demo scripts. M2M2 should not preserve those paths unless the
  package owner adopts them.
- Generated Manim can be long and brittle. The refactor should prefer a compact
  `scene_spec`, then regenerate code from that stable contract.
- Multi-agent demos can hide failures if every stage reruns on retry. Persisting
  artifacts makes repair cheaper and more auditable.
- Manim, LaTeX, and FFmpeg are external system dependencies; evals should report
  environment details on render failures.

## First Milestones

1. Define artifact dataclasses or JSON Schemas from `docs/ARTIFACT_SCHEMAS.md`.
2. Build a runner that can stop after each artifact stage.
3. Connect the prompt eval suite to the runner through `scene_spec`.
4. Add static Manim checks before render.
5. Promote one rendered reference scene to a golden example only after the media
   storage policy is decided.

