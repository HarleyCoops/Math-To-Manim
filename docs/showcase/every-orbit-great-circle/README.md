# Every Orbit Is a Great Circle

A planet's position traces an ellipse, but its velocity traces a circle.
Lift those velocity circles onto a sphere and every orbit of one energy
becomes a great circle. An orbit's eccentricity is then the sine of that
circle's tilt, and changing an orbit's shape without changing its energy is
a rotation of the sphere.

[Full movie](../assets/every-orbit-great-circle.mp4) ·
[Preview GIF](../assets/every-orbit-great-circle.gif) ·
[Contact sheet](../assets/every-orbit-great-circle-contact-sheet.png) ·
[Manim source](../../../examples/mythos/every_orbit_great_circle.py) ·
[Production request](../../prompts/every-orbit-great-circle.md)

**166.4 s, rendered at 1920 × 1080, 60 fps.** The committed MP4 is
re-encoded at 30 fps (9.1 MB) to keep the repository small; the 60 fps
master stays in the run directory.

## The argument, act by act

| Act | What the viewer sees | The claim |
|---|---|---|
| 1 | Twelve velocity arrows stamped around an e = 0.6 orbit slide tail to tail; their tips land on a circle. | Hamilton (1846): the velocity always runs around a circle, $\vec v=\frac{GM}{h}(-\sin\theta,\;e+\cos\theta)$. |
| 2 | Five orbits with e = 0, 0.3, 0.55, 0.75, 0.9 and equal long axes; the planets leave perihelion together and return together. | $E=-\frac{GM}{2a}$ and $T=2\pi\sqrt{a^3/GM}$ depend on $a$ alone. |
| 3 | The five velocity circles, all through the same two gold points, and the right triangle formed by the origin, a circle's center and a hinge point. | $R^2=d^2+p_0^2$ with $p_0=\sqrt{-2E}$: Pythagoras. |
| 4 | The plane tilts, a glass sphere of radius $p_0$ rises, rays from the north pole carry each circle onto the sphere. | Stereographic projection turns each circle into a great circle hinged on the two points. |
| 5 | Seen down the hinge, every ring is a line; the camera dives 3× into α; the ring stands up through the pole. | $e=\sin\alpha$; the head-on collision orbit is the ring through the north pole (Moser, 1970). |
| 6 | One ring rotates while an inset redraws its orbit; runners circle the rings under the title. | Earth, e = 0.0167, tilts 0.96°; Halley's comet, e = 0.967, tilts 75.3°. Fock (1935): the four-dimensional version explains hydrogen's $n^2$ degeneracy. |

Every number and identity above is checked in
[`tests/test_every_orbit_great_circle.py`](../../../tests/test_every_orbit_great_circle.py):
Kepler's equation, the synchronized return after $2\pi$, the hodograph
circle, equal energy $E=-\tfrac12$ across the family, the hinge points, the
lift to unit-sphere great circles with tilt $\arcsin e$, and the quoted
angles.

## How it was made

This film is a run of the **Mythos six-agent chain** (`mythos/harness.py`)
with a Claude session as the model backend. For each stage the operator
received the exact prompt the harness builds (the stage charter, the
previous artifact, the JSON contract, and the Cinematic Charter as system
text; each saved as `NN_*.prompt.txt` in the run directory) and wrote the
reply. The harness's own checks judged the replies:
`validate_stage_artifact` for each stage, the versioned manifest schema and
the static scene checks (AST, LaTeX fragments, charter lint).
[`scripts/operate_mythos_chain.py`](../../../scripts/operate_mythos_chain.py)
runs the chain the same way for any operator. Previews and the final film
were rendered by calling Manim directly: the harness renderer's 600-second
CPU limit is too short for a 1080p film.

| Stage | Artifact |
|---|---|
| 1 Intent | [01_intent.json](01_intent.json) |
| 2 Cartographer | [02_knowledge_map.json](02_knowledge_map.json) |
| 3 Curriculum | [03_curriculum.json](03_curriculum.json) |
| 4 Math director | [04_math_dossier.json](04_math_dossier.json) |
| 5 Cinematographer | [05_shot_list.json](05_shot_list.json) |
| 6 Scene composer | [06_scene_spec.json](06_scene_spec.json) |
| Codegen | [the scene](../../../examples/mythos/every_orbit_great_circle.py) |
| Render review | [08_review.json](08_review.json) |

The stage artifacts are kept exactly as the chain produced them. Four review
passes over rendered frames changed the scene code afterwards; each change
and the frame evidence behind it is in `08_review.json`. The run manifest is
[manifest.json](manifest.json).

## Rendering technique

The film uses Manim's Cairo `ThreeDScene` with its built-in shading turned
off. All lighting is computed in the scene, per frame, from the true camera
position:

- **Glass sphere.** 2,592 faces carry Lambert key light, a faint sky
  reflection on upward faces, a broad specular sheen and a weak Fresnel term.
  The sharp highlight is a camera-facing billboard at the half-vector point,
  and the rim glow is drawn at the sphere's exact perspective silhouette.
- **Rings on the glass.** Each great circle is split every frame into runs
  facing toward and away from the camera. Front runs draw on top; back runs
  are depth-sorted at the sphere's center, so the near half of the glass
  veils them.
- **Astrolabe plate.** The velocity plane stays as a plate of fine rings and
  ticks, built from depth-sorted segments so the sphere occludes it
  correctly.
- **Stars and planets.** Glows are nested camera-facing disks whose combined
  opacity follows a smooth falloff. Each planet's highlight is offset toward
  the star. Comet trails fade along their own chord.
- **Honest motion.** Planets move by Kepler's equation (Newton's method on
  $M=E-e\sin E$), so they whip around perihelion and linger at aphelion.
  The runners on the rings move at the rate the same equation gives.
- **Sky.** A procedural background pixel array: a faint central lift,
  vignette and about 800 stars. No image files are read.

## Render and verification

The final render ran as three animation ranges: `manim -qh -n 0,79` and
`-n 80,99` in parallel on two cores (21 minutes), then `-n 100,999` for the
last eight animations (8 minutes). The ranges were joined with FFmpeg's
concat demuxer without re-encoding; frames on either side of each join
match. FFprobe reports
166.4 s at 1920 × 1080 and 60 fps, and FFmpeg decoded the joined file
without errors. The contact sheet samples the actual movie.

No Jev or Astra review was run on this film; it is a Mythos-chain film
reviewed by the operator from rendered frames.
