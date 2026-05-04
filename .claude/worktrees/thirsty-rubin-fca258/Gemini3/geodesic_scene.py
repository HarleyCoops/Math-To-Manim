from manim import *
import numpy as np

# --- Global Configuration ---
config.background_color = "#0B1020"  # Midnight Blue

# --- Color Palette ---
C_TEXT = "#E0E0E0"   # Off-white
C_CALC = "#4ECDC4"   # Teal
C_GEO = "#FF6B6B"    # Coral Red
C_PHYS = "#FFE66D"   # Gold
C_TENSOR = "#9D4EDD" # Violet
C_GRID = "#1A2542"   # Darker Blue for grid lines

class Act1_EuclideanFoundation(ThreeDScene):
    def construct(self):
        # --- Scene 1: The Tangent Slider ---
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 4, 1],
            axis_config={"color": C_GRID},
        ).add_coordinates()
        
        # Curve f(x) = 0.5x^2 - 1
        func = lambda x: 0.5 * x**2 - 1
        curve = axes.plot(func, color=WHITE, stroke_width=2)
        label_curve = MathTex("f(x)", color=WHITE).next_to(curve, UP)
        
        # Dot and Tangent
        t_tracker = ValueTracker(-3)
        dot = always_redraw(lambda: Dot(point=axes.c2p(t_tracker.get_value(), func(t_tracker.get_value())), color=C_CALC))
        label_dot = always_redraw(lambda: MathTex("x", color=C_CALC).next_to(dot, DOWN))
        
        # Tangent Line Updater
        def get_tangent_line():
            x = t_tracker.get_value()
            slope = x # derivative of 0.5x^2 - 1 is x
            angle = np.arctan(slope)
            line = Line(LEFT, RIGHT, color=C_PHYS, stroke_width=4).scale(1.5)
            line.rotate(angle)
            line.move_to(dot.get_center())
            return line

        tangent = always_redraw(get_tangent_line)

        self.add(axes, curve, label_curve, dot, label_dot, tangent)
        self.wait(2)
        
        # Animation: Slide
        self.play(t_tracker.animate.set_value(3), run_time=4, rate_func=smooth)
        
        # Freeze and isolate
        text_deriv = Tex(r"The Derivative: $f'(x)$ describes local change.", color=C_TEXT)
        text_deriv.to_edge(UP)
        
        self.play(
            FadeOut(axes), FadeOut(curve), FadeOut(label_curve), FadeOut(label_dot),
            Write(text_deriv)
        )
        self.wait(1)
        
        # Transition cleanup
        self.play(FadeOut(dot), FadeOut(tangent), FadeOut(text_deriv))

        # --- Scene 2: The Flexible Grid ---
        # Creating a manual grid to deform
        grid = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1], 
            background_line_style={"stroke_color": GREY, "stroke_opacity": 0.3}
        )
        
        vector = Arrow(grid.c2p(0,0), grid.c2p(2,1), buff=0, color=C_PHYS, stroke_width=6)
        i_hat = Arrow(grid.c2p(0,0), grid.c2p(1,0), buff=0, color=RED, stroke_width=4)
        j_hat = Arrow(grid.c2p(0,0), grid.c2p(0,1), buff=0, color=GREEN, stroke_width=4)
        
        text_lin_alg = Tex("Linear Algebra: Vectors follow the grid.", color=C_TEXT).to_edge(UP)
        
        self.play(Create(grid), GrowArrow(vector), GrowArrow(i_hat), GrowArrow(j_hat))
        self.play(Write(text_lin_alg))
        
        # Apply Matrix [[1, 0.5], [0, 1.5]]
        matrix = [[1, 0.5], [0, 1.5]]
        
        self.play(
            grid.animate.apply_matrix(matrix),
            vector.animate.apply_matrix(matrix),
            i_hat.animate.apply_matrix(matrix),
            j_hat.animate.apply_matrix(matrix),
            run_time=3
        )
        self.wait(1)
        self.play(FadeOut(Group(grid, vector, i_hat, j_hat, text_lin_alg)))

        # --- Scene 3: The Deterministic Arc ---
        # 3D setup prep
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        
        particle = Dot(color=C_PHYS, radius=0.1)
        path = TracedPath(particle.get_center, stroke_color=WHITE, stroke_width=2, dissipating_time=2)
        
        # Projectile kinematics
        v0 = np.array([3, 4, 0])
        acc = np.array([0, -2, 0])
        p0 = np.array([-4, -2, 0])
        
        time_tracker = ValueTracker(0)
        
        def update_particle(m):
            t = time_tracker.get_value()
            pos = p0 + v0 * t + 0.5 * acc * t**2
            m.move_to(pos)
            
        particle.add_updater(update_particle)
        
        # Velocity and Acc Vectors
        vel_vector = always_redraw(lambda: Arrow(
            particle.get_center(), 
            particle.get_center() + (v0 + acc * time_tracker.get_value())*0.5, 
            buff=0, color=GREEN
        ))
        acc_vector = always_redraw(lambda: Arrow(
            particle.get_center(), 
            particle.get_center() + acc*0.5, 
            buff=0, color=RED
        ))
        
        self.add(path, particle, vel_vector, acc_vector)
        self.play(time_tracker.animate.set_value(4), run_time=5, rate_func=linear)
        
        # Transition to Act 2 style
        full_path = ParametricFunction(
            lambda t: p0 + v0 * t + 0.5 * acc * t**2,
            t_range=[0, 4], color=C_PHYS
        )
        
        self.remove(path)
        self.add(full_path)
        
        # Pan and rotate to 3D
        self.move_camera(phi=60*DEGREES, theta=-45*DEGREES, zoom=0.8, run_time=2)
        self.wait(1)


