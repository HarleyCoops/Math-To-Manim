from manim import *
import numpy as np

# Aesthetic Configuration
config.background_color = "#2F353B"  # Slate Gray

class BrownianToFinance(ThreeDScene):
    def construct(self):
        # --- Setup Camera & Lights ---
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.7)
        
        # Add lighting to enhance 3D Feel
        # Manim Community v0.19.0 handles lighting via camera config or shading, 
        # explicit PointLight is not a standard Mobject in basic 3D scene setup easily.
        # We will rely on default shading or set light source.
        self.camera.light_source_start_point = [10, 10, 10]
        
        # Reflective Floor (Grid)
        floor = NumberPlane(
            x_range=(-10, 10, 1), y_range=(-10, 10, 1),
            background_line_style={"stroke_color": GREY_C, "stroke_width": 1, "stroke_opacity": 0.3}
        )
        floor.rotate(90 * DEGREES, axis=RIGHT).shift(DOWN * 2)
        self.add(floor)

        # --- Phase 1: The Pollen Grain (Brownian Motion) ---
        
        # The Pollen Grain
        pollen = Sphere(radius=0.5, resolution=(20, 20)).set_color(GOLD).set_gloss(0.8)
        pollen.shift(UP)
        
        # Water molecules (represented as small dots)
        molecules = VGroup(*[
            Dot3D(radius=0.05, color=BLUE_B).move_to(np.random.uniform(-3, 3, 3))
            for _ in range(50)
        ])
        
        title_1 = Text("1827: Robert Brown's Pollen", font_size=36).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title_1)
        self.play(FadeIn(title_1), Create(pollen), FadeIn(molecules))
        
        # Simulate Brownian Jitter
        # We move the pollen randomly based on "impacts"
        for _ in range(15):
            random_kick = np.random.normal(0, 0.3, 3)
            self.play(
                pollen.animate.shift(random_kick),
                molecules.animate.shift(np.random.normal(0, 0.1, (50, 3))),
                run_time=0.1, rate_func=linear
            )
            
        # Cleanup Phase 1
        self.play(FadeOut(title_1), FadeOut(molecules))
        
        # --- Phase 2: Einstein & The Heat Equation ---
        
        # Pollen becomes a point source for diffusion
        # We represent diffusion as a growing Gaussian cloud (Surface)
        
        def gaussian_surface(u, v, t):
            # u, v range -3 to 3
            # t is time parameter
            sigma = np.sqrt(2 * t + 0.1)
            r_sq = u**2 + v**2
            z = (1 / (sigma * np.sqrt(2*PI))) * np.exp(-r_sq / (2 * sigma**2))
            return [u, z * 5, v] # Map height to Y
            
        surface = Surface(
            lambda u, v: gaussian_surface(u, v, 0.1),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(30, 30)
        )
        surface.set_style(fill_opacity=0.6, stroke_color=BLUE_E, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE, BLUE_E, opacity=0.6)
        surface.shift(DOWN*1) # Align with floor roughly
        
        title_2 = Text("1905: Einstein & Diffusion", font_size=36).to_corner(UL)
        eq_2 = MathTex(r"\frac{\partial \rho}{\partial t} = D \nabla^2 \rho").next_to(title_2, DOWN).scale(0.8)
        
        self.add_fixed_in_frame_mobjects(title_2, eq_2)
        self.play(
            Transform(pollen, Dot3D(color=GOLD).move_to([0,1,0])), # Shrink pollen
            Write(title_2), Write(eq_2),
            Create(surface)
        )
        self.play(FadeOut(pollen))
        
        # Animate Diffusion (Spreading out)
        # Manim surfaces are tricky to animate param updates smoothly without ValueTracker + always_redraw
        # We will just scale it to simulate spreading as a hack for brevity
        self.play(
            surface.animate.scale([2, 0.5, 2]), # Widen X/Z, Flatten Y
            run_time=3
        )
        
        # Cleanup Phase 2
        self.play(FadeOut(title_2), FadeOut(eq_2), FadeOut(surface))
        
        # --- Phase 3: Financial Engineering (Black Scholes) ---
        
        # Rotate camera for a "Time Series" view
        self.move_camera(phi=75 * DEGREES, theta=-10 * DEGREES, zoom=0.8, run_time=2)
        
        title_3 = Text("1973: Black-Scholes Option Pricing", font_size=36).to_corner(UL)
        eq_3 = MathTex(r"dS_t = \mu S_t dt + \sigma S_t dW_t").next_to(title_3, DOWN).scale(0.8)
        self.add_fixed_in_frame_mobjects(title_3, eq_3)
        self.play(Write(title_3), Write(eq_3))
        
        # Generate a 3D Geometric Brownian Motion Path
        # Time on X, Price on Y, Z is just 0
        
        axes = ThreeDAxes(x_range=[0, 5], y_range=[0, 5], z_range=[-2, 2])
        axes.shift(DOWN * 2 + LEFT * 2)
        
        np.random.seed(42)
        t = np.linspace(0, 5, 100)
        W = np.cumsum(np.random.normal(0, np.sqrt(5/100), 100))
        S = 2 * np.exp((0.5 - 0.5 * 0.2**2) * t + 0.2 * W) # Geometric Brownian Motion
        
        # Create 3D curve points
        points = [axes.c2p(ti, Si, 0) for ti, Si in zip(t, S)]
        stock_path = VMobject().set_points_smoothly(points).set_color(GREEN)
        
        self.play(Create(axes))
        self.play(Create(stock_path, run_time=3, rate_func=linear))
        
        # Show the "Cone of Uncertainty" (The option price probability)
        # At T=5, show a vertical distribution (rotate the Gaussian)
        
        cone = ParametricFunction(
            lambda t: axes.c2p(5, 2 + 2*np.exp(-(t)**2), t),
            t_range=[-2, 2], color=RED
        )
        
        self.play(Create(cone))
        self.wait(2)
        
        # Final Cleanup
        self.play(FadeOut(title_3), FadeOut(eq_3), FadeOut(axes), FadeOut(stock_path), FadeOut(cone))
        self.wait(1)

