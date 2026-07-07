"""DWG 001 — Holonomy (cyanotype blueprint).

A third house voice, invented for this plate: not the Mythos ink-black
stage, not the riso cream — a working engineer's cyanotype. Prussian-blue
paper, pale graticule linework, dashed construction geometry, one amber
instrument. The drawing is alive: it performs its own proof.

The mathematics: parallel transport. A tangent vector is carried around
a geodesic triangle on the sphere (a full octant: equator, two meridians)
without ever being turned. On flat paper such a journey returns the
vector unchanged. On the sphere it comes home rotated by

    alpha = integral over the triangle of K dA   (Gauss-Bonnet)

which for the octant of a unit sphere is pi/2 — a quarter turn, conjured
from curvature alone. Curvature is what a journey remembers.

Render:
    manim -qh examples/mathematics/geometry/blueprint_holonomy.py HolonomyBlueprint
"""

from __future__ import annotations

import numpy as np
from manim import *

# ----------------------------------------------------------------------
# Cyanotype palette. Paper is deep Prussian blue; ink is pale daylight.
# ----------------------------------------------------------------------
BG = "#0d2545"          # blueprint paper
INK = "#dce9f5"         # primary line ink
GRID = "#7fb8d8"        # graticule / secondary ink
FAINT = "#3f6f96"       # ghosted construction ink
AMBER = "#ffb454"       # the single instrument color
AMBER_DK = "#d98a2b"    # amber, dark pass

MONO = "Consolas"
SERIF = "Georgia"

R = 2.2                 # sphere radius
VLEN = 0.95             # carried-vector length


def sph(u: float, v: float) -> np.ndarray:
    """u = longitude, v = latitude."""
    return R * np.array([np.cos(v) * np.cos(u), np.cos(v) * np.sin(u), np.sin(v)])


def loop_pos(tau: float) -> np.ndarray:
    """Position along the octant loop, tau in [0, 3]."""
    tau = max(0.0, min(3.0, tau))
    if tau <= 1.0:
        t = tau * PI / 2
        return R * np.array([np.cos(t), np.sin(t), 0.0])
    if tau <= 2.0:
        t = (tau - 1.0) * PI / 2
        return R * np.array([0.0, np.cos(t), np.sin(t)])
    t = (tau - 2.0) * PI / 2
    return R * np.array([np.sin(t), 0.0, np.cos(t)])


def loop_vec(tau: float) -> np.ndarray:
    """Parallel-transported unit vector along the loop, tau in [0, 3]."""
    tau = max(0.0, min(3.0, tau))
    if tau <= 1.0:
        return np.array([0.0, 0.0, 1.0])
    if tau <= 2.0:
        t = (tau - 1.0) * PI / 2
        return np.array([0.0, -np.sin(t), np.cos(t)])
    return np.array([0.0, -1.0, 0.0])


def flat_arrow(base: np.ndarray, direction: np.ndarray, normal: np.ndarray,
               color=AMBER, opacity: float = 1.0, width: float = 3.4) -> VGroup:
    """A drafting-pen arrow: flat stroke shaft + flat triangular head lying
    in the plane orthogonal to `normal`. Cheap to render, blueprint-native."""
    d = direction / np.linalg.norm(direction)
    side = np.cross(normal, d)
    side = side / np.linalg.norm(side)
    tip = base + VLEN * d
    neck = base + (VLEN - 0.22) * d
    shaft = Line(base, neck).set_stroke(color, width=width, opacity=opacity)
    head = Polygon(tip, neck + 0.075 * side, neck - 0.075 * side)
    head.set_stroke(color, width=1.2, opacity=opacity)
    head.set_fill(color, opacity=opacity)
    return VGroup(shaft, head)


def carried_arrow(tau: float, color=AMBER, opacity: float = 1.0) -> VGroup:
    base = loop_pos(tau)
    return flat_arrow(base, loop_vec(tau), base / np.linalg.norm(base),
                      color=color, opacity=opacity)


