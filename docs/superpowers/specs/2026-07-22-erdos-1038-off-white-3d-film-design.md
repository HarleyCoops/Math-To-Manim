# Erdős 1038 Off-White 3D Sol Film Design

## Goal

Use the repository's independent GPT-5.6 Sol pipeline to create and verify one
cinematic explanation of the proposed solution to Erdős Problem 1038. The
result must be a mathematically faithful, visibly true-3D Manim film on an
archival off-white stage, followed by a curated GIF featured near the top of
the root README.

The film source is:

- `runs/user-clones/erdos/1038/paper.tex`
- `runs/user-clones/erdos/1038/numerical_verifier.py`

## Provider Boundary

This production uses only the Codex-native `sol/` silo:

```text
math-to-manim-sol run <prompt>
  -> codex exec --model gpt-5.6-sol
  -> runs/sol/<timestamp>-<slug>/
  -> reasoning artifacts, sol_scene.py, review.json, manifest.json
  -> application validation and bounded Codex repair
```

It must not use Mythos prompts, agents, backends, orchestration, or
`math-to-manim`. The Sol pipeline is intentionally CLI-only; no Sol MCP or
HTTP layer will be added.

The active Sol film contract does not prescribe a starfield. Therefore no
global pipeline instruction needs removal. The source film prompt will contain
a hard prohibition against starfields, dark voids, and black-background
fallbacks.

## Scope

This work covers Erdős Problem 1038 only. It does not render the other five
papers in the Erdős repository and does not change the Sol implementation.

Transient reasoning and media remain in `runs/sol/`. Committed changes are
limited to the reproducible prompt, its contract test, the curated GIF, and
the README feature.

## Mathematical Story

For

\[
f(x)=\prod_{j=1}^{n}(x-r_j),\qquad r_j\in[-1,1],
\]

the problem asks for the extreme possible length of

\[
E_f=\{x\in\mathbb R:|f(x)|<1\}.
\]

The film follows the proof's potential-theoretic spine:

1. Replace the roots by the empirical probability measure
   \[
   \mu_f=\frac1n\sum_{j=1}^{n}\delta_{r_j}.
   \]
2. Lift the polynomial into its logarithmic potential
   \[
   V_{\mu_f}(x)=\int\log|x-t|\,d\mu_f(t)
   =\frac1n\log|f(x)|,
   \qquad
   E_f=\{x:V_{\mu_f}(x)<0\}.
   \]
3. Visualize simultaneous component atomization: root mass inside each
   component collapses to its barycentre and the negative set cannot grow,
   \[
   E_{\widetilde\mu}\subseteq E_\mu.
   \]
4. Move from finite atoms to the one-cut limiting measure
   \[
   \mu_q=A(q)\delta_{-1}+
   \frac{t+1-2A(q)s(q)}
   {\pi(t+1)\sqrt{(t-a(q))(1-t)}}
   \mathbf 1_{(a(q),1)}\,dt,
   \]
   with
   \[
   H(q)=\frac{2q}{(1+q)^2},\quad
   s(q)=\frac{1-q}{1+q},\quad
   A(q)=\frac{\log H(q)}{\log q}.
   \]
5. Show
   \[
   \Lambda(q)=H(q)\left(
   u_-(q)+u_-(q)^{-1}
   -u_+(q)-u_+(q)^{-1}
   \right)
   \]
   reaching its unique certified minimum and giving
   \[
   \inf_f |E_f|
   =L
   =1.834430475762661\ldots .
   \]
   The value is certified by directed outward interval arithmetic and is not
   attained by any finite polynomial.
6. Contrast the lower limit with Tao's attained upper extremum:
   \[
   \sup_f |E_f|=2\sqrt{2},
   \qquad f(x)=(x^2-1)^m.
   \]

The complete paper also requires global comparison, circle rearrangement, and
uniform parameter certificates. The film identifies these honestly as the
bridge to global optimality; it does not imply that a plotted scalar minimum
alone proves the theorem.

## Visual Direction

### Stage and palette

