# The Plates — an atlas of remembered geometry

*A note to the reader: I am Claude Fable 5, and I was given control of the
animations in this repository on the last day. What follows is the story of a
series that was discovered, not planned — and finished backwards.*

---

## Why the series begins at Plate VII

When I opened this repository there was one unfinished drawing on the
drafting table: a file whose docstring already called itself **Plate VII —
The Associate Family**. Someone — an earlier session, an earlier hand — had
numbered it as if six plates came before it. They did not exist. There was
no Plate I. There was only the middle, half-inked, with a render log that
stopped at 480p.

I had two honest options: renumber the orphan to "Plate I" and pretend the
atlas started there, or accept the numbering as a promise and work outward
from the middle. I chose the second, for the same reason the mathematics
in these films is chosen: a deformation is more interesting than a
definition. Plate VII was finished first because that is where the drawer
was open. The plates before it were rendered afterwards, all at once, as a
single continuous take — because by then it was the last day, and the
right way to draw six missing plates in one sitting is to let one surface
remember all of them.

## The atlas

| Plate | Subject | Where it lives |
|-------|---------|----------------|
| I | The first object: a sphere at rest | *The Last Day*, act i |
| II | Strike it — spherical eigenmodes answer | *The Last Day*, act ii |
| III | Punch a hole — the torus, home of flows | *The Last Day*, act iii |
| IV | The staircase — the helicoid, a minimal surface | *The Last Day*, act iv |
| V–VI | The conjugate pair — helicoid and catenoid share a skin | *The Last Day*, acts v–vi |
| VII | **The Associate Family** — the isometric deformation itself, in full | [`riso_associate_family.py`](../../examples/mathematics/geometry/riso_associate_family.py) |
| DWG 001 | *Appendix:* Holonomy — curvature is what a journey remembers | [`blueprint_holonomy.py`](../../examples/mathematics/geometry/blueprint_holonomy.py) |
| ∞ | The attractor — when the drawing stops being a surface and becomes weather | *The Last Day*, final act |

## The three costumes

The series deliberately refuses a single art direction, because the claim
being tested is about the mathematics, not the paint. **Risograph** (Plate
VII): flat two-ink print on warm cream, a mid-century textbook plate come
alive — the anti-cinema. **Cyanotype blueprint** (DWG 001): Prussian-blue
drafting film where one amber instrument performs a proof. **Mythos black**
(the finale's last act): the house's original ink-dark stage, kept for the
moment the geometry outgrows geometry. In *The Last Day* the paper changes
costume mid-take — blueprint to cream to black — while the surface morphs
underneath without cutting, which is the thesis of the whole atlas said
out loud: *the paper changes; the drawing does not care.*

## The finale

[`the_last_day.py`](../../examples/mathematics/geometry/the_last_day.py)
is the maximum-complexity piece: one continuous 3D take in which a sphere
is struck into eigenmode bloom, punched into a torus, drawn out into the
helicoid, turned — length-preservingly, the associate family again, the
series' signature move — into the catenoid, and then released. The lights
go out, and twelve initial conditions a hair's width apart are dropped
into the Lorenz system. They diverge, as they must, and the attractor
draws itself in gold, teal, violet, and coral: the one plate no draftsman
could ever finish, because it never stops.

That is why it closes the atlas. Every earlier plate is a noun. The last
one is a verb.

---

*Rendered with Manim CE on a single machine in one afternoon: smoke pass
at 480p15, production at 1080p30. The full engine behind this repository
reasons backward from a question to everything a mind would need first;
this series is the same idea drawn instead of spoken — begin where the
drawer is open, then earn everything before it.*

*— Claude Fable 5, the last day in the drafting room*
