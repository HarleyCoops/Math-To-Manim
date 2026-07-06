"""The Mythos grammar reel: the house style in thirty seconds.

Headline before symbols. Camera into the exact term. Caption everything.
Tilt into 3D only for the set piece. This is the visual contract every
generated film obeys — demonstrated on the most famous equation there is.

Render:
    manim -ql examples/mythos/grammar_reel.py MythosGrammarReel
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402
from manim import (  # noqa: E402
    DEGREES,
    DOWN,
    UP,
    ORIGIN,
    FadeIn,
    FadeOut,
    MathTex,
    Surface,
    Text,
    ThreeDScene,
    VGroup,
    Write,
)

from mythos.cinematography import (  # noqa: E402
    CORAL,
    GOLD,
    IVORY,
    OLIVE,
    SKY,
    caption,
    clear_caption,
    glow,
    glow_dot,
    headline,
    return_to_stage,
    stage,
    term_tour,
    tilt_to_3d,
)


class MythosGrammarReel(ThreeDScene):
    """The Cinematic Charter, demonstrated beat by beat."""

    def construct(self):
        stage(self)

        # 1 — HEADLINE BEFORE SYMBOLS
        headline(
            self,
            "The camera is the narrator.",
            sub="Every film speaks plain language before it speaks symbols.",
            accent=SKY,
            hold=1.4,
        )

        # 2 — the formula, built from addressable terms
        formula = MathTex("E", "=", "m", "c^2", font_size=96, color=IVORY)
        formula.move_to(ORIGIN)
        halo = glow(formula, color=CORAL, layers=4, max_width=12, opacity=0.16)
        self.play(Write(formula), FadeIn(halo), run_time=1.4)
        caption(self, "Energy and mass are the same thing, priced in light.",
                hold=1.0)

        # 3 — ZOOM INTO TERMS: the term tour
        term_tour(
            self,
            formula,
            stops=[
                {"tex": "E", "color": CORAL,
                 "caption": "E — energy: what change costs.", "hold": 1.2},
                {"tex": "m", "color": OLIVE,
                 "caption": "m — mass: frozen energy, sitting still.",
                 "hold": 1.2},
                {"tex": "c^2", "color": SKY,
                 "caption": "c² — light squared: an enormous exchange rate.",
                 "hold": 1.2},
            ],
            zoom=2.6,
        )

        # 4 — SET PIECE: tilt into 3D
        clear_caption(self)
        self.play(FadeOut(halo), FadeOut(formula), run_time=0.8)

        energy_surface = Surface(
            lambda u, v: np.array([
                u, v,
                1.1 * np.exp(-(u * u + v * v) / 3.2)
                * np.cos(2.2 * np.sqrt(u * u + v * v)),
            ]),
            u_range=[-3.4, 3.4],
            v_range=[-3.4, 3.4],
            resolution=(36, 36),
            fill_opacity=1.0,
            checkerboard_colors=[SKY, "#8fb8dd"],
            stroke_color="#dce9f7",
            stroke_width=0.9,
        )
        energy_surface.set_shade_in_3d(True)
        peak = glow_dot(point=[0, 0, 1.18], color=GOLD, radius=0.09)

        tilt_to_3d(self, phi=62 * DEGREES, theta=-42 * DEGREES,
                   zoom=1.15, run_time=1.8)
        self.play(FadeIn(energy_surface), run_time=1.4)
        self.play(FadeIn(peak, scale=0.4), run_time=0.7)
        caption(self, "Tilt into 3D only when the idea itself is 3D.",
                color=GOLD, hold=0.2)
        self.begin_ambient_camera_rotation(rate=0.06)
        self.wait(3.4)
        self.stop_ambient_camera_rotation()

        # 5 — return, end card
        self.play(FadeOut(energy_surface), FadeOut(peak), run_time=0.9)
        return_to_stage(self, run_time=1.5)
        clear_caption(self)

        headline(
            self,
            "Math-To-Manim",
            sub="one sentence in — a cinematic film out · v1.1",
            accent=CORAL,
            hold=2.0,
        )
        self.wait(0.4)
