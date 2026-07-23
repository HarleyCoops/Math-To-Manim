# ERDŐS 1038 — THE POTENTIAL LANDSCAPE

Use the complete GPT-5.6 Sol film pipeline to create a gorgeous,
mathematically faithful explanation of the proposed complete solution to
Erdős Problem 1038.

The problem. Let \(f\) range over all nonconstant monic real polynomials
whose roots, counted with multiplicity, lie in \([-1,1]\):
\[
f(x)=\prod_{j=1}^{n}(x-r_j),\qquad r_j\in[-1,1].
\]
Determine the infimum and supremum of
\[
E_f=\{x\in\mathbb R:|f(x)|<1\},\qquad |E_f|.
\]

The answer the film must earn is
\[
\inf_f |E_f|=L=1.834430475762661\ldots,
\qquad
\sup_f |E_f|=2\sqrt{2}.
\]
The lower value is not attained by any finite polynomial. It is the exact
number \(L=\Lambda(q_*)\), where \(q_*\) is the unique certified minimizer
described below. The upper value is attained exactly by
\[
f(x)=(x^2-1)^m,\qquad m\ge1.
\]

Use the proof's actual potential-theoretic spine. Introduce
\[
\mu_f=\frac1n\sum_{j=1}^{n}\delta_{r_j}
\]
and transform the polynomial into
\[
V_{\mu_f}(x)
=\int\log|x-t|\,d\mu_f(t)
=\frac1n\log|f(x)|.
\]
Therefore
\[
E_f=\{x:V_{\mu_f}(x)<0\}.
\]
Make this the central visual mechanism: roots become physical sources,
\(V_{\mu_f}\) becomes a sculpted 3D landscape, level \(0\) becomes a
translucent plane, and the footprint below it is exactly \(E_f\).

Visualize simultaneous component atomization. Root mass in each sublevel
component collapses to its barycentre. The potential outside rises, so the
negative region cannot grow:
\[
E_{\widetilde\mu}\subseteq E_\mu.
\]
Show an actual geometric before-and-after transformation.

Morph the finite atoms into the one-cut limiting measure
\[
\mu_q=A(q)\delta_{-1}+
\frac{t+1-2A(q)s(q)}
{\pi(t+1)\sqrt{(t-a(q))(1-t)}}
\mathbf 1_{(a(q),1)}\,dt,
\]
where
\[
H(q)=\frac{2q}{(1+q)^2},\qquad
s(q)=\frac{1-q}{1+q},\qquad
A(q)=\frac{\log H(q)}{\log q}.
\]
Give the endpoint atom and continuous density different but coherent 3D
forms.

Build
\[
\Lambda(q)=H(q)\left(
u_-(q)+u_-(q)^{-1}
-u_+(q)-u_+(q)^{-1}
\right)
\]
as a physical raised curve or valley. Travel along it and isolate
\[
0.025715536866527<q_*<0.025715536866528
\]
before revealing
\[
1.834430475762661<L<1.834430475762662.
\]
Explain that global comparison, circle rearrangement, and uniform parameter
certificates prove no finite root configuration can do better. The enclosure
is certified by directed outward interval arithmetic, not a sampled graph.
Do not imply that the scalar plot alone proves global optimality.

For the opposite extreme, transform the scene into equal endpoint masses at
\(-1\) and \(1\). Show that
\[
f(x)=(x^2-1)^m
\]
reduces the condition to
\[
|x^2-1|<1
\]
and gives width \(2\sqrt{2}\). Contrast the attained maximum with the
unattained lower limit in the final tableau.

Beat plan:

1. "The question has a shape." Introduce roots and \(E_f\).
2. "A polynomial becomes terrain." Reveal the potential, zero plane, and
   below-zero footprint.
3. "Collapse without expansion." Animate atomization and
   \(E_{\widetilde\mu}\subseteq E_\mu\).
4. "The limiting one-cut shape." Morph atoms into endpoint mass plus density.
5. "The certified floor." Travel along \(\Lambda(q)\), mark \(q_*\), reveal
   \(L\), state non-attainment, and name the certificate boundary.
6. "The opposite extreme." Expand to the endpoint-root maximizer and finish
   with both extremal values.

Hard production contract:

- Produce one self-contained Manim `ThreeDScene`, 60–90 seconds.
- It must read as true 3D. Class inheritance alone does not count. Use
  meaningful depth, raised root pillars or wells, a genuine potential surface
  or extruded ribbon, a translucent zero plane, a sculpted one-cut density,
  and a raised \(\Lambda(q)\) valley.
- Use at least four perspective-changing calls to `move_camera()` or
  `set_camera_orientation()` so parallax is unmistakable. Never call
  `.animate` on `self.camera`.
- Set every frame to archival off-white near `#f3ecd8`. Use dark sepia
  `#241a12` for text and axes, with muted oxide red, verdigris, indigo, and
  old gold accents.
- Do not use a starfield, stars, black background, cosmic void, nebula, or
  deep-space motif. Do not flash through a dark fallback between scenes.
- All displayed mathematics must use complete valid LaTeX. Build important
  formulas from addressable `MathTex` parts.
- Headline before symbols. Zoom into the active term or 3D object, then pull
  back to restore context and create whitespace.
- Keep at most one headline or two short text blocks visible. Replace
  captions; never stack them.
- Geometry must carry the argument; do not place paragraphs on screen.
- Keep labels readable at a 720-pixel-wide README size.
- End on a strong off-white 3D master frame containing the potential
  landscape, certified lower value, and endpoint-root maximum.

Render and inspect the film. Record frame/contact-sheet evidence and any
repairs in `review.json`. The result is acceptable only when:

- the background remains off-white throughout with no stars or dark flashes;
- perspective, depth, and parallax make the film unmistakably 3D;
- the zero plane and potential surface make \(E_f\) geometrically legible;
- atomization, \(\Lambda(q)\), the certified enclosure, non-attainment,
  \(2\sqrt{2}\), and \((x^2-1)^m\) appear accurately;
- every formula fits with complete LaTeX;
- camera pull-backs create whitespace;
- the final frame works as a README showcase image.
