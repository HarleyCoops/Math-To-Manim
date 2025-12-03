from manim import *
import numpy as np

class BiasVarianceTradeoff(Scene):
    def construct(self):
        # ---------------------------------------------------------
        # Global Constants & Style
        # ---------------------------------------------------------
        self.camera.background_color = "#1E1E1E"
        
        # Colors
        C_TRUTH = "#FFFFFF"
        C_MODEL = "#58C4DD"     # Teal
        C_BIAS = "#FC6255"      # Red
        C_VAR = "#FFFF00"       # Yellow
        C_NOISE = "#9A72AC"     # Purple
        C_DATA = "#C0C0C0"      # Silver
        C_EXP = "#83C167"       # Green
        
        # Fixed Seed for Reproducibility
        np.random.seed(42)

        # ---------------------------------------------------------
        # SCENE 1: The Probabilistic Toolkit
        # ---------------------------------------------------------
        
        # 1. Setup Algebra
        alg_eq = MathTex(r"(A - B)^2", r"=", r"A^2 - 2AB + B^2")
        alg_eq.scale(1.5)
        self.play(Write(alg_eq))
        self.wait(1)

        # 2. Transformation to Variance
        # \text{Var}(X) = \mathbb{E}[(X - \mathbb{E}[X])^2]
        var_eq = MathTex(
            r"\text{Var}(X)", r"=", r"\mathbb{E}[", r"(X - ", r"\mathbb{E}[X]", r")^2", r"]"
        )
        var_eq.scale(1.5)
        
        # Coloring
        var_eq[0].set_color(C_VAR) # Var(X)
        var_eq[4].set_color(C_EXP) # E[X] inner

        self.play(TransformMatchingTex(alg_eq, var_eq))
        self.wait(1)

        # 3. Visualization (Normal Distribution)
        self.play(var_eq.animate.to_edge(UP).scale(0.7))

        ax_s1 = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 0.5, 0.1],
            axis_config={"include_tip": False, "color": GRAY},
        ).scale(0.8).shift(DOWN * 0.5)
        
        # ValueTracker for Sigma (Standard Deviation)
        sigma_tracker = ValueTracker(1.0)

        # Dynamic Graph
        def get_bell_curve():
            s = sigma_tracker.get_value()
            return ax_s1.plot(
                lambda x: (1/(s * np.sqrt(2*np.pi))) * np.exp(-0.5 * (x/s)**2),
                color=C_MODEL
            ).set_fill(C_MODEL, opacity=0.5)

        curve = always_redraw(get_bell_curve)

        # Expectation Line (Mean is always 0 here)
        exp_line = DashedLine(
            start=ax_s1.c2p(0, 0),
            end=ax_s1.c2p(0, 0.4), # approximated peak height for sigma=1
            color=C_EXP
        )
        exp_label = MathTex(r"\mathbb{E}[X]", color=C_EXP).next_to(exp_line, UP)
        
        # Dynamic Expectation Line Height
        exp_line.add_updater(lambda m: m.put_start_and_end_on(
            ax_s1.c2p(0,0),
            ax_s1.c2p(0, (1/(sigma_tracker.get_value() * np.sqrt(2*np.pi))))
        ))
        exp_label.add_updater(lambda m: m.next_to(exp_line, UP))

        # Variance Arrows (Horizontal)
        def get_var_arrow():
            s = sigma_tracker.get_value()
            # Draw arrow at 60% of peak height
            y_height = (1/(s * np.sqrt(2*np.pi))) * 0.6
            x_width = s  # 1 standard deviation
            return DoubleArrow(
                start=ax_s1.c2p(-x_width, y_height),
                end=ax_s1.c2p(x_width, y_height),
                color=C_VAR,
                buff=0
            )

        var_arrow = always_redraw(get_var_arrow)
        var_label = MathTex(r"\text{Var}(X)", color=C_VAR).add_updater(
            lambda m: m.next_to(var_arrow, UP, buff=0.1)
        )

        self.play(Create(ax_s1), FadeIn(curve))
        self.play(Create(exp_line), FadeIn(exp_label))
        self.play(Create(var_arrow), FadeIn(var_label))

        # Breathing Effect
        self.play(sigma_tracker.animate.set_value(1.5), run_time=1.5) # Widen
        self.play(sigma_tracker.animate.set_value(0.6), run_time=1.5) # Narrow
        self.play(sigma_tracker.animate.set_value(1.0), run_time=1.0) # Reset

        self.wait(1)
        
        # Cleanup Scene 1
        self.play(FadeOut(Group(var_eq, ax_s1, curve, exp_line, exp_label, var_arrow, var_label)))

        # ---------------------------------------------------------
        # SCENE 2: The Signal and The Noise
        # ---------------------------------------------------------
        
        # 1. The Truth
        ax_s2 = Axes(
            x_range=[-1, 7, 1],
            y_range=[-2, 4, 1],
            x_length=10,
            y_length=6,
            axis_config={"color": GRAY}
        )

        def true_func(x):
            return np.sin(x) + 0.3 * x

        truth_graph = ax_s2.plot(true_func, color=C_TRUTH, stroke_width=4)
        truth_graph.set_shadow(0.5)
        truth_label = MathTex("f(x)", color=C_TRUTH).next_to(truth_graph, UP, buff=-0.5).shift(RIGHT*2)

        self.play(Create(ax_s2))
        self.play(Create(truth_graph), Write(truth_label))

        # 2. The Noise (Data Generation)
        x_data = np.linspace(0, 6, 20)
        noise = np.random.normal(0, 0.4, size=x_data.shape)
        y_data = true_func(x_data) + noise

        dots = VGroup()
        for x, y in zip(x_data, y_data):
            dot = Dot(ax_s2.c2p(x, y), color=C_NOISE)
            dots.add(dot)

        noise_label = MathTex(r"y = f(x) + \epsilon", color=C_NOISE)
        noise_label.move_to(ax_s2.c2p(1, 2.5))

        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.05))
        self.play(Write(noise_label))

        # 3. The Attempt (Simple Linear Model)
        # Linear Regression
        coefs = np.polyfit(x_data, y_data, 1)
        poly1 = np.poly1d(coefs)

        model_line = ax_s2.plot(lambda x: poly1(x), color=C_MODEL, x_range=[-0.5, 6.5])
        
        # Simulated Cursor
        cursor = Triangle(color=C_MODEL, fill_opacity=1).scale(0.2).rotate(-90*DEGREES)
        cursor.move_to(model_line.get_start())
        
        self.play(FadeIn(cursor))
        self.play(
            Create(model_line),
            MoveAlongPath(cursor, model_line),
            run_time=2
        )
        self.play(FadeOut(cursor))

        # Residuals
        residuals = VGroup()
        for x, y in zip(x_data, y_data):
            y_hat = poly1(x)
            line = DashedLine(
                start=ax_s2.c2p(x, y),
                end=ax_s2.c2p(x, y_hat),
                color=C_BIAS,
                stroke_width=2
            )
            residuals.add(line)
        
        res_text = Text("Residuals", font_size=24, color=C_BIAS).next_to(residuals[10], LEFT)

        self.play(Create(residuals), run_time=1.5)
        self.play(Write(res_text))
        self.wait(1)

        # Cleanup Scene 2
        self.play(FadeOut(Group(ax_s2, truth_graph, truth_label, dots, noise_label, model_line, residuals, res_text)))

        # ---------------------------------------------------------
        # SCENE 3: The Dartboard Analogy
        # ---------------------------------------------------------
        
        # Setup targets
        def create_target():
            g = VGroup()
            for r, c in zip([2.0, 1.5, 1.0, 0.5], [GRAY_D, GRAY_C, GRAY_B, WHITE]):
                g.add(Circle(radius=r, color=GRAY_A, fill_color=c, fill_opacity=0.3))
            return g

        left_target = create_target().shift(LEFT * 3.5)
        right_target = create_target().shift(RIGHT * 3.5)

        title_bias = Text("High Bias", color=C_BIAS, font_size=36).next_to(left_target, UP)
        title_var = Text("High Variance", color=C_VAR, font_size=36).next_to(right_target, UP)

        self.play(
            FadeIn(left_target), Write(title_bias),
            FadeIn(right_target), Write(title_var)
        )

        # Left Darts (High Bias - Clustered but wrong)
        # Center of cluster at (1, 1) relative to target center
        bias_center = left_target.get_center() + np.array([1.0, 1.0, 0])
        bias_darts = VGroup()
        for _ in range(10):
            offset = np.random.normal(0, 0.15, 3) # Low spread
            offset[2] = 0
            pos = bias_center + offset
            dart = Dot(point=pos, color=C_MODEL, radius=0.1)
            bias_darts.add(dart)

        # Right Darts (High Variance - Correct average but scattered)
        # Center at (0,0) relative to target center
        var_center = right_target.get_center()
        var_darts = VGroup()
        var_points = []
        for _ in range(10):
            offset = np.random.normal(0, 0.8, 3) # High spread
            offset[2] = 0
            pos = var_center + offset
            var_points.append(pos)
            dart = Dot(point=pos, color=C_MODEL, radius=0.1)
            var_darts.add(dart)

        # Animation Left
        self.play(LaggedStart(*[
            GrowFromCenter(d) for d in bias_darts
        ], lag_ratio=0.1))
        
        # Bias Arrow
        bias_arrow = Arrow(bias_center, left_target.get_center(), color=C_BIAS, buff=0)
        bias_label = Text("Bias", color=C_BIAS, font_size=24).next_to(bias_arrow, UP, buff=0)
        
        self.play(GrowArrow(bias_arrow), FadeIn(bias_label))
        text_bias_desc = Text("Consistent... but wrong", font_size=24).next_to(left_target, DOWN)
        self.play(Write(text_bias_desc))

        # Animation Right
        self.play(LaggedStart(*[
            GrowFromCenter(d) for d in var_darts
        ], lag_ratio=0.1))

        # Average Dart
        avg_pos = np.mean(var_points, axis=0)
        ghost_dart = Dot(avg_pos, color=WHITE, radius=0.15).set_opacity(0.8)
        self.play(FadeIn(ghost_dart, scale=2), run_time=0.5)
        self.play(FadeOut(ghost_dart), run_time=0.5)

        # Variance Halo
        var_halo = Circle(radius=1.2, color=C_VAR, fill_color=C_VAR, fill_opacity=0.2)
        var_halo.move_to(var_center)
        var_label = Text("Variance", color=C_VAR, font_size=24).next_to(var_halo, UP, buff=0)

        self.play(FadeIn(var_halo), FadeIn(var_label))
        text_var_desc = Text("Unreliable", font_size=24).next_to(right_target, DOWN)
        self.play(Write(text_var_desc))

        self.wait(1)
        self.clear()

        # ---------------------------------------------------------
        # SCENE 4: The Mathematical Surgery
        # ---------------------------------------------------------
        
        # Step 1: MSE
        mse_eq = MathTex(
            r"\text{MSE}", r"=", r"\mathbb{E}[", r"(y - \hat{f})^2", r"]"
        ).scale(1.2)
        self.play(Write(mse_eq))
        self.wait(1)

        # Step 2: The Trick (+f -f)
        # We group {{y-f}} and {{f-\hat{f}}} for later separation
        trick_eq = MathTex(
            r"\text{MSE}", r"=", r"\mathbb{E}[", r"((y - f)", r"+", r"(f - \hat{f}))^2", r"]"
        ).scale(1.2)
        
        # Highlight inserted f
        # Note: Indexing depends on specific structure, hardcoded for visual effect here
        # trick_eq contains: MSE, =, E[, ((y-f), +, (f-f_hat))^2, ]
        
        self.play(TransformMatchingTex(mse_eq, trick_eq))
        self.wait(1)

        # Step 3: Expansion
        expanded_eq = MathTex(
            r"=", 
            r"\mathbb{E}[", r"(y - f)^2", r"]", r"+", 
            r"\mathbb{E}[", r"(f - \hat{f})^2", r"]", r"+",
            r"2\mathbb{E}[", r"(y - f)(f - \hat{f})", r"]"
        ).scale(1)
        expanded_eq.shift(UP * 0.5)

        # Color coding
        # (y-f)^2 -> Noise
        expanded_eq[2].set_color(C_NOISE) 
        # (f-f_hat)^2 -> Model Error
        expanded_eq[6].set_color(C_MODEL)
        # Cross term -> Gray
        expanded_eq[9:].set_color(GRAY)

        self.play(TransformMatchingTex(trick_eq, expanded_eq))
        self.wait(1)

        # Step 4: Cross term vanishes
        cross_term = expanded_eq[8:] # + 2E[...]
        
        indep_text = Text("Assumed Independent -> 0", font_size=24, color=GRAY).next_to(cross_term, DOWN)
        self.play(FadeIn(indep_text))
        self.play(FadeOut(cross_term), FadeOut(indep_text))
        
        # Step 5: Final Form
        final_eq = MathTex(
            r"\text{Error}", r"=", r"\text{Bias}^2", r"+", r"\text{Variance}", r"+", r"\text{Irreducible Error}"
        ).scale(1.2)
        
        final_eq[2].set_color(C_BIAS)
        final_eq[4].set_color(C_VAR)
        final_eq[6].set_color(C_NOISE)

        # Use replacement transform to gather parts
        self.play(ReplacementTransform(expanded_eq[0:8], final_eq))
        
        box = SurroundingRectangle(final_eq, color=WHITE, buff=0.2)
        self.play(Create(box))
        self.wait(2)

        self.clear()

        # ---------------------------------------------------------
        # SCENE 5: The Tradeoff & The Sweet Spot
        # ---------------------------------------------------------

        # Layout Setup
        # Top: Data & Model
        ax_top = Axes(
            x_range=[0, 6, 1], y_range=[-2, 4, 1],
            x_length=8, y_length=3,
            axis_config={"include_tip": False}
        ).shift(UP * 2)

        # Reuse data from Scene 2
        top_dots = VGroup()
        for x, y in zip(x_data, y_data):
            top_dots.add(Dot(ax_top.c2p(x, y), color=C_NOISE, radius=0.06))

        # Bottom: Error Curves
        ax_bot = Axes(
            x_range=[0, 10, 1], y_range=[0, 10, 2],
            x_length=8, y_length=3,
            axis_config={"include_tip": False}
        ).shift(DOWN * 2)
        
        # Labels
        lab_c = Text("Model Complexity", font_size=20).next_to(ax_bot, DOWN)
        lab_e = Text("Error", font_size=20).next_to(ax_bot, LEFT).rotate(90*DEGREES)

        self.play(Create(ax_top), Create(top_dots))
        self.play(Create(ax_bot), Write(lab_c), Write(lab_e))


        # Complexity Slider Tracker
        # Map 0 -> 1 (deg 1) to 1 -> 10 (deg 12 roughly)
        complexity_tracker = ValueTracker(1) 

        # --- Dynamic Top Graph (Polynomial Fit) ---
        def get_poly_curve():
            k = int(complexity_tracker.get_value())
            # Limit degree to len(x)-1
            deg = min(k, 15) 
            
            # Use polyfit
            # Suppress RankWarning for high degrees on small data
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                coefs = np.polyfit(x_data, y_data, deg)
                poly = np.poly1d(coefs)
            
            # Plot
            graph = ax_top.plot(lambda x: poly(x), color=C_MODEL, x_range=[0, 6])
            
            # Text status
            status = "Underfitting" if k < 3 else "Overfitting" if k > 7 else "Balanced"
            col = C_BIAS if k < 3 else C_VAR if k > 7 else C_EXP
            lbl = Text(status, color=col, font_size=24).move_to(ax_top.c2p(5, 3))
            
            return VGroup(graph, lbl)

        poly_anim = always_redraw(get_poly_curve)
        self.add(poly_anim)

        # --- Dynamic Bottom Curves ---
        # Analytical Functions as per prompt
        # Bias: 4 * e^(-0.5 * x)
        # Var: 0.1 * x^2
        # Noise: 0.5 constant
        # Total: Sum
        
        # Use a clipping rectangle or TracedPath to reveal curves
        # Mapping tracker (1 to 12) to x-axis of bottom graph (0 to 10)
        # Let's map directly: x = tracker - 1. 
        
        def get_bias_curve():
            x_limit = complexity_tracker.get_value() - 1
            if x_limit < 0: x_limit = 0.01
            return ax_bot.plot(lambda x: 4 * np.exp(-0.5 * x), x_range=[0, x_limit], color=C_BIAS)
        
        def get_var_curve():
            x_limit = complexity_tracker.get_value() - 1
            if x_limit < 0: x_limit = 0.01
            return ax_bot.plot(lambda x: 0.1 * x**2, x_range=[0, x_limit], color=C_VAR)
            
        def get_total_curve():
            x_limit = complexity_tracker.get_value() - 1
            if x_limit < 0: x_limit = 0.01
            return ax_bot.plot(lambda x: 4 * np.exp(-0.5 * x) + 0.1 * x**2 + 0.5, x_range=[0, x_limit], color=WHITE)

        bias_curve = always_redraw(get_bias_curve)
        var_curve = always_redraw(get_var_curve)
        total_curve = always_redraw(get_total_curve)
        noise_line = DashedLine(ax_bot.c2p(0, 0.5), ax_bot.c2p(10, 0.5), color=C_NOISE)

        # Labels for curves (static positions at end)
        lbl_bias = MathTex(r"\text{Bias}^2", color=C_BIAS, font_size=20).move_to(ax_bot.c2p(1, 3))
        lbl_var = Text("Variance", color=C_VAR, font_size=20).move_to(ax_bot.c2p(8, 7))
        lbl_total = Text("Total Error", color=WHITE, font_size=20).move_to(ax_bot.c2p(5, 7))

        self.add(noise_line, bias_curve, var_curve, total_curve)
        self.play(FadeIn(lbl_bias), FadeIn(lbl_var), FadeIn(lbl_total))

        # ANIMATION LOOP
        # Move complexity from 1 to 11
        # Calculate optimal point for "green line" later.
        # f(x) = 4e^-0.5x + 0.1x^2 + 0.5. Min is roughly x=3.5.
        # Tracker value will be x+1 approx 4.5.
        
        self.play(complexity_tracker.animate.set_value(11), run_time=10, rate_func=linear)

        # Conclusion: The Sweet Spot
        # Optimal x approx 3.5 -> tracker 4.5
        opt_x = 3.5
        opt_tracker_val = 4.5
        
        self.play(complexity_tracker.animate.set_value(opt_tracker_val), run_time=1)
        
        # Draw vertical line
        opt_line = DashedLine(
            start=ax_bot.c2p(opt_x, 0),
            end=ax_bot.c2p(opt_x, 10),
            color=C_EXP
        )
        opt_text = Text("Optimal Complexity", color=C_EXP, font_size=24).next_to(opt_line, UP)

        self.play(Create(opt_line), Write(opt_text))

        # Final Zoom effect
        self.play(
            FadeOut(ax_top), FadeOut(top_dots), FadeOut(poly_anim),
            ax_bot.animate.scale(1.5).move_to(ORIGIN),
            Group(bias_curve, var_curve, total_curve, noise_line, opt_line, lbl_bias, lbl_var, lbl_total).animate.scale(1.5).move_to(ORIGIN).shift(RIGHT*0.5 + UP*0.5) # Approximate adjustment
        )
        
        final_title = Text("The Bias-Variance Tradeoff", font_size=48).to_edge(UP)
        self.play(Write(final_title))

        self.wait(3)