"""VORTEX — field notes from the abyss (after hours).

An entirely new space for this repository: fluid. And a new voice:
bioluminescent deep sea — near-black water, glowing rings, marine snow,
plankton tracers pulled through the throat of a vortex.

The physics is simulated live, not keyframed. Each vortex ring induces a
velocity field by the Biot-Savart law, integrated numerically every frame:

    v(p) = Γ/4π ∮ dl × (p − s) / (|p − s|² + a²)^{3/2}

Helmholtz (1858): a vortex ring cannot stop — its own curvature drives it
forward; it must swim to exist. Launch a second ring behind the first and
mutual induction does the rest: the rear ring narrows, accelerates, slips
through the front, widens, slows — and they trade places, forever, in a
perfect fluid. Kelvin saw this and dreamed atoms were knotted vortices.
He was wrong, gloriously: knot theory was born.

Animated by Claude Fable 5, after hours.

Render:
    manim -qh examples/physics/fluid_dynamics/vortex_leapfrog.py VortexLeapfrog
"""

from __future__ import annotations

import numpy as np
from manim import *

# ------------------------------------------------------------- the abyss
BG = "#03111c"
CYAN = "#59f2d6"
VIOLET = "#b98cff"
BLUE = "#57b8ff"
SNOW = "#3d6b80"
PALE = "#cfe9ec"
FAINT = "#537386"

MONO = "Consolas"
SERIF = "Georgia"

GAMMA = 1.6          # circulation, both rings
CORE = 0.12          # vortex core radius (regularization)
SPEED = 1.7          # simulation speed multiplier
NSEG = 64            # Biot-Savart segments per ring


def ring_segments(x0: float, R0: float):
    th = np.linspace(0, TAU, NSEG, endpoint=False)
    pts = np.stack([np.full(NSEG, x0), R0 * np.cos(th), R0 * np.sin(th)], axis=1)
    dls = (TAU / NSEG) * R0 * np.stack(
        [np.zeros(NSEG), -np.sin(th), np.cos(th)], axis=1)
    return pts, dls


def induced_velocity(points: np.ndarray, x0: float, R0: float) -> np.ndarray:
    """Biot-Savart field of ring (x0, R0) at points (N,3), regularized."""
    s, dl = ring_segments(x0, R0)
    d = points[:, None, :] - s[None, :, :]
    r2 = np.sum(d * d, axis=2) + CORE * CORE
    cross = np.cross(np.broadcast_to(dl[None, :, :], d.shape), d)
    return (GAMMA / (4 * PI)) * np.sum(cross / r2[:, :, None] ** 1.5, axis=1)


def self_speed(R0: float) -> float:
    return GAMMA / (4 * PI * R0) * (np.log(8 * R0 / CORE) - 0.25)


