"""Small Manim CE reference scene for M2M2 renderer checks.

Render with:
    python -m manim -ql examples/reference/limit_tangent_reference.py LimitTangentReference
"""

from manim import *


class LimitTangentReference(Scene):
    def construct(self):
        title = Text("Derivative as a tangent slope", font_size=34)
        title.to_edge(UP)

        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 5, 1],
            x_length=7,
            y_length=4,
            tips=False,
        ).shift(DOWN * 0.35)
        labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        graph = axes.plot(lambda x: 0.22 * (x - 1) ** 2 + 1, x_range=[-0.5, 4.5], color=BLUE)

        a = 1.4
        h_start = 2.0
        h_end = 0.55
        dot_a = Dot(axes.c2p(a, graph.underlying_function(a)), color=YELLOW)
        dot_h = Dot(axes.c2p(a + h_start, graph.underlying_function(a + h_start)), color=YELLOW)

        def secant_line(h, color=GREEN):
            p1 = axes.c2p(a, graph.underlying_function(a))
            p2 = axes.c2p(a + h, graph.underlying_function(a + h))
            return Line(p1, p2, color=color).scale(1.7)

        secant = secant_line(h_start)
        tangent = secant_line(h_end, color=ORANGE)

        formula = MathTex(
            r"f'(a)=\lim_{h\to 0}\frac{f(a+h)-f(a)}{h}",
            font_size=34,
        ).to_edge(DOWN)
        caption = Text("Shrink the interval: secant slope -> tangent slope", font_size=24)
        caption.next_to(formula, UP, buff=0.25)

        self.play(Write(title), Create(axes), Write(labels))
        self.play(Create(graph), FadeIn(dot_a), FadeIn(dot_h))
        self.play(Create(secant), FadeIn(caption), Write(formula))

        moving_dot = Dot(axes.c2p(a + h_end, graph.underlying_function(a + h_end)), color=YELLOW)
        self.play(Transform(dot_h, moving_dot), Transform(secant, tangent), run_time=2)
        self.play(Indicate(tangent), Indicate(formula))
        self.wait(1)

