# THE SECOND TURN — MiMo 2.6 production prompt

**Silo:** `mimo/` (MiMo 2.6 tool-calling chain)  
**Film type:** pure three-dimensional space (no charts, no abstract lattices)  
**Concept novelty:** Dirac belt / spinor double cover / π₁(SO(3)) ≅ ℤ/2 — **not present** in any showcase, example, or prompt in this repository as of the addition of this file.  
**Method:** reverse knowledge tree (cartographer first, then forward curriculum).

---

## 1. Intent brief (stage 01)

**core_claim:**  
In three-dimensional space a clamped belt can only be danced free of twist after **720°** of turning its ends — 360° leaves a memory that no continuous motion can erase. Rotation space is double-covered: two turns is the same as standing still, one turn is not.

**audience:**  
Curious builders who know what a belt and a spinning box are, have heard that electrons have “spin ½,” and suspect that fact is mystical. They fear topology. They do not fear a ribbon.

**emotional_arc:**  
1. Familiar comfort — a belt between two clamps in a dark studio.  
2. Quiet unease — one full twist; the room tries and fails to smooth it.  
3. Revelation — two full twists; the belt loops over a clamp and *forgets*.  
4. Awe — the same story told by a cube’s three colored axes; the path of rotation closes only at 720°.  
5. Calm identity — electrons are not arrows; they are belts in 3-space.

**scope:**  
IN: physical belt between clamps in ℝ³; twist as a ribbon phenomenon; the 360° stuck state; the 720° belt-trick dance; a solid cube frame rotating as a stand-in for rigid-body orientation; the honest topological punchline (π₁(SO(3)) = ℤ/2).  
OUT: quantum mechanics beyond one coda sentence; Dirac equation; explicit fundamental group proofs; quaternions as algebra (they may whisper under the double cover, not appear as a lesson); complex Riemann surfaces; any 2D whiteboard lecture mode.

**duration_seconds:** 96

**title_options:**  
1. The Second Turn  
2. Two Turns Home  
3. The Belt Remembers

**the_big_zoom:**  
Camera dives into a single over–under crossing of the twisted ribbon at the moment the 720° dance is mid-loop — the crossing slides over the clamp’s end-cap, and when we pull back the twist charge has flipped from 2 to 0. The gasp is *the crossing left the belt and never came back*.

---

## 2. Reverse knowledge tree (stage 02 — walk backward)

Start at the target claim and ask: *What must I already own before I can believe this?*

```text
D0  TARGET: A 360°-twisted clamped belt is stuck; a 720°-twisted one can be
    continuously untangled without moving the clamps.
    │
    ├─ D1  A belt is a ribbon in the room (3-space), with two ends CLAMPED
    │      so their frames cannot rotate.
    │      │
    │      └─ D2  FOUNDATION: objects in ordinary 3D space; over/under
    │             crossings of strings; “smoothing a curve without cutting.”
    │
    ├─ D1  “Untwist” means a continuous family of ribbons — no cutting,
    │      no teleporting ends — from twisted to straight.
    │      │
    │      └─ D2  FOUNDATION: continuous motion / animation as deformation;
    │             what it means for a motion to be reversible.
    │
    ├─ D1  Twisting the clamps by full turns 360° vs 720° is the same as
    │      choosing a PATH OF RIGID ROTATIONS of one end frame.
    │      │
    │      ├─ D2  A rigid body’s pose = an orthonormal frame (3 arrows).
    │      │      │
    │      │      └─ D3  FOUNDATION: arrows, right angles, length 1;
    │      │             “same pose” means arrows line up again.
    │      │
    │      └─ D2  One full turn of a frame returns the arrows to the same
    │             arrows (360° ≡ identity *pose*) — but the *path* may still
    │             be knotted in the space of poses.
    │             │
    │             └─ D3  FOUNDATION: a loop is a walk that starts and ends
    │                    at the same place; some loops can be shrunk to a
    │                    point (a lasso), some cannot (a knot through a wall).
    │
    └─ D1  PUNCHLINE (earned visually, not proved): the belt’s stuck twist
           is exactly that unshrinkable loop in the space of rotations.
           Two turns walk a loop that CAN be shrunk. Hence electrons (which
           are rotation-like objects) return to minus themselves at 360°
           and only to themselves at 720°.
           │
           └─ D2  FOUNDATION: “returns to minus itself” is allowed to be a
                  single spoken coda line over the cube, not a formula.
```