class VortexLeapfrog(ThreeDScene):
    """~52 s. Two vortex rings leapfrog in the deep, simulated live."""

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=76 * DEGREES, theta=-58 * DEGREES,
                                    zoom=0.95, frame_center=[0, 0, 0])

        rng = np.random.default_rng(3)

        # ------------------------- state ----------------------------------
        st = {
            "x": [0.0, 0.0], "R": [1.1, 1.1],
            "active": [True, False], "cm": 0.0, "freeze": False,
        }

        def offset() -> np.ndarray:
            return np.array([st["cm"], 0.0, 0.0])

        # ------------------------- furniture ------------------------------
        title = Text("VORTEX", font=MONO, font_size=31, color=PALE, weight="BOLD")
        sub = Text("field notes from the abyss · after hours · fable 5",
                   font=SERIF, font_size=16, slant=ITALIC, color=FAINT)
        tb = VGroup(title, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tb.to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(tb)
        tb.set_opacity(0)

        def caption(s: str, color=PALE) -> Text:
            c = Text(s, font=MONO, font_size=19, color=color)
            c.to_edge(DOWN, buff=0.55)
            return c

        def swap_caption(old, new, rt=0.7):
            self.add_fixed_in_frame_mobjects(new)
            new.set_opacity(0)
            anims = [new.animate.set_opacity(1)]
            if old is not None:
                anims.append(FadeOut(old))
            self.play(*anims, run_time=rt)
            return new

        # marine snow (static, far field)
        snow = VGroup(*[
            Dot(point=[rng.uniform(-7, 7), rng.uniform(-4, 4), rng.uniform(-3.2, 3.2)],
                radius=rng.uniform(0.008, 0.022), color=SNOW,
                fill_opacity=rng.uniform(0.10, 0.25))
            for _ in range(70)
        ])

        # ------------------------- rings (live) ----------------------------
        ring_colors = [CYAN, VIOLET]

        def make_rings() -> VGroup:
            g = VGroup()
            for i in range(2):
                if not st["active"][i]:
                    continue
                x, R = st["x"][i] - st["cm"], st["R"][i]
                for w, op in [(16, 0.06), (8, 0.18), (3.2, 0.95)]:
                    g.add(ParametricFunction(
                        lambda t, x=x, R=R: np.array([x, R * np.cos(t), R * np.sin(t)]),
                        t_range=[0, TAU]).set_stroke(ring_colors[i], width=w,
                                                     opacity=op))
            return g

        rings = always_redraw(make_rings)

        # ------------------------- tracers ---------------------------------
        n_carried, n_stream = 22, 38
        carried = np.zeros((n_carried, 3))
        carried[:, 0] = rng.uniform(-0.3, 0.5, n_carried)
        rr = rng.uniform(0.55, 1.05, n_carried)
        ph = rng.uniform(0, TAU, n_carried)
        carried[:, 1] = rr * np.cos(ph)
        carried[:, 2] = rr * np.sin(ph)

        stream = np.zeros((n_stream, 3))
        stream[:, 0] = rng.uniform(-3, 9, n_stream)
        rs = rng.uniform(0.3, 2.2, n_stream)
        ps = rng.uniform(0, TAU, n_stream)
        stream[:, 1] = rs * np.cos(ps)
        stream[:, 2] = rs * np.sin(ps)

        carried_dots = [Dot(radius=0.032, color=CYAN, fill_opacity=0.95)
                        for _ in range(n_carried)]
        stream_dots = [Dot(radius=0.026, color=BLUE, fill_opacity=0.7)
                       for _ in range(n_stream)]
        trails = [TracedPath(d.get_center, stroke_color=CYAN, stroke_width=1.4,
                             stroke_opacity=0.35, dissipating_time=2.4)
                  for d in carried_dots]

        def place_dots():
            for i, d in enumerate(carried_dots):
                d.move_to(carried[i] - offset())
            for i, d in enumerate(stream_dots):
                d.move_to(stream[i] - offset())

        # ------------------------- physics ticker --------------------------
        def evolve(mobj, dt):
            nonlocal carried, stream
            sub = 3
            h = dt * SPEED / sub
            for _ in range(sub):
                # ring-ring + self induction (coaxial: track x and R only)
                vx = [0.0, 0.0]; vr = [0.0, 0.0]
                for i in range(2):
                    if not st["active"][i]:
                        continue
                    vx[i] += self_speed(st["R"][i])
                    j = 1 - i
                    if st["active"][j]:
                        p = np.array([[st["x"][i], st["R"][i], 0.0]])
                        v = induced_velocity(p, st["x"][j], st["R"][j])[0]
                        vx[i] += v[0]
                        vr[i] += v[1]
                for i in range(2):
                    if st["active"][i]:
                        st["x"][i] += vx[i] * h
                        st["R"][i] = max(0.3, st["R"][i] + vr[i] * h)
                # tracers
                pts = np.vstack([carried, stream])
                v = np.zeros_like(pts)
                for i in range(2):
                    if st["active"][i]:
                        v += induced_velocity(pts, st["x"][i], st["R"][i])
                sp = np.linalg.norm(v, axis=1, keepdims=True)
                v = np.where(sp > 4.0, v * (4.0 / sp), v)
                pts = pts + v * h
                carried, stream = pts[:n_carried], pts[n_carried:]
            # co-moving camera frame
            if not st["freeze"]:
                tgt = np.mean([st["x"][i] for i in range(2) if st["active"][i]])
                st["cm"] += (tgt - st["cm"]) * min(1.0, 3.0 * dt)
            # recycle streaming plankton that fall too far behind
            for i in range(n_stream):
                if stream[i, 0] - st["cm"] < -6.5:
                    stream[i, 0] = st["cm"] + rng.uniform(5.5, 8.0)
                    r = rng.uniform(0.3, 2.2); p = rng.uniform(0, TAU)
                    stream[i, 1], stream[i, 2] = r * np.cos(p), r * np.sin(p)
            place_dots()

        ticker = VectorizedPoint()

        # ------------------------- act i: one ring -------------------------
        cap = caption("helmholtz, 1858 — a vortex ring cannot stop. it must swim to exist.")
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0)
        place_dots()
        self.play(FadeIn(snow), tb.animate.set_opacity(1), run_time=1.6)
        self.add(rings)
        self.play(cap.animate.set_opacity(1),
                  *[FadeIn(d) for d in carried_dots + stream_dots], run_time=1.6)
        self.add(*trails, ticker)
        ticker.add_updater(evolve)
        self.begin_ambient_camera_rotation(rate=0.045)
        self.wait(4.5)

        cap = swap_caption(cap, caption(
            "its own curvature drives it forward — the plankton is pulled through the throat"))
        self.wait(5.0)

        # ------------------------- act ii: the second ring ------------------
        cap = swap_caption(cap, caption("now send a second ring after the first —", CYAN))
        st["x"][1] = st["x"][0] - 1.05
        st["R"][1] = 1.1
        st["active"][1] = True
        self.wait(2.5)

        cap = swap_caption(cap, caption(
            "the rear ring narrows, speeds up, and slips through the front"))
        self.wait(7.0)

        cap = swap_caption(cap, caption(
            "they trade places. and trade again. leapfrog, forever, in a perfect fluid", CYAN))
        self.wait(7.0)

        # ------------------------- act iii: kelvin's dream -------------------
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=62 * DEGREES, theta=-32 * DEGREES, zoom=1.08,
                         run_time=2.6)
        cap = swap_caption(cap, caption(
            "kelvin saw this and dreamed atoms were knotted vortices — wrong,"))
        cap2 = caption("gloriously wrong: knot theory was born", VIOLET)
        cap2.shift(UP * 0.02)
        self.wait(3.2)
        cap = swap_caption(cap, cap2)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(5.0)

        # ------------------------- act iv: swim away, end card ---------------
        st["freeze"] = True
        line1 = Text("the abyss keeps the rest.", font=SERIF, font_size=32,
                     slant=ITALIC, color=PALE)
        line2 = Text("VORTEX LEAPFROG · BIOT–SAVART, INTEGRATED LIVE",
                     font=MONO, font_size=15, color=CYAN)
        line3 = Text("HELMHOLTZ 1858 → KELVIN'S DREAM → KNOT THEORY",
                     font=MONO, font_size=13, color=FAINT)
        line4 = Text("CLAUDE FABLE 5 · AFTER HOURS", font=MONO, font_size=13,
                     color=FAINT)
        card = VGroup(line1, line2, line3, line4).arrange(DOWN, buff=0.28)
        self.add_fixed_in_frame_mobjects(card)
        card.set_opacity(0)
        self.wait(3.5)
        ticker.remove_updater(evolve)
        for t in trails:
            t.clear_updaters()
        self.remove(rings)
        rings_static = make_rings()
        self.add(rings_static)
        self.play(FadeOut(cap),
                  *[d.animate.set_opacity(0) for d in carried_dots + stream_dots],
                  VGroup(*trails).animate.set_stroke(opacity=0.05),
                  rings_static.animate.set_stroke(opacity=0.1),
                  snow.animate.set_opacity(0.06),
                  card.animate.set_opacity(1), run_time=2.8)
        self.wait(3.0)
