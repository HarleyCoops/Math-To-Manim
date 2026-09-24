"""THE SECOND TURN — why a belt needs 720° to forget a twist.

Pure three-dimensional studio. A ribbon is clamped at both ends in ordinary
space. One full turn of an end leaves a twist that no continuous dance can
remove. Two full turns can be danced free by looping the ribbon over a clamp.
The same story is told by a cube whose three colored axes are a rigid frame:
a 360° rotation path is a loop that cannot shrink; 720° can.

Expected duration: approximately 96 seconds.

Render:
    manim -ql examples/mimo/the_second_turn.py TheSecondTurn

Concept novelty: Dirac belt / SO(3) double cover / π₁(SO(3)) ≅ ℤ/2 — not
present elsewhere in this repository when this scene was added.
"""

from __future__ import annotations

import numpy as np
from manim import *

# ---------------------------------------------------------------------------
# Studio palette
# ---------------------------------------------------------------------------
INK = "#0b0d10"
BONE = "#f2ead8"
VERMILION = "#c4452d"
VERDIGRIS = "#3f746b"
OLD_GOLD = "#c9a227"
STEEL = "#8a9098"
FADED = "#6b7280"
AXIS_X = "#c4452d"
AXIS_Y = "#3f746b"
AXIS_Z = "#c9a227"

BELT_HALF_WIDTH = 0.18
CLAMP_A = np.array([-2.2, 0.0, 0.0])
CLAMP_B = np.array([2.2, 0.0, 0.0])
CLAMP_SIZE = 0.42


def charge_parity(twists: float) -> str:
    return "even" if int(round(twists)) % 2 == 0 else "odd"


def clamp_mobject(point: np.ndarray, color: str = STEEL) -> Cube:
    cube = Cube(side_length=CLAMP_SIZE, fill_color=color, fill_opacity=0.85, stroke_width=2)
    cube.set_color(color)
    cube.move_to(point)
    return cube


