from manim import *
import numpy as np

# Aesthetic Configuration from JSON
# Background: Slate Grey (#2F353B)
# Lighting: Ambient + Spotlight
# Materials: Glossy/Reflective

config.background_color = "#2F353B"

class StunningFinanceAnimation(ThreeDScene):
    def construct(self):
        # --- SCENE SETUP ---
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES, zoom=0.6)
        
        # Add ambient light and a point light source for 3D depth
        self.renderer.camera.light_source.move_to([10, 10, 10])
        
        # 1. Microscopic Chaos
        # "A large 3D 'Pollen Grain' (Yellow Sphere) being buffeted by thousands of invisible/tiny water molecules"
        
        title_1 = Text("Microscopic Chaos: Brownian Motion", font_size=40).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title_1)
        self.play(Write(title_1))

        # Pollen Grain
        pollen = Sphere(radius=0.8, resolution=(32, 32))
        pollen.set_color(GOLD)
        pollen.set_gloss(0.8) # Glossy material
        pollen.set_shadow(0.5)
        
        # Water Molecules - using many small dots
        # Using fewer than "thousands" to maintain render performance, but enough to look dense
        num_molecules = 400
        molecule_radius = 0.03
        box_size = 4
        
        molecules = VGroup()
        molecule_velocities = []
        
        for _ in range(num_molecules):
            pos = np.random.uniform(-box_size, box_size, 3)
            # Ensure they don't start inside the pollen
            while np.linalg.norm(pos) < 1.0:
                pos = np.random.uniform(-box_size, box_size, 3)
                
            mol = Dot3D(point=pos, radius=molecule_radius, color=BLUE_C)
            molecules.add(mol)
            molecule_velocities.append(np.random.normal(0, 0.05, 3))

        self.play(Create(pollen), FadeIn(molecules))
        self.wait(0.5)

        # Simulation Loop for "Buffeting"
        # Use updaters for efficient particle movement
        
        def shake_pollen(mob, dt):
            mob.shift(np.random.normal(0, 0.15 * dt, 3))
            
        def wiggle_molecule(mob, dt):
            mob.shift(np.random.normal(0, 1.0 * dt, 3))
            # Keep them somewhat bounded so they don't fly off screen entirely
            if np.linalg.norm(mob.get_center()) > 5:
                 mob.move_to(np.random.uniform(-2, 2, 3))

        pollen.add_updater(shake_pollen)
        for mol in molecules:
            mol.add_updater(wiggle_molecule)
            
        self.wait(3)
        
        pollen.remove_updater(shake_pollen)
        for mol in molecules:
            mol.remove_updater(wiggle_molecule)
            
        # Ensure pollen is back near center for the transition
        self.play(pollen.animate.move_to(ORIGIN), run_time=0.5)

        # --- TRANSITION TO MACRO ---
        # "Zoom out. The individual particles disappear, replaced by a smooth 3D density cloud spreading out (Gaussian)."
        
        # Use move_camera with added_anims to synchronize
        self.move_camera(
            zoom=0.5,
            added_anims=[
                FadeOut(molecules),
                FadeOut(title_1),
                pollen.animate.scale(0.1).move_to(ORIGIN) # Shrink pollen to point source
            ]
        )
        
        # 2. Macro Diffusion
        title_2 = Text("Macro Diffusion: The Heat Equation", font_size=40).to_corner(UL)
        eq_diffusion = MathTex(r"\frac{\partial \rho}{\partial t} = D \nabla^2 \rho", font_size=36)
        eq_diffusion.next_to(title_2, DOWN)
        
        self.add_fixed_in_frame_mobjects(title_2, eq_diffusion)
        self.play(Write(title_2), Write(eq_diffusion))
        
        # Define Gaussian Surface
        # P(x,y,t) ~ (1/t) * exp(-(x^2+y^2)/4Dt)
        
        def gaussian_func(u, v, sigma):
            # u, v are x, z coordinates
            r_sq = u**2 + v**2
            # Scale height for visibility
            height = 4 * (1 / (sigma * np.sqrt(2 * PI))) * np.exp(-r_sq / (2 * sigma**2))
            return [u, height, v]

        # Initial tight gaussian
        sigma_start = 0.5
        surface = Surface(
            lambda u, v: gaussian_func(u, v, sigma_start),
            u_range=[-4, 4],
            v_range=[-4, 4],
            resolution=(40, 40),
        )
        
        surface.set_style(fill_opacity=0.7, stroke_color=BLUE_E, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_D, BLUE_B, opacity=0.7)
        surface.set_gloss(0.5)
        
        self.play(Create(surface), FadeOut(pollen))
        
        # Animate spreading (increasing sigma)
        # Since Surface parameters aren't easily tweened, we'll use a ValueTracker with always_redraw 
        # or just transform to a flatter surface. Transform is safer for caching.
        
        sigma_end = 2.0
        surface_end = Surface(
            lambda u, v: gaussian_func(u, v, sigma_end),
            u_range=[-4, 4],
            v_range=[-4, 4],
            resolution=(40, 40),
        )
        surface_end.set_style(fill_opacity=0.6, stroke_color=BLUE_E, stroke_width=0.5)
        surface_end.set_fill_by_checkerboard(BLUE_D, BLUE_B, opacity=0.6)
        
        self.play(Transform(surface, surface_end), run_time=3)
        
        # --- TRANSITION TO FINANCE ---
        # "The bell curve cloud rotates and transforms into a 3D stock price path surface"
        # "Overlay: Black-Scholes Equation"
        
        self.play(FadeOut(title_2), FadeOut(eq_diffusion))
        
        title_3 = Text("Financial Abstraction: Black-Scholes", font_size=40).to_corner(UL)
        eq_bs = MathTex(r"dS_t = \mu S_t dt + \sigma S_t dW_t", font_size=36)
        eq_bs.next_to(title_3, DOWN)
        
        self.add_fixed_in_frame_mobjects(title_3, eq_bs)
        self.play(Write(title_3), Write(eq_bs))
        
        # Rotate camera to see "Time" evolution
        self.move_camera(phi=60 * DEGREES, theta=-120 * DEGREES, zoom=0.5, run_time=2)
        
        # Transform the Gaussian (Heat) into Log-Normal PDF Surface (Finance)
        # X-axis: Time (t)
        # Y-axis: Stock Price (S)
        # Z-axis: Probability (PDF) - represented as height or color intensity? 
        # Manim 3D usually implies Y is UP. 
        # Let's map: X=Time, Y=Probability(Height), Z=Stock Price
        
        # Coordinates:
        # u -> Time (0 to 3)
        # v -> Stock Price (0 to 5)
        
        axes = ThreeDAxes(
            x_range=[0, 4, 1],
            y_range=[0, 1, 0.2], # Probability height
            z_range=[0, 6, 1],   # Stock Price
            x_length=6,
            y_length=3,
            z_length=6
        ).shift(DOWN*1 + LEFT*2)
        
        labels = axes.get_axis_labels(x_label="Time", y_label="Prob", z_label="Price")
        
        self.play(FadeOut(surface), Create(axes), Create(labels))
        
        # Log Normal PDF Function
        # f(x) = 1/(x*sigma*sqrt(2pi*t)) * exp(...)
        # We'll plot this surface evolving over time
        
        def log_normal_surface(u, v):
            # u = Time (t)
            # v = Price (S)
            
            t = u + 0.1 # Avoid t=0
            S = v
            
            # Parameters
            sigma = 0.3
            mu = 0.1
            S0 = 2.0
            
            if S <= 0.01:
                return axes.c2p(u, 0, v)
                
            # Log-normal pdf
            # P(S, t)
            prefactor = 1 / (S * sigma * np.sqrt(2 * PI * t))
            exponent = -((np.log(S) - np.log(S0) - (mu - 0.5 * sigma**2) * t)**2) / (2 * sigma**2 * t)
            pdf = prefactor * np.exp(exponent)
            
            # Scaling pdf for visibility
            pdf_height = pdf * 1.5 
            
            return axes.c2p(u, pdf_height, v)

        finance_surface = Surface(
            log_normal_surface,
            u_range=[0, 4], # Time
            v_range=[0.1, 5], # Price
            resolution=(40, 40)
        )
        
        finance_surface.set_style(fill_opacity=0.8, stroke_color=GREEN_E, stroke_width=0.2)
        finance_surface.set_fill_by_value(axes=axes, colors=[(RED, 0.0), (GREEN, 0.5), (BLUE, 1.0)], axis=1)
        
        self.play(Create(finance_surface), run_time=3)
        
        # Add a sample path on top of the surface (optional but helps context)
        # Simulating one stock path
        
        t_vals = np.linspace(0, 4, 100)
        dt = t_vals[1] - t_vals[0]
        S_path = [2.0] # S0
        current_S = 2.0
        mu = 0.1
        sigma = 0.3
        
        points = [axes.c2p(0, 0, 2.0)]
        
        np.random.seed(42)
        for _ in range(99):
            dW = np.random.normal(0, np.sqrt(dt))
            dS = current_S * mu * dt + current_S * sigma * dW
            current_S += dS
            # Project onto the "floor" of probability (y=0) or maybe slightly above?
            # Or map height to the actual PDF value at that point?
            # Let's just draw the path on the "floor" (y=0 plane effectively, though y is up here)
            # Wait, in our axes, Y is Probability. So the path should travel through Time(X) and Price(Z).
            # We can lift it slightly in Y so it's visible.
            points.append(axes.c2p(t_vals[len(points)], 0.05, current_S))
            
        path_mobj = VMobject().set_points_smoothly(points).set_color(WHITE).set_stroke(width=3)
        
        self.play(Create(path_mobj), run_time=2)
        
        self.wait(2)