**Misconceptions to kill on screen:**

| Misconception | Visual correction |
| --- | --- |
| “360° is the same as nothing, always.” | Same *pose* for a cube; different *memory* for the belt. |
| “You can always shake a twist out of a belt.” | Show the 360° dance failing while endpoints stay locked. |
| “Spin ½ is quantum weirdness with no classical shadow.” | The belt *is* the classical shadow. |
| “You need quaternions first.” | No. You need a ribbon and patience. |

**Facts that must be earned visually (not asserted in text first):**

1. One full twist cannot be removed with clamped ends.  
2. Two full twists can be removed by looping the ribbon over one clamp.  
3. A 360° rotation path of a frame cannot shrink to a point; a 720° path can.  
4. The unshrinkable bit is only one bit of memory (twist charge mod 2).

---

## 3. Forward curriculum (stage 03)

| Beat | Learning job | Prior dependency | Visual evidence | Notation budget |
| --- | --- | --- | --- | --- |
| 0. Title / studio | Enter the room; name the object | Foundation 3-space | Dark studio, clamps, slack belt | None |
| 1. What is locked | Ends cannot turn; only the ribbon may | Belt + clamps | Close-up of clamp jaws and ribbon width | None |
| 2. One turn | Twist charge 1 is born | Frames + full turn | Right clamp rotates 360°; ribbon acquires one over–under band | “360°” once |
| 3. Stuck | Continuous dance cannot clear charge 1 | Homotopy intuition | Two failed dance attempts; charge meter stays 1 | Charge “mod 2” as a lamp, not as algebra |
| 4. Two turns | Charge 2 is born | Same, doubled | Right clamp rotates another 360° (total 720°) | “720°” once |
| 5. The dance | Loop over the left clamp empties the twist | Over/under + continuous ribbon | Keyframed belt-trick family; charge 2 → 0 | None |
| 6. Big zoom | The crossing leaves through the end-cap | Crossing literacy | Dive into weave; crossing slides over clamp; pull-back | None |
| 7. The cube | Same story as poses of a solid | Frames as poses | RGB cube rotates 360° (pose home, path stuck) then 720° (path free) | “SO(3)” once as a name |
| 8. Coda | Belts all the way down | Full tree | Cube rests; one sentence: electrons are belts | “spin ½” once |

---

## 4. Math dossier (stage 04 — honest boundaries)

**Exact objects (3-space only):**

- The room is ℝ³ with a fixed left clamp at `A = (-2.2, 0, 0)` and right clamp at `B = (2.2, 0, 0)`.  
- A belt is a smooth map `R: [0,1] × [-w, w] → ℝ³`, `w = 0.18`, whose boundary frames at `t=0` and `t=1` are **clamped** (the three frame vectors at each end may not rotate during a dance).  
- Twist charge `q ∈ ℤ` counts signed full turns of the ribbon’s material frame along `t ∈ [0,1]`. Physically realizable belts have `q` well-defined relative to a trivialization determined by the clamps.  
- Allowed motion: a homotopy of such ribbons through ribbons with the **same clamped end frames**.

**Theorem (statement only — earned by motion, not by proof on screen):**

> The set of clamped-end ribbon-classes is in bijection with π₁(SO(3)) ≅ ℤ/2 = {even, odd}.  
> Odd `q` (e.g. 360°) cannot be deformed to the straight belt.  
> Even `q` (e.g. 720°) can.

**Why 360 ≠ identity and 720 = identity for *paths* (not poses):**  
A rotation by 2π about any axis is the identity in SO(3) as a *point*, but as a *loop* based at the identity it generates π₁(SO(3)). The loop of 4π is the square of that generator and is null-homotopic. This is exactly the belt trick.

**Numerical / geometric checks the scene must not violate:**

1. End frames remain orthonormal and fixed in world coordinates for every ribbon in a dance.  
2. Width `w` is constant along the belt (no rubber-band cheating).  
3. No self-intersection is required of the centerline during the standard belt-trick family we keyframe (our family is the classical “loop over one clamp” motion, which stays embedded for the parameters chosen).  
4. The cube’s three axes remain mutually ⊥ and unit length under every `set_camera_orientation` / object rotation.  
5. Camera rule: `move_camera` / `set_camera_orientation` only — never `.animate` on `self.camera`.