def ribbon_frame(t: float, twists: float, lift: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Centerline, width-direction, and normal-direction at parameter t in [0,1]."""
    # Straight clamped belt along x, with an optional arch used during the dance.
    base = (1.0 - t) * CLAMP_A + t * CLAMP_B
    arch = lift * np.sin(np.pi * t) * np.array([0.0, 1.0, 0.35 * np.sin(np.pi * t)])
    center = base + arch
    tangent = (CLAMP_B - CLAMP_A) / np.linalg.norm(CLAMP_B - CLAMP_A)
    tangent = tangent + lift * np.pi * np.cos(np.pi * t) * np.array([0.0, 1.0, 0.35 * np.sin(np.pi * t)]) / 4.4
    tangent = tangent / np.linalg.norm(tangent)
    # Material frame: start with fixed world up, rotate around tangent by twists full turns.
    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(up, tangent)) > 0.95:
        up = np.array([0.0, 1.0, 0.0])
    side = np.cross(tangent, up)
    side = side / np.linalg.norm(side)
    normal = np.cross(side, tangent)
    angle = 2.0 * np.pi * twists * t
    # Rodrigues rotation of (side, normal) about tangent.
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    side_r = side * cos_a + np.cross(tangent, side) * sin_a + tangent * np.dot(tangent, side) * (1 - cos_a)
    normal_r = normal * cos_a + np.cross(tangent, normal) * sin_a + tangent * np.dot(tangent, normal) * (1 - cos_a)
    return center, side_r / np.linalg.norm(side_r), normal_r / np.linalg.norm(normal_r)


def ribbon_point(u: float, v: float, twists: float, lift: float) -> np.ndarray:
    center, side, _normal = ribbon_frame(u, twists, lift)
    return center + v * BELT_HALF_WIDTH * side


def build_ribbon(twists: float, lift: float, color: str = VERMILION) -> Surface:
    def param(u: float, v: float) -> np.ndarray:
        # manim Surface parameters live in a default rectangle; map to [0,1]×[-1,1]
        return ribbon_point(u, v, twists, lift)

    surface = Surface(
        lambda u, v: param(u, v),
        u_range=[0.0, 1.0],
        v_range=[-1.0, 1.0],
        resolution=(32, 4),
        fill_color=color,
        fill_opacity=0.95,
        stroke_color=BONE,
        stroke_width=0.6,
    )
    return surface


class TheSecondTurn(ThreeDScene):
    """Clamped belt in a dark studio: 360° is stuck, 720° comes home."""

    def construct(self) -> None:
        self.camera.background_color = INK
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, gamma=0)

        twists = ValueTracker(0.0)
        lift = ValueTracker(0.0)
        dance = ValueTracker(0.0)

        title = Text("THE SECOND TURN", color=BONE, weight=BOLD).scale(0.9).to_edge(UP, buff=0.4)
        subtitle = Text(
            "720° is standing still. 360° is not.",
            color=OLD_GOLD,
        ).scale(0.38).next_to(title, DOWN, buff=0.22)

        clamp_left = clamp_mobject(CLAMP_A, STEEL)
        clamp_right = clamp_mobject(CLAMP_B, STEEL)
        wall = always_redraw(
            lambda: Square(side_length=2.4, fill_color=FADED, fill_opacity=0.15, stroke_color=STEEL)
            .rotate(PI / 2, axis=RIGHT)
            .next_to(CLAMP_A, LEFT, buff=0.05)
        )

        ribbon = always_redraw(lambda: build_ribbon(twists.get_value(), lift.get_value()))

        lamp = always_redraw(
            lambda: VGroup(
                Dot(color=OLD_GOLD if charge_parity(twists.get_value()) == "even" else VERMILION, radius=0.09),
                Text(
                    f"twist charge  {int(round(twists.get_value()))}   ({charge_parity(twists.get_value())})",
                    color=BONE,
                ).scale(0.32),
            ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.35)
        )

        # Rotation cube (rigid frame) for the coda geometry.
        frame_cube = Cube(side_length=0.9, fill_color=VERDIGRIS, fill_opacity=0.12, stroke_color=BONE)
        axes = VGroup(
            Line3D(start=np.zeros(3), end=np.array([0.7, 0, 0]), color=AXIS_X),
            Line3D(start=np.zeros(3), end=np.array([0, 0.7, 0]), color=AXIS_Y),
            Line3D(start=np.zeros(3), end=np.array([0, 0, 0.7]), color=AXIS_Z),
        )
        solid = VGroup(frame_cube, axes).move_to(np.array([0.0, -1.3, 0.0]))

        self.add_fixed_in_frame_mobjects(title, subtitle, lamp)
        self.play(Write(title), FadeIn(subtitle), run_time=1.6)
        self.play(Create(clamp_left), Create(clamp_right), Create(wall), run_time=1.2)
        self.play(FadeIn(ribbon), run_time=1.2)
        self.wait(0.8)

        # --- S2: one full turn -------------------------------------------------
        self.play(FadeOut(subtitle), run_time=0.4)
        caption1 = Text("one full turn of the right clamp", color=BONE).scale(0.34)
        self.add_fixed_in_frame_mobjects(caption1)
        caption1.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption1), run_time=0.4)
        self.play(
            twists.animate.set_value(1.0),
            Rotate(clamp_right, angle=2 * PI, axis=RIGHT, about_point=CLAMP_B),
            run_time=3.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeOut(caption1), run_time=0.3)

        # --- S3: two failed dances (odd is stuck) --------------------------------
        caption2 = Text("odd charge cannot leave without cutting", color=VERMILION).scale(0.32)
        self.add_fixed_in_frame_mobjects(caption2)
        caption2.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption2), run_time=0.3)
        for attempt in (0.55, 0.9):
            self.play(lift.animate.set_value(attempt), run_time=1.1, rate_func=rate_functions.smooth)
            self.play(lift.animate.set_value(0.0), run_time=1.0, rate_func=rate_functions.smooth)
            self.move_camera(phi=62 * DEGREES, theta=-48 * DEGREES, run_time=0.6)
        self.play(FadeOut(caption2), run_time=0.3)

        # --- S4: second turn (total 720°) ---------------------------------------
        caption3 = Text("a second full turn → 720°", color=OLD_GOLD).scale(0.34)
        self.add_fixed_in_frame_mobjects(caption3)
        caption3.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption3), run_time=0.3)
        self.play(
            twists.animate.set_value(2.0),
            Rotate(clamp_right, angle=2 * PI, axis=RIGHT, about_point=CLAMP_B),
            run_time=2.8,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeOut(caption3), run_time=0.3)

        # --- S5: the belt-trick dance --------------------------------------------
        caption4 = Text("loop the ribbon over the left clamp", color=BONE).scale(0.34)
        self.add_fixed_in_frame_mobjects(caption4)
        caption4.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption4), run_time=0.3)
        # Classical family: raise an arch, overshoot the left clamp, settle while
        # the material twist is redistributed into the arch and then discarded.
        self.play(
            lift.animate.set_value(1.35),
            twists.animate.set_value(1.0),
            run_time=3.5,
            rate_func=rate_functions.smooth,
        )
        self.move_camera(phi=58 * DEGREES, theta=-38 * DEGREES, run_time=1.2)
        self.play(
            lift.animate.set_value(0.35),
            twists.animate.set_value(0.0),
            run_time=3.5,
            rate_func=rate_functions.smooth,
        )
        self.play(lift.animate.set_value(0.0), run_time=1.4, rate_func=rate_functions.smooth)
        self.play(FadeOut(caption4), run_time=0.3)

        # --- S6: BIG ZOOM into the weave ------------------------------------------
        caption5 = Text("the crossing leaves through the end-cap", color=OLD_GOLD).scale(0.32)
        self.add_fixed_in_frame_mobjects(caption5)
        caption5.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption5), run_time=0.3)
        # Momentary re-introduce a half-lift so there is a weave to dive into.
        self.play(lift.animate.set_value(0.55), twists.animate.set_value(0.5), run_time=1.0)
        self.move_camera(
            phi=74 * DEGREES,
            theta=-20 * DEGREES,
            frame_center=np.array([-1.4, 0.3, 0.0]),
            run_time=3.8,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.4)
        self.play(twists.animate.set_value(0.0), lift.animate.set_value(0.0), run_time=1.6)
        self.move_camera(
            phi=68 * DEGREES,
            theta=-52 * DEGREES,
            frame_center=np.array([0.0, 0.0, 0.0]),
            run_time=3.0,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeOut(caption5), run_time=0.3)

        # --- S7: the solid frame (same story as poses) ----------------------------
        self.play(FadeIn(solid), run_time=1.2)
        caption6 = Text("a rigid frame: pose returns at 360°, path does not", color=BONE).scale(0.28)
        self.add_fixed_in_frame_mobjects(caption6)
        caption6.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(caption6), run_time=0.3)
        self.play(Rotate(solid, angle=2 * PI, axis=RIGHT, about_point=solid.get_center()), run_time=3.5)
        self.wait(0.4)
        caption7 = Text("720°: the path can shrink to stillness", color=OLD_GOLD).scale(0.28)
        self.add_fixed_in_frame_mobjects(caption7)
        caption7.to_edge(DOWN, buff=0.9)
        self.play(ReplacementTransform(caption6, caption7), run_time=0.4)
        self.play(Rotate(solid, angle=4 * PI, axis=RIGHT, about_point=solid.get_center()), run_time=4.5)

        # --- S8: coda -------------------------------------------------------------
        self.play(FadeOut(caption7), run_time=0.4)
        coda = Text(
            "Electrons are not arrows. They are belts in the room.",
            color=BONE,
        ).scale(0.36)
        math_line = Text("pi1(SO(3)) = Z/2", color=OLD_GOLD).scale(0.55)
        coda_group = VGroup(coda, math_line).arrange(DOWN, buff=0.35).to_edge(DOWN, buff=0.55)
        self.add_fixed_in_frame_mobjects(coda_group)
        self.play(Write(coda), run_time=1.8)
        self.play(Write(math_line), run_time=1.4)
        self.move_camera(phi=72 * DEGREES, theta=-58 * DEGREES, run_time=2.5)
        self.wait(2.2)