class Act2_GeometryAndTensors(ThreeDScene):
    def construct(self):
        # --- Scene 4: The Gradient Hill ---
        self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES)
        
        # Gaussian Surface
        surface = Surface(
            lambda u, v: np.array([u, v, 2 * np.exp(-(u**2 + v**2))]),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(24, 24),
            fill_opacity=0.5,
            stroke_color=C_GRID,
            stroke_width=0.5
        )
        
        self.play(Create(surface))
        
        # Gradient Vectors (randomly placed)
        vectors = VGroup()
        for _ in range(15):
            u, v = np.random.uniform(-1.5, 1.5, 2)
            pt = np.array([u, v, 2 * np.exp(-(u**2 + v**2))])
            # Gradient of z = 2e^-(x^2+y^2) is (-4x z, -4y z) approx
            # pointing UP hill means pointing towards origin in xy
            direction = -np.array([u, v, 0]) 
            norm = np.linalg.norm(direction)
            if norm > 0.1:
                direction = direction / norm * 0.5 # Scale length
                # Tilt to be tangent? Simplified: just show vectors on surface
                vec = Arrow3D(
                    start=pt, 
                    end=pt + direction + np.array([0,0,0.5]), # slight z lift
                    color=C_CALC,
                    resolution=8
                )
                vectors.add(vec)
        
        self.play(LaggedStart(*[GrowArrow(v) for v in vectors], lag_ratio=0.1))
        self.wait(1)
        
        # Focus on a path
        curve_func = lambda t: np.array([np.cos(t), np.sin(t), 2 * np.exp(-1)]) # circle at radius 1
        path = ParametricFunction(curve_func, t_range=[0, 2*PI], color=WHITE)
        
        self.play(FadeOut(vectors), FadeOut(surface))
        self.play(Create(path))
        
        # --- Scene 5: Parametric Curves & Tangent ---
        bead = Dot3D(color=WHITE)
        tau_val = ValueTracker(0)
        
        bead.add_updater(lambda m: m.move_to(curve_func(tau_val.get_value())))
        
        tangent_vec = always_redraw(lambda: Arrow3D(
            start=bead.get_center(),
            end=bead.get_center() + np.array([-np.sin(tau_val.get_value()), np.cos(tau_val.get_value()), 0]),
            color=C_GEO
        ))
        
        # Fixed in frame labels
        label_tau = MathTex(r"\tau", color=WHITE).to_corner(UL)
        label_eq = MathTex(r"u^\mu = \frac{dx^\mu}{d\tau}", color=C_GEO).next_to(label_tau, DOWN)
        self.add_fixed_in_frame_mobjects(label_tau, label_eq)
        
        self.add(bead, tangent_vec)
        self.play(tau_val.animate.set_value(2*PI), run_time=4)
        
        self.play(FadeOut(path), FadeOut(bead), FadeOut(tangent_vec), FadeOut(label_tau), FadeOut(label_eq))
        
        # --- Scene 6: Einstein Summation ---
        self.set_camera_orientation(phi=0, theta=-90*DEGREES) # Back to 2D view effectively
        
        eq1 = MathTex(r"a_\mu b^\mu", font_size=72)
        eq2 = MathTex(r"a_{\color{#9D4EDD}\mu} b^{\color{#9D4EDD}\mu}", font_size=72)
        eq3 = MathTex(r"\sum_{i=1}^n a_i b_i", font_size=72)
        eq4 = MathTex(r"a_\mu b^\mu", font_size=72)
        text_sum = Tex("Implied Summation", color=C_TEXT).next_to(eq4, DOWN)
        
        self.play(Write(eq1))
        self.wait(1)
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait(1)
        self.play(Transform(eq2, eq3))
        self.wait(1)
        self.play(Transform(eq2, eq4), Write(text_sum))
        self.wait(2)
        
        self.clear()
        
        # --- Scene 7: Tensor Algebra (Machine) ---
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
        
        cube = Cube(side_length=2, fill_opacity=0.4, fill_color=C_TENSOR, stroke_width=2)
        label_T = MathTex("T", color=WHITE).scale(2)
        # Billboard the label
        label_T.rotate(90*DEGREES, RIGHT).rotate(45*DEGREES, OUT) 
        
        input_vec = Arrow3D(start=LEFT*4, end=LEFT*1.2, color=C_PHYS)
        output = MathTex("42", color=C_PHYS).scale(1.5).move_to(RIGHT*3)
        self.add_fixed_in_frame_mobjects(output)
        output.set_opacity(0)
        
        self.play(Create(cube))
        self.play(GrowArrow(input_vec))
        self.play(input_vec.animate.move_to(ORIGIN).scale(0), cube.animate.scale(1.1))
        self.play(cube.animate.scale(1/1.1), output.animate.set_opacity(1))
        self.wait(1)
        
        self.clear()
        self.set_camera_orientation(phi=0, theta=-90*DEGREES) # Reset to 2D
        
        # --- Scene 8: Coordinate Transformations ---
        # Fixed vector
        vec_fixed = Arrow(ORIGIN, UP*2 + RIGHT*1, buff=0, color=C_PHYS, stroke_width=6)
        
        # Grid morphing logic
        grid_group = VGroup()
        
        # We simulate the grid change by changing background lines
        # Cartesian
        cart_grid = NumberPlane(axis_config={"stroke_opacity": 0})
        # Polar lines (circles and rays)
        polar_grid = VGroup()
        for r in range(1, 5):
            polar_grid.add(Circle(radius=r, color=C_GRID, stroke_width=2))
        for theta in np.arange(0, 2*PI, PI/4):
            polar_grid.add(Line(ORIGIN, 5*np.array([np.cos(theta), np.sin(theta), 0]), color=C_GRID, stroke_width=2))
            
        # Coordinates Text
        coord_val = DecimalNumber(0, num_decimal_places=2, color=C_TEXT)
        coord_label = MathTex("(x, y): ").next_to(vec_fixed.get_end(), RIGHT)
        coord_group = VGroup(coord_label, coord_val).next_to(vec_fixed.get_end(), RIGHT)
        
        self.add(cart_grid, vec_fixed, coord_group)
        
        # Animate coords changing (simulated)
        self.play(
            cart_grid.animate.set_opacity(0.2),
            Transform(cart_grid, polar_grid),
            coord_val.animate.set_value(2.23), # Magnitude r
            run_time=3
        )
        
        text_inv = Tex("Coordinates change. Physical objects do not.", color=C_TEXT).to_edge(DOWN)
        self.play(Write(text_inv))
        self.wait(2)


