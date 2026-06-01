# Roadmap: Editable Animation Workflow

M2M2 is not trying to make the rendered MP4 itself the main editing surface.
The current design makes the video editable by keeping the pipeline artifacts
that produced it: prompt, concept intent, prerequisite graph, curriculum,
math packet, storyboard, scene spec, generated Manim code, validation report,
render result, review report, and manifest.

## Current Progress

- Intermediate artifacts are already the editing contract. A deterministic run
  writes inspectable JSON and `generated_scene.py` into `runs/<run_id>/`, so a
  reviewer can see which prompt, storyboard, scene spec, and code produced the
  output.
- Prompt-level editing is supported by rerunning the CLI with a revised prompt,
  style, quality, or render option.
- Spec/code-level editing is the near-term workflow: edit `scene_spec.json` or
  `generated_scene.py`, then rerun validation and render against the same run
  bundle.
- Static validation is already the gate before rendering. Failed validation
  should stop before Manim runs.
- Render repair is part of the architecture: failed renders can feed Manim
  stderr/stdout plus the frozen `scene_spec` back into the code repair path
  without recomputing the whole planning chain.
- Hermes and Codex are the agent-assisted iteration layer. Hermes can inspect
  artifacts, patch prompts/specs/code, run CLI smoke checks, review frames or
  GIFs, and keep the edit history explicit; Codex can be used for generated-code
  and repair stages when the local Codex CLI provider is selected.

## Planned Editing Loop

```text
prompt
  -> typed planning artifacts
  -> storyboard / scene_spec edits
  -> generated_scene.py edits or Codex-assisted repair
  -> static validation
  -> Manim rerender
  -> video review artifacts
  -> next edit
```

The important product direction is artifact-first editing:

- Edit the prompt when the explanation goal, audience, style, or duration is
  wrong.
- Edit the storyboard or `scene_spec.json` when the teaching sequence or visual
  objects are wrong.
- Edit `generated_scene.py` when Manim implementation details are wrong.
- Use the repair loop when validation or rendering fails.
- Use Hermes/Codex to make those edits repeatable instead of treating each video
  as a one-off render.

## Not In Scope Yet

- A full browser video editor timeline.
- Direct MP4 frame-by-frame editing.
- A large UI for dragging Manim objects on a canvas.

Those may come later, but the first useful editable workflow is the one that is
already aligned with M2M2's architecture: preserve the artifacts, edit the stage
where the problem was introduced, and rerender.
