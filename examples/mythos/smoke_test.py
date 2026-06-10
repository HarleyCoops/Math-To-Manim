"""Smoke test: exercises every Mythos cinematography helper in ~25s of film.

Render:  manim -ql examples/mythos/smoke_test.py MythosSmoke
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *
from mythos.cinematography import (
    CORAL, GOLD, IVORY, SKY, caption, clear_caption, glow_dot, headline,
    photon_path, pull_back, return_to_stage, spotlight, stage, starfield,
    term_tour, tilt_to_3d, unspotlight, zoom_to,
)


class MythosSmoke(ThreeDScene):
    def construct(self):
        stage(self)
        stars = starfield(n=40)
        self.add(stars)
        headline(self, "Smoke test.", sub="Every helper, once.", hold=0.5)

        L = MathTex(r"\mathcal{L}", "=", r"\bar{\psi}", r"(i\gamma^\mu D_\mu - m)", r"\psi",
                    "-", r"\tfrac{1}{4}", r"F_{\mu\nu}F^{\mu\nu}", font_size=56, color=IVORY)
        self.play(Write(L), run_time=1.0)
        caption(self, "A caption beneath a formula.")

        term_tour(self, L, stops=[
            dict(part=L[3], color=GOLD, zoom=2.4, hold=0.4, caption="Zooming into one term."),
        ])

        f = spotlight(self, L, L[7], color=SKY)
        zoom_to(self, L[7], zoom=2.2, run_time=0.8)
        pull_back(self, run_time=0.8)
        unspotlight(self, L, f)
        self.play(FadeOut(L), run_time=0.5)

        ph = photon_path([-3, -1, 0], [3, 1, 0], color=SKY)
        dot = glow_dot([0, 0, 0], color=CORAL)
        self.play(Create(ph), FadeIn(dot), run_time=0.8)

        tilt_to_3d(self, run_time=1.0)
        axes = ThreeDAxes(x_range=[-2, 2], y_range=[-2, 2], z_range=[-1, 1],
                          x_length=4, y_length=4, z_length=2)
        surf = Surface(lambda u, v: axes.c2p(u, v, 0.3 * np.sin(2 * u) * np.cos(2 * v)),
                       u_range=[-2, 2], v_range=[-2, 2], resolution=(12, 12),
                       fill_opacity=0.4)
        self.play(FadeIn(axes), FadeIn(surf), run_time=1.0)
        return_to_stage(self, run_time=1.0)
        clear_caption(self)
        self.play(FadeOut(ph), FadeOut(dot), FadeOut(axes), FadeOut(surf), FadeOut(stars),
                  run_time=0.6)
