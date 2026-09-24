"""OLIN — the off-white 3D space hiding in one tweet-sized p5.js sketch.

This is a deterministic, self-contained Mythos production scene.  It first
reconstructs the tweet's literal two-dimensional coordinates, then gives them
the exact shadow-preserving lift

    E(i,t) = (u, 40 sin(c), v),

and only afterwards introduces C as a separate cylindrical interpretation.
Every animated point cloud uses one evenly spaced 5,000-sample subset; the
full-density reference shadow contains all 10,000 samples.

Expected duration: approximately 70 seconds.

Render:
    manim -qm examples/mythos/olin_off_white_3d_space.py OlinOffWhite3DSpace
"""

from __future__ import annotations

import numpy as np
from manim import *


STATIC_SAMPLE_COUNT = 10_000
ANIMATED_SAMPLE_COUNT = 5_000
TIME_STEP = np.pi / 80

PAPER = "#f3ecd8"
INK = "#241a12"
OXIDE = "#a24f3d"
VERDIGRIS = "#3f746b"
INDIGO = "#485b7a"
OLD_GOLD = "#a17f35"
PLUM = "#75566f"
FADED_INK = "#796d5d"

DISPLAY_SCALE = 0.017
DISPLAY_VERTICAL_CENTER = 200.0


def olin_terms(i: np.ndarray | float, t: float) -> tuple[np.ndarray, ...]:
    """Evaluate the dictated definition chain in its original order."""
    i = np.asarray(i, dtype=float)
    y = i / 235.0
    k = (4.0 + np.cos(i / 9.0 - 2.0 * t)) * np.cos(i / 35.0)
    e = y / 7.0 - 13.0
    d = np.sqrt(k * k + e * e) + np.sin(e / 9.0 + t / 2.0) - 4.0
    c = d - t
    q = (
        2.0 * np.sin(3.0 * k)
        - (y / 35.0)
        * k
        * (9.0 + k * np.sin(9.0 * np.cos(e) - 2.0 * d + t))
    )
    return y, k, e, d, c, q


def tweet_coordinates(i: np.ndarray | float, t: float) -> np.ndarray:
    """Return the centered tweet coordinates ``(u, v)`` without display scaling."""
    _, _, _, d, c, q = olin_terms(i, t)
    u = q + 40.0 * np.cos(c)
    v = q * np.sin(c) + 35.0 * d
    return np.stack((u, v), axis=-1)


def exact_lift_coordinates(i: np.ndarray | float, t: float) -> np.ndarray:
    """Return E: the exact 3D lift whose xz projection is the tweet."""
    _, _, _, d, c, q = olin_terms(i, t)
    u = q + 40.0 * np.cos(c)
    hidden_y = 40.0 * np.sin(c)
    v = q * np.sin(c) + 35.0 * d
    return np.stack((u, hidden_y, v), axis=-1)


def cylindrical_coordinates(i: np.ndarray | float, t: float) -> np.ndarray:
    """Return C: a cylindrical reinterpretation, not a literal shadow source."""
    _, _, _, d, c, q = olin_terms(i, t)
    radius = 40.0 + q
    return np.stack(
        (radius * np.cos(c), radius * np.sin(c), 35.0 * d),
        axis=-1,
    )


