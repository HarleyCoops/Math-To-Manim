from manim import *
import random
import numpy as np

# Global Style Constants
BACKGROUND_COLOR = "#1E1E1E" # DARK_SLATE_GREY
MAJORITY_COLOR = "#008080"   # TEAL
MINORITY_COLOR = "#FF00FF"   # MAGENTA
SYNTHETIC_COLOR = "#39FF14"  # NEON_GREEN
TEXT_COLOR = WHITE
ACCENT_BLUE = "#58C4DD"
ACCENT_RED = "#FF5252"
ACCENT_ORANGE = "#FFA500"

class ClassImbalanceSaga(ThreeDScene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # --- SCENE 1: Foundations – The Feature Space ---
        self.scene_01_vectors()
        
        # --- SCENE 2: Similarity – Euclidean Distance ---
        self.scene_02_distance()
        
        # --- SCENE 3: The Mechanism – Linear Interpolation ---
        self.scene_03_interpolation()
        
        # --- SCENE 4: Distribution Context ---
        self.scene_04_distributions()
        
        # --- SCENE 5: The Goal – Supervised Learning ---
        self.scene_05_supervised_learning()
        
        # --- SCENE 6: Classification Boundaries ---
        self.scene_06_boundaries()
        
        # --- SCENE 7: Local Logic – k-Nearest Neighbors ---
        self.scene_07_knn()
        
        # --- SCENE 8 & 9: The Trap – Accuracy Paradox ---
        self.scene_08_09_accuracy_paradox()
        
        # --- SCENE 10: Better Metrics ---
        self.scene_10_metrics()
        
        # --- SCENE 11: The Problem Visualized ---
        self.scene_11_problem_visualized()
        
        # --- SCENE 12: Naive Solutions ---
        self.scene_12_naive_solutions()
        
        # --- SCENE 13: The Elegant Solution – SMOTE ---
        self.scene_13_smote()

    def scene_01_vectors(self):
        # Setup Axes
        axes = ThreeDAxes(
            x_range=[-1, 5], y_range=[-1, 5], z_range=[-1, 5],
            x_length=7, y_length=7, z_length=7
        )
        
        # Initial Camera State (2D)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        
        # Create Axes
        self.play(Create(axes))
        
        # Rotate to 3D
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=2)
        
        # Vector and Point
        coords = [3, 2, 4]
        vector = Arrow3D(
            start=axes.c2p(0, 0, 0), 
            end=axes.c2p(*coords), 
            color=ACCENT_BLUE
        )
        dot = Dot3D(point=axes.c2p(*coords), color=ACCENT_BLUE, radius=0.1)
        dot.set_glow_factor(0.5)
        
        label = MathTex(r"\mathbf{x} = [x_1, x_2, x_3]^T").next_to(dot, RIGHT)
        self.add_fixed_orientation_mobjects(label) # Keep label facing camera
        
        self.play(Create(vector), FadeIn(dot))
        self.play(Write(label))
        
        # Basis Vectors
        e1 = Arrow3D(axes.c2p(0,0,0), axes.c2p(1,0,0), color=YELLOW)
        e2 = Arrow3D(axes.c2p(0,0,0), axes.c2p(0,1,0), color=YELLOW)
        e3 = Arrow3D(axes.c2p(0,0,0), axes.c2p(0,0,1), color=YELLOW)
        
        self.play(Create(e1), Create(e2), Create(e3), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(e1, e2, e3))
        
        self.wait(1)
        
        # Cleanup for transition
        self.play(FadeOut(vector), FadeOut(dot), FadeOut(label), FadeOut(axes))
        
    def scene_02_distance(self):
        # Reset Camera to 2D
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1)
        
        # Setup Plane
        plane = NumberPlane(
            x_range=[-1, 6], y_range=[-1, 6], 
            background_line_style={"stroke_opacity": 0.3}
        )
        
        p1_coord = plane.c2p(1, 1)
        p2_coord = plane.c2p(4, 5)
        
        dot1 = Dot(p1_coord, color=WHITE)
        dot2 = Dot(p2_coord, color=WHITE)
        label_A = MathTex("A").next_to(dot1, DOWN)
        label_B = MathTex("B").next_to(dot2, UP)
        
        self.play(Create(plane), FadeIn(dot1, dot2, label_A, label_B))
        
        # Distance line
        line = DashedLine(p1_coord, p2_coord, color=ACCENT_RED)
        label_d = MathTex(r"d(\mathbf{a}, \mathbf{b})", color=ACCENT_RED).next_to(line, LEFT)
        
        self.play(Create(line), Write(label_d))
        
        # Triangle components
        corner = plane.c2p(4, 1)
        leg_h = DashedLine(p1_coord, corner, color=GRAY)
        leg_v = DashedLine(corner, p2_coord, color=GRAY)
        
        self.play(Create(leg_h), Create(leg_v))
        
        # Formula
        formula = MathTex(r"d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}").to_edge(UP)
        self.play(Write(formula))
        
        # Highlight transformation
        term_x = MathTex("x_2 - x_1").scale(0.7).next_to(leg_h, DOWN)
        term_y = MathTex("y_2 - y_1").scale(0.7).next_to(leg_v, RIGHT)
        
        self.play(TransformFromCopy(formula[0][4:11], term_x))
        self.play(TransformFromCopy(formula[0][13:20], term_y))
        
        self.play(line.animate.set_stroke(width=6), run_time=0.5)
        self.wait(1)
        
        # Cleanup
        self.play(FadeOut(Group(plane, dot1, dot2, label_A, label_B, line, label_d, leg_h, leg_v, formula, term_x, term_y)))

    def scene_03_interpolation(self):
        # Local coordinate system
        a_pos = LEFT * 3 + DOWN * 1
        b_pos = RIGHT * 3 + UP * 2
        
        dot_a = Dot(a_pos, color=WHITE)
        dot_b = Dot(b_pos, color=WHITE)
        label_a = MathTex(r"\mathbf{a}").next_to(dot_a, DOWN)
        label_b = MathTex(r"\mathbf{b}").next_to(dot_b, UP)
        
        line = Line(a_pos, b_pos, color=WHITE)
        
        self.play(FadeIn(dot_a, dot_b, label_a, label_b), Create(line))
        
        formula = MathTex(r"\mathbf{p} = \mathbf{a} + \delta \cdot (\mathbf{b} - \mathbf{a})").to_edge(UP)
        self.play(Write(formula))
        
        # Bead and Tracker
        delta = ValueTracker(0.0)
        bead = Dot(color=ACCENT_ORANGE, radius=0.15)
        
        bead.add_updater(lambda m: m.move_to(
            dot_a.get_center() + delta.get_value() * (dot_b.get_center() - dot_a.get_center())
        ))
        
        delta_label = DecimalNumber(0, num_decimal_places=2).next_to(formula, DOWN)
        delta_label.add_updater(lambda m: m.set_value(delta.get_value()))
        delta_text = Tex(r"$\delta = $").next_to(delta_label, LEFT)
        
        self.add(bead, delta_text, delta_label)
        
        # Animate
        self.play(delta.animate.set_value(1), run_time=4, rate_func=linear)
        self.wait(1)
        
        self.clear() # Clear screen

    def scene_04_distributions(self):
        # Split screen setup
        ax_top = Axes(x_range=[-4, 4], y_range=[0, 0.5], x_length=6, y_length=2.5).shift(UP*2)
        ax_bot = Axes(x_range=[0, 10], y_range=[0, 0.5], x_length=6, y_length=2.5).shift(DOWN*2)
        
        # Normal Distribution
        curve_norm = ax_top.plot(lambda x: np.exp(-x**2/2) / np.sqrt(2*np.pi), color=ACCENT_BLUE)
        scan_line = Line(ax_top.c2p(-3, 0), ax_top.c2p(-3, 0.4), color=WHITE)
        
        self.play(Create(ax_top), Create(curve_norm))
        self.play(MoveAlongPath(scan_line, curve_norm), run_time=2)
        self.play(FadeOut(scan_line))
        
        # Skewed Distribution
        # Using a Log-Normal like shape or Chi-Square approximation for skew
        curve_skew = ax_bot.plot(lambda x: (x * np.exp(-x/1.5))/2 if x > 0 else 0, color=ACCENT_RED)
        self.play(Create(ax_bot), Create(curve_skew))
        
        # Transform to Histogram
        rects = VGroup()
        for x in range(1, 9):
            height = (x * np.exp(-x/1.5))/2
            rect = Rectangle(width=0.6, height=height*5, color=ACCENT_RED, fill_opacity=0.5) # Scale height for vis
            rect.move_to(ax_bot.c2p(x, 0), aligned_edge=DOWN)
            rects.add(rect)
            
        self.play(ReplacementTransform(curve_skew, rects))
        
        maj_text = Text("Majority", font_size=20).next_to(rects[1], UP)
        min_text = Text("Minority", font_size=20).next_to(rects[6], UP)
        
        self.play(Write(maj_text), Write(min_text))
        self.wait(1)
        self.clear()

    def scene_05_supervised_learning(self):
        # 3D Setup again
        self.set_camera_orientation(phi=60 * DEGREES, theta=-30 * DEGREES)
        axes = ThreeDAxes(x_range=[-3,3], y_range=[-3,3], z_range=[-3,3], x_length=6, y_length=6, z_length=4)
        
        # Generate random points near a plane z = x + 0.5y
        points = VGroup()
        residuals = VGroup()
        
        for _ in range(20):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(-2, 2)
            z_true = 0.5 * x + 0.3 * y
            z_noise = z_true + np.random.normal(0, 0.5)
            p = Dot3D(point=axes.c2p(x, y, z_noise), color=WHITE, radius=0.08)
            points.add(p)
            
        # The fitting plane
        plane = Surface(
            lambda u, v: axes.c2p(u, v, 0.5*u + 0.3*v), # Perfect fit
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(4, 4),
            fill_color="#83C167",
            fill_opacity=0.3,
            checkerboard_colors=False
        )
        
        # Start plane at wrong angle
        plane.rotate(20*DEGREES, axis=RIGHT)
        
        self.play(Create(axes))
        self.play(FadeIn(points))
        self.play(Create(plane))
        
        # Draw residuals
        def get_residuals():
            res_group = VGroup()
            for p in points:
                # Project point to plane (approximate visual vertical distance)
                # Since plane is z ~ x,y, we just drop a line z axis
                # Visual approximation for animation
                start = p.get_center()
                # Find z on plane at this x,y
                # This is tricky with a rotated Mobject plane. 
                # Simpler approach: Connect point to plane center? No.
                # Just draw lines down a bit to represent error
                end = start + DOWN * 0.5 # Dummy residual
                line = Line3D(start, end, color=ACCENT_RED)
                res_group.add(line)
            return res_group

        # Animate Fit
        # Simply rotating the plane back to the "correct" orientation defined in Surface lambda
        self.play(Rotate(plane, -20*DEGREES, axis=RIGHT), run_time=2)
        
        self.wait(1)
        self.move_camera(phi=0, theta=-90, run_time=1)
        self.clear()
        self.set_camera_orientation(phi=0, theta=-90) # Force 2D

    def scene_06_boundaries(self):
        # Clusters
        c0 = VGroup(*[Dot(np.array([-2, 1, 0]) + np.random.normal(0, 0.5, 3), color=MAJORITY_COLOR) for _ in range(20)])
        c1 = VGroup(*[Dot(np.array([2, -1, 0]) + np.random.normal(0, 0.5, 3), color=MINORITY_COLOR) for _ in range(20)])
        
        self.play(FadeIn(c0), FadeIn(c1))
        
        # Boundary Line
        boundary = Line(start=UP*3 + LEFT*1, end=DOWN*3 + RIGHT*1, color=WHITE, stroke_width=4)
        self.play(Create(boundary))
        
        # Region Coloring
        # Visual trick: Large rectangles with low opacity underneath
        # We need the boundary to define the cut. 
        # Line equation roughly: y = -1.5x + 0.5 => 1.5x + y - 0.5 = 0
        
        poly_maj = Polygon(
            UP*4 + LEFT*5, UP*4 + RIGHT*5, DOWN*4 + LEFT*5, 
            color=MAJORITY_COLOR, fill_opacity=0.2, stroke_opacity=0
        )
        # Simplified visual regions
        region_0 = Polygon(
            [-7, 4, 0], [1, 4, 0], [2, -4, 0], [-7, -4, 0],
            color=MAJORITY_COLOR, fill_color=MAJORITY_COLOR, fill_opacity=0.2, stroke_width=0
        )
        region_1 = Polygon(
            [1, 4, 0], [7, 4, 0], [7, -4, 0], [2, -4, 0],
            color=MINORITY_COLOR, fill_color=MINORITY_COLOR, fill_opacity=0.2, stroke_width=0
        )

        self.play(FadeIn(region_0), FadeIn(region_1))
        
        l0 = Text("Class 0").move_to([-3, 2, 0])
        # Highlight Bottom Row (Actual Positives - assuming standard matrix layout: Rows=Actual, Cols=Pred?
        # Standard: Rows=Actual, Cols=Predicted.
        # Row 1 (Top): Actual Neg. Row 2 (Bottom): Actual Pos.
        # Bottom Left: FN, Bottom Right: TP.
        
        recall_rect = SurroundingRectangle(VGroup(self.matrix_group[2][2], self.matrix_group[2][3]), color=YELLOW)
        recall_tex = MathTex(r"\text{Recall} = \frac{TP}{TP + FN} = \frac{0}{0+1} = 0").to_edge(RIGHT)
        
        self.play(Create(recall_rect))
        self.play(Write(recall_tex))
        self.wait(1)
        self.play(FadeOut(recall_rect), FadeOut(recall_tex))
        
        # Precision Formula (TP / (TP + FP))
        # Col 2 (Right): Predicted Positives.
        precision_rect = SurroundingRectangle(VGroup(self.matrix_group[2][1], self.matrix_group[2][3]), color=BLUE)
        prec_tex = MathTex(r"\text{Precision} = \frac{TP}{TP + FP}").to_edge(RIGHT)
        
        self.play(Create(precision_rect))
        self.play(Write(prec_tex))
        self.wait(1)
        self.play(FadeOut(precision_rect), FadeOut(prec_tex))
        
        # F1 Score
        f1_tex = MathTex(r"F_1 = 2 \cdot \frac{P \cdot R}{P + R}").scale(1.5).move_to(ORIGIN)
        self.play(FadeOut(self.matrix_group))
        self.play(Write(f1_tex))
        self.wait(1)
        self.clear()

    def scene_11_problem_visualized(self):
        # 2D Blob setup
        teal_blob = VGroup(*[Dot(np.random.normal([-2, 0, 0], 1, 3), color=MAJORITY_COLOR) for _ in range(50)])
        magenta_blob = VGroup(*[Dot(np.random.normal([3, 0, 0], 1, 3), color=MINORITY_COLOR) for _ in range(5)])
        
        self.play(FadeIn(teal_blob), FadeIn(magenta_blob))
        
        # Boundary Line
        boundary = Line(UP*3, DOWN*3, color=WHITE)
        self.play(Create(boundary))
        
        # Physics Push
        arrows = VGroup(*[Arrow(start=[-2, y, 0], end=[0, y, 0], color=MAJORITY_COLOR) for y in range(-2, 3)])
        self.play(FadeIn(arrows))
        
        # Push boundary right
        self.play(
            boundary.animate.shift(RIGHT * 2.5),
            rate_func=linear, run_time=2
        )
        
        # Override Magenta
        self.play(magenta_blob.animate.set_color(RED))
        
        bias_text = Text("Bias towards Majority", color=RED).to_edge(UP)
        self.play(Write(bias_text))
        self.wait(1)
        self.clear()

    def scene_12_naive_solutions(self):
        # Split Screen
        line = Line(UP*4, DOWN*4)
        to_remove = l_points[:24]
        self.play(FadeOut(to_remove))
        
        warn_l = Text("Loss of Info", color=RED, font_size=24).next_to(l_points[24:], DOWN)
        self.play(Write(warn_l))
        
        # Action Right: Duplicate
        copies = r_points.copy()
        self.play(copies.animate.shift(RIGHT*0.1 + UP*0.1).set_color(WHITE)) # Flash white then settle
        self.play(copies.animate.set_color(MINORITY_COLOR))
        
        warn_r = Text("Overfitting Risk", color=RED, font_size=24).next_to(r_points, DOWN)
        self.play(Write(warn_r))
        
        self.wait(1)
        self.clear()

    def scene_13_smote(self):
        # Setup specific cluster for logic viz
        pts_coords = [
            [-2, -1, 0], [-1, 2, 0], [0, -2, 0], [1, 1, 0], [2, -1, 0]
        ]
        title = Text("SMOTE", font_size=60, color=SYNTHETIC_COLOR).to_edge(UP)
        subtitle = Text("Synthetic Minority Over-sampling Technique", font_size=24).next_to(title, DOWN)
        
        self.play(Write(title), Write(subtitle))
        self.wait(2)