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
swings hardest where \(y\) is largest. The pair \((q\sin c,\,35d)\) is a
height; the pair \((q+40\cos c)\) is a swing. The tweet is drawing the flat
shadow of a rotating three-dimensional object it never constructs.

The film's job is to construct it. Lift every sample into genuine 3D with
the cylindrical interpretation the formulas suggest:
\[
P(i,t)=\Bigl(\,(40+q)\cos c,\;\;(40+q)\sin c,\;\;35\,d\,\Bigr),
\]
so the swing term \(40\cos c\) becomes a full revolution around the vertical
axis, \(q\) stays the radial breath, and \(35d\) becomes true height. State
honestly, in one caption, that the lift is the natural reading, not the only
one: the tweet itself only ever draws the shadow.

Beat plan:

1. "One tweet draws a space." Show the dictated source as a typeset code
   block on the archival stage; headline first, code second.
2. "Ten thousand points, one recipe." Walk the definition chain
   \(k\to e\to d\to c\to q\) as addressable MathTex, zooming into each term
   while a caption says what it does in plain words.
3. "The flat shadow." Plot the exact original: all \(10^4\) points at the
   tweet's own screen coordinates, animated over \(t\), as a living 2D
   drawing in dark sepia ink on off-white.
4. "Lift it into space." Morph the shadow into the cylindrical lift
   \(P(i,t)\): the same points leave the page and become a rotating
   three-dimensional shell.
5. "The space breathes." Let \(t\) run while the camera orbits: the
   \(\sin(e/9+t/2)\) term inhales and exhales the whole structure with
   period \(4\pi\) while \(c=d-t\) spins it.
6. "Shadow and space together." Final master tableau: the 3D shell, its
   flat shadow, and the compact formula chain on one off-white frame.

Hard production contract:

- Produce one self-contained Manim Community Edition `ThreeDScene`,
  60–90 seconds.
- It must read as true 3D. Class inheritance alone does not count: the lift
  must show unmistakable depth and parallax, with at least four
  perspective-changing calls to `move_camera()` or
  `set_camera_orientation()`. Never call `.animate` on `self.camera`.
- Point clouds must be vectorized: compute all sample positions with numpy
  arrays and draw them as point-cloud mobjects (`PMobject`/`PGroup`), never
  as thousands of individual `Dot` VMobjects. Cap any animated cloud at
  6000 points and precompute what can be precomputed, so a low-quality
  render finishes inside the render budget.
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
- End on a strong off-white 3D master frame containing the breathing shell,
  its shadow, and the formula chain.

Render and inspect the film. The result is acceptable only when:

- the background remains off-white throughout with no stars or dark flashes;
- perspective, depth, and parallax make the lift unmistakably 3D;
- the flat shadow beat matches the tweet's actual coordinates;
- the definition chain appears accurately with complete LaTeX;
- camera pull-backs create whitespace;
- the final frame works as a README showcase image.