class OlinOffWhite3DSpace(ThreeDScene):
    """A paper-stage proof of the tweet shadow, its exact lift E, and alternate C."""

    def construct(self) -> None:
        self.camera.background_color = PAPER
        self.caption_mob = None

        full_indices = np.arange(STATIC_SAMPLE_COUNT, dtype=float)
        animated_indices = np.linspace(
            0,
            STATIC_SAMPLE_COUNT - 1,
            ANIMATED_SAMPLE_COUNT,
            dtype=np.int64,
        ).astype(float)
        frame_index = ValueTracker(1.0)

        # Front-on for typography.  All camera changes use the ThreeDScene API.
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)

        # ------------------------------------------------------------------
        # 1. The source
        # ------------------------------------------------------------------
        self.headline("One tweet draws a space.", hold=1.0)
        source_label = Text(
            "THE ENTIRE SKETCH · ONE DICTATED FUNCTION",
            font_size=22,
            color=OXIDE,
            weight=BOLD,
        ).to_edge(UP, buff=0.55)
        source = Text(
            "a=(y,d=mag(k=(4+cos(i/9-t*2))*cos(i/35),\n"
            "e=y/7-13)+sin(e/9+t/2)-4)=>\n"
            " point((q=2*sin(k*3)-y/35*k*(9+k*sin(\n"
            " cos(e)*9-d*2+t)))+40*cos(c=d-t)+200,\n"
            " q*sin(c)+d*35)\n"
            "t=0, draw=$=>{t||createCanvas(w=400,w);\n"
            " background(9).stroke(w,96);\n"
            " for(t+=PI/80,i=1e4;i--;)a(i/235)}",
            font="DejaVu Sans Mono",
            font_size=19,
            color=INK,
            line_spacing=0.86,
        )
        if source.width > 11.7:
            source.scale_to_fit_width(11.7)
        source.next_to(source_label, DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(source_label, source)
        self.play(
            FadeIn(source_label, shift=0.08 * UP),
            FadeIn(source, shift=0.08 * UP),
            run_time=0.8,
        )
        self.wait(2.0)
        self.play(FadeOut(source_label), FadeOut(source), run_time=0.6)
        self.remove(source_label, source)

        # ------------------------------------------------------------------
        # 2. The addressable definition chain
        # ------------------------------------------------------------------
        self.headline("Ten thousand points, one recipe.", hold=1.0)
        equations = self.definition_chain()
        self.play(FadeIn(equations, lag_ratio=0.08), run_time=0.9)

        term_captions = (
            "The carrier wave braids two cosine clocks.",
            "The ladder coordinate orders all 10,000 samples.",
            "Distance from (k,e), plus a slow global breath.",
            "Distance becomes rotation:  c = d − t.",
            "The flourish grows with y and buckles the silhouette.",
        )
        for active, words in zip(equations, term_captions):
            self.play(
                *[
                    eq.animate.set_opacity(1.0 if eq is active else 0.28)
                    for eq in equations
                ],
                run_time=0.18,
            )
            self.move_camera(
                frame_center=active.get_center(),
                zoom=1.08,
                run_time=0.42,
            )
            self.replace_caption(words, hold=0.35)

        self.move_camera(frame_center=ORIGIN, zoom=0.88, run_time=0.7)
        self.play(*[eq.animate.set_opacity(1.0) for eq in equations], run_time=0.25)
        self.replace_caption(
            "Read in order:  carrier → ladder → distance → spin → flourish.",
            hold=0.5,
        )
        self.clear_caption(run_time=0.25)
        self.play(FadeOut(equations), run_time=0.6)

        # ------------------------------------------------------------------
        # 3. The literal flat shadow
        # ------------------------------------------------------------------
        self.headline("The flat shadow.", hold=1.0)
        self.set_camera_orientation(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
            zoom=0.88,
            frame_center=ORIGIN,
        )

        tweet_frame = self.tweet_frame()
        reference_t = TIME_STEP
        static_shadow = self.point_cloud(
            self.stage_shadow(tweet_coordinates(full_indices, reference_t)),
            INK,
            width=2.15,
            opacity=0.9,
        )
        self.play(Create(tweet_frame), FadeIn(static_shadow), run_time=0.8)
        self.replace_caption(
            "All 10,000 samples at one exact full-density reference frame.",
            hold=1.0,
        )

        shadow_cloud = self.point_cloud(
            self.stage_shadow(tweet_coordinates(animated_indices, reference_t)),
            INK,
            width=2.35,
            opacity=0.92,
        )
        self.play(
            FadeOut(static_shadow),
            FadeIn(shadow_cloud),
            run_time=0.6,
        )

        def update_shadow(mob: PMobject) -> None:
            t = round(frame_index.get_value()) * TIME_STEP
            mob.set_points(
                self.stage_shadow(tweet_coordinates(animated_indices, t))
            )

        shadow_cloud.add_updater(update_shadow)
        self.replace_caption(
            "The same evenly spaced 5,000 samples move; every step is Δt = π/80.",
            hold=0.4,
        )
        self.play(
            frame_index.animate.set_value(97.0),
            run_time=4.0,
            rate_func=linear,
        )
        shadow_cloud.clear_updaters()
        self.replace_caption(
            "These are the tweet's exact centered coordinates (u,v).",
            hold=0.6,
        )
        self.clear_caption(run_time=0.25)

        # ------------------------------------------------------------------
        # 4. E: the exact shadow-preserving lift
        # ------------------------------------------------------------------
        self.headline("Lift it exactly.", hold=1.0)
        current_t = round(frame_index.get_value()) * TIME_STEP
        e_formula = MathTex(
            r"E(i,t)=\Bigl(q+40\cos c,\;40\sin c,\;"
            r"q\sin c+35d\Bigr)",
            font_size=35,
            color=INK,
        ).to_edge(UP, buff=0.36)
        e_formula.set_color_by_tex(r"40\sin c", VERDIGRIS)
        self.add_fixed_in_frame_mobjects(e_formula)
        self.play(FadeIn(e_formula, shift=0.06 * DOWN), run_time=0.6)
        self.replace_caption(
            "E copies u and v exactly; only the hidden y-coordinate is new.",
            hold=0.4,
        )

        lift_cloud = self.point_cloud(
            self.stage_shadow(tweet_coordinates(animated_indices, current_t)),
            VERDIGRIS,
            width=2.5,
            opacity=0.88,
        )
        self.remove(shadow_cloud)
        cloud_pair = PGroup(shadow_cloud, lift_cloud)
        self.add(cloud_pair)

        self.move_camera(
            phi=70 * DEGREES,
            theta=-58 * DEGREES,
            zoom=0.88,
            frame_center=ORIGIN,
            run_time=1.9,
        )
        lift_target = self.point_cloud(
            self.stage_space(exact_lift_coordinates(animated_indices, current_t)),
            VERDIGRIS,
            width=2.5,
            opacity=0.88,
        )
        self.play(Transform(lift_cloud, lift_target), run_time=1.6)
        self.replace_caption(
            "Every point leaves the paper along y, without changing x or z.",
            hold=0.4,
        )

        depth_filaments = self.depth_filaments(animated_indices, current_t)
        self.play(FadeIn(depth_filaments), run_time=0.6)
        self.move_camera(
            phi=58 * DEGREES,
            theta=18 * DEGREES,
            zoom=0.94,
            frame_center=ORIGIN,
            run_time=2.2,
        )
        self.replace_caption(
            "Orbiting exposes real depth and parallax: this is not a flat redraw.",
            hold=0.4,
        )

        self.move_camera(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
            zoom=0.88,
            frame_center=ORIGIN,
            run_time=2.2,
        )
        projection_formula = MathTex(
            r"\pi_{xz}\!\left(E(i,t)\right)"
            r"=\Bigl(q+40\cos c,\;q\sin c+35d\Bigr)=(u,v)",
            font_size=34,
            color=INK,
        ).to_edge(UP, buff=0.36)
        projection_formula.set_color_by_tex(r"\pi_{xz}", OXIDE)
        self.play(FadeOut(e_formula, shift=0.04 * UP), run_time=0.25)
        self.remove(e_formula)
        self.add_fixed_in_frame_mobjects(projection_formula)
        self.play(FadeIn(projection_formula, shift=0.04 * UP), run_time=0.25)
        self.replace_caption(
            "Orthographic down y, E collapses point-for-point onto the tweet.",
            hold=0.8,
        )
        self.clear_caption(run_time=0.25)

        # ------------------------------------------------------------------
        # 5. C: explicitly separate cylindrical interpretation
        # ------------------------------------------------------------------
        self.play(
            FadeOut(projection_formula),
            FadeOut(depth_filaments),
            run_time=0.5,
        )
        self.headline("A cylindrical reading.", hold=1.0)
        self.move_camera(
            phi=64 * DEGREES,
            theta=-46 * DEGREES,
            zoom=0.92,
            frame_center=ORIGIN,
            run_time=1.8,
        )

        c_formula = MathTex(
            r"C(i,t)=\Bigl((40+q)\cos c,\;(40+q)\sin c,\;35d\Bigr)",
            font_size=34,
            color=INK,
        )
        c_label = Text(
            "C · ALTERNATE CYLINDRICAL INTERPRETATION",
            font_size=19,
            color=OXIDE,
            weight=BOLD,
        )
        c_panel = VGroup(c_formula, c_label).arrange(DOWN, buff=0.12)
        c_panel.to_edge(UP, buff=0.28)
        self.add_fixed_in_frame_mobjects(c_panel)
        self.play(FadeIn(c_panel, shift=0.06 * DOWN), run_time=0.5)

        c_target = self.point_cloud(
            self.stage_space(cylindrical_coordinates(animated_indices, current_t)),
            OXIDE,
            width=2.5,
            opacity=0.88,
        )
        self.play(Transform(lift_cloud, c_target), run_time=1.8)
        self.replace_caption(
            "C is a cylindrical reinterpretation; it does not project back to the tweet.",
            hold=0.7,
        )

        def update_cylinder(mob: PMobject) -> None:
            t = round(frame_index.get_value()) * TIME_STEP
            mob.set_points(
                self.stage_space(cylindrical_coordinates(animated_indices, t))
            )

        lift_cloud.add_updater(update_cylinder)
        self.replace_caption(
            "The sin(e/9+t/2) breath has period 4π while c=d−t spins.",
            hold=0.25,
        )
        self.play(
            frame_index.animate.set_value(217.0),
            run_time=3.8,
            rate_func=linear,
        )
        lift_cloud.clear_updaters()
        self.move_camera(
            phi=70 * DEGREES,
            theta=28 * DEGREES,
            zoom=0.9,
            frame_center=ORIGIN,
            run_time=2.0,
        )
        self.wait(0.4)
        self.clear_caption(run_time=0.25)

        # ------------------------------------------------------------------
        # 6. Final master tableau: exact E, its shadow, and the chain
        # ------------------------------------------------------------------
        self.play(FadeOut(c_panel), run_time=0.5)
        self.headline("Shadow and space together.", hold=1.0)
        final_t = round(frame_index.get_value()) * TIME_STEP
        final_shadow = self.point_cloud(
            self.stage_shadow(tweet_coordinates(animated_indices, final_t)),
            INK,
            width=2.35,
            opacity=0.78,
        )
        final_lift = self.point_cloud(
            self.stage_space(exact_lift_coordinates(animated_indices, final_t)),
            VERDIGRIS,
            width=2.55,
            opacity=0.92,
        )
        self.play(
            Transform(shadow_cloud, final_shadow),
            Transform(lift_cloud, final_lift),
            run_time=1.6,
        )
        self.move_camera(
            phi=66 * DEGREES,
            theta=-54 * DEGREES,
            zoom=0.86,
            frame_center=ORIGIN,
            run_time=2.1,
        )
        final_filaments = self.depth_filaments(animated_indices, final_t)
        self.play(FadeIn(final_filaments), run_time=0.5)

        final_title = Text(
            "SHADOW AND SPACE TOGETHER",
            font_size=21,
            color=INK,
            weight=BOLD,
        ).to_corner(UL, buff=0.38)
        final_chain = MathTex(
            r"k", r"\longrightarrow", r"e", r"\longrightarrow",
            r"d", r"\longrightarrow", r"c", r"\longrightarrow",
            r"q", r"\longrightarrow", r"E",
            r"\xrightarrow{\ \pi_{xz}\ }", r"(u,v)",
            font_size=25,
            color=INK,
        )
        final_chain[0].set_color(INDIGO)
        final_chain[2].set_color(OLD_GOLD)
        final_chain[4].set_color(VERDIGRIS)
        final_chain[6].set_color(OXIDE)
        final_chain[8].set_color(PLUM)
        final_chain[10].set_color(VERDIGRIS)
        final_chain[11].set_color(OXIDE)
        final_note = Text(
            "E is exact · sepia is its xz shadow · C remains an alternate reading",
            font_size=15,
            color=FADED_INK,
        )
        final_panel = VGroup(final_chain, final_note).arrange(DOWN, buff=0.1)
        final_panel.to_corner(UR, buff=0.36)
        if final_panel.width > 9.4:
            final_panel.scale_to_fit_width(9.4)
            final_panel.to_corner(UR, buff=0.36)
        self.add_fixed_in_frame_mobjects(final_title, final_panel)
        self.play(
            FadeIn(final_title, shift=0.06 * UP),
            FadeIn(final_panel, shift=0.06 * UP),
            run_time=0.7,
        )
        self.wait(3.2)

    # ------------------------------------------------------------------
    # Visual helpers.  These stay on this one scene; no archive imports.
    # ------------------------------------------------------------------
    def point_cloud(
        self,
        points: np.ndarray,
        color: str,
        *,
        width: float,
        opacity: float,
    ) -> PMobject:
        cloud = PMobject(stroke_width=width)
        cloud.add_points(np.asarray(points, dtype=float), color=color, alpha=opacity)
        return cloud

    def stage_shadow(self, uv: np.ndarray) -> np.ndarray:
        uv = np.asarray(uv, dtype=float)
        points = np.zeros((len(uv), 3), dtype=float)
        points[:, 0] = DISPLAY_SCALE * uv[:, 0]
        points[:, 2] = DISPLAY_SCALE * (uv[:, 1] - DISPLAY_VERTICAL_CENTER)
        return points

    def stage_space(self, xyz: np.ndarray) -> np.ndarray:
        xyz = np.asarray(xyz, dtype=float).copy()
        xyz[:, 2] -= DISPLAY_VERTICAL_CENTER
        return DISPLAY_SCALE * xyz

    def tweet_frame(self) -> VGroup:
        half = 200.0 * DISPLAY_SCALE
        border = VGroup(
            Line([-half, 0, -half], [half, 0, -half]),
            Line([half, 0, -half], [half, 0, half]),
            Line([half, 0, half], [-half, 0, half]),
            Line([-half, 0, half], [-half, 0, -half]),
        ).set_stroke(INK, width=1.2, opacity=0.45)
        grid = VGroup()
        for raw in (-100.0, 0.0, 100.0):
            p = raw * DISPLAY_SCALE
            grid.add(
                Line([p, 0, -half], [p, 0, half]),
                Line([-half, 0, p], [half, 0, p]),
            )
        grid.set_stroke(FADED_INK, width=0.7, opacity=0.18)
        return VGroup(border, grid)

    def depth_filaments(self, indices: np.ndarray, t: float) -> VGroup:
        pick = np.linspace(0, len(indices) - 1, 17, dtype=int)
        chosen = np.asarray(indices)[pick]
        shadow = self.stage_shadow(tweet_coordinates(chosen, t))
        lift = self.stage_space(exact_lift_coordinates(chosen, t))
        return VGroup(
            *[
                Line(a, b, color=OLD_GOLD, stroke_width=1.0)
                .set_opacity(0.48)
                for a, b in zip(shadow, lift)
            ]
        )

    def definition_chain(self) -> VGroup:
        k_eq = MathTex(
            r"k", r"=", r"\bigl(4+\cos(i/9-2t)\bigr)\cos(i/35)",
            font_size=32,
            color=INK,
        )
        e_eq = MathTex(
            r"e", r"=", r"\frac{y}{7}-13",
            font_size=32,
            color=INK,
        )
        d_eq = MathTex(
            r"d", r"=",
            r"\sqrt{k^2+e^2}+\sin\!\left(\frac{e}{9}+\frac{t}{2}\right)-4",
            font_size=32,
            color=INK,
        )
        c_eq = MathTex(
            r"c", r"=", r"d-t",
            font_size=32,
            color=INK,
        )
        q_eq = MathTex(
            r"q", r"=",
            r"2\sin(3k)-\frac{y}{35}k"
            r"\Bigl(9+k\sin\bigl(9\cos e-2d+t\bigr)\Bigr)",
            font_size=32,
            color=INK,
        )
        for equation, color in zip(
            (k_eq, e_eq, d_eq, c_eq, q_eq),
            (INDIGO, OLD_GOLD, VERDIGRIS, OXIDE, PLUM),
        ):
            equation[0].set_color(color)
        chain = VGroup(k_eq, e_eq, d_eq, c_eq, q_eq)
        chain.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        if chain.width > 11.6:
            chain.scale_to_fit_width(11.6)
        chain.move_to(ORIGIN)
        return chain

    def headline(self, words: str, *, hold: float) -> None:
        self.clear_caption(run_time=0)
        paper_card = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=PAPER,
            fill_opacity=1.0,
        )
        title = Text(
            words,
            font_size=58,
            color=INK,
            weight=BOLD,
        )
        self.add_fixed_in_frame_mobjects(paper_card, title)
        self.play(FadeIn(paper_card), run_time=0.2)
        self.play(FadeIn(title, shift=0.1 * UP), run_time=0.45)
        self.wait(hold)
        self.play(FadeOut(title), run_time=0.35)
        self.play(FadeOut(paper_card), run_time=0.2)
        self.remove(title, paper_card)

    def replace_caption(self, words: str, *, hold: float) -> None:
        new_caption = Text(
            words,
            font_size=26,
            color=INK,
        )
        if new_caption.width > config.frame_width - 1.0:
            new_caption.scale_to_fit_width(config.frame_width - 1.0)
        new_caption.to_edge(DOWN, buff=0.36)
        new_caption.set_stroke(PAPER, width=7, background=True)
        self.add_fixed_in_frame_mobjects(new_caption)
        if self.caption_mob is None:
            self.play(FadeIn(new_caption, shift=0.05 * UP), run_time=0.25)
        else:
            old_caption = self.caption_mob
            self.play(
                ReplacementTransform(old_caption, new_caption),
                run_time=0.25,
            )
            self.remove(old_caption)
        self.caption_mob = new_caption
        if hold:
            self.wait(hold)

    def clear_caption(self, *, run_time: float) -> None:
        if self.caption_mob is None:
            return
        old_caption = self.caption_mob
        self.caption_mob = None
        if run_time:
            self.play(FadeOut(old_caption), run_time=run_time)
        self.remove(old_caption)
