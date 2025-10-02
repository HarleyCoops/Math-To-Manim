from manim import *
import numpy as np

class Scene1_IntroProbabilitySpace(Scene):
    def construct(self):
        # Title
        title = Text("Wasserstein Metric Space", font_size=48, color=BLUE)
        subtitle = Text("Section 1: Introduction to P_p(Ω)", font_size=32, color=GRAY)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Create domain Omega (circle)
        omega = Circle(radius=2, color=BLUE, fill_opacity=0.1)
        label_omega = MathTex(r"\Omega", font_size=48).next_to(omega, DOWN)

        self.play(Create(omega), Write(label_omega))
        self.wait(1)

        # Create probability measure (Gaussian)
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 2, 0.5],
            x_length=4,
            y_length=2,
            tips=False
        ).shift(UP * 0.5)

        mu_graph = axes.plot(
            lambda x: 1.5 * np.exp(-x**2),
            color=YELLOW,
            x_range=[-3, 3]
        )
        mu_label = MathTex(r"\mu", font_size=36, color=YELLOW).next_to(mu_graph, UP)

        self.play(Create(axes), Create(mu_graph), Write(mu_label))
        self.wait(1)

        # Main equation
        equation = MathTex(
            r"\mathcal{P}_p(\Omega) := \left\{\mu \in \mathcal{M}(\Omega) \,\bigg|\, ",
            r"\mu(\Omega)=1, \,",
            r"\int_{\Omega}|x|^p \, d\mu(x) < +\infty",
            r"\right\}",
            font_size=32
        ).to_edge(DOWN)

        self.play(Write(equation))
        self.wait(2)

        # Highlight constraints
        box1 = SurroundingRectangle(equation[1], color=GREEN)
        constraint1 = Text("Total mass = 1", font_size=24, color=GREEN).next_to(box1, UP)

        self.play(Create(box1), Write(constraint1))
        self.wait(1)

        box2 = SurroundingRectangle(equation[2], color=ORANGE)
        constraint2 = Text("Finite p-th moment", font_size=24, color=ORANGE).next_to(box2, UP)

        self.play(ReplacementTransform(box1, box2), ReplacementTransform(constraint1, constraint2))
        self.wait(2)

        # Fade out all VMobjects (excluding camera which is a Mobject)
        all_objects = VGroup(omega, label_omega, axes, mu_graph, mu_label, equation, box2, constraint2)
        self.play(FadeOut(all_objects))


