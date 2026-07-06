"""The reverse reasoning tree, filmed.

The signature move of Math-To-Manim: a question decomposes backward into
everything a mind must already hold, bottoms out at known ground, then the
chain walks the tree FORWARD as a curriculum. This scene is the README's
thesis rendered in the Mythos house style.

Render:
    manim -ql examples/mythos/reverse_reasoning_tree.py MythosReverseReasoning
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    DEGREES,
    DOWN,
    UP,
    ORIGIN,
    Create,
    FadeIn,
    FadeOut,
    Flash,
    LaggedStart,
    Line,
    Text,
    ThreeDScene,
    VGroup,
)

from mythos.cinematography import (  # noqa: E402
    CORAL,
    FOG,
    GOLD,
    IVORY,
    OLIVE,
    SKY,
    caption,
    clear_caption,
    glow_dot,
    headline,
    pull_back,
    return_to_stage,
    stage,
    starfield,
    tilt_to_3d,
    zoom_to,
)


class MythosReverseReasoning(ThreeDScene):
    """Backward to known ground, forward as a curriculum."""

    def construct(self):
        stage(self)

        stars = starfield(n=120, z=0.0)
        stars.set_opacity(0.28)
        self.add(stars)

        headline(
            self,
            "Ask a question. Get a movie.",
            sub="But first: what must a mind already know?",
            accent=CORAL,
            hold=1.4,
        )

        # ---- the tree, built backward ---------------------------------- #
        def node(label: str, point, color: str, scale: float = 1.0) -> VGroup:
            dot = glow_dot(point=point, color=color, radius=0.06 * scale)
            text = Text(label, font_size=int(24 * scale), color=IVORY)
            text.next_to(dot, DOWN, buff=0.18)
            return VGroup(dot, text)

        root = node("explain quantum field theory", [0, 2.9, 0], CORAL, 1.15)

        l1 = [
            node("special relativity", [-3.1, 1.1, 0], SKY),
            node("quantum mechanics", [3.1, 1.1, 0], SKY),
        ]
        l2 = [
            node("spacetime intervals", [-4.6, -0.9, 0], OLIVE, 0.85),
            node("Lorentz invariance", [-1.7, -0.9, 0], OLIVE, 0.85),
            node("wavefunctions", [1.7, -0.9, 0], OLIVE, 0.85),
            node("operators", [4.6, -0.9, 0], OLIVE, 0.85),
        ]
        l3 = [
            node("distance", [-5.4, -2.6, 0], FOG, 0.7),
            node("symmetry", [-2.4, -2.6, 0], FOG, 0.7),
            node("waves", [2.4, -2.6, 0], FOG, 0.7),
            node("vectors", [5.4, -2.6, 0], FOG, 0.7),
        ]

        def edge(a: VGroup, b: VGroup) -> Line:
            return Line(
                a[0].get_center(), b[0].get_center(),
                color=FOG, stroke_width=1.8, stroke_opacity=0.7,
            )

        edges_down = [
            edge(root, l1[0]), edge(root, l1[1]),
            edge(l1[0], l2[0]), edge(l1[0], l2[1]),
            edge(l1[1], l2[2]), edge(l1[1], l2[3]),
            edge(l2[0], l3[0]), edge(l2[1], l3[1]),
            edge(l2[2], l3[2]), edge(l2[3], l3[3]),
        ]

        self.play(FadeIn(root, shift=DOWN * 0.3), run_time=0.9)
        caption(self, "The chain reasons backward from the target…",
                color=CORAL, hold=0.4)

        self.play(
            LaggedStart(*[Create(e) for e in edges_down[:2]], lag_ratio=0.3),
            LaggedStart(*[FadeIn(n, shift=DOWN * 0.2) for n in l1],
                        lag_ratio=0.3),
            run_time=1.4,
        )
        self.play(
            LaggedStart(*[Create(e) for e in edges_down[2:6]], lag_ratio=0.2),
            LaggedStart(*[FadeIn(n, shift=DOWN * 0.2) for n in l2],
                        lag_ratio=0.2),
            run_time=1.6,
        )
        self.play(
            LaggedStart(*[Create(e) for e in edges_down[6:]], lag_ratio=0.2),
            LaggedStart(*[FadeIn(n, shift=DOWN * 0.2) for n in l3],
                        lag_ratio=0.2),
            run_time=1.6,
        )

        # ---- zoom to known ground -------------------------------------- #
        zoom_to(self, l3[2][0], zoom=2.6, run_time=1.5)
        caption(self, "…until it bottoms out at things you already know.",
                color=OLIVE, hold=1.2)
        pull_back(self, run_time=1.3)

        # ---- walk it forward -------------------------------------------- #
        caption(self, "Then it walks the tree forward, as a curriculum.",
                color=GOLD, hold=0.3)
        for tier in (l3, l2, l1, [root]):
            self.play(
                *[t[0].animate.set_color(GOLD) for t in tier],
                *[Flash(t[0], color=GOLD, flash_radius=0.45,
                        line_length=0.14) for t in tier],
                run_time=0.75,
            )
        self.wait(0.5)

        # ---- 3D set piece ------------------------------------------------ #
        clear_caption(self)
        tilt_to_3d(self, phi=58 * DEGREES, theta=-38 * DEGREES,
                   zoom=0.85, run_time=2.0)
        caption(self, "Six agents build this tree before one line of code.",
                color=IVORY, hold=0.2)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(3.2)
        self.stop_ambient_camera_rotation()

        return_to_stage(self, run_time=1.6)
        clear_caption(self)
        tree = VGroup(root, *l1, *l2, *l3, *edges_down)
        self.play(FadeOut(tree), stars.animate.set_opacity(0.12),
                  run_time=1.0)

        headline(
            self,
            "Six agents. One film.",
            sub="intent · cartographer · curriculum · math-director · cinematographer · scene-composer",
            accent=GOLD,
            hold=1.8,
        )
        self.wait(0.4)