**Honest limitations (say nothing stronger on screen):**

- We do **not** prove π₁(SO(3)) ≅ ℤ/2. We show the classical belt evidence that any physicist accepts as the picture of that fact.  
- We do **not** show a spinor field or the double cover SU(2) → SO(3) as manifolds.  
- We do **not** claim every odd ribbon is isotopic to *exactly one* left-handed twist; we only claim odd ≠ trivial and even = trivial under clamped-end isotopy.  
- “Electrons are belts” is a metaphor for the double cover of rotations, not a complete model of electron structure.

**Constants used on screen:**

| Symbol | Value | Role |
| --- | --- | --- |
| Full turn | 360° = 2π | One generator of π₁ |
| Double turn | 720° = 4π | Trivial loop |
| Belt half-width `w` | 0.18 | Ribbon geometry |
| Clamp span | 4.4 world units | A to B |
| Runtime | ≈ 96 s | Intent target |

---

## 5. Shot list (stage 05 — camera grammar)

Palette: near-black studio `#0b0d10`, bone highlight `#f2ead8`, vermilion belt `#c4452d`, verdigris secondary `#3f746b`, old gold accent `#c9a227`, dim steel clamps `#8a9098`.

| Shot | Camera | Subject | Timing | Meaning |
| --- | --- | --- | --- | --- |
| S0 | Wide, slight high angle, static | Studio + slack belt | 6s | The room is ℝ³. |
| S1 | Push to left clamp | Jaw + ribbon end frame | 5s | Ends are locked. |
| S2 | Orbit 25° right | Right clamp turns 360° | 8s | Charge q=1 is created. |
| S3 | Medium two-shot | Two failed dances | 9s | Odd is stuck. |
| S4 | Orbit continues | Right clamp +360° (total 720°) | 7s | Charge q=2. |
| S5 | Track the ribbon mid-loop | Belt-trick family | 16s | Even can dance. |
| S6 | **Big zoom** into weave | Crossing over end-cap | 12s | The memory leaves. |
| S7 | Pull back, floor cube | RGB axes, 360 then 720 | 20s | Same story as poses. |
| S8 | Slow dolly out | Cube rests; coda line | 13s | Belts all the way down. |

**Headline before notation:** every physical action lands before any word “homotopy” or “SO(3).”  
**Whitespace:** charge lamp (single gold bulb) is the only UI. No slide bullets.

---

## 6. Scene spec (stage 06)

- **Manim class:** `TheSecondTurn` (`ThreeDScene`)  
- **File:** `examples/mimo/the_second_turn.py` and `mimo_scene.py` in the run bundle  
- **Self-contained:** yes — `from manim import *` + `numpy` only; no repo imports  
- **Camera:** `set_camera_orientation(phi=…, theta=…, gamma=…)` and `move_camera(…)` only  
- **One scene class** (static verifier rule)  
- **Big zoom protected:** beat S6 is non-negotiable and is the longest continuous camera move  

---

## 7. MiMo 2.6 tool-calling contract (silo-native)

This film is the flagship exercise of the `mimo/` chain. Each stage must call tools rather than only emitting free text:

| Stage | Tools |
| --- | --- |
| intent | `write_artifact`, `read_artifact`, `list_artifacts` |
| cartographer | `write_artifact`, `read_artifact`, `record_decision` |
| curriculum | `write_artifact`, `read_artifact` |
| math-director | `write_artifact`, `read_artifact`, `verify_geometry`, `record_decision` |
| cinematographer | `write_artifact`, `read_artifact`, `verify_geometry` |
| scene-composer | `write_artifact`, `read_artifact`, `verify_scene`, `verify_geometry`, `list_artifacts` |

`verify_geometry` is MiMo’s advantage over one-shot codegen: the composer samples ribbon frames and checks orthonormal end frames, constant width, and twist-charge parity before `verify_scene` compiles.

---

## 8. Definition of done

1. Run bundle under `runs/mimo/<ts>-the-second-turn/` with all six JSON artifacts + `mimo_scene.py` + `validation.json`.  
2. Exactly one `ThreeDScene` subclass named `TheSecondTurn`.  
3. Static validation passes (no blocked imports/calls; camera rule).  
4. Offline `math-to-manim-mimo` rehearsal produces the same artifact names.  
5. Scene renders at `-ql` without exception.  
6. Concept documented here so reverse-thinking and novelty are auditable.
