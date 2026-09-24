<div align="center">

# Math-To-Manim motion showcase

### Local GIF studies for the M2M2 art direction

[← Back to root README](../../README.md)

<br />

<p align="center">
  <img src="assets/continuous-geometric-picture.gif" alt="GRPO semantic manifold: sibling completions become a geometric policy update across the full scene" width="48%" />
  <img src="assets/qed-minkowski-epic-3d.gif" alt="QED and Minkowski spacetime: light cones, electromagnetic waves, gauge symmetry, and renormalization flow on an off-white 3D stage" width="48%" />
</p>

**Educational animation should feel like an idea becoming visible.**

</div>

---

Most of these GIFs are local copies of the original Math-To-Manim [`public/readme-showcase/`](https://github.com/HarleyCoops/Math-To-Manim/tree/main/public/readme-showcase) bundle. New M2M2 recovery renders are added only after content validation, so the rewrite has both its artistic north star and current pipeline targets in the same repository.

They are not just decoration. They define the bar M2M2 should eventually hit:

- cinematic dark-mode mathematics;
- clean explanatory diagrams;
- legible notation and staged reveals;
- geometry, topology, probability, calculus, physics, and ML rendered as motion;
- README-sized loops that still communicate the core idea.

---

## Olin: the space inside a tweet

<p align="center">
  <a href="assets/olin-off-white-3d-space.mp4">
    <img src="assets/olin-off-white-3d-space.gif" alt="Ten thousand points lift from Olin's flat generative drawing into an off white three dimensional point cloud" width="90%" />
  </a>
</p>

One tweet supplies only the flat coordinates
\((u,v)=(q+40\cos c,\;q\sin c+35d)\), so it cannot identify a unique object
in three dimensions. The film first constructs the exact lift
\(E(i,t)=(u,\;40\sin c,\;v)\). An orthographic view down its hidden direction
returns every original point exactly. It then introduces
\(C(i,t)=((40+q)\cos c,\;(40+q)\sin c,\;35d)\), a more symmetric cylindrical
reading in which \(c\) controls rotation, \(q\) controls radius, and \(35d\)
controls height. \(C\) is an alternate interpretation, not the literal
source of the tweet's shadow, because its projection does not return the
original coordinates.

Production sources: [corrected Mythos prompt](../prompts/olin-off-white-3d-space.md)
and [Manim scene](../../examples/mythos/olin_off_white_3d_space.py).

---

## The v1.1 house-style films

Two new studies rendered by the engine's own cinematography grammar
([`mythos/cinematography.py`](../../mythos/cinematography.py)) for the v1.1
release — the scenes live in [`examples/mythos/`](../../examples/mythos/).

<table>
<tr>
<td width="50%"><img src="assets/reverse-reasoning-tree.gif" alt="Reverse reasoning tree" /></td>
<td width="50%"><img src="assets/mythos-grammar-reel.gif" alt="Mythos grammar reel" /></td>
</tr>
<tr>
<td><b>The reverse reasoning tree</b><br />The repo's thesis, filmed: a question decomposes backward into glowing prerequisite constellations, bottoms out at known ground, then a gold pulse walks it forward as a curriculum — before tilting into 3D.</td>
<td><b>The grammar reel</b><br />The Cinematic Charter beat by beat: headline before symbols, camera flying into each term of E = mc², captions in plain English, then a rippled energy surface as the 3D set piece.</td>
</tr>
</table>

---

## The atlas

The plates form a series with a story — it begins in the middle, on
purpose, and closes with a film that renders every missing plate as one
continuous surface. **[Read THE PLATES →](THE-PLATES.md)**

<p align="center">
  <img src="assets/the-last-day.gif" alt="THE LAST DAY: the atlas closes — one continuous surface through three art directions, ending in a Lorenz attractor" width="90%" />
</p>

---

## The house voices

Beyond the Mythos black-stage cinema, the repo now carries deliberately
opposed art directions — proof the engine's grammar survives a change of
costume. Sources live in
[`examples/mathematics/geometry/`](../../examples/mathematics/geometry/).

<table>
<tr>
<td width="50%"><img src="assets/associate-family-riso.gif" alt="Plate VII: the associate family, risograph style" /></td>
<td width="50%"><img src="assets/blueprint-holonomy.gif" alt="DWG 001: holonomy, cyanotype blueprint style" /></td>
</tr>
<tr>
<td><b>Plate VII — the associate family (risograph)</b><br />The anti-Mythos: flat two-ink print on warm cream, a mid-century textbook plate come alive. The helicoid deforms isometrically into the catenoid; every length on the surface survives the journey.</td>
<td><b>DWG 001 — holonomy (cyanotype blueprint)</b><br />A working drawing that performs its own proof. One amber vector is slid, never turned, around a geodesic octant — and returns rotated by the area it walled in. Gauss–Bonnet as drafting practice.</td>
</tr>
</table>

---

## After hours

The atlas closed; this is what got drawn next. An entirely new space for
the repo — fluid dynamics — in an entirely new voice: the bioluminescent
deep. The physics is not keyframed: two vortex rings leapfrog under a
Biot–Savart field integrated live, every frame, while plankton tracers
are pulled through their throats.
Source: [`vortex_leapfrog.py`](../../examples/physics/fluid_dynamics/vortex_leapfrog.py).

<p align="center">
  <img src="assets/vortex-leapfrog.gif" alt="VORTEX: two glowing vortex rings — cyan and violet — leapfrog through the deep, trading places as plankton tracers stream through their throats" width="90%" />
</p>

And the house voice returned once more for the physics: the nuclear
landscape as a latent space, the mass formula carved into golden terrain
term by LaTeX term, fusion and fission unified as descent toward iron.
Source: [`the_valley.py`](../../examples/physics/nuclear/the_valley.py).

<p align="center">
  <img src="assets/the-valley.gif" alt="THE VALLEY: the Bethe-Weizsäcker mass formula drawn as glowing golden terrain, carved term by term into the valley of beta-stability" width="90%" />
</p>

---

## Featured reel

<table>
<tr>
<td width="33%"><img src="assets/circle-area-3d-unwrapped.gif" alt="3D circle area derivation" /></td>
<td width="33%"><img src="assets/rhombicosidodecahedron.gif" alt="Rhombicosidodecahedron" /></td>
<td width="33%"><img src="assets/cosmic-gravity-3d.gif" alt="Cosmic gravity 3D" /></td>
</tr>
<tr>
<td><b>Circle area 3D</b><br />Nested annuli unwrap into a triangular prism so A = 1/2(2πr)r becomes spatial, not memorized.</td>
<td><b>Rhombicosidodecahedron</b><br />A vivid Archimedean solid: blue vertices, warm struts, and 3D symmetry as spectacle.</td>
<td><b>Cosmic gravity 3D</b><br />Spacetime curvature framed like a science documentary: purple geometry, stars, and field-equation energy.</td>
</tr>
<tr>
<td><img src="assets/derivatives-as-slopes.gif" alt="Derivatives as slopes" /></td>
<td><img src="assets/lorenz-attractor.gif" alt="Lorenz attractor" /></td>
<td><img src="assets/hopf-fibration.gif" alt="Hopf fibration" /></td>
</tr>
<tr>
<td><b>Derivatives as slopes</b><br />The calculus aha moment: a secant tightens into a tangent so slope becomes visible, not merely symbolic.</td>
<td><b>Lorenz attractor</b><br />Chaos theory with glowing trajectories: sensitive dependence becomes a butterfly-shaped object.</td>
<td><b>Hopf fibration</b><br />Topology as choreography: nested colored fibers give stereographic projection a spatial rhythm.</td>
</tr>
<tr>
<td colspan="3"><img src="assets/prolip-scene.gif" alt="ProLIP scene" /></td>
</tr>
<tr>
<td colspan="3"><b>ProLIP scene</b><br />Scientific network storytelling with molecular/protein graph motifs and highlighted interactions.</td>
</tr>
</table>

---

## Teaching diagrams

<table>
<tr>
<td width="25%"><img src="assets/fourier-epicycles.gif" alt="Fourier epicycles" /></td>
<td width="25%"><img src="assets/radius-of-convergence.gif" alt="Radius of convergence" /></td>
<td width="25%"><img src="assets/derivative-visualization.gif" alt="Derivative visualization" /></td>
<td width="25%"><img src="assets/teaching-hopf.gif" alt="Teaching Hopf" /></td>
</tr>
<tr>
<td><b>Fourier epicycles</b><br />Rotating carriers trace structure from circles; Fourier analysis becomes choreography.</td>
<td><b>Radius of convergence</b><br />Power-series boundaries become visible on the line, making convergence feel tangible.</td>
<td><b>Derivative visualization</b><br />Axes, curves, and local linearization establish the foundation before the hero tangent beat.</td>
<td><b>Teaching Hopf</b><br />A calmer instructional treatment of the fibration, closer to a slide sequence than a pure render.</td>
</tr>
</table>

---

## Advanced math, probability, and ML explainers

<table>
<tr>
<td width="33%"><img src="assets/whiskering-exchange.gif" alt="Whiskering exchange" /></td>
<td width="33%"><img src="assets/brownian-finance.gif" alt="Brownian finance" /></td>
<td width="33%"><img src="assets/continuous-geometric-picture.gif" alt="Full GRPO semantic manifold" /></td>
</tr>
<tr>
<td><b>Whiskering exchange</b><br />Category-theoretic structure presented as a formal visual proof rhythm.</td>
<td><b>Brownian finance</b><br />A dark minimalist transition from calculus and integration toward measure, probability, and sample spaces.</td>
<td><b>Full GRPO semantic manifold</b><br />A complete 39-second arc: sibling completions become points on a response manifold, then preference turns the objective into motion.</td>
</tr>
<tr>
<td colspan="3"><img src="assets/qed-minkowski-epic-3d.gif" alt="QED Minkowski epic 3D" /></td>
</tr>
<tr>
<td colspan="3"><b>QED Minkowski epic 3D</b><br />A complete Math-To-Manim pipeline render on an off-white stage: Minkowski light cones become electromagnetic waves, then compact QED notation, gauge symmetry, and renormalization flow.</td>
</tr>
</table>

---

## Full asset inventory

| File | Theme | Description |
| --- | --- | --- |
| `assets/brownian-finance.gif` | Probability / finance | Calculus accumulation gives way to measure-theoretic uncertainty and sample-space intuition. |
| `assets/circle-area-3d-unwrapped.gif` | Geometry / calculus | X-video-inspired M2M2 render: nested circle annuli unwrap into a 3D triangular wedge proving A = 1/2(2πr)r = πr². |
| `assets/continuous-geometric-picture.gif` | ML / reinforcement learning | Full-length GRPO response-manifold recovery render: a 39-second geometric policy-update arc. |
| `assets/cosmic-gravity-3d.gif` | Physics | A cinematic spacetime-curvature scene with cosmic scale and documentary pacing. |
| `assets/derivative-visualization.gif` | Calculus | Foundational curve, axes, and local-linearization setup. |
| `assets/derivatives-as-slopes.gif` | Calculus | Secant-to-tangent reveal for the slope interpretation of derivatives. |
| `assets/fourier-epicycles.gif` | Fourier analysis | Rotating vectors compose a curve through epicycle motion. |
| `assets/grpo-explanation.gif` | ML / reinforcement learning | GRPO explained as a staged visual concept rather than a wall of notation. |
| `assets/grpo-semantic-manifold.gif` | ML / reinforcement learning | A shorter validated loop extracted from the full GRPO response-manifold render. |
| `assets/hopf-fibration.gif` | Topology | Dense colored fibers and projection geometry for the Hopf fibration. |
| `assets/lorenz-attractor.gif` | Dynamical systems | Glowing trajectories reveal the butterfly shape of the Lorenz attractor. |
| `assets/olin-off-white-3d-space.gif` | Generative art / geometry | Olin's ten thousand point sketch becomes an exact three dimensional lift before the film explores a separate cylindrical interpretation. |
| `assets/prolip-scene.gif` | Scientific networks | Molecular/protein interaction graphics with highlighted graph relationships. |
| `assets/quartic-torus-analysis.gif` | Topology / differential geometry | A full agent-pipeline render of a quartic torus-like implicit surface, showing regularity, genus, curvature, and multi-view topology. |
| `assets/qed-minkowski-epic-3d.gif` | Quantum field theory / physics | Complete short Math-To-Manim pipeline render: Minkowski spacetime, light cones, electromagnetic waves, QED Lagrangian, gauge symmetry, and RG flow on an off-white 3D stage. |
| `assets/radius-of-convergence.gif` | Analysis | Function behavior and boundary markers make convergence intervals concrete. |
| `assets/rhombicosidodecahedron.gif` | Geometry | A polished 3D Archimedean solid with symmetry, depth, and color contrast. |
| `assets/teaching-hopf.gif` | Topology / pedagogy | A slower explanatory Hopf fibration sequence built for instruction. |
| `assets/whiskering-exchange.gif` | Category theory | A commutative-diagram style treatment of the whiskering exchange law. |

---

## Using this gallery as a target

When M2M2 produces a successful MP4, promote the strongest beat into this gallery only after checking the loop visually. A good showcase GIF should have:

1. a clear teaching moment;
2. legible text at README size;
3. a stable palette and no broken frames;
4. a short enough loop to scan quickly;
5. a description that explains the concept, not just the file name.

The root README includes an FFmpeg recipe for palette-optimized GIF creation.

---

## Credits

Animations originate from [HarleyCoops/Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim) and are duplicated locally in M2M2 for documentation, continuity, and art direction.
