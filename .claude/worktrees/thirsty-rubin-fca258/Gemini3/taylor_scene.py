from manim import *
import numpy as np

# 1. Global Configuration & Style Guidelines
config.background_color = "#0F172A"  # Deep Slate Blue

class RadiusOfConvergence(ThreeDScene):
    def construct(self):
        # --- Color Palette & Constants ---
        COLOR_REAL = "#22D3EE"      # Cyan
        COLOR_APPROX = "#FACC15"    # Gold
        COLOR_BAD = "#EF4444"       # Red
        COLOR_GRID = "#334155"      # Slate 700
        COLOR_TEXT = "#F8FAFC"      # Slate 50
        
        # --- Helper Functions ---
        def f_real(x):
            return 1 / (1 + x**2)

        def taylor_term(x, n):
            # Sum (-1)^k * x^(2k) from k=0 to n
            val = 0
            for k in range(n + 1):
                val += ((-1)**k) * (x**(2*k))
            return val

        # =========================================================================
        # SCENE 1: The Mystery of the Real Line
        # =========================================================================
        
        # 1. Setup Axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            x_length=10,
            y_length=5,
            axis_config={"color": COLOR_TEXT, "stroke_width": 2},
            tips=False
        )
        # Hide grid initially or make it very subtle
        
        # Plot f(x)
        curve_real = axes.plot(f_real, color=COLOR_REAL, stroke_width=4)
        label_func = MathTex(r"f(x) = \frac{1}{1+x^2}", color=COLOR_TEXT).to_corner(UL)

        self.play(Create(axes), Create(curve_real), Write(label_func), run_time=3)
        self.wait(1)

        # 2. Taylor Approximations
        # We will transform P2 -> P4 -> P10
        # P_n corresponds to degree 2n here based on the prompt's sum definition
        
        # P_2 (n=1 in sum formula implies degree 2)
        poly_2 = axes.plot(lambda x: taylor_term(x, 1), x_range=[-2, 2], color=COLOR_APPROX, stroke_width=3)
        # P_4 (n=2 in sum formula implies degree 4)
        poly_4 = axes.plot(lambda x: taylor_term(x, 2), x_range=[-1.5, 1.5], color=COLOR_APPROX, stroke_width=3)
        # P_10 (n=5 in sum formula implies degree 10)
        poly_10 = axes.plot(lambda x: taylor_term(x, 5), x_range=[-1.2, 1.2], color=COLOR_APPROX, stroke_width=3)

        label_poly = MathTex(r"P_n(x) = \sum_{k=0}^{n} (-1)^k x^{2k}", color=COLOR_APPROX).next_to(label_func, DOWN)

        self.play(Create(poly_2), Write(label_poly))
        self.wait(1)
        self.play(Transform(poly_2, poly_4))
        self.wait(1)
        self.play(Transform(poly_2, poly_10))
        self.wait(2)

        # 3. The Barrier
        barrier_right = DashedLine(
            start=axes.c2p(1, -2), end=axes.c2p(1, 2), color=COLOR_BAD
        )
        barrier_left = DashedLine(
            start=axes.c2p(-1, -2), end=axes.c2p(-1, 2), color=COLOR_BAD
        )

        self.play(Create(barrier_right), Create(barrier_left))
        
        # 4. The Question
        self.play(
            FadeOut(poly_2), # This is the object holding the current state of the polynomial
            FadeOut(label_poly)
        )
        
        question_text = Text("Smooth on R. Why divergence at |x| >= 1?", font_size=36, color=COLOR_TEXT)
        question_text.to_edge(UP)
        self.play(Write(question_text))
        self.wait(2)
        self.play(FadeOut(question_text), FadeOut(label_func), FadeOut(barrier_left), FadeOut(barrier_right))

        # =========================================================================
        # SCENE 2: Unfolding the Hidden Dimension
        # =========================================================================

        # 1. Camera Movement & Grid
        # Add a NumberPlane to represent the Complex Plane (lying on z=0)
        complex_plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            background_line_style={"stroke_color": COLOR_GRID, "stroke_opacity": 0.5}
        )
        complex_plane.z_index = -1 # Put behind axes

        self.play(FadeIn(complex_plane))
        
        # Tilt to 3D
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=4)
        
        # 2. Revealing the Villain
        # Axis labels (Billboard to face camera or mapped to plane)
        label_re = Text("Re(z)", font_size=24, color=COLOR_TEXT).move_to(axes.c2p(4.5, 0, 0))
        label_im = Text("Im(z)", font_size=24, color=COLOR_TEXT).move_to(axes.c2p(0, 2.5, 0)).rotate(90*DEGREES, axis=OUT)
        # Note: In standard Manim axes, Y is up. In 3D complex plane metaphor, Y axis is Imaginary.
        # We need to explicitly make the labels 3D compatible.
        self.add_fixed_in_frame_mobjects(label_re) # Hack to make reading easier? 
        # Actually, let's place them in the scene and rotate them to lie on the plane
        label_re = Text("Re(z)", font_size=24, color=COLOR_TEXT).move_to(RIGHT * 4.5).rotate(180*DEGREES, axis=RIGHT).rotate(-90*DEGREES, axis=OUT)
        # The prompt asks for labels. Simple Texts rotated to face camera is usually best.
        # Let's use fixed_in_frame for clarity as requested in notes.
        
        # Create Singularities (i and -i)
        # i is at (0, 1) in the plane.
        singularity_pos = Dot3D(point=complex_plane.c2p(0, 1, 0), color=COLOR_BAD, radius=0.15)
        singularity_neg = Dot3D(point=complex_plane.c2p(0, -1, 0), color=COLOR_BAD, radius=0.15)
        
        self.play(
            GrowFromCenter(singularity_pos),
            GrowFromCenter(singularity_neg)
        )
        
        # Pulsate effect
        self.play(
            singularity_pos.animate.scale(1.5),
            singularity_neg.animate.scale(1.5),
            rate_func=there_and_back,
            run_time=1
        )

        # Explanation Text floating
        eq_complex = MathTex(r"1+z^2 = (z-i)(z+i)", color=COLOR_TEXT)
        eq_complex.rotate(90*DEGREES, axis=RIGHT) # Stand it up
        eq_complex.rotate(-45*DEGREES, axis=UP) # Face camera roughly
        eq_complex.move_to(np.array([2, 1, 1])) # Floating near dots
        
        text_sing = Text("Singularities at z = ±i", font_size=32, color=COLOR_TEXT)
        self.add_fixed_in_frame_mobjects(text_sing)
        text_sing.to_corner(UR)

        self.play(Write(eq_complex), Write(text_sing))
        self.wait(3)

        # Transition to Top-Down
        self.play(
            FadeOut(curve_real),
            FadeOut(eq_complex),
            FadeOut(text_sing),
            FadeOut(axes) # We keep the NumberPlane (complex_plane)
        )
        
        # Move camera to top down
        # theta = -90 degrees usually puts +x to the right and +y to the top
        self.move_camera(phi=0, theta=-90*DEGREES, run_time=3)
        
        # =========================================================================
        # SCENE 3: Topology and the Open Disk
        # =========================================================================
        
        # 1. Setup z0
        z0 = Dot(point=complex_plane.c2p(0, 0, 0), color=WHITE)
        label_z0 = MathTex("z_0", color=WHITE).next_to(z0, DL, buff=0.1)
        
        self.play(Create(z0), Write(label_z0))
        
        # 2. The Radar (Convergence Circle)
        # We need to grow a circle until it hits (0,1)
        radius_tracker = ValueTracker(0)
        
        def get_circle():
            r = radius_tracker.get_value()
            c = Circle(radius=r, color=COLOR_APPROX, stroke_opacity=1, stroke_width=4)
            c.set_fill(COLOR_APPROX, opacity=0.3)
            # Dotted stroke isn't native to Circle easily without DashedVMobject, 
            # but standard circle is fine. We can use DashedVMobject wrapper.
            return c

        conv_circle = always_redraw(get_circle)
        self.add(conv_circle)
        
        self.play(radius_tracker.animate.set_value(1), run_time=5, rate_func=linear)
        
        # 3. Labeling
        # Radius Line
        radius_line = Line(complex_plane.c2p(0,0,0), complex_plane.c2p(0,1,0), color=WHITE)
        brace = Brace(radius_line, direction=LEFT)
        label_r1 = MathTex("R = 1").next_to(brace, LEFT)
        
        self.play(Create(radius_line), Create(brace), Write(label_r1))
        
        insight_text = Text("Convergence limited by the nearest singularity.", font_size=24, color=COLOR_TEXT)
        insight_text.to_edge(DOWN)
        self.play(Write(insight_text))
        self.wait(3)
        
        # Cleanup
        self.remove(conv_circle) # Remove updater
        self.play(
            FadeOut(conv_circle), 
            FadeOut(radius_line), 
            FadeOut(brace), 
            FadeOut(label_r1),
            FadeOut(insight_text)
        )

        # =========================================================================
        # SCENE 4: The Pythagorean Connection
        # =========================================================================

        # 1. Move Center
        new_center = complex_plane.c2p(2, 0, 0)
        self.play(
            z0.animate.move_to(new_center),
            label_z0.animate.next_to(new_center, DL, buff=0.1)
        )
        
        # 2. New Expansion
        # Target radius is sqrt(2^2 + 1^2) = sqrt(5) approx 2.236
        target_radius = np.sqrt(5)
        
        radius_tracker.set_value(0)
        conv_circle_2 = always_redraw(get_circle).move_to(new_center)
        self.add(conv_circle_2)
        
        self.play(radius_tracker.animate.set_value(target_radius), run_time=4)
        
        # 3. Geometric Construction
        # Triangle vertices: (2,0), (0,0), (0,1) isn't the right triangle.
        # The distance is from z0=(2,0) to sing=(0,1).
        # Triangle is: (2,0) -> (0,0) -> (0,1) -> (2,0).
        # Leg 1: (0,0) to (2,0) [Length 2] on Real Axis
        # Leg 2: (0,0) to (0,1) [Length 1] on Imaginary Axis
        # Hypotenuse: (2,0) to (0,1).
        
        line_base = Line(complex_plane.c2p(0,0,0), complex_plane.c2p(2,0,0), color=WHITE, stroke_width=3)
        line_height = Line(complex_plane.c2p(0,0,0), complex_plane.c2p(0,1,0), color=WHITE, stroke_width=3)
        hypotenuse = Line(complex_plane.c2p(2,0,0), complex_plane.c2p(0,1,0), color=YELLOW, stroke_width=4)
        
        self.play(Create(line_base), Create(line_height))
        self.play(Create(hypotenuse))
        
        # 4. Calculation
        calc_label = MathTex(r"R = \sqrt{2^2 + 1^2} = \sqrt{5}", color=COLOR_TEXT)
        calc_label.next_to(hypotenuse.get_center(), RIGHT, buff=0.5)
        self.add_fixed_in_frame_mobjects(calc_label) # Ensure readability
        
        self.play(Write(calc_label))
        self.wait(4)
        
        # Cleanup
        self.remove(conv_circle_2)
        self.play(
            FadeOut(conv_circle_2),
            FadeOut(line_base), FadeOut(line_height), FadeOut(hypotenuse),
            FadeOut(calc_label),
            FadeOut(label_z0)
        )

        # =========================================================================
        # SCENE 5: Summary and Synthesis
        # =========================================================================

        # 1. Setup Field
        # Existing singularities: (0,1), (0,-1)
        # Add extras
        s3_pos = complex_plane.c2p(3, 2, 0)
        s4_pos = complex_plane.c2p(-2, -1, 0)
        
        singularity_3 = Dot3D(point=s3_pos, color=COLOR_BAD, radius=0.15)
        singularity_4 = Dot3D(point=s4_pos, color=COLOR_BAD, radius=0.15)
        
        self.play(FadeIn(singularity_3), FadeIn(singularity_4))
        
        singularities = [
            np.array([0, 1, 0]),
            np.array([0, -1, 0]),
            np.array([3, 2, 0]),
            np.array([-2, -1, 0])
        ]

        # 2. Dynamic Simulation
        t_tracker = ValueTracker(0)
        
        # Path function: A figure 8 or smooth curve
        def get_path_point(t):
            # Lissajous-like figure
            x = 2.5 * np.sin(0.5 * t)
            y = 1.5 * np.cos(t)
            return complex_plane.c2p(x, y, 0)

        # Update Center Dot
        z0.add_updater(lambda m: m.move_to(get_path_point(t_tracker.get_value())))
        
        # Dynamic Circle
        def get_dynamic_circle():
            center = z0.get_center()
            # Calculate min distance to any singularity (in scene coords)
            min_dist = float('inf')
            
            # Convert singularities to scene coords logic 
            # Since NumberPlane scale might differ, best to use scene coords directly
            # We defined singularities using c2p logic or are tracking known points.
            # Let's get actual scene coords of the red dots
            s_mobjects = [singularity_pos, singularity_neg, singularity_3, singularity_4]
            s_coords = [mob.get_center() for mob in s_mobjects]
            
            for s_coord in s_coords:
                dist = np.linalg.norm(center - s_coord)
                if dist < min_dist:
                    min_dist = dist
            
            c = Circle(radius=min_dist, color=COLOR_APPROX)
            c.set_fill(COLOR_APPROX, opacity=0.2)
            c.move_to(center)
            return c

        dynamic_circle = always_redraw(get_dynamic_circle)
        self.add(dynamic_circle)
        
        # Run Animation
        self.play(t_tracker.animate.set_value(4 * PI), run_time=8, rate_func=linear)
        
        # 3. Conclusion
        z0.clear_updaters()
        dynamic_circle.clear_updaters() # Freeze the final state
        
        final_formula = MathTex(r"R = \min |z_0 - z_{singularity}|", color=COLOR_TEXT)
        self.add_fixed_in_frame_mobjects(final_formula)
        final_formula.to_edge(UP)
        
        # Fade out everything except the circle and the nearest singularity
        # (Simplification: just fade out grid and other dots, keep the concept)
        
        self.play(
            FadeOut(complex_plane),
            FadeOut(singularity_3), # Assuming these might not be the closest at the end
            FadeOut(singularity_4), # just fading extras to focus
            Write(final_formula)
        )
        
        self.wait(4)
        
        # Fade to black
        self.play(FadeOut(Group(*self.mobjects)))