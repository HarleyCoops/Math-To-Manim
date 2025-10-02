from manim import *
import numpy as np


class DiffusionScene(Scene):
    def construct(self):
        # Create initial and final distributions
        alpha_0 = VGroup(*[Dot(radius=0.05, color=BLUE) for _ in range(50)])
        alpha_0.arrange_in_grid(rows=5, cols=10, buff=0.2)
        alpha_0.shift(LEFT * 3)

        alpha_1 = VGroup(*[Dot(radius=0.05, color=GOLD) for _ in range(50)])
        alpha_1.arrange_in_grid(rows=5, cols=10, buff=0.2)
        alpha_1.shift(RIGHT * 3)

        # Create interpolation path
        def get_alpha_t(t):
            return VGroup(*[
                Dot(
                    radius=0.05,
                    color=interpolate_color(BLUE, GOLD, t),
                    point=interpolate(
                        alpha_0[i].get_center(),
                        alpha_1[i].get_center(),
                        t
                    )
                )
                for i in range(len(alpha_0))
            ])

        # Animations
        self.play(Create(alpha_0), Create(alpha_1))
        self.play(
            UpdateFromAlphaFunc(
                alpha_0,
                lambda m, t: m.become(get_alpha_t(t))
            ),
            run_time=3
        )
        self.wait()
