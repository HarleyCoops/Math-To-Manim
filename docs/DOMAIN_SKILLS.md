# Domain Skills for Animation Quality

M2M2 treats physics and math skills as contributor guidance and review
procedure, not as hidden runtime dependencies. A domain skill should help Hermes,
Codex, or another operator turn a prompt into a better `storyboard.json`,
`scene_spec.json`, Manim implementation, and review record while preserving the
pipeline rule: typed artifacts first, code second, render only after validation.

## What a physics skill should contain

A physics-focused skill is useful when it makes physical intuition explicit
before Manim code is written. It should capture constraints such as:

- name the conserved or changing quantities before choosing visuals;
- show cause before effect, such as force arrows before acceleration or field
  geometry before particle motion;
- keep units, axes, labels, and scale changes consistent across shots;
- prefer local geometric evidence over symbolic shortcuts, such as slopes,
  flux, phase, curvature, or area accumulation;
- flag impossible motion, discontinuous state changes, misleading perspective,
  and decoration that suggests the wrong mechanism;
- state which approximations are being visualized, such as small-angle motion,
  frictionless motion, point masses, ideal fluids, or nonrelativistic limits.

Those constraints belong in the planning artifacts where possible. For example,
a gravity prompt should produce storyboard beats that reveal curvature, orbit
state, and conservation cues before a scene spec asks Manim to animate a camera
move. A quantum prompt should distinguish amplitude, probability, measurement,
and basis choice instead of treating all glow or randomness as interchangeable.

## Reusable Manim patterns

Domain skills can also maintain a library of reusable patterns without turning
the repository into a style clone. Good candidates are small, inspectable
recipes:

- tangent or secant transforms for derivatives and local linearity;
- vector fields, streamlines, and field-line density for forces and flows;
- phase-space traces and energy contours for dynamics;
- wave superposition, envelopes, and interference for oscillation topics;
- distribution clouds, histograms, and highlighted sample paths for stochastic
  processes;
- camera-safe 3D axes, surface slices, and projection helpers for geometry.

These should be described as constraints and examples that a code generator can
adapt to the current `ManimSceneSpec`. They should not require importing Hermes
or any skill package from `math_to_manim`; package dependencies stay in
`pyproject.toml`, and skills remain operator-side procedure.

## Validation and review loops

A domain skill cannot guarantee correctness by itself. It improves the prompts,
checks, and review rubric around the existing M2M2 loop:

1. `IntentAgent` and `CurriculumAgent` identify the physical or mathematical
   idea, prerequisites, and learner-facing misconception risks.
2. `StoryboardAgent` records the intuition beats: what appears first, what moves,
   what stays invariant, and where labels or equations enter.
3. `SceneSpecAgent` turns those beats into concrete Manim objects, timing, camera
   choices, and validation expectations.
4. `StaticReviewAgent` blocks unsafe or malformed generated Python before render.
5. Render and video review inspect whether the animation actually communicates
   the intended mechanism, not just whether a file was produced.

For Hermes/Codex work, the skill should preload alongside
`codebase-inspection`, `manim-video`, and `systematic-debugging`. The operator
can then inspect the run bundle, compare `storyboard.json` against
`generated_scene.py`, render when dependencies are available, and record whether
the final motion obeys the domain constraints.

## 3Blue1Brown inspiration policy

3Blue1Brown is a valuable reference point for mathematical communication:
geometric first principles, progressive reveal, careful camera motion, readable
notation, and one clear idea per beat. M2M2 can distill those general principles
into skills and rubrics.

M2M2 should not copy proprietary 3Blue1Brown code, recreate a video shot-for-shot,
or market generated scenes as 3Blue1Brown-style replicas. A good skill describes
transferable teaching patterns, such as "introduce notation only after the
geometry is visible" or "keep one invariant visually anchored while another
quantity changes." It should avoid instructions like "copy this scene," "match
this exact palette," or "reproduce this animation."

The practical answer to issue #39 is therefore yes, domain-specific skills are a
good fit for improving physical intuition and reusable Manim craft, but they
should live as transparent Hermes/Codex procedures and review rubrics. They
should distill broadly useful principles and local repo patterns, not private
code or proprietary artistic identity.