class Act3_CurvedSpace(ThreeDScene):
    def construct(self):
        # --- Scene 9: Differentiable Manifolds ---
        sphere = Sphere(radius=2, resolution=(24, 24), fill_opacity=0.3, fill_color=BLUE, stroke_opacity=0.1)
        self.add(sphere)
        self.set_camera_orientation(phi=60*DEGREES, theta=30*DEGREES)
        
        # Patch visualization
        patch = Surface(
            lambda u, v: np.array([2*np.sin(u)*np.cos(v), 2*np.sin(u)*np.sin(v), 2*np.cos(u)]),
            u_range=[PI/2 - 0.2, PI/2 + 0.2],
            v_range=[-0.2, 0.2],
            color=YELLOW, fill_opacity=0.5
        )
        
        self.play(Create(patch))
        self.play(self.camera.frame.animate.move_to(patch).set_width(1.5), run_time=3)
        
        # Show flat grid locally
        flat_grid = NumberPlane(x_range=[-1,1], y_range=[-1,1]).scale(0.2).rotate(PI/2, axis=RIGHT).move_to(patch)
        self.play(FadeIn(flat_grid))
        
        lbl_euc = Tex("Locally Euclidean", color=C_TEXT).scale(0.2).next_to(flat_grid, UP)
        self.play(Write(lbl_euc))
        
        # Zoom out
        self.play(
            FadeOut(flat_grid), FadeOut(lbl_euc),
            self.camera.frame.animate.move_to(ORIGIN).set_width(14), # Reset zoom (approx)
            run_time=3
        )
        self.remove(patch, sphere)

        # --- Scene 10: The Metric Tensor ---
        # Warped Grid (2D viewed in 3D)
        warped_plane = ParametricFunction(
            lambda t: np.array([t, 0.2*np.sin(2*t), 0]), t_range=[-4, 4], color=C_GRID
        ) # Simplification: Just lines
        
        def metric_surface(u, v):
            # Distortion function
            stretch = 1 + 0.5 * np.exp(-u**2)
            return np.array([u * stretch, v, 0])

        grid_lines = VGroup()
        for i in range(-5, 6):
            grid_lines.add(ParametricFunction(lambda t: metric_surface(t, i*0.5), t_range=[-2, 2], color=C_GRID))
            grid_lines.add(ParametricFunction(lambda t: metric_surface(i*0.5, t), t_range=[-2, 2], color=C_GRID))
        
        self.play(Create(grid_lines))
        
        p1 = Dot(metric_surface(-1, 0), color=C_PHYS)
        p2 = Dot(metric_surface(-0.5, 0), color=C_PHYS)
        line = Line(p1.get_center(), p2.get_center(), color=C_GEO)
        
        eqn_metric = MathTex(r"ds^2 = g_{\mu\nu} dx^\mu dx^\nu", color=C_TEXT).to_edge(UP)
        self.add_fixed_in_frame_mobjects(eqn_metric)
        self.add(p1, p2, line)
        
        # Move points to "stretched" area (around u=0)
        p1_new = metric_surface(-0.25, 0)
        p2_new = metric_surface(0.25, 0)
        
        self.play(
            p1.animate.move_to(p1_new),
            p2.animate.move_to(p2_new),
            line.animate.put_start_and_end_on(p1_new, p2_new),
            run_time=2
        )
        
        # Visual cue for metric scaling (Coloring the center red)
        red_zone = Surface(
            lambda u, v: metric_surface(u, v),
            u_range=[-0.5, 0.5], v_range=[-2, 2],
            color=RED, fill_opacity=0.3, resolution=(10,10)
        )
        self.play(FadeIn(red_zone))
        self.wait(1)
        self.clear()
        self.remove(eqn_metric) # remove HUD

        # --- Scene 11: Christoffel Symbols ---
        # 2D Wavy grid logic
        wavy_grid = VGroup()
        for x in np.linspace(-3, 3, 10):
            # curve lines up/down
            wavy_grid.add(ParametricFunction(lambda t: np.array([x + 0.2*np.sin(t), t, 0]), t_range=[-3, 3], color=C_GRID))
        for y in np.linspace(-3, 3, 10):
            wavy_grid.add(ParametricFunction(lambda t: np.array([t, y + 0.2*np.sin(t), 0]), t_range=[-3, 3], color=C_GRID))
            
        self.play(Create(wavy_grid))
        
        # Gammas
        gammas = VGroup()
        for i in [-1, 1]:
            g = MathTex(r"\Gamma", color=C_GEO).move_to(np.array([i + 0.2*np.sin(i), i, 0]))
            gammas.add(g)
            
        self.play(ScaleInPlace(gammas, 1.5))
        lbl_chris = Tex("Christoffel Symbols track curvature", color=C_TEXT).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(lbl_chris)
        self.wait(2)
        
        self.clear() # Clear specific objects
        self.remove(lbl_chris) # Clear HUD

        # --- Scene 13: Parallel Transport (The Sphere) ---
        sphere = Sphere(radius=2.5, fill_opacity=0.2, resolution=(24, 24))
        self.play(Create(sphere))
        
        # Path points
        pt_start = np.array([0, -2.5, 0]) # "Equator" front
        pt_pole = np.array([0, 0, 2.5])   # "North Pole"
        pt_side = np.array([2.5, 0, 0])   # "Right Side" (90 deg diff)
        
        # Vector
        vec = Arrow3D(start=pt_start, end=pt_start + np.array([0, 0, 1]), color=C_PHYS, color_start=C_PHYS, color_end=C_PHYS)
        
        # 1. Move North
        # Visual trick: Rotate everything or move vector? Move vector.
        # Moving along surface from (0,-R,0) to (0,0,R). Arc in YZ plane.
        # Vector stays tangent to longitude, so it rotates from pointing Z to pointing Y.
        
        path1 = Arc(start_angle=-PI/2, angle=PI/2, radius=2.5, arc_center=ORIGIN).rotate(PI/2, axis=Y)
        # Actually simplest to just manually calculate start/end positions and rotations
        
        # Step 1: Up to pole
        # Start: Pos(0, -2.5, 0), Vec(0, 0, 1)
        # End: Pos(0, 0, 2.5), Vec(0, 1, 0)
        self.play(
            Rotate(vec, angle=PI/2, axis=RIGHT, about_point=ORIGIN),
            run_time=2
        )
        
        # Step 2: Down to side (90 deg longitude diff)
        # Path: Pole(0, 0, 2.5) to Side(2.5, 0, 0) via XZ plane arc.
        # Vector: At pole points (0, 1, 0) (This is Y).
        # As we move down XZ plane, the local basis rotates, but Y is perpendicular to the motion.
        # So vector stays pointing in Y (0, 1, 0).
        
        vec_step2_end = Arrow3D(start=pt_side, end=pt_side + np.array([0, 1, 0]), color=C_PHYS)
        
        # Animation: Rotate pos around Y axis? No, movement is along XZ arc.
        # We rotate the vector object around the center of sphere, but vector orientation stays locked to global Y?
        # Yes, Parallel transport along a geodesic perp to the vector preserves the vector direction in embedding space for this specific case? 
        # Actually, simpler: Just animate the position.
        
        self.play(
             Rotate(vec, angle=PI/2, axis=Y, about_point=ORIGIN), # This moves (0,0,2.5) to (2.5,0,0) and rotates the vector body
             # Wait, if we rotate around Y, the vector at (0,0,2.5) pointing (0,1,0) 
             # moves to (2.5,0,0) but still points (0,1,0). This is correct for PT along this line.
             run_time=2
        )
        
        # Step 3: Back to start along Equator
        # From (2.5, 0, 0) to (0, -2.5, 0). Arc in XY plane.
        # Vector is pointing (0, 1, 0) (Tangent to equator).
        # Transport along equator (geodesic): vector stays tangent.
        # So vector rotates with position.
        
        self.play(
            Rotate(vec, angle=-PI/2, axis=Z, about_point=ORIGIN),
            run_time=2
        )
        
        # Final check: Start vector was (0,0,1). End vector is (-1, 0, 0)? 
        # Let's check rotation: (0,1,0) rot -90 around Z -> (1, 0, 0).
        # It is rotated 90 degrees relative to original orientation at that point (which was Z).
        
        lbl_pt = Tex("Parallel Transport reveals curvature.", color=C_TEXT).to_edge(UP)
        self.add_fixed_in_frame_mobjects(lbl_pt)
        self.play(Write(lbl_pt))
        self.wait(2)


