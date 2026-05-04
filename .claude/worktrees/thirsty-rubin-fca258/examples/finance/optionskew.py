from manim import *
import numpy as np

####################################
# Helper functions for various steps
####################################

def create_star_field(num_stars=200, spread=50):
    """
    Creates a random distribution of small dots to mimic a star field in 3D.
    """
    stars = VGroup()
    for _ in range(num_stars):
        # Randomly place stars in a cubic region
        x = np.random.uniform(-spread, spread)
        y = np.random.uniform(-spread, spread)
        z = np.random.uniform(-spread, spread)
        star = Dot3D(point=[x, y, z], radius=0.05, color=WHITE)
        stars.add(star)
    return stars

def create_spherical_point_cloud(num_points=100, radius=3):
    """
    Creates a set of points randomly distributed within a sphere of given radius.
    """
    points = VGroup()
    for _ in range(num_points):
        # Random direction, random radius
        theta = np.random.uniform(0, 2*PI)
        phi = np.random.uniform(0, PI)
        r = np.random.uniform(0, radius)
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        dot = Dot3D(point=[x, y, z], radius=0.05, color=YELLOW)
        points.add(dot)
    return points

def create_random_paths_3d(num_paths=6, path_length=5, step_size=0.2):
    """
    Creates a labyrinth of interwoven random (Brownian-like) paths in 3D.
    """
    paths = VGroup()
    colors = [RED, BLUE, GREEN, ORANGE, PURPLE, GOLD, MAROON]
    for i in range(num_paths):
        # Start near origin
        path_coords = []
        x, y, z = 0, 0, 0
        path_coords.append([x, y, z])
        for _ in np.arange(0, path_length, step_size):
            # Brownian step in 3D
            dx = np.random.normal(0, 0.2)
            dy = np.random.normal(0, 0.2)
            dz = np.random.normal(0, 0.2)
            x += dx
            y += dy
            z += dz
            path_coords.append([x, y, z])

        path = Line(
            path_coords[0],
            path_coords[1],
            color=colors[i % len(colors)],
            stroke_width=3
        )
        # Build up the path in segments
        for j in range(1, len(path_coords) - 1):
            segment = Line(
                path_coords[j],
                path_coords[j+1],
                color=colors[i % len(colors)],
                stroke_width=3
            )
            path = VGroup(path, segment)
        paths.add(path)
    return paths

def create_heat_equation_surface(u_min=-3, u_max=3, resolution=30):
    """
    Creates a wavy parametric surface reminiscent of the heat/diffusion effect.
    We use a simple function: z = A * exp(-x^2 - y^2) * cos(...)
    just as a conceptual stand-in for a 'heat' wave.
    """
    def surface(u, v):
        x = u
        y = v
        # A toy wave + Gaussian
        r2 = x**2 + y**2
        # This is purely for a shimmering effect
        z = 0.8 * np.exp(-0.3*r2) * np.sin(2*r2)
        return np.array([x, y, z])
    surface_mesh = Surface(
        surface,
        u_range=[u_min, u_max],
        v_range=[u_min, u_max],
        resolution=(resolution, resolution),
        should_make_jagged=True,
        fill_opacity=0.7,
        checkerboard_colors=[BLUE_D, BLUE_B]
    )
    return surface_mesh

def create_black_scholes_surface(u_min=1, u_max=5, v_min=0.1, v_max=2, resolution=20):
    """
    Creates a 3D surface to represent something akin to an option pricing or
    implied volatility function, e.g., z = f(S,K) or z = sigma(K,T).
    We'll approximate a 'smile' shape in 3D.
    - S or K axis: range ~ [u_min, u_max]
    - T axis: range ~ [v_min, v_max]
    - z = sigma -> define some function that 'smiles'
    """
    def surface(u, v):
        # For a volatility surface, we might have:
        # sigma = a + b * (some shape)
        # We'll just do a "smile" in the u dimension, modulated by v.
        # E.g. sigma = 0.2 + 0.1 * (u - 3)^2 + 0.05*v
        # Then we clamp or transform for aesthetic effect.
        sigma = 0.2 + 0.1 * (u - 3)**2 + 0.05 * (v - 1)
        return np.array([u, v, sigma])
    surface_mesh = Surface(
        surface,
        u_range=[u_min, u_max],
        v_range=[v_min, v_max],
        resolution=(resolution, resolution),
        should_make_jagged=True,
        fill_opacity=0.8,
        checkerboard_colors=[GREEN_D, GREEN_B]
    )
    return surface_mesh


