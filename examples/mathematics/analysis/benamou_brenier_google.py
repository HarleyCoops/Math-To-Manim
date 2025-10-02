from manim import *

class DiffusionOptimalTransportScene(Scene):
    def construct(self):
        # Scene Setup
        self.camera.background_color = BLACK
        title = Tex("Diffusion Models and Optimal Transport", font_size=48).to_edge(UP)
        subtitle = Tex("(Benamou-Brenier Theorem and Wasserstein Distance)", font_size=36).next_to(title, DOWN)
        self.play(Write(title), Write(subtitle))
        self.wait(1)

        # 1. Diffusion's Nebula
        self.diffusion_nebula_section()

        # 2. River of Least Resistance
        self.river_of_least_resistance_section()

        # 3. Wasserstein's Forge
        self.wasserstein_forge_section()

        # 4. Benamou-Brenier's Symphony
        self.benamou_brenier_symphony_section()

        # Final Quote
        quote = Tex(
            "In the calculus of shapes, Wasserstein is the sculptor,",
            "and Benamou-Brenier the chisel—carving geodesics from the marble of probability.",
            font_size=30
        ).to_edge(DOWN).shift(UP*0.5)
        self.play(Write(quote))
        self.wait(3)

    def diffusion_nebula_section(self):
        self.clear() # clear screen for new section
        section_title = Tex("1. Diffusion's Nebula", font_size=40).to_edge(UP)
        self.play(Write(section_title))

        # 1a. Initial Galaxies alpha_0 and alpha_1
        alpha_0_points = np.random.normal(0, 1, size=(100, 2)) # Gaussian distribution 0
        alpha_1_points = np.random.normal(2, 1, size=(100, 2)) # Gaussian distribution 1, shifted

        # Create VGroups of dots with proper 3D point conversion
        alpha_0 = VGroup(*[Dot(point=[x, y, 0], color=BLUE) for x, y in alpha_0_points]).shift(LEFT * 3)
        alpha_1 = VGroup(*[Dot(point=[x, y, 0], color=GOLD) for x, y in alpha_1_points]).shift(RIGHT * 3)


        alpha_0_label = MathTex(r"\alpha_0").next_to(alpha_0, DOWN)
        alpha_1_label = MathTex(r"\alpha_1").next_to(alpha_1, DOWN)

        self.play(FadeIn(alpha_0), Write(alpha_0_label), FadeIn(alpha_1), Write(alpha_1_label))
        self.wait(1)

        # 1b. Formula for alpha_t
        alpha_t_formula = MathTex(r"\alpha_t = \left( (1 - t)P_0 + tP_1 \right)_\# (\alpha_0 \otimes \alpha_1)").to_edge(UP)
        self.play(Write(alpha_t_formula), Transform(section_title, Tex("1. Diffusion's Nebula: Dynamic Formulation", font_size=40).to_edge(UP)))
        self.wait(2)

        # 1c. Animate alpha_t as a bridge (REVISED with AnimationGroup - REPLACE THE OLD LOOP ENTIRELY)
        alpha_t_bridge = VGroup()
        connecting_dot_anims = [] # List to store all animations

        dots_0 = [dot.get_center() for dot in alpha_0] # Get centers BEFORE loop
        dots_1 = [dot.get_center() for dot in alpha_1] # Get centers BEFORE loop


        for i in range(100):
            connecting_dot = Dot(point=dots_0[i], color=BLUE) # Starting point for morph
            alpha_t_bridge.add(connecting_dot)

            def update_connecting_dot(mob, alpha): # alpha from 0 to 1
                p0 = dots_0[i] # Use pre-calculated centers
                p1 = dots_1[i] # Use pre-calculated centers
                mob.move_to((1-alpha) * p0 + alpha * p1)
                mob.set_color(interpolate_color(BLUE, GOLD, alpha)) # Color interpolation
                return mob

            anim = UpdateFromAlphaFunc(connecting_dot, update_connecting_dot)
            connecting_dot_anims.append(anim) # Add animation to list

        self.play(FadeOut(alpha_0), FadeOut(alpha_1), FadeIn(alpha_t_bridge)) # Fade out galaxies first

        # Play ALL animations in AnimationGroup for simultaneous morphing
        self.play(AnimationGroup(*connecting_dot_anims), run_time=2, rate_func=linear) # Animate ALL dots together over 2 seconds - SINGLE PLAY CALL

        self.wait(2)
        self.play(FadeOut(alpha_t_bridge), FadeOut(alpha_0_label), FadeOut(alpha_1_label), FadeOut(alpha_t_formula), FadeOut(section_title))

    def river_of_least_resistance_section(self):
        self.clear()
        section_title = Tex("2. River of Least Resistance", font_size=40).to_edge(UP)
        self.play(Write(section_title))

        # 2a. Visualize Velocity Field nu_t
        vector_field = VectorField(lambda p: np.array([0.5, 0, 0]))  # Add z-component of 0 for 3D
        stream_lines = StreamLines(
            vector_field.func,
            x_range=[-5, 5, 0.5],
            y_range=[-3, 3, 0.5],
            stroke_width=1,
            padding=1
        )

        self.play(Create(vector_field), Transform(section_title, Tex("2. River of Least Resistance: Velocity Field", font_size=40).to_edge(UP)))
        self.play(Create(stream_lines))
        self.wait(2)
        self.play(stream_lines.animate.shift(RIGHT * 2))  # Animate the flow
        self.wait(1)

        # 2b. Optimization and Continuity Equation
        optimization_formula = MathTex(
            r"\min_{\nu_t} \left\{ \int \|\nu_t\|_{L^2(\alpha_t)}^2 \, dt \ : \ \text{div}(\alpha_t \nu_t) + \partial_t \alpha_t = 0 \right\}"
        ).to_edge(UP)
        continuity_equation = MathTex(r"\text{div}(\alpha_t \nu_t) + \partial_t \alpha_t = 0").next_to(optimization_formula, DOWN, buff=0.5)

        self.play(Transform(section_title, Tex("2. River of Least Resistance: Optimization", font_size=40).to_edge(UP)), FadeOut(vector_field))
        self.play(Write(optimization_formula))
        self.wait(2)
        self.play(Write(continuity_equation), Transform(section_title, Tex("2. River of Least Resistance: Continuity Equation", font_size=40).to_edge(UP)))
        self.wait(3)

        # 2c. Visual explanation of Continuity Equation
        continuity_explanation = Tex("Mass Conservation:", "No particles lost or gained", font_size=30).next_to(continuity_equation, DOWN, buff=0.5)
        continuity_explanation[1].set_color(GREEN)
        self.play(Write(continuity_explanation))
        self.wait(2)

        self.play(FadeOut(stream_lines), FadeOut(optimization_formula), FadeOut(continuity_equation), FadeOut(continuity_explanation), FadeOut(section_title))

    def wasserstein_forge_section(self):
        self.clear()
        section_title = Tex("3. Wasserstein's Forge", font_size=40).to_edge(UP)
        self.play(Write(section_title))

        # 3a. Wasserstein Distance Formula
        wasserstein_formula = MathTex(
            r"W_2^2(\alpha_0, \alpha_1) = \inf_{T_1} \left\{ \int \|x - T_1(x)\|^2 \, d\alpha_0(x) \ : \ (T_1)_\# \alpha_0 = \alpha_1 \right\}"
        ).to_edge(UP)
        self.play(Write(wasserstein_formula), Transform(section_title, Tex("3. Wasserstein's Forge: Wasserstein Distance", font_size=40).to_edge(UP)))
        self.wait(2)

        # 3b. Optimal Map T_1 (Grid Warping)
        # Create grid using lines
        grid = VGroup()
        # Vertical lines
        for x in np.arange(-3, 3.1, 0.5):
            grid.add(Line(np.array([x, -3, 0]), np.array([x, 3, 0]), stroke_width=1, color=GRAY))
        # Horizontal lines
        for y in np.arange(-3, 3.1, 0.5):
            grid.add(Line(np.array([-3, y, 0]), np.array([3, y, 0]), stroke_width=1, color=GRAY))
            
        self.play(Create(grid))
        self.wait(0.5)

        def warp_grid(mob, alpha):
            for line in mob:
                points = line.points
                points[:, 0] += alpha * 2 * np.exp(-((points[:, 1])**2)/2)  # Add some curvature for visual interest
            return mob

        warped_grid = grid.copy()
        self.play(
            UpdateFromAlphaFunc(warped_grid, warp_grid),
            Transform(section_title, Tex("3. Wasserstein's Forge: Optimal Map $T_1$", font_size=40).to_edge(UP)),
            run_time=2
        )
        self.wait(2)

        # 3c. Geodesic Path formula
        geodesic_formula = MathTex(r"\alpha_t = \left( (1 - t)\text{Id} + tT_1 \right)_\# \alpha_0").next_to(wasserstein_formula, DOWN, buff=0.5)
        self.play(Write(geodesic_formula), Transform(section_title, Tex("3. Wasserstein's Forge: Geodesic Path", font_size=40).to_edge(UP)))
        self.wait(2)
        self.play(FadeOut(grid), FadeOut(warped_grid), FadeOut(wasserstein_formula), FadeOut(geodesic_formula), FadeOut(section_title))

    def benamou_brenier_symphony_section(self):
        self.clear()
        section_title = Tex("4. Benamou-Brenier's Symphony", font_size=40).to_edge(UP)
        self.play(Write(section_title))

        # 4a. Recap and Combination
        symphony_text = VGroup(
            Tex("Velocity Field ", r"$\nu_t$", ": guiding the flow").scale(0.7),
            Tex("Continuity Equation ", r"div($\alpha_t \nu_t$) + $\partial_t \alpha_t = 0$", ": mass conservation").scale(0.7),
            Tex("Wasserstein Metric ", r"$W_2^2(\alpha_0, \alpha_1)$", ": minimal effort").scale(0.7)
        ).arrange(DOWN, aligned_edge=LEFT)
        symphony_text[0][1].set_color(YELLOW)
        symphony_text[1][1].set_color(GREEN)
        symphony_text[2][1].set_color(BLUE)

        self.play(Transform(section_title, Tex("4. Benamou-Brenier's Symphony: Harmonizing Concepts", font_size=40).to_edge(UP)))
        for text_part in symphony_text:
            self.play(Write(text_part))
            self.wait(1)

        benamou_brenier_theorem = Tex(
            "Benamou-Brenier Theorem:",
            "Connects Optimal Transport and Fluid Dynamics",
            font_size=35
        ).to_edge(DOWN*2)
        benamou_brenier_theorem[1].set_color(PURPLE)
        self.play(Write(benamou_brenier_theorem))
        self.wait(3)
        self.play(FadeOut(symphony_text), FadeOut(benamou_brenier_theorem), FadeOut(section_title))