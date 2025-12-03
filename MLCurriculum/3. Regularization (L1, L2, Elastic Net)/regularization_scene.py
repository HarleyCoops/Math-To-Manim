from manim import *
import numpy as np

class MathematicsOfML(ThreeDScene):
    def construct(self):
        # --- Global Configuration ---
        self.camera.background_color = "#1E1E1E"
        
        # Color Palette
        self.TEAL_C = "#00C9A7"
        self.RED_C = "#FF4B4B"
        self.YELLOW_C = "#FFD700"
        self.GREY_C = "#444444"
        self.ORANGE_C = "#FF9F00"
        
        # Subtitle tracking
        self.subtitle = Text("", font_size=24, font="Arial").to_edge(DOWN * 1.5)
        self.add_fixed_in_frame_mobjects(self.subtitle)

        # --- Animation Sequence ---
        self.show_linear_algebra()
        self.show_calculus()
        self.show_statistics()
        self.show_vector_norms()
        self.show_gradients()
        # self.show_constrained_optimization()
        self.show_loss_functions()
        self.show_bias_variance()
        self.show_optimization_algorithms()
        self.show_overfitting()
        self.show_regularization()

    def update_subtitle(self, text_str, wait_time=0):
        new_subtitle = Text(text_str, font_size=28, font="Arial", color=WHITE).to_edge(DOWN * 2)
        # Ensure subtitle is fixed on screen even during camera moves
        self.add_fixed_in_frame_mobjects(new_subtitle)
        
        if self.subtitle.text != "":
            self.play(Transform(self.subtitle, new_subtitle), run_time=0.5)
        else:
            self.subtitle = new_subtitle
            self.play(FadeIn(self.subtitle), run_time=0.5)
            
        if wait_time > 0:
            self.wait(wait_time)

    def clear_scene(self):
        # Helper to wipe everything but the subtitle
        mobjects = [m for m in self.mobjects if m is not self.subtitle]
        mobjects = [m for m in self.mobjects if m is not self.subtitle]
        self.remove(*mobjects)
        self.wait(0.1)

    # --- Part 1: Linear Algebra ---
    def show_linear_algebra(self):
        self.update_subtitle("Linear Algebra describes space transformations. A matrix stretches and skews the very fabric of the grid.")
        
        # Setup
        grid = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-5, 5, 1], 
            background_line_style={"stroke_color": self.GREY_C, "stroke_width": 2, "stroke_opacity": 0.5}
        )
        
        vec_start = Vector([1, 2, 0], color=self.YELLOW_C)
        vec_label = MathTex(r"\mathbf{x}", color=self.YELLOW_C).next_to(vec_start.get_end(), RIGHT)
        
        matrix_tex = MathTex(r"A = \begin{bmatrix} 2 & 1 \\ 0 & 1 \end{bmatrix}").to_corner(UL).set_opacity(0.7)
        
        self.play(Create(grid), GrowArrow(vec_start), Write(vec_label), Write(matrix_tex))
        self.wait(1)
        
        # Transform
        matrix = [[2, 1], [0, 1]]
        
        # We need to transform the grid and the vector
        # ApplyMatrix applies a linear transform to the mobject
        self.play(
            ApplyMatrix(matrix, grid),
            ApplyMatrix(matrix, vec_start),
            vec_label.animate.move_to([4, 2, 0] + RIGHT * 0.5), # Manual move for label approximation
            vec_start.animate.set_color(self.ORANGE_C),
            run_time=3
        )
        self.wait(1)
        self.clear_scene()

    # --- Part 2: Multivariable Calculus ---
    def show_calculus(self):
        self.update_subtitle("Calculus measures change. The tangent plane captures the slope of the hill at a single point.")
        
        # Switch to 3D
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=1.5)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 1])
        
        def func(u, v):
            return np.array([u, v, -((u**2 + v**2) / 4)])
        
        surface = Surface(
            func,
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(24, 24),
            fill_opacity=0.8
        ).set_fill_by_checkerboard(BLUE, GREEN, opacity=0.8)
        
        dot = Sphere(radius=0.1, color=self.RED_C).move_to(func(1.5, 1.5))
        
        # Tangent plane logic (simplified visual)
        tangent_plane = Surface(
            lambda u, v: np.array([u, v, 0]), # Placeholder, will update
            u_range=[-0.5, 0.5],
            v_range=[-0.5, 0.5],
            fill_opacity=0.5,
            color=WHITE
        )

        def update_plane(mob):
            x, y, z = dot.get_center()
            # Derivs: dz/dx = -x/2, dz/dy = -y/2
            dzdx = -x/2
            dzdy = -y/2
            # Normal vector approx [-dzdx, -dzdy, 1]
            normal = np.array([-dzdx, -dzdy, 1])
            normal = normal / np.linalg.norm(normal)
            
            mob.become(
                Square(side_length=1.5)
                .set_fill(WHITE, opacity=0.3)
                .set_stroke(width=0)
                .move_to(dot.get_center())
                .rotate(np.arctan(dzdx), axis=UP) # Approximation for rotation logic
                .rotate(np.arctan(dzdy), axis=RIGHT)
                # Ideally we use a rotation matrix based on normal, but lookat is easier
                # .look_at(dot.get_center() + normal)
            )

        tangent_plane.add_updater(update_plane)
        
        self.play(Create(axes), Create(surface))
        self.play(FadeIn(dot), FadeIn(tangent_plane))
        
        # Animate dot movement
        path_curve = ParametricFunction(
            lambda t: func(1.5 * np.cos(t), 1.5 * np.sin(t)),
            t_range=[0, PI],
            color=YELLOW
        )
        
        self.play(MoveAlongPath(dot, path_curve), run_time=4)
        self.wait(1)
        
        tangent_plane.remove_updater(update_plane)
        self.clear_scene()
        
        # Reset camera
        self.move_camera(phi=0, theta=-90*DEGREES, run_time=1)

    # --- Part 3: Basic Statistics ---
    def show_statistics(self):
        self.update_subtitle("Statistics summarizes data. The Mean finds the center; Variance measures the spread.")
        
        number_line = NumberLine(x_range=[-4, 4, 1], include_numbers=True).shift(DOWN)
        self.play(Create(number_line))
        
        dots = VGroup()
        np.random.seed(42)
        points = np.random.normal(0, 1, 20)
        
        for p in points:
            d = Dot(color=WHITE).move_to(number_line.n2p(p) + UP * 3)
            dots.add(d)
        
        # Lagged Start Drop
        self.play(
            LaggedStart(
                *[d.animate.move_to(number_line.n2p(p)) for d, p in zip(dots, points)],
                lag_ratio=0.1
            ),
            run_time=2
        )
        
        mean_line = Line(UP, DOWN, color=self.TEAL_C).move_to(number_line.n2p(0))
        mean_label = Tex("Mean", color=self.TEAL_C).next_to(mean_line, UP)
        
        variance_brace = Brace(Line(number_line.n2p(-1), number_line.n2p(1)), UP, buff=0.5)
        var_text = variance_brace.get_text("Variance").set_color(BLUE)
        
        self.play(Create(mean_line), Write(mean_label))
        self.play(GrowFromCenter(variance_brace), FadeIn(var_text))
        self.wait(2)
        self.clear_scene()

    # --- Part 4: Vector Norms ---
    def show_vector_norms(self):
        self.update_subtitle("Norms define 'size'. L2 is a circle, but L1 is a diamond. This shape difference is crucial.")
        
        axes = Axes(x_range=[-3, 3], y_range=[-3, 3])
        self.play(Create(axes))
        
        # L2 Norm (Circle)
        l2_shape = Circle(radius=2, color=BLUE)
        label = MathTex(r"\|\mathbf{x}\|_2 = 1").to_corner(UR)
        
        self.play(Create(l2_shape), Write(label))
        self.wait(1)
        
        # L1 Norm (Diamond)
        l1_shape = Square(side_length=2 * np.sqrt(2), color=self.RED_C).rotate(45 * DEGREES)
        l1_label = MathTex(r"\|\mathbf{x}\|_1 = 1").to_corner(UR)
        
        self.play(
            Transform(l2_shape, l1_shape),
            Transform(label, l1_label),
            run_time=2
        )
        self.wait(1)
        
        # L-inf Norm (Square)
        linf_shape = Square(side_length=4, color=GREEN)
        linf_label = MathTex(r"\|\mathbf{x}\|_\infty = 1").to_corner(UR)
        
        self.play(
            Transform(l2_shape, linf_shape),
            Transform(label, linf_label),
            run_time=2
        )
        self.wait(1)
        self.clear_scene()

    # --- Part 5: Gradients ---
    def show_gradients(self):
        self.update_subtitle("The Gradient points uphill. To minimize loss, we descend in the opposite direction.")
        
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
        
        # Paraboloid
        axes = ThreeDAxes(x_range=[-2, 2], y_range=[-2, 2], z_range=[0, 4])
        surface = Surface(
            lambda u, v: np.array([u, v, u**2 + v**2]),
            u_range=[-1.5, 1.5],
            v_range=[-1.5, 1.5],
            resolution=(20, 20),
            fill_opacity=0.3,
            checkerboard_colors=[BLUE_D, BLUE_E],
            stroke_color=WHITE,
            stroke_width=0.5
        )
        
        ball = Sphere(radius=0.1, color=self.RED_C).move_to(axes.c2p(1.5, 0, 1.5**2))
        arrow = Arrow3D(
            start=axes.c2p(1.5, 0, 1.5**2),
            end=axes.c2p(1.5 + 0.5, 0, 1.5**2 + 0.5), # Approx gradient direction
            color=self.YELLOW_C
        )
        
        self.play(Create(axes), Create(surface), FadeIn(ball))
        
        # Roll down logic
        path = ParametricFunction(
            lambda t: axes.c2p((1.5-t), 0, (1.5-t)**2),
            t_range=[0, 1.5],
            color=RED
        )
        
        self.play(FadeIn(arrow))
        self.wait(0.5)
        # Move ball and fade arrow out as it moves (gradient changes)
        self.play(MoveAlongPath(ball, path), FadeOut(arrow), run_time=3)
        self.wait(1)
        
        self.clear_scene()
        self.move_camera(phi=0, theta=-90*DEGREES)

    # --- Part 6: Constrained Optimization ---
    def show_constrained_optimization(self):
        self.update_subtitle("Constrained Optimization finds the best solution that touches the rule boundary.")
        
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3])
        
        # x + y = 2 -> y = -x + 2
        constraint_line = axes.plot(lambda x: 2 - x, color=self.RED_C)
        constraint_label = MathTex("x+y=2", color=self.RED_C).next_to(constraint_line, UP)
        
        center_dot = Dot(axes.c2p(0, 0), color=WHITE)
        
        self.play(Create(axes), Create(constraint_line), Write(constraint_label), Create(center_dot))
        
        # Expanding circles
        circles = VGroup()
        # Optimal radius is distance to line x+y=2 from (0,0) -> distance is |0+0-2|/sqrt(1+1) = sqrt(2) approx 1.414
        target_radius = np.sqrt(2)
        
        for r in np.linspace(0.1, target_radius, 5):
            c = Circle(radius=r * axes.x_length / 4, color=BLUE_B).move_to(axes.c2p(0,0)) # scale logic approx
            # Better way to size circle relative to axes:
            c = axes.get_graph(lambda x: np.sqrt(max(0, r**2 - x**2))).set_color(BLUE_B) # Upper half
            c2 = axes.get_graph(lambda x: -np.sqrt(max(0, r**2 - x**2))).set_color(BLUE_B) # Lower half
            circles.add(VGroup(c, c2))

        # Just animate one circle growing
        growing_circle = Circle(radius=0.1, color=self.TEAL_C).move_to(axes.c2p(0,0))
        
        def update_circle(mob, alpha):
            current_r = alpha * target_radius
            # Manim circle radius is in unit coordinates, need to scale by axis unit size
            unit_size = axes.x_axis.unit_size
            mob.become(Circle(radius=current_r * unit_size, color=self.TEAL_C).move_to(axes.c2p(0,0)))

        self.play(UpdateFromAlphaFunc(growing_circle, update_circle), run_time=3)
        
        # Tangent point
        tangent_point = Dot(axes.c2p(1, 1), color=WHITE).scale(1.5)
        flash = Flash(tangent_point, color=YELLOW, flash_radius=0.5)
        
        self.play(FadeIn(tangent_point), flash)
        self.wait(1)
        self.clear_scene()

    # --- Part 7: Loss Functions ---
    def show_loss_functions(self):
        self.update_subtitle("The Loss Function sums the squared errors. Our goal is to minimize this total area.")
        
        axes = Axes(x_range=[0, 6], y_range=[0, 6], axis_config={"include_tip": False})
        
        # Data points
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [1.2, 1.8, 3.5, 3.8, 5.2]
        dots = VGroup(*[Dot(axes.c2p(x, y), color=WHITE) for x, y in zip(x_vals, y_vals)])
        
        # Regression Line (approx)
        line = axes.plot(lambda x: 1.0 * x + 0.1, color=self.TEAL_C)
        
        self.play(Create(axes), Create(dots), Create(line))
        
        # Residuals
        residuals = VGroup()
        squares = VGroup()
        
        total_error = 0
        
        for x, y in zip(x_vals, y_vals):
            y_pred = 1.0 * x + 0.1
            diff = y - y_pred
            
            # Line segment
            p1 = axes.c2p(x, y)
            p2 = axes.c2p(x, y_pred)
            res_line = Line(p1, p2, color=self.RED_C)
            residuals.add(res_line)
            
            # Square visualization
            side = abs(p1[1] - p2[1]) # Screen units height
            sq = Square(side_length=side, color=self.RED_C, fill_opacity=0.5).move_to(res_line.get_center())
            squares.add(sq)
            
            total_error += diff**2

        self.play(Create(residuals))
        self.wait(0.5)
        self.play(Transform(residuals, squares))
        
        # Transform to bar
        bar = Rectangle(height=4, width=1, color=self.RED_C, fill_opacity=0.8).to_edge(RIGHT)
        label = Tex("Cost $J$").next_to(bar, UP)
        
        self.play(
            ReplacementTransform(squares, bar),
            Write(label),
            FadeOut(dots), FadeOut(line), FadeOut(axes)
        )
        self.wait(1)
        self.clear_scene()

    # --- Part 8: Bias-Variance ---
    def show_bias_variance(self):
        self.update_subtitle("Bias is being consistently wrong. Variance is being inconsistent. We seek the balance.")
        
        # Create 3 targets
        targets = VGroup()
        for i in range(3):
            t = VGroup()
            for r in [1.5, 1.0, 0.5]:
                t.add(Circle(radius=r, color=self.GREY_C, stroke_width=2))
            t.add(Dot(color=RED)) # Bullseye
            targets.add(t)
            
        targets.arrange(RIGHT, buff=1)
        
        # High Bias (Tight cluster, off center)
        shots1 = VGroup(*[Dot(radius=0.08, color=GREEN).move_to(targets[0].get_center() + np.array([0.8, 0.8, 0]) + np.random.normal(0, 0.1, 3)) for _ in range(5)])
        label1 = Text("High Bias", font_size=20).next_to(targets[0], UP)
        
        # High Variance (Scattered, centered)
        shots2 = VGroup(*[Dot(radius=0.08, color=GREEN).move_to(targets[1].get_center() + np.random.normal(0, 0.5, 3)) for _ in range(5)])
        label2 = Text("High Variance", font_size=20).next_to(targets[1], UP)
        
        # Good (Tight cluster, centered)
        shots3 = VGroup(*[Dot(radius=0.08, color=GREEN).move_to(targets[2].get_center() + np.random.normal(0, 0.15, 3)) for _ in range(5)])
        label3 = Text("Balanced", font_size=20).next_to(targets[2], UP)
        
        self.play(Create(targets))
        
        self.play(ShowIncreasingSubsets(shots1), Write(label1), run_time=1.5)
        self.play(ShowIncreasingSubsets(shots2), Write(label2), run_time=1.5)
        self.play(ShowIncreasingSubsets(shots3), Write(label3), run_time=1.5)
        
        self.wait(1)
        self.clear_scene()

    # --- Part 9: Optimization Algorithms ---
    def show_optimization_algorithms(self):
        self.update_subtitle("Gradient Descent takes steps perpendicular to contours, zig-zagging towards the minimum.")
        
        axes = Axes(x_range=[-3, 3], y_range=[-3, 3])
        
        # Contour lines (Ellipses)
        contours = VGroup()
        for i in range(1, 6):
            c = Ellipse(width=i*1.5, height=i*1.0, color=BLUE_B).move_to(ORIGIN)
            contours.add(c)
            
        self.play(FadeIn(contours))
        
        # Path logic (Zig Zag)
        points = [
            [2.5, 2.0, 0],
            [1.0, 1.8, 0],
            [1.2, 0.5, 0],
            [0.2, 0.4, 0],
            [0, 0, 0]
        ]
        
        path = VMobject().set_points_as_corners(points).set_color(self.YELLOW_C)
        dot = Dot(points[0], color=self.YELLOW_C)
        
        self.play(FadeIn(dot))
        self.play(Create(path), MoveAlongPath(dot, path), run_time=4)
        
        self.wait(1)
        self.clear_scene()

    # --- Part 10: Overfitting ---
    def show_overfitting(self):
        self.update_subtitle("Overfitting occurs when the model memorizes the noise instead of learning the pattern.")
        
        axes = Axes(x_range=[0, 6], y_range=[0, 5])
        
        x_vals = np.linspace(0.5, 5.5, 10)
        # Underlying function + noise
        y_vals = 0.5 * x_vals**2 - 2 * x_vals + 3 + np.random.normal(0, 0.5, 10)
        
        dots = VGroup(*[Dot(axes.c2p(x, y), color=WHITE) for x, y in zip(x_vals, y_vals)])
        
        # Good Fit (Quadratic)
        good_graph = axes.plot(lambda x: 0.5 * x**2 - 2 * x + 3, color=GREEN)
        
        # Bad Fit (Interpolation) - Visual trick, just a jagged line through points
        bad_path_points = [axes.c2p(x,y) for x,y in zip(x_vals, y_vals)]
        bad_graph = VMobject().set_points_smoothly(bad_path_points).set_color(self.RED_C)
        
        self.play(Create(axes), Create(dots))
        self.play(Create(good_graph))
        self.wait(1)
        self.play(ReplacementTransform(good_graph, bad_graph))
        self.wait(1)
        self.clear_scene()

    # --- Part 11: Regularization ---
    def show_regularization(self):
        self.update_subtitle("L2 touches gently, keeping weights small. L1 hits the corners, forcing sparsity.", wait_time=0)
        
        # Split Screen Layout
        left_plane = NumberPlane(x_range=[-3,3], y_range=[-3,3], background_line_style={"stroke_opacity": 0.2}).scale(0.5).to_edge(LEFT)
        right_plane = NumberPlane(x_range=[-3,3], y_range=[-3,3], background_line_style={"stroke_opacity": 0.2}).scale(0.5).to_edge(RIGHT)
        
        title_l2 = Text("L2 Ridge", font_size=24, color=GREEN).next_to(left_plane, UP)
        title_l1 = Text("L1 Lasso", font_size=24, color=RED).next_to(right_plane, UP)
        
        self.play(FadeIn(left_plane), FadeIn(right_plane), Write(title_l2), Write(title_l1))
        
        # Constraints
        # L2: Circle
        l2_region = Circle(radius=1.5 * 0.5, color=GREEN, fill_opacity=0.3).move_to(left_plane.get_center()) # scale 0.5 applied
        # L1: Diamond
        l1_region = Square(side_length=1.5 * np.sqrt(2) * 0.5, color=RED, fill_opacity=0.3).rotate(45*DEGREES).move_to(right_plane.get_center())
        
        self.play(DrawBorderThenFill(l2_region), DrawBorderThenFill(l1_region))
        
        # Loss Center (Theoretical "Unconstrained Best")
        # Relative to the mini-planes
        # Let's say center is at (1.0, 1.0) in scaled coords relative to origin
        loss_center_offset = np.array([1.5, 1.5, 0]) 
        
        l2_center = left_plane.get_center() + loss_center_offset
        l1_center = right_plane.get_center() + loss_center_offset
        
        l2_dot = Dot(l2_center, color=BLUE)
        l1_dot = Dot(l1_center, color=BLUE)
        
        self.play(FadeIn(l2_dot), FadeIn(l1_dot))
        
        # Expanding Contours
        # Use ValueTracker to animate expansion
        expansion = ValueTracker(0.1)
        
        # Define contours based on expansion
        l2_contours = VGroup()
        l1_contours = VGroup()
        
        def get_contours(center, size):
            g = VGroup()
            for i in range(3):
                # Ellipses
                e = Ellipse(width=(size+i*0.5), height=(size+i*0.5)*0.6, color=BLUE_B).rotate(45*DEGREES).move_to(center)
                g.add(e)
            return g

        l2_cont_mob = get_contours(l2_center, 0.1)
        l1_cont_mob = get_contours(l1_center, 0.1)
        
        self.add(l2_cont_mob, l1_cont_mob)
        
        def update_contours(mob, center_point):
            val = expansion.get_value()
            mob.become(get_contours(center_point, val))
            
        l2_cont_mob.add_updater(lambda m: update_contours(m, l2_center))
        l1_cont_mob.add_updater(lambda m: update_contours(m, l1_center))
        
        # Animate expansion until collision
        # Collision target size approx 2.0
        self.play(expansion.animate.set_value(2.5), run_time=5)
        
        l2_cont_mob.clear_updaters()
        l1_cont_mob.clear_updaters()
        
        # Mark intersections
        # L2 Intersection (Smooth point)
        int_l2_pos = left_plane.get_center() + np.array([0.5, 0.55, 0]) # Visual approximation
        dot_int_l2 = Dot(int_l2_pos, color=YELLOW)
        lbl_l2 = Text("Small weights", font_size=16).next_to(dot_int_l2, LEFT)
        
        # L1 Intersection (Corner on Y axis)
        # Center of right plane is origin. Corner is UP * scale
        int_l1_pos = right_plane.get_center() + UP * 0.75 # Since radius was 1.5 * 0.5
        dot_int_l1 = Dot(int_l1_pos, color=YELLOW)
        lbl_l1 = Text("Sparsity (x=0)", font_size=16).next_to(dot_int_l1, LEFT)
        
        self.play(Flash(dot_int_l2), FadeIn(lbl_l2), Flash(dot_int_l1), FadeIn(lbl_l1))
        
        self.wait(3)
        
        # Final fade out
        self.clear_scene()