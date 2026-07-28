# OLIN — THE OFF-WHITE 3D SPACE

Use the complete Claude Fable 5 Mythos pipeline, through the Claude Code CLI
subscription login, to create a gorgeous, mathematically faithful film about
the 3D space hiding inside one tweet-sized p5.js sketch.

The source. This entire generative artwork fits in one dictated formula:

```javascript
a=(y,d=mag(k=(4+cos(i/9-t*2))*cos(i/35),e=y/7-13)+sin(e/9+t/2)-4)=>
  point((q=2*sin(k*3)-y/35*k*(9+k*sin(cos(e)*9-d*2+t)))+40*cos(c=d-t)+200,
        q*sin(c)+d*35)
t=0,draw=$=>{t||createCanvas(w=400,w);background(9).stroke(w,96);
             for(t+=PI/80,i=1e4;i--;)a(i/235)}
```

The mathematics the film must earn. Each frame advances time by
\(\Delta t=\pi/80\) and replots \(10^4\) samples indexed by
\(i\in\{0,\dots,9999\}\) with \(y=i/235\). Every sample runs through one
chain of definitions:

\[
k=\bigl(4+\cos(i/9-2t)\bigr)\cos(i/35),
\qquad
e=\frac{y}{7}-13,
\]
\[
d=\sqrt{k^2+e^2}+\sin\!\Bigl(\frac{e}{9}+\frac{t}{2}\Bigr)-4,
\qquad
c=d-t,
\]
\[
q=2\sin(3k)-\frac{y}{35}\,k\Bigl(9+k\sin\bigl(9\cos e-2d+t\bigr)\Bigr),
\]
and lands on the canvas at
\[
\bigl(x,\,y_{\mathrm{screen}}\bigr)
=\bigl(q+40\cos c+200,\;\; q\sin c+35\,d\bigr).
\]

Read the chain out loud, in order: a carrier wave \(k\), a ladder coordinate
\(e\), a distance-with-breath \(d=\sqrt{k^2+e^2}+\text{breath}-4\), a spin
angle \(c=d-t\) that turns distance into rotation, and a flourish \(q\) that
swings hardest where \(y\) is largest. After removing the canvas offset,
write
\[
u=x-200=q+40\cos c,
\qquad
v=y_{\mathrm{screen}}=q\sin c+35d.
\]
The tweet supplies only \((u,v)\), so it does not determine a unique 3D
object. The film must distinguish an exact shadow-preserving embedding from a
separate cylindrical interpretation.

First lift every sample into genuine 3D with
\[
E(i,t)=\Bigl(q+40\cos c,\;40\sin c,\;q\sin c+35d\Bigr).
\]
The middle coordinate restores hidden depth while leaving the visible
coordinates untouched:
\[
\pi_{xz}\!\left(E(i,t)\right)
=\Bigl(q+40\cos c,\;q\sin c+35d\Bigr)=(u,v).
\]
This is an exact statement: an orthographic view down the \(y\)-axis
reproduces the centered tweet coordinates.

Only after proving that correspondence, show the more symmetric cylindrical
interpretation suggested by the formulas:
\[
C(i,t)=\Bigl((40+q)\cos c,\;(40+q)\sin c,\;35d\Bigr),
\]
so the swing term \(40\cos c\) becomes a full revolution around the vertical
axis, \(q\) becomes radial breath, and \(35d\) becomes true height. State
honestly, in one caption, that \(C\) is a cylindrical reinterpretation, not
the tweet's literal shadow source: unlike \(E\), \(C\) does not project back
to the tweet coordinates.

Beat plan:

1. "One tweet draws a space." Show the dictated source as a typeset code
   block on the archival stage; headline first, code second.
2. "Ten thousand points, one recipe." Walk the definition chain
   \(k\to e\to d\to c\to q\) as addressable MathTex, zooming into each term
   while a caption says what it does in plain words.
3. "The flat shadow." Plot the exact original at the tweet's own screen
   coordinates in dark sepia ink on off-white. Show all \(10^4\) points at
   one full-density reference frame, then animate a deterministic,
   evenly-spaced subset of at most 6000 samples over \(t\) using the exact
   same coordinate formula.
4. "Lift it exactly." Morph the shadow into \(E(i,t)\): the same visible
   coordinates leave the page only along the hidden \(y\)-axis. Orbit the
   camera, then return to the orthographic \(xz\) view so the points collapse
   exactly onto the tweet.
5. "A cylindrical reading." Deform \(E\) into \(C\) only after the exact
   projection has been earned. Label the change as an interpretation. Let
   \(t\) run while the camera orbits: the
   \(\sin(e/9+t/2)\) term inhales and exhales the whole structure with
   period \(4\pi\) while \(c=d-t\) spins it.
6. "Shadow and space together." Final master tableau: the exact lift \(E\),
   its \(xz\) projection, and the compact formula chain on one off-white
   frame. A small label may identify \(C\) as the alternate cylindrical
   reading, but it must not imply that \(C\)'s projection is the tweet.

Hard production contract:

- Produce one self-contained Manim Community Edition `ThreeDScene`,
  60–90 seconds.
- It must read as true 3D. Class inheritance alone does not count: the lift
  must show unmistakable depth and parallax, with at least four
  perspective-changing calls to `move_camera()` or
  `set_camera_orientation()`. Never call `.animate` on `self.camera`.
- Point clouds must be vectorized: compute all sample positions with numpy
  arrays and draw them as point-cloud mobjects (`PMobject`/`PGroup`), never
  as thousands of individual `Dot` VMobjects. The one static full-density
  shadow keyframe may contain all 10,000 samples. Every animated cloud must
  use the same deterministic, evenly-spaced subset of at most 6000 samples.
  Precompute what can be precomputed so a low-quality render finishes inside
  the render budget.
- Set every frame to archival off-white near `#f3ecd8`. This is an
  off-white film: the background is paper, never black, and there is no
  dark fallback between beats. Ink the points and text in dark sepia
  `#241a12`, with muted oxide red, verdigris, indigo, and old gold accents
  keyed consistently to \(k\), \(e\), \(d\), \(q\), and \(c\).
- Do not use a starfield, stars, black background, cosmic void, nebula, or
  deep-space motif.
- All displayed mathematics must use complete valid LaTeX. Build the
  definition chain from addressable `MathTex` parts.
- Headline before symbols. Zoom into the active term or 3D object, then
  pull back to restore context and create whitespace.
- Keep at most one headline or two short text blocks visible. Replace
  captions; never stack them.
- Geometry must carry the argument; do not place paragraphs on screen.
- Keep labels readable at a 720-pixel-wide README size.
- End on a strong off-white 3D master frame containing the exact lift, its
  shadow, and the formula chain.

Render and inspect the film. The result is acceptable only when:

- the background remains off-white throughout with no stars or dark flashes;
- perspective, depth, and parallax make the lift unmistakably 3D;
- the flat shadow beat matches the tweet's actual coordinates and the
  orthographic \(xz\) view of \(E\) reproduces them exactly;
- the film labels \(C\) as an alternate cylindrical interpretation and never
  presents its projection as the tweet;
- the definition chain appears accurately with complete LaTeX;
- camera pull-backs create whitespace;
- the final frame works as a README showcase image.