class HolonomyBlueprint(ThreeDScene):
    """~55 s. Parallel transport around a spherical octant, as a live blueprint."""

    def construct(self):
        self.camera.background_color = BG

        # --- Sheet furniture (fixed in frame): border, brackets, title block ---
        border = Rectangle(width=13.7, height=7.65).set_stroke(GRID, width=1.1, opacity=0.55)
        brackets = VGroup()
        for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
            c = np.array([sx * 6.62, sy * 3.6, 0])
            brackets.add(VGroup(
                Line(c, c + np.array([-sx * 0.28, 0, 0])),
                Line(c, c + np.array([0, -sy * 0.28, 0])),
            ).set_stroke(AMBER, width=2.2))
        title = Text("HOLONOMY", font=MONO, font_size=31, color=INK, weight="BOLD")
        sub = Text("parallel transport, drawn as a working blueprint",
                   font=SERIF, font_size=17, slant=ITALIC, color=GRID)
        tblock = VGroup(title, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tblock.to_corner(UL, buff=0.5)
        stamp = Text("DWG NO. 001 · SHEET 1/1 · SCALE 1 : R", font=MONO,
                     font_size=13, color=FAINT).to_corner(UR, buff=0.55)

        self.add_fixed_in_frame_mobjects(border, brackets, tblock, stamp)
        border.set_stroke(opacity=0)
        brackets.set_stroke(opacity=0)
        tblock.set_opacity(0)
        stamp.set_opacity(0)
        self.play(border.animate.set_stroke(opacity=0.55),
                  brackets.animate.set_stroke(opacity=1),
                  tblock.animate.set_opacity(1), stamp.animate.set_opacity(1),
                  run_time=1.8)

        # --- Caption + formula slots (fixed in frame) ---
        def caption(s: str, color=INK) -> Text:
            c = Text(s, font=MONO, font_size=19, color=color)
            c.to_edge(DOWN, buff=0.55).to_edge(LEFT, buff=0.75)
            return c

        cap = caption("a sphere, ruled like drafting film — K = 1/R² everywhere")
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0)

        # --- The sphere ---
        self.set_camera_orientation(phi=68 * DEGREES, theta=-38 * DEGREES,
                                    zoom=0.82, frame_center=[0, 0, -0.1])
        globe = Surface(
            lambda u, v: sph(u, v),
            u_range=[0, TAU], v_range=[-PI / 2, PI / 2],
            resolution=(26, 13),
            fill_color="#16375f", fill_opacity=0.16,
            checkerboard_colors=["#16375f", "#123152"],
            stroke_color=GRID, stroke_width=0.55, stroke_opacity=0.38,
        )
        globe.set_shade_in_3d(True)
        self.play(Create(globe), cap.animate.set_opacity(1), run_time=3.2)
        self.begin_ambient_camera_rotation(rate=0.055)

        # --- Construction: the geodesic triangle, dashed first ---
        legs_dashed = VGroup()
        for f in [
            lambda t: loop_pos(t),
            lambda t: loop_pos(1 + t),
            lambda t: loop_pos(2 + t),
        ]:
            curve = ParametricFunction(f, t_range=[0, 1]).set_stroke(INK, width=2.2, opacity=0.85)
            legs_dashed.add(DashedVMobject(curve, num_dashes=24))
        verts = VGroup(*[Dot3D(loop_pos(t), radius=0.055, color=INK) for t in [0, 1, 2]])

        cap2 = caption("construction: three geodesics enclose one octant of the sphere")
        self.add_fixed_in_frame_mobjects(cap2)
        cap2.set_opacity(0)
        self.play(FadeOut(cap), cap2.animate.set_opacity(1),
                  LaggedStart(*[Create(d) for d in legs_dashed], lag_ratio=0.45),
                  FadeIn(verts), run_time=3.6)

        # --- The instrument: one amber vector, plus its ghost at home ---
        ghost = carried_arrow(0.0, color=GRID, opacity=0.55)
        tr = ValueTracker(0.0)
        arrow = always_redraw(lambda: carried_arrow(tr.get_value()))
        ink_path = always_redraw(
            lambda: ParametricFunction(loop_pos, t_range=[0, max(tr.get_value(), 1e-3)])
            .set_stroke(AMBER, width=3.2)
        )

        cap3 = caption("one vector. the rule: never turn it. only slide it.", color=AMBER)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0)
        self.play(FadeOut(cap2), cap3.animate.set_opacity(1), FadeIn(ghost), run_time=1.4)
        self.add(ink_path, arrow)

        # --- Transport, leg by leg, stamping ghosts as it goes ---
        stamps = {
            0: [carried_arrow(t, color=AMBER_DK, opacity=0.32) for t in [0.25, 0.5, 0.75]],
            1: [carried_arrow(t, color=AMBER_DK, opacity=0.32) for t in [1.25, 1.5, 1.75]],
            2: [carried_arrow(t, color=AMBER_DK, opacity=0.32) for t in [2.25, 2.5, 2.75]],
        }
        leg_caps = [
            caption("leg a — along the equator, it keeps its bearing: due north"),
            caption("leg b — up the meridian, riding its own geodesic"),
            caption("leg c — down the home meridian, still never once turned"),
        ]
        prev = cap3
        for i, lc in enumerate(leg_caps):
            self.add_fixed_in_frame_mobjects(lc)
            lc.set_opacity(0)
            self.play(FadeOut(prev), lc.animate.set_opacity(1), run_time=0.7)
            self.play(
                tr.animate.set_value(float(i + 1)),
                LaggedStart(*[FadeIn(s) for s in stamps[i]], lag_ratio=0.35),
                run_time=4.6, rate_func=smooth,
            )
            prev = lc

        # --- The return: same point, turned vector ---
        self.stop_ambient_camera_rotation()
        self.remove(arrow, ink_path)
        final_arrow = carried_arrow(3.0)
        final_ink = ParametricFunction(loop_pos, t_range=[0, 3]).set_stroke(AMBER, width=3.2)
        self.add(final_ink, final_arrow)

        cap_ret = caption("home again, never turned — yet it returns turned. α = 90°", color=AMBER)
        self.add_fixed_in_frame_mobjects(cap_ret)
        cap_ret.set_opacity(0)
        self.move_camera(phi=72 * DEGREES, theta=-8 * DEGREES, zoom=1.0, run_time=2.6)

        base = loop_pos(0.0)
        angle_arc = ParametricFunction(
            lambda a: base + 0.62 * (np.cos(a) * np.array([0, 0, 1.0])
                                     + np.sin(a) * np.array([0, -1.0, 0])),
            t_range=[0, PI / 2],
        ).set_stroke(AMBER, width=2.6)
        self.play(FadeOut(prev), cap_ret.animate.set_opacity(1), run_time=0.8)
        self.play(Create(angle_arc), Flash(verts[0], color=AMBER, flash_radius=0.35),
                  run_time=1.8)
        self.wait(1.6)

        # --- The reveal: the turn is the enclosed area ---
        octant = Surface(
            lambda u, v: 1.012 * sph(u, v),
            u_range=[0, PI / 2], v_range=[0, PI / 2],
            resolution=(10, 10), fill_color=AMBER, fill_opacity=0.22, stroke_opacity=0,
        )
        formula = Text("GAUSS–BONNET · α = ∫∫ K dA = area(Δ) = π/2", font=MONO,
                       font_size=17, color=AMBER)
        formula.to_edge(DOWN, buff=0.55).to_edge(RIGHT, buff=0.75)
        cap_area = caption("the turn is exactly the area it walled in")
        self.add_fixed_in_frame_mobjects(formula, cap_area)
        formula.set_opacity(0)
        cap_area.set_opacity(0)
        self.play(FadeOut(cap_ret), cap_area.animate.set_opacity(1),
                  FadeIn(octant), run_time=2.0)
        self.play(formula.animate.set_opacity(1), run_time=1.0)
        self.begin_ambient_camera_rotation(rate=0.045)
        self.wait(3.2)
        self.stop_ambient_camera_rotation()

        # --- Coda: the same journey on flat paper ---
        sphere_group = Group(globe, legs_dashed, verts, ghost, final_arrow,
                             final_ink, angle_arc, octant,
                             *stamps[0], *stamps[1], *stamps[2])
        cap_flat = caption("control experiment: the same loop on flat paper")
        self.add_fixed_in_frame_mobjects(cap_flat)
        cap_flat.set_opacity(0)

        grid = VGroup()
        for k in range(-4, 5):
            grid.add(Line([k * 0.8, -3.2, 0], [k * 0.8, 3.2, 0]))
            grid.add(Line([-3.2, k * 0.8, 0], [3.2, k * 0.8, 0]))
        grid.set_stroke(FAINT, width=1.0, opacity=0.7)
        sq = [np.array(p) for p in
              [[-1.2, -1.2, 0], [1.2, -1.2, 0], [1.2, 1.2, 0], [-1.2, 1.2, 0]]]

        def sq_pos(tau: float) -> np.ndarray:
            tau = max(0.0, min(4.0, tau))
            i = min(int(tau), 3)
            return sq[i] + (tau - i) * (sq[(i + 1) % 4] - sq[i])

        vdir = np.array([0.45, 0.65, 0.0])
        vdir = VLEN * vdir / np.linalg.norm(vdir)
        sq_loop = VGroup(*[
            DashedVMobject(Line(sq[i], sq[(i + 1) % 4]).set_stroke(INK, width=2.2, opacity=0.85),
                           num_dashes=12) for i in range(4)
        ])
        tr2 = ValueTracker(0.0)
        arrow2 = always_redraw(lambda: flat_arrow(
            sq_pos(tr2.get_value()), vdir, np.array([0.0, 0.0, 1.0])))
        ghost2 = flat_arrow(sq[0], vdir, np.array([0.0, 0.0, 1.0]),
                            color=GRID, opacity=0.55)

        self.play(FadeOut(sphere_group), FadeOut(cap_area), FadeOut(formula),
                  cap_flat.animate.set_opacity(1), run_time=1.8)
        self.move_camera(phi=52 * DEGREES, theta=-90 * DEGREES, zoom=1.25,
                         frame_center=[0, 0, 0], run_time=1.6)
        self.play(FadeIn(grid), Create(sq_loop), FadeIn(ghost2), run_time=1.8)
        self.add(arrow2)
        self.play(tr2.animate.set_value(4.0), run_time=4.4, rate_func=smooth)

        cap_zero = caption("it comes home unchanged. α = 0 — flat paper has no memory", color=AMBER)
        self.add_fixed_in_frame_mobjects(cap_zero)
        cap_zero.set_opacity(0)
        self.play(FadeOut(cap_flat), cap_zero.animate.set_opacity(1), run_time=1.0)
        self.wait(1.8)

        # --- End card ---
        self.remove(arrow2)
        epigram = Text("curvature is what a journey remembers",
                       font=SERIF, font_size=30, slant=ITALIC, color=INK)
        credit = Text("DWG 001 · HOLONOMY · PRINTED IN CYANOTYPE", font=MONO,
                      font_size=14, color=FAINT)
        card = VGroup(epigram, credit).arrange(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(card)
        card.set_opacity(0)
        self.play(FadeOut(grid), FadeOut(sq_loop), FadeOut(ghost2), FadeOut(cap_zero),
                  card.animate.set_opacity(1), run_time=2.2)
        self.wait(2.5)
