from manim import *
import numpy as np

# --- Global Color Constants ---
COLOR_TRAIN = "#00C9A7"
COLOR_TEST = "#FF9F1C"
COLOR_MODEL = "#FFFFFF"
COLOR_ERROR = "#FF4B4B"
COLOR_TEXT = "#F0F0F0"
COLOR_ACCENT = "#FFE162"

class CrossValidationStory(Scene):
    def construct(self):
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # --- Helpers ---
        self.axes_config = {
            "x_range": [-4, 4, 1],
            "y_range": [0, 1, 0.2],
            "axis_config": {"include_tip": False, "color": GREY},
        }

        # --- Execution Sequence ---
        self.scene_1_stochastic_cloud()
        self.scene_2_cloning_machine()
        self.scene_3_data_bar()
        self.scene_4_fitting_signal()
        self.scene_5_bias_variance()
        self.scene_6_train_test_split()
        self.scene_7_class_imbalance()
        self.scene_8_temporal_leakage()
        self.scene_9_k_fold()
        self.scene_10_stratified()
        self.scene_11_time_series()
        self.outro_summary()

    def scene_1_stochastic_cloud(self):
        # Voiceover: "Machine Learning begins with an assumption..."
        
        # 1. Setup Dots
        n_dots = 300
        mu, sigma = 0, 1.5 # Adjusted sigma for visual spread on screen
        
        # Target x positions based on normal distribution
        target_xs = np.random.normal(mu, sigma, n_dots)
        # Clamp to screen width just in case
        target_xs = np.clip(target_xs, -6.5, 6.5)
        
        dots = VGroup()
        for x in target_xs:
            d = Dot(point=np.array([np.random.uniform(-6, 6), 4, 0]), radius=0.05, color=COLOR_TRAIN)
            # Store target destination in a custom attribute
            d.target_pos = np.array([x, -2.5 + np.random.normal(0, 0.1), 0]) 
            dots.add(d)

        # 2. Animation (The Drop)
        self.play(
            LaggedStart(
                *[d.animate(run_time=2).move_to(d.target_pos) for d in dots],
                lag_ratio=0.005
            )
        )
        self.wait(0.5)

        # 3. The Overlay (Gaussian Bell Curve)
        # Using axes for proper curve plotting, but hiding them or making them subtle
        axes = Axes(
            x_range=[-6, 6, 1], 
            y_range=[0, 0.5, 0.1],
            x_length=12, y_length=4,
            axis_config={"include_numbers": False, "stroke_opacity": 0}
        ).move_to(DOWN * 0.5)

        def pdf(x):
            return (1/(sigma * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((x-mu)/sigma)**2)

        bell_curve = axes.plot(pdf, color=COLOR_MODEL)
        
        # Dashed Line for Mean
        mean_line = DashedLine(
            start=axes.c2p(mu, 0), 
            end=axes.c2p(mu, pdf(mu)), 
            color=COLOR_ACCENT
        )
        mean_label = MathTex(r"\mu", color=COLOR_ACCENT).next_to(mean_line, UP)

        # Shaded Region (Sigma)
        area = axes.get_area(bell_curve, x_range=[mu-sigma, mu+sigma], color=COLOR_MODEL, opacity=0.2)
        sigma_label = MathTex(r"\sigma", color=COLOR_MODEL).move_to(area.get_center())

        self.play(Create(bell_curve))
        self.play(FadeIn(mean_line), Write(mean_label))
        self.play(FadeIn(area), FadeIn(sigma_label))

        # Title
        title = Text("The Underlying Distribution", font_size=36, color=COLOR_TEXT).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Cleanup for next scene (keep bell curve, remove specific annotations)
        self.remove(mean_line, mean_label, area, sigma_label, title)
        self.dots_pile = dots # Save for reuse/transform
        self.bell_curve = bell_curve
        self.dist_axes = axes

    def scene_2_cloning_machine(self):
        # Voiceover: "We assume data points are I.I.D..."
        
        # 1. Transition
        self.play(FadeOut(self.dots_pile))
        
        # Move curve up
        group = VGroup(self.bell_curve, self.dist_axes)
        self.play(group.animate.move_to(UP * 2))
        self.bell_curve.set_color(GRAY)

        # 2. The Machine
        # Stamping action
        new_dots = VGroup()
        for i in range(10):
            d = Dot(color=COLOR_TRAIN).move_to(self.dist_axes.c2p(0, 0.4)) # Start at peak
            # Target position in a lineup at bottom
            target_pos = LEFT * 4 + RIGHT * i * 0.9 + DOWN * 2
            
            # Flash effect
            flash_curve = self.bell_curve.copy().set_stroke(width=8, opacity=0.5).set_color(COLOR_ACCENT)
            
            self.play(
                FadeIn(d, run_time=0.1),
                Flash(d, color=COLOR_MODEL, line_length=0.2),
                Create(flash_curve, run_time=0.3)
            )
            self.play(d.animate.move_to(target_pos), FadeOut(flash_curve), run_time=0.3)
            new_dots.add(d)
        
        # 3. Math Definition
        iid_text = Text("I.I.D.", weight=BOLD, font_size=48).next_to(self.bell_curve, DOWN)
        formula = MathTex(r"P(X_1, ..., X_n) = \prod_{i=1}^n P(X_i)", color=COLOR_TEXT).next_to(iid_text, DOWN)

        self.play(Write(iid_text))
        self.play(Write(formula))
        self.wait(1)

        # Cleanup
        self.play(FadeOut(group), FadeOut(iid_text), FadeOut(formula))
        self.current_dots = new_dots # Pass to next scene

    def scene_3_data_bar(self):
        # Voiceover: "In practice, we view our finite dataset as a set..."
        
        # 1. Transformation to Bar
        data_bar = Rectangle(width=10, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN)
        data_bar.move_to(ORIGIN)
        
        label_S = MathTex(r"S", font_size=50).next_to(data_bar, UP)

        self.play(
            ReplacementTransform(self.current_dots, data_bar),
            Write(label_S)
        )
        
        # 2. Partition
        # Visual trick: Replace one rect with 3 smaller rects
        s1 = Rectangle(width=3, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN).move_to(LEFT * 3.5)
        s2 = Rectangle(width=4, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN).move_to(ORIGIN)
        s3 = Rectangle(width=3, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN).move_to(RIGHT * 3.5)
        
        group_split = VGroup(s1, s2, s3)
        
        self.remove(data_bar)
        self.add(group_split)
        
        # Animate separation
        self.play(
            s1.animate.shift(LEFT * 0.2),
            s3.animate.shift(RIGHT * 0.2),
            run_time=1
        )

        brace1 = Brace(s1, DOWN).add(MathTex("S_1").next_to(Brace(s1, DOWN), DOWN))
        brace2 = Brace(s2, DOWN).add(MathTex("S_2").next_to(Brace(s2, DOWN), DOWN))
        brace3 = Brace(s3, DOWN).add(MathTex("S_3").next_to(Brace(s3, DOWN), DOWN))
        
        disjoint_eq = MathTex(r"S_i \cap S_j = \emptyset", font_size=36).to_edge(UP)

        self.play(Create(brace1), Create(brace2), Create(brace3))
        self.play(Write(disjoint_eq))
        self.wait(1)

        # Cleanup
        self.play(
            FadeOut(group_split), FadeOut(brace1), FadeOut(brace2), FadeOut(brace3), 
            FadeOut(label_S), FadeOut(disjoint_eq)
        )

    def scene_4_fitting_signal(self):
        # Voiceover: "Our goal is to learn a function that maps inputs to outputs..."
        
        # 1. Setup Axes and Points
        axes = Axes(
            x_range=[0, 10, 1], y_range=[0, 10, 1],
            x_length=8, y_length=5,
            axis_config={"color": GREY}
        ).move_to(DOWN * 0.5)
        
        # Generate linear data + noise
        x_vals = np.linspace(1, 9, 20)
        true_slope, true_intercept = 0.8, 1
        y_vals = true_slope * x_vals + true_intercept + np.random.normal(0, 0.8, 20)
        
        points = VGroup(*[Dot(axes.c2p(x, y), color=COLOR_TRAIN) for x, y in zip(x_vals, y_vals)])
        
        labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        self.play(Create(axes), Create(labels), FadeIn(points))

        # 2. Regression Animation
        line = axes.plot(lambda x: 0 * x + 5, color=COLOR_MODEL) # Start horizontal
        self.play(Create(line))
        
        # Transform to fit
        fitted_line = axes.plot(lambda x: true_slope * x + true_intercept, color=COLOR_MODEL)
        
        # 3. Residuals & Loss
        loss_text = VGroup(Text("Loss (MSE): ", font_size=24), DecimalNumber(50.0, num_decimal_places=1, font_size=24))
        loss_text.arrange(RIGHT).to_corner(DR)
        
        formula = MathTex(r"\mathcal{L} = \frac{1}{n} \sum (y_i - \hat{y}_i)^2", font_size=30).next_to(loss_text, UP)

        self.play(FadeIn(loss_text), Write(formula))
        
        # Visualize residuals dynamic update (simplified for code gen: show start and end state)
        # Draw initial residuals
        residuals = VGroup()
        for x, y in zip(x_vals, y_vals):
            # Distance to flat line y=5
            p_data = axes.c2p(x, y)
            p_pred = axes.c2p(x, 5)
            residuals.add(Line(p_data, p_pred, color=COLOR_ERROR, stroke_width=2))
        
        self.add(residuals)
        
        # Update residuals to fitted line
        new_residuals = VGroup()
        for x, y in zip(x_vals, y_vals):
            pred_y = true_slope * x + true_intercept
            p_data = axes.c2p(x, y)
            p_pred = axes.c2p(x, pred_y)
            new_residuals.add(Line(p_data, p_pred, color=COLOR_ERROR, stroke_width=2))

        self.play(
            Transform(line, fitted_line),
            Transform(residuals, new_residuals),
            ChangeDecimalToValue(loss_text[1], 2.4),
            run_time=2
        )
        self.wait(1)
        
        # Store for next scene
        self.reg_axes = axes
        self.reg_points = points
        self.reg_x = x_vals
        self.reg_y = y_vals
        self.reg_line = line
        self.reg_residuals = residuals
        self.reg_labels = labels
        self.loss_group = VGroup(loss_text, formula)

    def scene_5_bias_variance(self):
        # Voiceover: "But a model can cheat..."
        
        # Clear previous lines/residuals, keep dots/axes
        self.play(FadeOut(self.reg_line), FadeOut(self.reg_residuals), FadeOut(self.loss_group))
        
        # 1. Underfit
        underfit_line = self.reg_axes.plot(lambda x: 5, color=COLOR_MODEL)
        label_bias = Text("High Bias", color=COLOR_ERROR).to_edge(UP)
        self.play(Create(underfit_line), Write(label_bias))
        self.wait(0.5)
        self.play(FadeOut(underfit_line), FadeOut(label_bias))

        # 2. Overfit (Polynomial)
        # Fit high degree poly
        p_coeff = np.polyfit(self.reg_x, self.reg_y, deg=15)
        poly_func = np.poly1d(p_coeff)
        
        # Plot only within range to avoid asymptotes exploding
        overfit_curve = self.reg_axes.plot(poly_func, x_range=[1, 9], color=COLOR_MODEL)
        label_var = Text("High Variance", color=COLOR_ERROR).to_edge(UP)
        
        self.play(Create(overfit_curve), Write(label_var))
        
        # 3. The Twist: Test Data
        # Generate new test points
        test_x = np.linspace(1.5, 8.5, 10)
        test_y = 0.8 * test_x + 1 + np.random.normal(0, 0.8, 10)
        test_points = VGroup(*[Dot(self.reg_axes.c2p(x, y), color=COLOR_TEST) for x, y in zip(test_x, test_y)])
        
        self.play(FadeIn(test_points))
        
        # Show error on test points for overfit curve
        test_residuals = VGroup()
        for x, y in zip(test_x, test_y):
            pred = poly_func(x)
            # Clamp prediction for visual sanity if it explodes
            if 0 <= pred <= 10:
                p_data = self.reg_axes.c2p(x, y)
                p_pred = self.reg_axes.c2p(x, pred)
                test_residuals.add(Line(p_data, p_pred, color=COLOR_ERROR))
        
        self.play(Create(test_residuals))
        self.wait(1)
        
        # 4. Good Fit
        good_curve = self.reg_axes.plot(lambda x: 0.8*x + 1, color=COLOR_ACCENT)
        label_good = Text("Generalization", color=COLOR_ACCENT).to_edge(UP)
        
        self.play(
            ReplacementTransform(overfit_curve, good_curve),
            FadeOut(test_residuals),
            ReplacementTransform(label_var, label_good)
        )
        self.wait(1)
        
        # Cleanup
        self.play(FadeOut(Group(self.reg_axes, self.reg_points, test_points, good_curve, label_good, self.reg_labels)))

    def scene_6_train_test_split(self):
        # Voiceover: "The simplest evaluation strategy is the Train-Test split..."
        
        # 1. Solid Data Bar
        bar_width = 10
        full_bar = Rectangle(width=bar_width, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN)
        self.play(FadeIn(full_bar))
        
        # 2. The Blade
        blade = Line(UP*2, DOWN*2, color=WHITE, stroke_width=5).move_to(RIGHT * 3) # 80% mark (approx) from left=-5
        self.play(Create(blade), run_time=0.2)
        self.play(Wiggle(blade))
        
        # Split
        train_rect = Rectangle(width=8, height=1, color=COLOR_TRAIN, fill_opacity=1, fill_color=COLOR_TRAIN).move_to(LEFT * 1)
        test_rect = Rectangle(width=2, height=1, color=COLOR_TEST, fill_opacity=1, fill_color=COLOR_TEST).move_to(RIGHT * 4)
        
        self.remove(full_bar)
        self.add(train_rect, test_rect)
        self.play(FadeOut(blade))
        
        # Slide apart
        self.play(test_rect.animate.shift(RIGHT * 0.5))
        
        # Labels
        lbl_train = Text("Training Set", font_size=24).next_to(train_rect, DOWN)
        lbl_test = Text("Hold-out Set", font_size=24, color=COLOR_TEST).next_to(test_rect, DOWN)
        
        self.play(Write(lbl_train), Write(lbl_test))
        
        # Process Flow
        model_box = RoundedRectangle(corner_radius=0.2, height=1, width=2, color=COLOR_MODEL).shift(UP * 2)
        model_txt = Text("Model", font_size=24).move_to(model_box)
        score_txt = Text("Score", font_size=24).next_to(test_rect, UP * 3)
        
        arrow1 = Arrow(train_rect.get_top(), model_box.get_bottom(), color=WHITE)
        arrow2 = Arrow(model_box.get_right(), test_rect.get_top() + UP*1.5, path_arc=-1.5, color=WHITE) # Curved arrowish
        # Simplified flow visually
        
        self.play(Create(model_box), Write(model_txt))
        self.play(GrowArrow(arrow1))
        self.play(Indicate(model_box))
        
        # Prediction
        arrow_pred = Arrow(model_box.get_bottom(), test_rect.get_top(), color=COLOR_TEST)
        self.play(GrowArrow(arrow_pred))
        self.play(Write(score_txt))
        self.wait(1)
        
        self.play(FadeOut(Group(train_rect, test_rect, lbl_train, lbl_test, model_box, model_txt, score_txt, arrow1, arrow_pred)))

    def scene_7_class_imbalance(self):
        # Voiceover: "But random splitting fails if rare events are missed..."
        
        # 1. Textured Bar
        bar = Rectangle(width=10, height=1.5, color=COLOR_TRAIN, fill_opacity=0.3, stroke_color=COLOR_TRAIN)
        
        # Add dots inside
        majority_dots = VGroup(*[Dot(point=np.array([np.random.uniform(-4.8, 4.8), np.random.uniform(-0.6, 0.6), 0]), color=COLOR_TRAIN, radius=0.08) for _ in range(50)])
        # Minority dots clustered at left
        minority_dots = VGroup(*[Dot(point=np.array([np.random.uniform(-4.5, -3.5), np.random.uniform(-0.6, 0.6), 0]), color=COLOR_ERROR, radius=0.1) for _ in range(8)])
        
        full_group = VGroup(bar, majority_dots, minority_dots).move_to(ORIGIN)
        self.play(FadeIn(full_group))
        
        # 2. Bad Split (Slice right side)
        test_zone = Rectangle(width=2, height=1.5, color=COLOR_TEST, fill_opacity=0.3).move_to(RIGHT * 4)
        
        self.play(Transform(bar, VGroup(
            Rectangle(width=8, height=1.5, color=COLOR_TRAIN, fill_opacity=0.3).move_to(LEFT*1),
            test_zone
        )))
        
        # Move test away
        test_contents = VGroup()
        # Find dots inside test zone (visually simplified logic: just animate copy)
        # Actually, in the setup above, no red dots are in the right side (Right * 4 vs Left * 4)
        
        self.play(test_zone.animate.shift(RIGHT * 1))
        
        # Zoom effect (Scale up)
        self.play(test_zone.animate.scale(2).move_to(ORIGIN), FadeOut(majority_dots), FadeOut(minority_dots), FadeOut(bar))
        
        label_bias = Text("Representation Bias", color=COLOR_ERROR).next_to(test_zone, UP)
        cross = Cross(test_zone)
        
        self.play(Write(label_bias))
        self.play(Create(cross))
        self.wait(1)
        
        self.play(FadeOut(Group(test_zone, label_bias, cross)))

    def scene_8_temporal_leakage(self):
        # Voiceover: "And for time-series data..."
        
        # 1. Timeline Ribbon
        ribbon = Rectangle(width=10, height=1).set_fill(color=[BLUE, BLUE_A], opacity=1).set_stroke(width=0)
        arrow = Arrow(LEFT, RIGHT, color=WHITE).next_to(ribbon, DOWN)
        lbl_time = Text("Time").next_to(arrow, DOWN)
        
        self.play(DrawBorderThenFill(ribbon), GrowArrow(arrow), Write(lbl_time))
        
        # 2. Shuffle Paradox
        # Break into chunks
        chunks = VGroup(*[Rectangle(width=1, height=1).set_fill(opacity=1).set_stroke(color=BLACK, width=2) for _ in range(10)])
        # Color gradient manually
        for i, c in enumerate(chunks):
            c.set_color(interpolate_color(BLUE, BLUE_A, i/9))
            c.set_fill(opacity=1) # Re-apply fill after set_color
        
        chunks.arrange(RIGHT, buff=0).move_to(ORIGIN)
        self.remove(ribbon)
        self.add(chunks)
        
        # Shuffle into two piles
        train_pile = VGroup()
        test_pile = VGroup()
        
        # Manually pick for demonstration: Train gets future (light), Test gets past (dark)
        # Chunk 9 (Future) -> Train. Chunk 2 (Past) -> Test.
        future_chunk = chunks[9]
        past_chunk = chunks[2]
        
        # Shuffle animation
        self.play(
            future_chunk.animate.move_to(LEFT * 3 + UP),
            past_chunk.animate.move_to(RIGHT * 3 + UP),
            *[c.animate.move_to(np.random.uniform(LEFT*4, RIGHT*4) * 0.5 + DOWN) for c in chunks if c not in [future_chunk, past_chunk]],
            run_time=1.5
        )
        
        lbl_leak = Text("Data Leakage", color=COLOR_ERROR).to_edge(UP)
        
        leak_arrow = CurvedArrow(future_chunk.get_top(), past_chunk.get_top(), color=COLOR_ERROR)
        
        self.play(Write(lbl_leak))
        self.play(Create(leak_arrow))
        self.play(Indicate(leak_arrow, color=RED))
        self.wait(1)
        
        self.play(FadeOut(Group(chunks, arrow, lbl_time, lbl_leak, leak_arrow)))

    def create_segmented_bar(self, width, segments, active_segment_index):
        bar = VGroup()
        seg_width = width / segments
        for i in range(segments):
            color = COLOR_TEST if i == active_segment_index else COLOR_TRAIN
            rect = Rectangle(width=seg_width, height=1, color=WHITE, stroke_width=2)
            rect.set_fill(color, opacity=0.8)
            rect.shift(RIGHT * (i * seg_width - width/2 + seg_width/2))
            bar.add(rect)
        return bar

    def scene_9_k_fold(self):
        # Voiceover: "The gold standard is K-Fold Cross-Validation..."
        
        title = Text("K-Fold Cross-Validation (K=5)").to_edge(UP)
        self.play(Write(title))
        
        scores = []
        
        # K=5 Loop
        for k in range(5):
            bar = self.create_segmented_bar(10, 5, k)
            self.add(bar)
            
            acc_val = 0.85 + k * 0.01
            label = Text(f"Acc: {acc_val:.2f}", font_size=24).next_to(bar[k], UP)
            
            self.play(FadeIn(label, run_time=0.5))
            self.wait(0.2)
            
            # Store score text for later aggregation
            score_copy = label.copy()
            scores.append(score_copy)
            
            if k < 4:
                self.remove(bar, label)
            else:
                self.final_bar = bar # Keep last one
                self.final_label = label

        # Aggregation
        self.play(FadeOut(self.final_bar), FadeOut(self.final_label))
        
        score_group = VGroup(*scores).arrange(DOWN).move_to(ORIGIN)
        self.play(FadeIn(score_group))
        
        avg_text = Text("Average Accuracy: 0.87", color=COLOR_ACCENT, weight=BOLD).scale(1.2)
        
        self.play(Transform(score_group, avg_text))
        self.wait(1)
        self.play(FadeOut(score_group), FadeOut(title))

    def scene_10_stratified(self):
        # Voiceover: "To fix imbalance, we use Stratified K-Fold..."
        
        # 1. Polka Dot Bar (disorganized)
        bar_width = 10
        bar = Rectangle(width=bar_width, height=1.5, color=WHITE, stroke_width=2)
        
        # Random positions
        red_dots = VGroup(*[Dot(color=COLOR_ERROR, radius=0.1).move_to(
            np.array([np.random.uniform(-4.5, 4.5), np.random.uniform(-0.5, 0.5), 0])) for _ in range(10)])
        
        teal_dots = VGroup(*[Dot(color=COLOR_TRAIN, radius=0.08).move_to(
            np.array([np.random.uniform(-4.8, 4.8), np.random.uniform(-0.6, 0.6), 0])) for _ in range(50)])
        
        self.play(Create(bar), FadeIn(teal_dots), FadeIn(red_dots))
        
        # 2. Sorting
        # Animate red dots to be equidistant
        sorted_positions = np.linspace(-4, 4, 10)
        anims = []
        for d, x in zip(red_dots, sorted_positions):
            anims.append(d.animate.move_to(np.array([x, 0, 0])))
            
        self.play(*anims, run_time=1.5)
        
        # 3. The Fold
        # Overlay grid
        grid = self.create_segmented_bar(10, 5, 2) # Highlight middle fold
        grid.set_opacity(0.3)
        
        self.play(FadeIn(grid))
        
        # Zoom to middle fold
        fold = grid[2]
        self.play(fold.animate.set_color(COLOR_TEST).set_opacity(0.5))
        
        # Highlight preserved ratio (2 red dots in the fold)
        label = Text("Preserved Ratio", color=COLOR_ACCENT).next_to(fold, DOWN)
        self.play(Write(label))
        self.wait(1)
        
        self.play(FadeOut(Group(bar, red_dots, teal_dots, grid, label)))

    def scene_11_time_series(self):
        # Voiceover: "For time series, we use a rolling origin..."
        
        # 1. Timeline
        timeline = NumberLine(x_range=[0, 100, 10], length=10, include_numbers=False)
        self.play(Create(timeline))
        
        # 2. Rolling Window Animation
        # Window 1
        train = Rectangle(width=2, height=0.5, color=COLOR_TRAIN, fill_opacity=0.8).align_to(timeline, LEFT).shift(UP*0.5)
        test = Rectangle(width=1, height=0.5, color=COLOR_TEST, fill_opacity=0.8).next_to(train, RIGHT, buff=0)
        
        self.play(FadeIn(train), FadeIn(test))
        self.wait(0.5)
        
        # Window 2 (Train Expands, Test Moves)
        train_2 = Rectangle(width=3, height=0.5, color=COLOR_TRAIN, fill_opacity=0.8).align_to(timeline, LEFT).shift(UP*0.5)
        test_2 = Rectangle(width=1, height=0.5, color=COLOR_TEST, fill_opacity=0.8).next_to(train_2, RIGHT, buff=0)
        
        self.play(Transform(train, train_2), Transform(test, test_2))
        self.wait(0.5)
        
        # Window 3
        train_3 = Rectangle(width=4, height=0.5, color=COLOR_TRAIN, fill_opacity=0.8).align_to(timeline, LEFT).shift(UP*0.5)
        test_3 = Rectangle(width=1, height=0.5, color=COLOR_TEST, fill_opacity=0.8).next_to(train_3, RIGHT, buff=0)
        
        self.play(Transform(train, train_3), Transform(test, test_3))
        self.wait(1)
        
        self.play(FadeOut(Group(timeline, train, test)))

    def outro_summary(self):
        # Voiceover: "By choosing the right validation strategy..."
        
        # Icons
        icon_kfold = Rectangle(width=2, height=2, color=COLOR_TRAIN)
        VGroup(*[Line(UP, DOWN).move_to(icon_kfold).shift(RIGHT*(i-0.5)*0.5) for i in range(2)]).set_color(WHITE).move_to(icon_kfold)
        lbl_kfold = Text("Standard", font_size=24).next_to(icon_kfold, DOWN)
        
        icon_strat = Circle(radius=1, color=COLOR_TRAIN)
        Dot(color=COLOR_ERROR).move_to(icon_strat)
        lbl_strat = Text("Imbalanced", font_size=24).next_to(icon_strat, DOWN)
        
        icon_time = Arrow(LEFT, RIGHT, color=COLOR_TRAIN).set_length(2)
        lbl_time = Text("Temporal", font_size=24).next_to(icon_time, DOWN)
        
        group = VGroup(
            VGroup(icon_kfold, lbl_kfold),
            VGroup(icon_strat, lbl_strat),
            VGroup(icon_time, lbl_time)
        ).arrange(RIGHT, buff=2)
        
        self.play(FadeIn(group))
        self.play(
            icon_kfold.animate.set_stroke(color=COLOR_ACCENT),
            icon_strat.animate.set_stroke(color=COLOR_ACCENT),
            icon_time.animate.set_color(COLOR_ACCENT)
        )
        
        self.wait(2)
        self.play(FadeOut(group, run_time=1))