class VolatilitySurfaceScene(ThreeDScene):
    def construct(self):
        # ---------------------------------------
        # 1. Celestial Introduction
        # ---------------------------------------
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES, distance=60)

        # Create star field
        star_field = create_star_field(num_stars=300, spread=40)
        self.play(FadeIn(star_field), run_time=3)

        # Show text: "Volatility Surface Visualization: Options Skew Model"
        title_text = Tex(r"Volatility Surface Visualization: Options Skew Model", font_size=48)
        title_text.set_color(YELLOW)
        title_text.to_edge(UP)

        self.play(Write(title_text))
        self.wait(2)
        
        # Subtle pulsing effect for stars (simulate cosmic fluctuation)
        self.play(star_field.animate.scale(1.05), run_time=1.5)
        self.play(star_field.animate.scale(1/1.05), run_time=1.5)
        self.wait()

        # ---------------------------------------
        # 2. From Cosmic Variability to Std Dev
        # ---------------------------------------
        # Morph stars into point cloud
        self.play(
            FadeOut(title_text, shift=UP),
            star_field.animate.scale(0.2).set_opacity(0.5),
            run_time=2
        )

        # Convert the star field into a spherical point cloud
        point_cloud = create_spherical_point_cloud(num_points=150, radius=3)
        self.play(ReplacementTransform(star_field, point_cloud), run_time=3)

        # Show the Std Dev equation
        std_dev_eq = MathTex(r"\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2}", font_size=42)
        std_dev_eq.shift(3*UP + 4*LEFT)
        self.play(Write(std_dev_eq))

        # Create the transparent sphere with label mu at center
        sphere = Sphere(radius=3, resolution=(24,24))
        sphere.set_stroke(color=WHITE, width=1)
        sphere.set_fill(color=BLUE_E, opacity=0.1)
        mu_label = Tex(r"$\mu$", font_size=36, color=YELLOW).move_to([0,0,0])
        self.play(FadeIn(sphere), FadeIn(mu_label))
        self.wait(1)

        # Animate pulsation of the sphere
        self.play(sphere.animate.scale(1.1), run_time=1.5)
        self.play(sphere.animate.scale(1/1.1), run_time=1.5)

        # Rotate the sigma text around
        self.play(Rotate(std_dev_eq, angle=TAU, about_point=ORIGIN), run_time=3)

        # Collapse into a bright flash
        flash = Circle(radius=8, color=WHITE).set_fill(WHITE, opacity=1).move_to(ORIGIN)
        flash.set_stroke(width=0)
        self.play(
            FadeIn(flash, run_time=0.5),
            FadeOut(VGroup(point_cloud, sphere, mu_label, std_dev_eq), run_time=0.5),
        )
        self.play(FadeOut(flash), run_time=0.2)

        # ---------------------------------------
        # 3. Drift Into Brownian Motion
        # ---------------------------------------
        # Reveal 3D labyrinth of random paths
        random_paths = create_random_paths_3d(num_paths=8, path_length=6, step_size=0.2)
        self.play(LaggedStartMap(FadeIn, random_paths, lag_ratio=0.1), run_time=3)

        # Equation for Brownian motion
        bm_eq = MathTex(
            r"S_t = S_0 \, e^{\left(r - \tfrac{1}{2}\sigma^2\right)t + \sigma\,W_t}",
            font_size=42
        )
        bm_eq.to_edge(UP)
        self.play(Write(bm_eq))

        # Bright endpoints
        # We'll just highlight them by coloring the last segments
        for path_group in random_paths:
            if isinstance(path_group, VGroup):
                # color the last subsegment bright
                path_group[-1].set_color(YELLOW)

        self.wait(1)

        # Gravitational well swirl: we can scale down to center
        self.play(random_paths.animate.scale(0.5).shift(0.5*IN), run_time=2)

        # Swirling vortex effect (rotate everything)
        self.play(Rotate(random_paths, angle=TAU/2, axis=OUT), run_time=3)

        # Flash out
        self.play(FadeOut(bm_eq, random_paths), run_time=2)

        # ---------------------------------------
        # 4. Heat Equation: Melting Paths -> Surface
        # ---------------------------------------
        # Show swirling fluid
        heat_surface = create_heat_equation_surface(u_min=-4, u_max=4, resolution=30)
        self.play(Create(heat_surface), run_time=3)

        # Show the PDE
        heat_eq = MathTex(
            r"\frac{\partial f}{\partial t} = \frac{1}{2}\sigma^2 \frac{\partial^2 f}{\partial x^2}",
            font_size=42
        )
        heat_eq.to_edge(UP).set_color(YELLOW)
        self.play(Write(heat_eq))

        # Gentle oscillation (scale up and down or rotate)
        self.play(heat_surface.animate.scale(1.1), run_time=2)
        self.play(heat_surface.animate.scale(1/1.1), run_time=2)

        # Intensify wave in the center
        glow_sphere = Sphere(radius=0.5, resolution=(24,24))
        glow_sphere.set_fill(color=WHITE, opacity=0.7)
        glow_sphere.set_stroke(width=0)
        self.play(FadeIn(glow_sphere.scale(0.01), run_time=0.5))
        self.play(glow_sphere.animate.scale(50), run_time=1.5)
        self.play(
            FadeOut(glow_sphere),
            FadeOut(heat_surface),
            FadeOut(heat_eq),
            run_time=1
        )

        # ---------------------------------------
        # 5. Black-Scholes & Implied Vol Emergence
        # ---------------------------------------
        # Reveal 3D axes
        axes = ThreeDAxes(
            x_range=[0, 6, 1],
            y_range=[0, 3, 1],
            z_range=[0, 1.0, 0.1],
            x_length=6,
            y_length=3,
            z_length=2
        )
        axes_labels = VGroup(
            Tex(r"$S$").next_to(axes.x_axis.get_end(), DOWN),
            Tex(r"$t$").next_to(axes.y_axis.get_end(), LEFT),
            Tex(r"$C$ / $\sigma$").next_to(axes.z_axis.get_end(), OUT)
        )
        self.play(Create(axes), FadeIn(axes_labels), run_time=2)

        # Black Scholes PDE
        bs_pde = MathTex(
            r"\frac{\partial C}{\partial t} + \frac{1}{2} \sigma^2 S^2 \frac{\partial^2 C}{\partial S^2}"
            r" + rS \frac{\partial C}{\partial S} - rC = 0",
            font_size=36
        ).to_edge(UP).set_color(BLUE)
        self.play(Write(bs_pde))

        # Grow the initial surface
        # We'll just reuse the "heat" style but with different color to represent an initial price function
        # Then morph it into color-coded patches for implied vol
        initial_surface = Surface(
            lambda u, v: np.array([u, v, 0.3*np.exp(-(u-3)**2-(v-1.5)**2)]),
            u_range=[0,6],
            v_range=[0,3],
            resolution=(30,30),
            fill_opacity=0.6,
            checkerboard_colors=[TEAL_D, TEAL_E]
        )
        self.play(Create(initial_surface), run_time=3)

        # Morph into color-coded implied vol surface
        self.wait(1)
        self.play(Transform(initial_surface, initial_surface.copy().set_fill_by_value(
            axes=axes,
            colors=[(BLUE, 0), (RED, 0.5)]
        )), run_time=2)

        # Nebula swirl around
        swirl = Circle(radius=4, color=ORANGE).move_to(axes.get_center()).set_opacity(0.2)
        swirl.set_stroke(width=10)
        self.play(Rotate(swirl, angle=TAU, about_point=axes.get_center()), run_time=3)
        self.play(FadeOut(swirl), run_time=1)

        # ---------------------------------------
        # 6. Vol Surface & Skew Model Reveal
        # ---------------------------------------
        # Transform the surface to the "volatility smile" shape
        self.play(FadeOut(initial_surface), run_time=1)

        vol_surface = create_black_scholes_surface(u_min=1, u_max=5, v_min=0.5, v_max=2.5, resolution=30)
        vol_surface.set_fill_by_value(axes=axes, colors=[(BLUE, 0.2), (GREEN, 0.3), (YELLOW, 0.4), (RED, 0.5)])
        self.play(Create(vol_surface), run_time=3)

        # Implied Vol text
        implied_vol_text = Tex(r"Implied Volatility Surface: $\sigma(K, T)$", font_size=36).set_color(YELLOW)
        implied_vol_text.to_edge(UP)
        self.play(Write(implied_vol_text), run_time=2)

        # Orbit around the surface
        self.begin_ambient_camera_rotation(rate=0.1)  # slowly rotate camera
        self.wait(4)
        self.stop_ambient_camera_rotation()

        # ---------------------------------------
        # 7. Finale: Convergence of Concepts
        # ---------------------------------------
        # Pull camera back, ghostly overlays
        self.move_camera(phi=45*DEGREES, theta=60*DEGREES, distance=70, run_time=3)

        # Ghostly overlays: we just re-show key items at low opacity
        std_sphere_ghost = sphere.copy().set_opacity(0.05)
        brownian_ghost = random_paths.copy().set_opacity(0.05)
        heat_ghost = heat_surface.copy().set_opacity(0.05)

        # (In a real production you'd store these, but here let's just fake it)
        self.play(FadeIn(std_sphere_ghost), FadeIn(brownian_ghost), FadeIn(heat_ghost), run_time=2)

        # Final text
        final_text = Tex(r"Volatility Surface Visualization --- A Cosmic Journey Through Financial Mathematics",
                         font_size=36).set_color(YELLOW)
        final_text.to_edge(DOWN)
        self.play(Write(final_text))
        self.wait(3)

        # Final bright burst & fade
        burst = Circle(radius=10, color=WHITE).set_fill(WHITE, opacity=1).move_to(axes.get_center())
        burst.set_stroke(width=0)
        self.play(FadeIn(burst, run_time=0.5), FadeOut(VGroup(
            vol_surface, implied_vol_text, axes, axes_labels,
            bs_pde, std_sphere_ghost, brownian_ghost, heat_ghost, final_text
        ), run_time=0.5))
        self.play(FadeOut(burst), run_time=1)

        self.wait(1)