class Scene2_WassersteinDistance(Scene):
    def construct(self):
        # Title
        title = Text("Wasserstein Distance W_p", font_size=40, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create two measures
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 2, 0.5],
            x_length=8,
            y_length=2,
            tips=False
        )

        mu_graph = axes.plot(lambda x: 1.5 * np.exp(-(x + 1.5)**2), color=RED, x_range=[-4, 4])
        nu_graph = axes.plot(lambda x: 1.5 * np.exp(-(x - 1.5)**2), color=BLUE, x_range=[-4, 4])

        mu_label = MathTex(r"\mu", font_size=36, color=RED).next_to(mu_graph, UL)
        nu_label = MathTex(r"\nu", font_size=36, color=BLUE).next_to(nu_graph, UR)

        self.play(Create(axes), Create(mu_graph), Create(nu_graph))
        self.play(Write(mu_label), Write(nu_label))
        self.wait(1)

        # Show multiple transport plans
        arrows = VGroup()
        for i in range(-3, 3):
            start = axes.c2p(i * 0.5 - 1.5, 1.5 * np.exp(-(i * 0.5)**2))
            end = axes.c2p(i * 0.5 + 1.5, 1.5 * np.exp(-(i * 0.5)**2))
            arrow = Arrow(start, end, buff=0, stroke_width=2, color=GRAY, stroke_opacity=0.5)
            arrows.add(arrow)

        self.play(LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.1))
        self.wait(1)

        # Highlight optimal transport
        optimal_arrows = VGroup()
        for i in range(-3, 3):
            start = axes.c2p(i * 0.5 - 1.5, 1.5 * np.exp(-(i * 0.5)**2))
            end = axes.c2p(i * 0.5 + 1.5, 1.5 * np.exp(-(i * 0.5)**2))
            arrow = Arrow(start, end, buff=0, stroke_width=4, color=YELLOW)
            optimal_arrows.add(arrow)

        self.play(ReplacementTransform(arrows, optimal_arrows))
        gamma_label = MathTex(r"\gamma^*", font_size=36, color=YELLOW).move_to(UP * 2)
        self.play(Write(gamma_label))
        self.wait(1)

        # Wasserstein distance equation
        equation = MathTex(
            r"W_p(\mu, \nu) := \left(",
            r"\min_{\gamma \in \operatorname{ADM}(\mu, \nu)} ",
            r"\int_{\Omega \times \Omega} |x-y|^p \, d\gamma(x,y)",
            r"\right)^{1/p}",
            font_size=28
        ).to_edge(DOWN)

        self.play(Write(equation))
        self.wait(2)

        # Highlight the optimization
        box = SurroundingRectangle(equation[1], color=GREEN)
        self.play(Create(box))
        self.wait(1)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene3_WpIsDistance(Scene):
    def construct(self):
        # Title
        title = Text("Proposition 1.1: W_p is a Distance", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Three properties
        prop1 = VGroup(
            Text("1. Non-negativity", font_size=28, color=GREEN),
            MathTex(r"W_p(\mu, \nu) \geq 0", font_size=32)
        ).arrange(DOWN, buff=0.3).shift(UP * 1.5)

        prop2 = VGroup(
            Text("2. Symmetry", font_size=28, color=ORANGE),
            MathTex(r"W_p(\mu, \nu) = W_p(\nu, \mu)", font_size=32)
        ).arrange(DOWN, buff=0.3).shift(UP * 0)

        prop3 = VGroup(
            Text("3. Triangle inequality", font_size=28, color=PURPLE),
            MathTex(r"W_p(\mu, \rho) \leq W_p(\mu, \nu) + W_p(\nu, \rho)", font_size=28)
        ).arrange(DOWN, buff=0.3).shift(DOWN * 1.5)

        self.play(FadeIn(prop1))
        self.wait(1)
        self.play(FadeIn(prop2))
        self.wait(1)
        self.play(FadeIn(prop3))
        self.wait(2)

        # Visual for triangle inequality
        self.play(FadeOut(prop1), FadeOut(prop2), prop3.animate.to_edge(UP).scale(0.8))

        # Three points in space
        mu_dot = Dot(point=LEFT * 3, color=RED, radius=0.15)
        nu_dot = Dot(point=RIGHT * 3 + UP * 1, color=BLUE, radius=0.15)
        rho_dot = Dot(point=DOWN * 2, color=GREEN, radius=0.15)

        mu_label = MathTex(r"\mu", color=RED).next_to(mu_dot, UP)
        nu_label = MathTex(r"\nu", color=BLUE).next_to(nu_dot, UP)
        rho_label = MathTex(r"\rho", color=GREEN).next_to(rho_dot, DOWN)

        self.play(Create(mu_dot), Create(nu_dot), Create(rho_dot))
        self.play(Write(mu_label), Write(nu_label), Write(rho_label))

        # Direct path
        direct = Line(mu_dot.get_center(), rho_dot.get_center(), color=YELLOW, stroke_width=4)
        direct_label = MathTex(r"W_p(\mu, \rho)", font_size=24, color=YELLOW).next_to(direct, LEFT)

        # Indirect path
        path1 = Line(mu_dot.get_center(), nu_dot.get_center(), color=GRAY, stroke_width=2)
        path2 = Line(nu_dot.get_center(), rho_dot.get_center(), color=GRAY, stroke_width=2)
        path1_label = MathTex(r"W_p(\mu, \nu)", font_size=20, color=GRAY).next_to(path1, UP)
        path2_label = MathTex(r"W_p(\nu, \rho)", font_size=20, color=GRAY).next_to(path2, RIGHT)

        self.play(Create(path1), Create(path2), Write(path1_label), Write(path2_label))
        self.wait(1)
        self.play(Create(direct), Write(direct_label))
        self.wait(2)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene4_CurvesMetricSpace(Scene):
    def construct(self):
        # Title
        title = Text("Curves on a Metric Space", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Grid background for abstract metric space X
        grid = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.2}
        )
        self.play(FadeIn(grid))

        # Curve omega(t)
        curve = ParametricFunction(
            lambda t: np.array([3 * np.cos(TAU * t), 2 * np.sin(TAU * t), 0]),
            t_range=[0, 1],
            color=YELLOW,
            stroke_width=4
        )

        self.play(Create(curve), run_time=2)

        # Moving point along curve
        dot = Dot(color=RED, radius=0.1)
        dot.move_to(curve.point_from_proportion(0))

        t_tracker = ValueTracker(0)
        dot.add_updater(lambda m: m.move_to(curve.point_from_proportion(t_tracker.get_value())))

        t_label = always_redraw(lambda: MathTex(
            f"t = {t_tracker.get_value():.2f}",
            font_size=28
        ).to_corner(UR))

        omega_label = MathTex(r"\omega(t)", font_size=32, color=YELLOW).next_to(curve, UP)

        self.play(FadeIn(dot), Write(t_label), Write(omega_label))
        self.play(t_tracker.animate.set_value(1), run_time=4, rate_func=linear)
        self.wait(1)

        # Metric derivative equation
        equation1 = MathTex(
            r"\omega: [0,1] \to X",
            font_size=32
        ).to_edge(DOWN).shift(UP * 1.5)

        equation2 = MathTex(
            r"|\omega'|(t) = \lim_{s \to t} \frac{d(\omega(s), \omega(t))}{|t-s|}",
            font_size=28
        ).next_to(equation1, DOWN)

        self.play(Write(equation1))
        self.wait(1)
        self.play(Write(equation2))
        self.wait(2)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene5_AbsolutelyContinuousCurves(Scene):
    def construct(self):
        # Title
        title = Text("Absolutely Continuous Curves", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Curve omega(t)
        axes = Axes(
            x_range=[0, 1, 0.2],
            y_range=[0, 3, 1],
            x_length=6,
            y_length=3,
            axis_config={"include_tip": True}
        ).shift(UP * 1)

        x_label = axes.get_x_axis_label("t")

        curve = axes.plot(
            lambda t: 1 + np.sin(2 * PI * t),
            color=YELLOW,
            x_range=[0, 1]
        )

        omega_label = MathTex(r"\omega(t)", font_size=32, color=YELLOW).next_to(curve, UP)

        self.play(Create(axes), Write(x_label))
        self.play(Create(curve), Write(omega_label))
        self.wait(1)

        # Graph of g(tau)
        g_axes = Axes(
            x_range=[0, 1, 0.2],
            y_range=[0, 2, 0.5],
            x_length=6,
            y_length=2,
            axis_config={"include_tip": True}
        ).shift(DOWN * 1.5)

        g_graph = g_axes.plot(
            lambda tau: 0.5 + 0.3 * np.sin(4 * PI * tau),
            color=GREEN,
            x_range=[0, 1]
        )

        g_label = MathTex(r"g(\tau)", font_size=32, color=GREEN).next_to(g_graph, UP)
        tau_label = g_axes.get_x_axis_label(r"\tau")

        self.play(Create(g_axes), Write(tau_label))
        self.play(Create(g_graph), Write(g_label))
        self.wait(1)

        # Highlight segment [s, t]
        s_val = 0.2
        t_val = 0.6

        s_line = DashedLine(g_axes.c2p(s_val, 0), g_axes.c2p(s_val, 2), color=RED)
        t_line = DashedLine(g_axes.c2p(t_val, 0), g_axes.c2p(t_val, 2), color=RED)

        s_label = MathTex("s", font_size=24, color=RED).next_to(s_line, DOWN)
        t_label = MathTex("t", font_size=24, color=RED).next_to(t_line, DOWN)

        self.play(Create(s_line), Create(t_line), Write(s_label), Write(t_label))

        # Shade integral region
        area = g_axes.get_riemann_rectangles(
            g_graph,
            x_range=[s_val, t_val],
            dx=0.02,
            color=GREEN,
            fill_opacity=0.3
        )

        self.play(FadeIn(area))
        self.wait(1)

        # Equation
        equation = MathTex(
            r"d(\omega(t), \omega(s)) \leq \int_s^t g(\tau) \, d\tau",
            font_size=32
        ).to_edge(DOWN)

        self.play(Write(equation))
        self.wait(2)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene6_MetricDerivativeLength(Scene):
    def construct(self):
        # Title
        title = Text("Theorem 1.3: Metric Derivative and Length", font_size=32, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.7))

        # Create curve
        axes = Axes(
            x_range=[0, 1, 0.2],
            y_range=[0, 2, 0.5],
            x_length=8,
            y_length=3,
            axis_config={"include_tip": True}
        )

        curve = axes.plot(
            lambda t: 1 + 0.5 * np.sin(4 * PI * t),
            color=YELLOW,
            x_range=[0, 1]
        )

        omega_label = MathTex(r"\omega(t)", font_size=32, color=YELLOW).next_to(curve, UP)

        self.play(Create(axes), Create(curve), Write(omega_label))
        self.wait(1)

        # Show partition
        n = 6
        partition_points = [i / n for i in range(n + 1)]
        dots = VGroup(*[
            Dot(axes.c2p(t, 1 + 0.5 * np.sin(4 * PI * t)), color=RED, radius=0.05)
            for t in partition_points
        ])

        self.play(LaggedStart(*[FadeIn(dot) for dot in dots], lag_ratio=0.1))

        # Connect with line segments
        segments = VGroup()
        for i in range(n):
            t0, t1 = partition_points[i], partition_points[i + 1]
            p0 = axes.c2p(t0, 1 + 0.5 * np.sin(4 * PI * t0))
            p1 = axes.c2p(t1, 1 + 0.5 * np.sin(4 * PI * t1))
            line = Line(p0, p1, color=GREEN, stroke_width=3)
            segments.add(line)

        self.play(LaggedStart(*[Create(seg) for seg in segments], lag_ratio=0.1))
        self.wait(1)

        # Sum notation
        sum_eq = MathTex(
            r"\sum_{i=0}^{n-1} d(\omega(t_i), \omega(t_{i+1}))",
            font_size=28
        ).to_corner(UL).shift(DOWN * 1.5)

        self.play(Write(sum_eq))
        self.wait(1)

        # Refine partition (more points)
        self.play(FadeOut(dots), FadeOut(segments))

        n2 = 20
        partition_points2 = [i / n2 for i in range(n2 + 1)]
        dots2 = VGroup(*[
            Dot(axes.c2p(t, 1 + 0.5 * np.sin(4 * PI * t)), color=RED, radius=0.03)
            for t in partition_points2
        ])

        self.play(LaggedStart(*[FadeIn(dot) for dot in dots2], lag_ratio=0.02), run_time=2)
        self.wait(1)

        # Equation
        equation = MathTex(
            r"\operatorname{length}(\omega) = \sup \left\{\sum d(\omega(t_i), \omega(t_{i+1}))\right\} = \int_0^1 |\omega'|(t) \, dt",
            font_size=24
        ).to_edge(DOWN)

        self.play(Write(equation))
        self.wait(2)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene7_LengthFormula(Scene):
    def construct(self):
        # Title
        title = Text("Proposition 1.5: Length Formula", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Split screen
        left_title = Text("Metric Derivative", font_size=28, color=YELLOW).shift(LEFT * 3 + UP * 2)
        right_title = Text("Integral", font_size=28, color=GREEN).shift(RIGHT * 3 + UP * 2)

        self.play(Write(left_title), Write(right_title))

        # Left: metric derivative visualization
        left_axes = Axes(
            x_range=[0, 1, 0.5],
            y_range=[0, 2, 1],
            x_length=3,
            y_length=2,
            axis_config={"include_tip": True}
        ).shift(LEFT * 3)

        derivative_graph = left_axes.plot(
            lambda t: 1 + 0.3 * np.cos(4 * PI * t),
            color=YELLOW,
            x_range=[0, 1]
        )

        derivative_label = MathTex(r"|\omega'|(t)", font_size=24, color=YELLOW).next_to(derivative_graph, UP)

        self.play(Create(left_axes), Create(derivative_graph), Write(derivative_label))
        self.wait(1)

        # Right: integral visualization
        right_axes = Axes(
            x_range=[0, 1, 0.5],
            y_range=[0, 2, 1],
            x_length=3,
            y_length=2,
            axis_config={"include_tip": True}
        ).shift(RIGHT * 3)

        integral_graph = right_axes.plot(
            lambda t: 1 + 0.3 * np.cos(4 * PI * t),
            color=GREEN,
            x_range=[0, 1]
        )

        area = right_axes.get_riemann_rectangles(
            integral_graph,
            x_range=[0, 1],
            dx=0.05,
            color=GREEN,
            fill_opacity=0.5
        )

        integral_label = MathTex(r"\int_0^1 |\omega'|(t) \, dt", font_size=24, color=GREEN).next_to(integral_graph, UP)

        self.play(Create(right_axes), Create(integral_graph), FadeIn(area), Write(integral_label))
        self.wait(1)

        # Main equation
        equation = MathTex(
            r"\operatorname{length}(\omega) = \int_0^1 |\omega'|(t) \, dt",
            font_size=36
        ).to_edge(DOWN).shift(UP * 0.5)

        box = SurroundingRectangle(equation, color=BLUE, buff=0.2)

        self.play(Write(equation), Create(box))
        self.wait(2)

        self.play(FadeOut(VGroup(*self.mobjects)))


class Scene8_FinalRecap(Scene):
    def construct(self):
        # Title
        title = Text("The Wasserstein Metric Space", font_size=44, color=BLUE, weight=BOLD)
        subtitle = MathTex(r"\mathbb{W}_p(\Omega)", font_size=60, color=GOLD)

        VGroup(title, subtitle).arrange(DOWN, buff=0.5)

        self.play(Write(title), run_time=1.5)
        self.play(Write(subtitle), run_time=1.5)
        self.wait(1)

        self.play(VGroup(title, subtitle).animate.scale(0.6).to_edge(UP))

        # Key concepts
        concepts = VGroup(
            MathTex(r"\mathcal{P}_p(\Omega) = \text{Probability measures with finite } p\text{-th moment}", font_size=24),
            MathTex(r"W_p(\mu, \nu) = \text{Wasserstein distance}", font_size=24),
            MathTex(r"\omega: [0,1] \to \mathbb{W}_p(\Omega) \text{ (Curves in Wasserstein space)}", font_size=24),
            MathTex(r"|\omega'|(t) = \text{Metric derivative}", font_size=24),
            MathTex(r"\operatorname{length}(\omega) = \int_0^1 |\omega'|(t) \, dt", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(DOWN * 0.5)

        for i, concept in enumerate(concepts):
            self.play(FadeIn(concept, shift=RIGHT * 0.5), run_time=0.8)
            self.wait(0.3)

        self.wait(2)

        # Final flash
        self.play(
            Flash(subtitle, line_length=0.5, num_lines=20, color=GOLD, flash_radius=1.5),
            subtitle.animate.set_color(YELLOW),
            run_time=1
        )
        self.wait(2)
