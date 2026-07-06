"""Plate VII — The Associate Family (risograph study).

A deliberate inversion of the Mythos house style: no ink-black stage, no
glow, no cinematic spotlight. Instead, a flat two-ink risograph print on
warm cream paper — the visual language of a mid-century geometry textbook
plate — watching the helicoid deform isometrically into the catenoid.

The mathematics: the helicoid and catenoid are conjugate minimal surfaces.
Their associate family

    X(theta) = cos(theta) * X_helicoid + sin(theta) * X_catenoid

is an isometric deformation: every intermediate surface is minimal, and
lengths measured on the surface never change while the shape does.

Render:
    manim -qm examples/mathematics/geometry/riso_associate_family.py AssociateFamilyRiso
"""

from __future__ import annotations

import numpy as np
from manim import *

# ----------------------------------------------------------------------
# Risograph palette — the anti-Mythos. Paper, not stage. Ink, not light.
# ----------------------------------------------------------------------
PAPER = "#f4ecdd"        # warm cream paper
INK_TEAL = "#0f6b6e"     # riso teal ink (surface, dark pass)
INK_TEAL_LT = "#7fb5b0"  # light pass of the teal drum
INK_VERM = "#d94f2b"     # vermilion ink (accents, annotations)
INK_DARK = "#2b2a26"     # near-black text ink
INK_FADE = "#8a8474"     # greyed ink for secondary text

SERIF = "Georgia"
MONO = "Consolas"

U_RANGE = (-PI, PI)
V_RANGE = (-1.35, 1.35)


def associate_point(u: float, v: float, theta: float) -> np.ndarray:
    """Associate family of the helicoid (theta=0) and catenoid (theta=pi/2)."""
    ct, st = np.cos(theta), np.sin(theta)
    x = ct * np.sinh(v) * np.sin(u) + st * np.cosh(v) * np.cos(u)
    y = -ct * np.sinh(v) * np.cos(u) + st * np.cosh(v) * np.sin(u)
    z = u * ct + v * st
    return np.array([x, y, z * 0.72])


def make_surface(theta: float) -> Surface:
    surf = Surface(
        lambda u, v: associate_point(u, v, theta),
        u_range=list(U_RANGE),
        v_range=list(V_RANGE),
        resolution=(42, 14),
        fill_opacity=1.0,
        stroke_color=INK_DARK,
        stroke_width=0.9,
        stroke_opacity=0.55,
        checkerboard_colors=[INK_TEAL, INK_TEAL_LT],
    )
    surf.set_shade_in_3d(True)
    return surf


class AssociateFamilyRiso(ThreeDScene):
    """~34 s. Flat duotone print aesthetic; slow drafting-table camera."""

    def construct(self):
        self.camera.background_color = PAPER

        # --- Title plate (fixed in frame, like a printed caption block) ---
        plate_no = Text("PLATE VII", font=MONO, font_size=21,
                        color=INK_VERM, weight="BOLD")
        title = Text("The Associate Family", font=SERIF, font_size=40,
                     color=INK_DARK)
        subtitle = Text("helicoid to catenoid, an isometric deformation",
                        font=SERIF, font_size=22, slant=ITALIC, color=INK_FADE)
        header = VGroup(plate_no, title, subtitle).arrange(DOWN, buff=0.18)
        header.to_edge(UP, buff=0.35)
        rule = Line(LEFT * 3.4, RIGHT * 3.4, color=INK_DARK, stroke_width=1.4)
        rule.next_to(header, DOWN, buff=0.22)

        # Registration marks — the riso print tell
        reg = VGroup(*[
            VGroup(Line(UP * 0.09, DOWN * 0.09), Line(LEFT * 0.09, RIGHT * 0.09))
            .set_stroke(INK_VERM, width=1.6).move_to(corner)
            for corner in [np.array([-6.6, 3.6, 0]), np.array([6.6, 3.6, 0]),
                           np.array([-6.6, -3.6, 0]), np.array([6.6, -3.6, 0])]
        ])

        self.add_fixed_in_frame_mobjects(header, rule, reg)
        self.play(FadeIn(header, shift=DOWN * 0.2), Create(rule),
                  FadeIn(reg), run_time=1.6)

        # --- Corner labels (fixed in frame) ---
        labels = [
            Text("θ = 0 · helicoid", font=MONO, font_size=24, color=INK_DARK),
            Text("θ = π/4 · half-turned, still minimal", font=MONO,
                 font_size=24, color=INK_DARK),
            Text("θ = π/2 · catenoid — every length preserved", font=MONO,
                 font_size=24, color=INK_DARK),
        ]
        for lab in labels:
            lab.to_corner(DL, buff=0.55)
        eq = Text("X(θ) = cos θ · H  +  sin θ · C", font=MONO, font_size=18,
                  color=INK_VERM).to_corner(DR, buff=0.65).shift(UP * 0.46)
        colophon = Text("printed in two inks · teal & vermilion on cream",
                        font=SERIF, font_size=18, slant=ITALIC, color=INK_FADE)
        colophon.to_edge(DOWN, buff=0.12)
        self.add_fixed_in_frame_mobjects(*labels, eq, colophon)
        for m in [*labels, eq, colophon]:
            m.set_opacity(0)

        # --- The surface, on a drafting-table camera ---
        self.set_camera_orientation(phi=68 * DEGREES, theta=-125 * DEGREES,
                                    zoom=0.78, frame_center=[0, 0, -0.2])

        theta_tracker = ValueTracker(0.0)

        first = make_surface(0.0)
        self.play(Create(first), run_time=3.0)
        self.play(labels[0].animate.set_opacity(1),
                  eq.animate.set_opacity(1), run_time=1.0)

        surface = always_redraw(
            lambda: make_surface(theta_tracker.get_value()))
        self.remove(first)
        self.add(surface)

        # --- The deformation, with a slow orbit ---
        self.begin_ambient_camera_rotation(rate=0.09)

        self.play(theta_tracker.animate.set_value(PI / 4), run_time=7.0,
                  rate_func=smooth)
        self.play(labels[0].animate.set_opacity(0),
                  labels[1].animate.set_opacity(1), run_time=0.8)
        self.wait(1.2)

        self.play(theta_tracker.animate.set_value(PI / 2), run_time=7.0,
                  rate_func=smooth)
        self.play(labels[1].animate.set_opacity(0),
                  labels[2].animate.set_opacity(1), run_time=0.8)

        self.wait(3.0)
        self.stop_ambient_camera_rotation()

        # --- Colophon ---
        self.play(colophon.animate.set_opacity(1), run_time=1.0)
        self.wait(2.0)