class Act4_TheConvergence(ThreeDScene):
    def construct(self):
        # --- Scene 14-16: Split Screen / Convergence ---
        # Note: True split screen is hard, using grouping.
        
        # Left Panel Group (Variational)
        left_group = VGroup()
        p1 = Dot(LEFT*4 + DOWN, color=C_PHYS)
        p2 = Dot(LEFT*4 + UP, color=C_PHYS)
        
        # Faint paths
        paths = VGroup()
        for i in range(5):
            paths.add(ArcBetweenPoints(p1.get_center(), p2.get_center(), angle=0.5 * (i-2), color=GREY, stroke_opacity=0.5))
        
        gold_path = Line(p1.get_center(), p2.get_center(), color=C_PHYS, stroke_width=4)
        eq_var = MathTex(r"\delta \int d\tau = 0", color=C_PHYS).next_to(gold_path, LEFT)
        left_group.add(p1, p2, paths, eq_var, gold_path)
        
        # Right Panel Group (Auto-Parallel)
        right_group = VGroup()
        path_r = Line(RIGHT*4 + DOWN, RIGHT*4 + UP, color=WHITE)
        dot_r = Dot(color=C_GEO).move_to(path_r.get_start())
        vec_r = Arrow(dot_r.get_center(), dot_r.get_center()+UP, color=C_GEO, buff=0)
        eq_cov = MathTex(r"\nabla_u u = 0", color=C_GEO).next_to(path_r, RIGHT)
        right_group.add(path_r, dot_r, vec_r, eq_cov)

        self.add(paths, p1, p2) # Left setup
        self.add(path_r, dot_r, vec_r) # Right setup
        
        # Animate Left
        self.play(Transform(paths, gold_path), Write(eq_var))
        
        # Animate Right
        self.play(
            dot_r.animate.move_to(path_r.get_end()),
            vec_r.animate.shift(UP*2),
            Write(eq_cov),
            run_time=2
        )
        
        # --- Scene 17: The Geodesic Equation ---
        self.clear()
        
        eq_newton = MathTex(r"a = 0", font_size=60)
        eq_cov_acc = MathTex(r"\frac{D u^\mu}{d\tau} = 0", font_size=60)
        
        # Final equation
        eq_final = MathTex(
            r"\frac{d^2 x^\mu}{d\tau^2}", 
            r"+", 
            r"\Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau} \frac{dx^\beta}{d\tau}", 
            r"= 0"
        ).scale(1.2)
        
        # Coloring
        eq_final[0].set_color(C_CALC) # Acceleration
        eq_final[2].set_color(C_GEO)  # Correction
        
        self.play(Write(eq_newton))
        self.wait(1)
        self.play(Transform(eq_newton, eq_cov_acc))
        self.wait(1)
        self.play(TransformMatchingTex(eq_newton, eq_final))
        
        # Labels
        lbl_acc = Tex("Coordinate Acceleration", color=C_CALC).next_to(eq_final[0], UP, buff=1).scale(0.7)
        lbl_curv = Tex("Curvature Correction", color=C_GEO).next_to(eq_final[2], DOWN, buff=1).scale(0.7)
        
        lines = VGroup(
            Line(lbl_acc.get_bottom(), eq_final[0].get_top(), color=C_CALC),
            Line(lbl_curv.get_top(), eq_final[2].get_bottom(), color=C_GEO)
        )
        
        self.play(FadeIn(lbl_acc), FadeIn(lbl_curv), Create(lines))
        self.wait(3)
        
        # --- Scene 18: Outro ---
        self.clear()
        self.set_camera_orientation(phi=70*DEGREES, theta=0)
        
        # Gravity Well
        well = Surface(
            lambda u, v: np.array([u, v, -2 * np.exp(-(u**2 + v**2)/2)]),
            u_range=[-4, 4], v_range=[-4, 4],
            resolution=(32, 32),
            fill_opacity=0.3, stroke_color=C_GRID, stroke_width=0.5
        )
        
        planet = Dot3D(color=C_PHYS, radius=0.2)
        planet_trace = TracedPath(planet.get_center, stroke_color=C_PHYS, stroke_width=2, dissipating_time=3)
        
        # Orbit logic (approximate circle at radius 2, z approx 0 for simplicity or matched to surface)
        def orbit_updater(m, dt):
            t = m.custom_t
            m.custom_t += dt
            u = 2 * np.cos(m.custom_t)
            v = 2 * np.sin(m.custom_t)
            z = -2 * np.exp(-(u**2 + v**2)/2)
            m.move_to(np.array([u, v, z]))

        planet.custom_t = 0
        planet.add_updater(orbit_updater)
        
        self.play(Create(well))
        self.add(planet, planet_trace)
        
        # Float Equation above
        eq_float = eq_final.copy().scale(0.7).to_corner(UR)
        self.add_fixed_in_frame_mobjects(eq_float)
        
        quote = Tex(
            r"Matter tells Spacetime how to curve.\\Spacetime tells Matter how to move.",
            color=C_TEXT
        ).scale(0.8).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(quote)
        
        self.play(Write(quote))
        self.wait(5)
        self.play(FadeOut(quote), FadeOut(eq_float), FadeOut(well), FadeOut(planet), FadeOut(planet_trace))

# To render, use command line:
# manim -pql filename.py Act1_EuclideanFoundation
# manim -pql filename.py Act2_GeometryAndTensors
# manim -pql filename.py Act3_CurvedSpace
# manim -pql filename.py Act4_TheConvergence