# Erdős 1038 Off-White 3D Film Design

## Goal

Use the existing Mythos Math-To-Manim pipeline to create and verify one
cinematic explanation of the proposed solution to Erdős Problem 1038. The
result must be a readable, mathematically faithful, true-3D Manim film on an
archival off-white stage, then a curated GIF featured near the top of the
repository's root README.

The source of mathematical truth is:

- `runs/user-clones/erdos/1038/paper.tex`
- `runs/user-clones/erdos/1038/numerical_verifier.py`

The film may simplify the proof's presentation, but it must not invent a
different argument or present the certified numerical constant as an
elementary closed form.

## Scope

This work covers Erdős Problem 1038 only. It does not render the other five
papers in the Erdős repository.

The work uses the established Mythos CLI/MCP, run ledger, generated Manim
scene, verifier, render, repair, and GIF workflows. It does not create a new
or parallel animation pipeline.

## Mathematical Story

For a monic real polynomial

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
   =\frac1n\log|f(x)|.
   \]
   The sublevel set becomes
   \[
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
5. Show the certified one-variable width
   \[
   \Lambda(q)=H(q)
   \left(
   u_-(q)+u_-(q)^{-1}
   -u_+(q)-u_+(q)^{-1}
   \right)
   \]
   reaching its unique minimum at \(q_*\), giving
   \[
   \inf_f |E_f|
   =L
   =1.834430475762661\ldots .
   \]
   The film states that this value is certified by outward interval
   arithmetic and that no finite polynomial attains it.
6. Contrast the lower limit with Tao's attained upper extremum:
   \[
   \sup_f |E_f|=2\sqrt2,
   \qquad f(x)=(x^2-1)^m.
   \]

The full analytic proof contains global comparison, circle rearrangement,
and uniform interval certificates. The film represents these honestly as the
bridge that establishes global optimality; it does not pretend that the
animated scalar minimum alone proves the theorem.

## Visual Direction

### Stage and palette

- Every frame uses a warm archival off-white background close to `#f3ecd8`.
- Text, axes, and primary outlines use dark sepia near `#241a12`.
- Accents are muted mineral pigments: oxide red, verdigris, indigo, and old
  gold.
- Black backgrounds, starfields, cosmic voids, nebulae, and deep-space
  motifs are forbidden for this film.
- The active Mythos instructions will stop prescribing the old ink-black
  house palette. They will default to archival paper and explicitly avoid
  starfields unless a user asks for one.
- Existing starfield helpers, historical examples, and showcase media remain
  intact; this is an instruction-level art-direction change, not deletion of
  reusable code or past work.

### True-3D requirement

Using `ThreeDScene` alone is insufficient. The rendered result must visibly
read as three-dimensional:

- roots become raised pillars or logarithmic wells with meaningful depth;
- the potential is a genuine surface or extruded ribbon in world space;
- the zero threshold is a translucent plane with visible thickness and
  intersections;
- the one-cut density becomes a sculpted distribution or curtain over
  \([-1,1]\);
- the \(\Lambda(q)\) minimization appears as a raised curve or valley with a
  physical marker at \(q_*\);
- at least four `move_camera()` or `set_camera_orientation()` changes expose
  perspective and parallax;
- the camera starts readable, tilts into the landscape, moves through the
  proof, and returns to a final master tableau;
- no `.animate` call is made on `self.camera`.

Representative-frame review must reject a flat composition masquerading as
3D.

### Typography and whitespace

- Every displayed mathematical expression uses valid, complete LaTeX.
- Important formulas are constructed as multi-part `MathTex` objects so the
  active term can be addressed.
- A formula appears only after a plain-language headline establishes its
  purpose.
- The camera zooms into the active object or term, then pulls back before the
  next explanation.
- No more than one headline or two short text blocks are visible at once.
- Captions replace one another; they never accumulate.
- Text must remain readable in a 720-pixel-wide README GIF.

## Beat Plan

1. **The question has a shape.** Introduce \(f\), its confined roots, and the
   moving interval \(E_f\). Build \(|f(x)|=1\) as the threshold.
2. **A polynomial becomes terrain.** Transform the product into
   \(V_{\mu_f}=\frac1n\log|f|\); tilt the camera to reveal the zero plane and
   the negative trench whose footprint is \(E_f\).
3. **Collapse without expansion.** Several clusters descend into barycentric
   atoms while the below-zero footprint contracts or stays fixed. Display
   \(E_{\widetilde\mu}\subseteq E_\mu\).
4. **The limiting one-cut shape.** Morph the discrete atoms into the endpoint
   mass plus continuous density. Create whitespace before showing the full
   measure formula.
5. **The certified floor.** Travel along the physical \(\Lambda(q)\) valley,
   isolate \(q_*\), and reveal \(L\). Briefly show circle rearrangement and
   interval certificates as the global-optimality bridge. State
   non-attainment.
6. **The opposite extreme.** Pull back to endpoint masses at \(-1\) and \(1\);
   the symmetric shape expands to width \(2\sqrt2\). End with both exact
   extremal statements in one off-white 3D tableau.

Target duration is 60–90 seconds. Geometry carries the explanation; prose
does not become a wall of text.

## Comprehensive Pipeline Prompt

The final prompt supplied to Mythos will include:

- the exact problem statement and main theorem;
- the six-beat mathematical story above;
- the full off-white palette and explicit no-starfield prohibition;
- the true-3D acceptance requirements;
- the complete-LaTeX and whitespace/camera requirements;
- the trust boundary around the computer-assisted certificates;
- a request for one `ThreeDScene`, 60–90 seconds, with a strong final frame
  suitable for a README GIF.

The source prompt will be saved as
`docs/prompts/erdos-1038-off-white-3d.md` so the run is reproducible.

## Pipeline and Verification Flow

1. Run the complete native pipeline offline to validate plumbing and artifact
   schemas without spending model or render time.
2. Run the real native pipeline without rendering and inspect the intent,
   knowledge map, curriculum, math dossier, shot list, scene spec, generated
   code, and manifest.
3. Run static validation and Python compilation.
4. Render a low-quality preview.
5. Extract representative frames and a contact sheet. Check:
   - background is consistently off-white;
   - no starfield or dark fallback appears;
   - the scene is visibly 3D;
   - formulas are complete and readable;
   - no text overlaps or leaves frame;
   - the minimum, non-attainment, maximum, and extremizers are accurate;
   - camera moves create whitespace and restore context.
6. Repair generated code through the existing bounded repair workflow, then
   rerender and reinspect.
7. Produce a palette-optimized README GIF from the best teaching beat or
   final sequence.
8. Copy only the curated GIF into `docs/showcase/assets/`.
9. Add the film near the top of the root README without removing the star
   chart or existing showcase material.
10. Run the offline test suite and verify all README asset paths.

## Failure Handling

- If the real model run fails, preserve its run bundle and retry through the
  pipeline's configured native fallback behavior.
- If generation succeeds but the render fails, repair syntax, imports,
  schema mismatches, or Manim incompatibilities before visual work.
- If the film is flat, dark, crowded, or mathematically misleading, it does
  not qualify for README placement even if Manim exits successfully.
- If a full 60–90 second render exceeds the budget, create a shorter
  substantive cut rather than slowing weak footage or skipping visual review.
- The root README is changed only after a verified GIF exists.

## Deliverables

- Reproducible Erdős 1038 Mythos prompt.
- Complete run bundle in `runs/mythos/`.
- Generated and, if needed, repaired Manim source.
- Verified MP4 and contact sheet.
- Curated README GIF in `docs/showcase/assets/`.
- Root README feature with accurate alt text and mathematical caption.
- Updated active Mythos art-direction instructions and mirrored Claude agent
  charter, removing the prescribed dark/starfield bias.
