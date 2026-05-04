from manim import *

class IntroProbabilitySpaceRevised(Scene):
    def construct(self):
        # Step 1: Introduce Omega (Domain)
        omega = Circle(radius=2, color=BLUE)
        label_omega = Tex(r"Domain $\Omega$").next_to(omega, DOWN)
        self.play(Create(omega), Write(label_omega))
        self.wait(2)

        # Step 2: Introduce Measures
        dots = VGroup(*[Dot(color=YELLOW).move_to(omega.point_from_proportion(x)) for x in np.linspace(0, 1, 20)])
        self.play(LaggedStart(*[Create(dot) for dot in dots], lag_ratio=0.1))
        self.wait(1)
        self.play(Transform(dots, FunctionGraph(
            lambda x: np.exp(-x**2) * 2 + omega.get_center()[1],
            color=YELLOW,
            x_range=[-3, 3]
        )))
        label_mu = Tex(r"Measure $\mu$").next_to(dots, UP)
        self.play(Write(label_mu))
        self.wait(2)

        # Step 3: Probability Measure (Total Mass = 1)
        # Create a simple balance scale using basic shapes
        scale_base = Line(LEFT*2, RIGHT*2, color=WHITE)
        scale_stand = Line(ORIGIN, UP*2, color=WHITE).move_to(scale_base.get_center())
        scale_beam = Line(LEFT, RIGHT, color=WHITE).next_to(scale_stand.get_end(), UP, buff=0)
        scale = VGroup(scale_base, scale_stand, scale_beam).scale(0.5).to_edge(LEFT)
        
        mass_counter = DecimalNumber(0, num_decimal_places=2).next_to(scale, UP)
        self.play(Create(scale), FadeIn(mass_counter))
        self.play(mass_counter.animate.set_value(1), run_time=2)
        label_prob = Tex(r"Probability Measure: $\mu(\Omega) = 1$").to_edge(UP)
        self.play(Write(label_prob))
        self.wait(2)

        # Step 4: The p-th Moment (Visualize Spread)
        lever = Line(LEFT*3, RIGHT*3).to_edge(DOWN)
        weights = VGroup(*[
            Dot(color=RED).move_to(lever.point_from_proportion(np.abs(x/6 + 0.5))).scale(1 + 0.5*np.abs(x)**2)
            for x in np.linspace(-3, 3, 10)
        ])
        moment_label = Tex(r"$\int_{\Omega} |x|^p \, d\mu(x)$").next_to(lever, UP)
        self.play(Create(lever), Create(weights), Write(moment_label))
        self.wait(2)

        # Step 5: Finite Moment Condition
        gaussian = FunctionGraph(
            lambda x: np.exp(-x**2) * 2,
            color=GREEN,
            x_range=[-3, 3]
        )
        heavy_tail = FunctionGraph(
            lambda x: 1/(1 + x**2),
            color=RED,
            x_range=[-3, 3]
        )
        finite_label = Tex(r"Finite $p$-th moment").next_to(gaussian, UP)
        infinite_label = Tex(r"Infinite $p$-th moment").next_to(heavy_tail, UP)
        self.play(Transform(dots, gaussian), Write(finite_label))
        self.wait(1)
        self.play(Transform(dots, heavy_tail), Write(infinite_label))
        self.wait(2)

        # Step 6: Assemble the Full Equation
        equation = MathTex(
            r"\mathcal{P}_p(\Omega) := \left\{\mu \in \mathcal{M}(\Omega) \,\bigg|\, \mu(\Omega)=1, \, \int_{\Omega}|x|^p \, d\mu(x) < +\infty \right\}"
        ).scale(0.8).to_edge(UP)
        self.play(FadeOut(scale, mass_counter, lever, weights, moment_label, finite_label, infinite_label))
        self.play(Transform(label_prob, equation))
        self.wait(3)