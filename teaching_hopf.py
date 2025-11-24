from manim import *
import numpy as np

# Aesthetic Configuration
config.background_color = "#F5F5F0"
config.pixel_height = 1080
config.pixel_width = 1920

class TeachingHopf(ThreeDScene):
    def construct(self):
        # --- Setup ---
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES, zoom=0.6)
        
        # Math Definitions
        title = Text("The Hopf Fibration", font="Helvetica", weight=BOLD).scale(0.8)
        title.to_corner(UL).set_color(BLACK)
        
        equation_group = VGroup(
            MathTex(r"f: S^3 \to S^2", color=BLACK),
            MathTex(r"(z_1, z_2) \mapsto (2z_1\bar{z}_2, |z_1|^2 - |z_2|^2)", color=BLACK).scale(0.8)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=0.5).to_edge(LEFT)
        
        explanation_text = Text(
            "Every point on the sphere S2\nlifts to a circle (fiber) in S3",
            font="Helvetica", font_size=24, color="#444444"
        ).next_to(equation_group, DOWN, buff=0.5, aligned_edge=LEFT)

        # Fix them to the screen (HUD)
        self.add_fixed_in_frame_mobjects(title)
        
        # --- Helper Functions ---
        floor_level = -3
        
        def get_fiber_points(eta, phi_start=0, n_points=100):
            # eta: torus selector (0 to pi/2)
            # phi_start: fiber selector on that torus
            xi1_range = np.linspace(0, TAU, n_points)
            path_points = []
            for xi1 in xi1_range:
                # Hopf Map Inverse param
                # z1 = exp(i * (xi1 + xi2)) * sin(eta) ? No, let's use the standard param
                # Standard Torus parametrization of S3:
                # z1 = cos(eta) * exp(i * xi1)
                # z2 = sin(eta) * exp(i * (xi1 + phi_start)) 
                # This ensures they are fibers.
                
                p0 = np.cos(eta) * np.exp(1j * xi1)
                p1 = np.sin(eta) * np.exp(1j * (xi1 + phi_start))
                
                # Stereographic Projection
                x1, y1 = p0.real, p0.imag
                x2, y2 = p1.real, p1.imag
                
                denom = 1 - y2
                if abs(denom) < 0.001: denom = 0.001
                
                path_points.append([x1/denom, y1/denom, x2/denom])
            return np.array(path_points)

        # --- Geometry Creation ---
        fibers_all = VGroup()
        reflections_all = VGroup()
        
        # Create a nice dense bundle
        colors = [TEAL_E, BLUE_E, PURPLE_E, MAROON_E]
        etas = np.linspace(0.3, 1.2, 4) # 4 Layers
        
        for i, eta in enumerate(etas):
            c = colors[i]
            n_fibers = 8
            for k in range(n_fibers):
                phi = k * TAU / n_fibers
                pts = get_fiber_points(eta, phi)
                
                # Rotate to look nice
                # The stereographic projection is already 3D, but let's orient it
                # so the 'hole' is along Z? It's already roughly there.
                # Let's just rotate for view.
                
                fiber = VMobject()
                fiber.set_points_smoothly(pts)
                fiber.set_stroke(c, width=4, opacity=0.8)
                
                # Reflection
                refl = fiber.copy()
                refl.apply_function(lambda p: np.array([p[0], p[1], -p[2] + 2*floor_level]))
                refl.set_stroke(color=GRAY, width=1, opacity=0.15)
                
                fibers_all.add(fiber)
                reflections_all.add(refl)

        # Special "Linked Pair" for later
        link_fiber_1 = VMobject().set_points_smoothly(get_fiber_points(0.5, 0))
        link_fiber_1.set_stroke(RED, width=8, opacity=1)
        
        link_fiber_2 = VMobject().set_points_smoothly(get_fiber_points(1.0, PI/2))
        link_fiber_2.set_stroke(ORANGE, width=8, opacity=1)
        
        linked_pair = VGroup(link_fiber_1, link_fiber_2)

        # --- Animation Sequence ---
        
        # 1. Intro
        self.play(Write(title))
        self.play(Create(fibers_all, lag_ratio=0.01, run_time=3), FadeIn(reflections_all))
        self.wait()
        
        # 2. Show Equations
        self.add_fixed_in_frame_mobjects(equation_group)
        self.play(Write(equation_group))
        self.add_fixed_in_frame_mobjects(explanation_text)
        self.play(FadeIn(explanation_text))
        self.wait(2)
        
        # 3. Deconstruct - Focus on one shell
        # Fade out everything except the second shell (index 1 in etas)
        # Logic to select sub-mobjects is tricky in flat VGroup, 
        # let's just fade everything to low opacity
        self.play(
            fibers_all.animate.set_stroke(opacity=0.1),
            reflections_all.animate.set_stroke(opacity=0.05),
            run_time=1.5
        )
        
        # 4. The Linking Demo
        # Show the two specific linked fibers
        self.play(Create(linked_pair, run_time=2))
        
        # Rotate to show the link structure clearly
        self.move_camera(phi=30 * DEGREES, theta=120 * DEGREES, run_time=3)
        self.wait()
        self.move_camera(phi=70 * DEGREES, theta=30 * DEGREES, run_time=3)
        
        # 5. Re-Integrate
        self.play(
            FadeOut(linked_pair),
            fibers_all.animate.set_stroke(opacity=0.8),
            reflections_all.animate.set_stroke(opacity=0.15),
            run_time=2
        )
        
        # 6. Fly Through / Zoom
        # Move camera into the center
        self.move_camera(phi=90 * DEGREES, theta=0 * DEGREES, zoom=2.5, run_time=4)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(4)