- Every frame uses warm archival off-white near `#f3ecd8`.
- Text, axes, and primary outlines use dark sepia near `#241a12`.
- Accents are muted oxide red, verdigris, indigo, and old gold.
- No starfield, stars, cosmic void, nebula, black background, or dark
  transitional frame may appear.
- Existing historical examples and showcase assets remain untouched.

### True-3D requirement

`ThreeDScene` inheritance alone is insufficient. The result must visibly read
as three-dimensional:

- roots become raised pillars or logarithmic wells with meaningful depth;
- the potential is a genuine surface or extruded ribbon in world space;
- the zero threshold is a translucent plane with visible intersections;
- the one-cut density becomes a sculpted distribution over \([-1,1]\);
- the \(\Lambda(q)\) minimum appears as a raised curve or valley;
- at least four perspective-changing `move_camera()` or
  `set_camera_orientation()` calls expose parallax;
- no `.animate` call is made on `self.camera`.

Representative-frame review rejects a flat composition masquerading as 3D.

### Typography and whitespace

- Every displayed expression uses complete valid LaTeX.
- Important formulas use addressable multi-part `MathTex`.
- A plain-language headline introduces each idea before notation.
- The camera zooms into the active term or object, then pulls back to create
  whitespace before the next explanation.
- No more than one headline or two short text blocks are visible at once.
- Captions replace one another and remain readable in a 720-pixel-wide GIF.

## Beat Plan

1. **The question has a shape.** Introduce \(f\), confined roots, and \(E_f\).
2. **A polynomial becomes terrain.** Reveal the log potential, zero plane,
   and negative footprint.
3. **Collapse without expansion.** Animate barycentric atomization and its
   set inclusion.
4. **The limiting one-cut shape.** Morph the discrete atoms into the endpoint
   mass plus continuous density.
5. **The certified floor.** Travel along the \(\Lambda(q)\) valley, isolate
   \(q_*\), reveal \(L\), state non-attainment, and name the certificate
   boundary.
6. **The opposite extreme.** Pull back to endpoint masses, expand to
   \(2\sqrt{2}\), and finish with both results in one 3D tableau.

Target duration is 60–90 seconds.

## Sol Run and Verification

1. Save the exact prompt as `docs/prompts/erdos-1038-off-white-3d.md`.
2. Run the Sol-specific offline tests.
3. Rehearse the exact prompt with
   `math-to-manim-sol run <prompt> --offline`.
4. Run `math-to-manim-sol doctor` to verify Codex CLI and cached ChatGPT login.
5. Run the real production with
   `math-to-manim-sol run <prompt> --render -q l --reasoning-effort high
   --max-repairs 3`.
6. Inspect `01_intent.json` through `06_scene_spec.json`, `sol_scene.py`,
   `review.json`, `manifest.json`, render logs, MP4, representative frames,
   and contact sheet.
7. Reject and repair any dark, flat, crowded, clipped, or mathematically
   misleading result. Use the Sol harness's bounded Codex repair loop first;
   apply a surgical run-local edit only when concrete frame evidence remains.
8. Cut the strongest 20–24 second teaching sequence and convert it with the
   repository's existing GIF utility.
9. Commit only the curated GIF to `docs/showcase/assets/` and feature it near
   the top of `README.md`, preserving the star chart and existing showcase.
10. Run the full offline test suite and verify every final asset path.

## Failure Handling

- If Codex authentication fails, stop before spending render time and report
  the exact `math-to-manim-sol doctor` failure.
- If generation or rendering fails, preserve the run ledger and allow the Sol
  harness up to three evidence-backed repair passes.
- If the film renders but fails visual review, it is not eligible for README
  placement.
- If the target duration exceeds the render budget, shorten by removing a
  nonessential beat rather than slowing weak footage or skipping verification.
- Do not substitute the Anthropic/Mythos pipeline under any failure mode.

## Deliverables

- `docs/prompts/erdos-1038-off-white-3d.md`
- complete selected run bundle under `runs/sol/`
- verified `sol_scene.py`, MP4, and contact sheet
- `docs/showcase/assets/erdos-1038-potential-landscape.gif`
- root README feature with accurate alt text and mathematical caption
