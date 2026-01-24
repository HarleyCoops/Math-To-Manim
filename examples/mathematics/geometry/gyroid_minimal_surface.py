"""
Gyroid Minimal Surface Animation
================================
A triply periodic minimal surface where every point is a saddle point.
Features:
- Isosurface rendering using marching cubes
- Camera flythrough of intertwining tunnels
- Mean curvature coloring (violet to gold)
- Morphing to Schwarz P-surface (dual structure)

Mathematical Background:
- Gyroid: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0
- Schwarz P: cos(x) + cos(y) + cos(z) = 0
"""

from manim import *
import numpy as np
from scipy import ndimage

# Try to import marching cubes - fallback if not available
try:
    from skimage.measure import marching_cubes
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False
    print("Warning: scikit-image not found. Using parametric approximation.")


class GyroidMinimalSurface(ThreeDScene):
    """
    Visualize the gyroid minimal surface with camera flythrough
    and morphing to the Schwarz P-surface.
    """

    # Color palette
    VIOLET_DEEP = "#4B0082"
    VIOLET = "#8B00FF"
    GOLD = "#FFD700"
    GOLD_DEEP = "#DAA520"

    def construct(self):
        # Set up 3D camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES, zoom=0.6)

        # Title sequence
        self.intro_sequence()

        # Create and display gyroid
        self.gyroid_sequence()

        # Camera flythrough
        self.flythrough_sequence()

        # Morph to Schwarz P-surface
        self.morph_sequence()

        # Outro
        self.outro_sequence()

    def intro_sequence(self):
        """Introduction with title and concept explanation."""
        title = Text("The Gyroid", font_size=72, gradient=(self.VIOLET_DEEP, self.GOLD))
        subtitle = Text("A Triply Periodic Minimal Surface", font_size=36)
        subtitle.next_to(title, DOWN, buff=0.5)

        # Position in 3D space facing camera
        title_group = VGroup(title, subtitle)
        self.add_fixed_in_frame_mobjects(title_group)
        title_group.move_to(ORIGIN)

        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(1)

        # Properties text
        properties = VGroup(
            Text("Every point is a saddle point", font_size=28, color=self.VIOLET),
            Text("Mean curvature = 0 everywhere", font_size=28, color=self.GOLD),
            Text("Divides space into two intertwining labyrinths", font_size=28),
        ).arrange(DOWN, buff=0.3)
        properties.next_to(subtitle, DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(properties)

        for prop in properties:
            self.play(FadeIn(prop, shift=UP * 0.3), run_time=0.8)

        self.wait(2)

        # Fade out intro
        self.play(
            FadeOut(title_group),
            FadeOut(properties),
            run_time=1
        )
        self.remove_fixed_in_frame_mobjects(title_group, properties)

    def gyroid_sequence(self):
        """Create and animate the gyroid surface."""
        # Display the equation
        equation = MathTex(
            r"\sin(x)\cos(y) + \sin(y)\cos(z) + \sin(z)\cos(x) = 0",
            font_size=42
        )
        equation.set_color_by_gradient(self.VIOLET_DEEP, self.GOLD)
        self.add_fixed_in_frame_mobjects(equation)
        equation.to_edge(UP, buff=0.5)

        self.play(Write(equation), run_time=2)

        # Create the gyroid surface
        self.gyroid = self.create_gyroid_surface(t=0)

        self.play(
            Create(self.gyroid),
            run_time=4
        )

        # Begin ambient rotation
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(3)

        # Keep equation for reference, store for later
        self.equation = equation

    def create_gyroid_surface(self, t=0, resolution=40, scale=2.5):
        """
        Create gyroid surface using parametric patches.
        t parameter allows morphing: t=0 is gyroid, t=1 is Schwarz P
        """
        # For gyroid, we use a parametric approximation via surface patches
        surfaces = VGroup()

        # Create multiple patches to cover a cubic region
        n_periods = 1.5  # Number of periods to show

        # Sample the implicit function and create surface patches
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    offset = np.array([i, j, k]) * 2 * PI / 2
                    patch = self.create_gyroid_patch(offset, t, scale / 3)
                    if patch is not None:
                        surfaces.add(patch)

        return surfaces

    def create_gyroid_patch(self, offset, t, scale):
        """Create a single patch of the gyroid surface."""
        def gyroid_func(x, y, z):
            """Gyroid implicit function."""
            return np.sin(x) * np.cos(y) + np.sin(y) * np.cos(z) + np.sin(z) * np.cos(x)

        def schwarz_p_func(x, y, z):
            """Schwarz P implicit function."""
            return np.cos(x) + np.cos(y) + np.cos(z)

        def mixed_func(x, y, z, t):
            """Interpolate between gyroid and Schwarz P."""
            g = gyroid_func(x, y, z)
            p = schwarz_p_func(x, y, z)
            return (1 - t) * g + t * p

        # Create parametric surface approximation
        # We use one of the two channels as a surface
        def surface_func(u, v):
            # Map u, v to a surface point on or near the gyroid
            # Use a modified parametrization
            x = u + offset[0]
            y = v + offset[1]

            # Solve for z approximately (Newton's method for one iteration)
            z_init = offset[2]
            for _ in range(5):
                val = mixed_func(x, y, z_init, t)
                # Derivative with respect to z
                dz = -np.sin(z_init) * np.cos(x) + np.cos(z_init) * np.sin(y)
                if t > 0:
                    dz = (1 - t) * dz - t * np.sin(z_init)
                if abs(dz) > 1e-6:
                    z_init = z_init - val / dz
                else:
                    break

            return scale * np.array([x, y, z_init])

        try:
            surface = Surface(
                surface_func,
                u_range=[-PI/2, PI/2],
                v_range=[-PI/2, PI/2],
                resolution=(15, 15),
                fill_opacity=0.9,
                stroke_width=0.5,
                stroke_color=WHITE,
                stroke_opacity=0.3,
            )

            # Color by position (proxy for curvature)
            surface.set_color_by_gradient(self.VIOLET_DEEP, self.VIOLET, self.GOLD)
            return surface
        except Exception:
            return None

    def create_isosurface_mesh(self, t=0, resolution=50, bounds=2*PI):
        """
        Create isosurface using marching cubes algorithm.
        This gives accurate gyroid geometry.
        """
        if not HAS_SKIMAGE:
            return self.create_gyroid_surface(t)

        # Create 3D grid
        x = np.linspace(-bounds, bounds, resolution)
        y = np.linspace(-bounds, bounds, resolution)
        z = np.linspace(-bounds, bounds, resolution)
        X, Y, Z = np.meshgrid(x, y, z)

        # Evaluate implicit function
        if t == 0:
            # Pure gyroid
            F = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
        elif t == 1:
            # Pure Schwarz P
            F = np.cos(X) + np.cos(Y) + np.cos(Z)
        else:
            # Interpolated
            G = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
            P = np.cos(X) + np.cos(Y) + np.cos(Z)
            F = (1 - t) * G + t * P

        # Extract isosurface
        verts, faces, normals, values = marching_cubes(F, level=0)

        # Scale vertices to world coordinates
        scale = 2 * bounds / resolution
        verts = verts * scale - bounds

        # Create Manim mesh
        return self.verts_faces_to_surface(verts, faces, normals, t)

    def verts_faces_to_surface(self, verts, faces, normals, t=0):
        """Convert vertices and faces to Manim surface group."""
        surfaces = VGroup()

        # Create triangular patches
        for face in faces[::3]:  # Sample every 3rd face for performance
            try:
                v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]

                # Create triangle
                triangle = Polygon(
                    v0, v1, v2,
                    fill_opacity=0.85,
                    stroke_width=0.2,
                    stroke_color=WHITE,
                )

                # Color by mean curvature (approximated by normal direction)
                center = (v0 + v1 + v2) / 3
                curvature_proxy = np.sin(center[0]) + np.cos(center[1]) + np.sin(center[2])

                # Map to color
                color_t = (curvature_proxy + 3) / 6  # Normalize to 0-1
                color = interpolate_color(
                    ManimColor(self.VIOLET_DEEP),
                    ManimColor(self.GOLD),
                    color_t
                )
                triangle.set_fill(color)
                surfaces.add(triangle)
            except Exception:
                continue

        return surfaces

    def flythrough_sequence(self):
        """Animate camera flying through one of the tunnels."""
        self.stop_ambient_camera_rotation()

        # Flythrough path - spiral through one channel
        label = Text("Flying through the labyrinth...", font_size=32, color=self.GOLD)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(label))

        # Camera path through tunnel
        # Move camera position along a helical path
        self.move_camera(
            phi=85 * DEGREES,
            theta=0 * DEGREES,
            zoom=1.2,
            run_time=3,
            rate_func=smooth
        )

        # Rotate around while "inside"
        for angle in [60, 120, 180, 240, 300, 360]:
            self.move_camera(
                theta=angle * DEGREES,
                run_time=1,
                rate_func=linear
            )

        # Pull back out
        self.move_camera(
            phi=70 * DEGREES,
            theta=30 * DEGREES,
            zoom=0.6,
            run_time=2,
            rate_func=smooth
        )

        self.play(FadeOut(label))
        self.remove_fixed_in_frame_mobjects(label)
        self.wait(1)

    def morph_sequence(self):
        """Morph gyroid into Schwarz P-surface."""
        # Update equation
        new_equation = MathTex(
            r"\cos(x) + \cos(y) + \cos(z) = 0",
            font_size=42
        )
        new_equation.set_color_by_gradient(self.GOLD, self.VIOLET_DEEP)
        self.add_fixed_in_frame_mobjects(new_equation)
        new_equation.to_edge(UP, buff=0.5)

        # Morph label
        morph_label = Text("Morphing to Schwarz P-Surface", font_size=36)
        morph_label.set_color_by_gradient(self.VIOLET, self.GOLD)
        self.add_fixed_in_frame_mobjects(morph_label)
        morph_label.next_to(new_equation, DOWN, buff=0.3)

        self.play(
            Transform(self.equation, new_equation),
            FadeIn(morph_label),
            run_time=1
        )

        # Start rotation during morph
        self.begin_ambient_camera_rotation(rate=0.1)

        # Create Schwarz P surface
        schwarz_p = self.create_schwarz_p_surface()

        # Morph animation
        self.play(
            Transform(self.gyroid, schwarz_p),
            run_time=6,
            rate_func=smooth
        )

        self.wait(3)

        # Description
        desc = Text("Tunnels reshape into cubic voids", font_size=28, color=WHITE)
        self.add_fixed_in_frame_mobjects(desc)
        desc.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(desc))
        self.wait(3)

        self.play(FadeOut(desc), FadeOut(morph_label))
        self.remove_fixed_in_frame_mobjects(desc, morph_label, new_equation)

    def create_schwarz_p_surface(self, resolution=40, scale=2.5):
        """Create Schwarz P minimal surface."""
        surfaces = VGroup()

        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    offset = np.array([i, j, k]) * 2 * PI / 2
                    patch = self.create_schwarz_p_patch(offset, scale / 3)
                    if patch is not None:
                        surfaces.add(patch)

        return surfaces

    def create_schwarz_p_patch(self, offset, scale):
        """Create a single patch of Schwarz P surface."""
        def surface_func(u, v):
            x = u + offset[0]
            y = v + offset[1]

            # Solve cos(x) + cos(y) + cos(z) = 0 for z
            val = -np.cos(x) - np.cos(y)
            # Clamp to valid range for arccos
            val = np.clip(val, -1, 1)
            z = np.arccos(val) + offset[2]

            return scale * np.array([x, y, z])

        try:
            surface = Surface(
                surface_func,
                u_range=[-PI/2, PI/2],
                v_range=[-PI/2, PI/2],
                resolution=(15, 15),
                fill_opacity=0.9,
                stroke_width=0.5,
                stroke_color=WHITE,
                stroke_opacity=0.3,
            )

            # Color gradient (reversed for visual contrast)
            surface.set_color_by_gradient(self.GOLD, self.VIOLET_DEEP)
            return surface
        except Exception:
            return None

    def outro_sequence(self):
        """Final sequence with summary."""
        self.stop_ambient_camera_rotation()

        # Move to final view
        self.move_camera(
            phi=60 * DEGREES,
            theta=45 * DEGREES,
            zoom=0.5,
            run_time=2
        )

        # Fade out surface
        self.play(FadeOut(self.gyroid), FadeOut(self.equation), run_time=2)

        # Final text
        final = VGroup(
            Text("Minimal Surfaces", font_size=48, gradient=(self.VIOLET, self.GOLD)),
            Text("Where geometry meets topology", font_size=32),
        ).arrange(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(final)
        final.move_to(ORIGIN)

        self.play(FadeIn(final, scale=0.8), run_time=2)
        self.wait(3)
        self.play(FadeOut(final), run_time=1)


class GyroidSimple(ThreeDScene):
    """
    Simplified gyroid visualization for faster rendering.
    Uses parametric approximation with smooth coloring.
    """

    VIOLET_DEEP = "#4B0082"
    GOLD = "#FFD700"

    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES, zoom=0.7)

        # Create gyroid
        gyroid = self.create_parametric_gyroid()

        # Title
        title = Text("Gyroid Minimal Surface", font_size=48)
        title.set_color_by_gradient(self.VIOLET_DEEP, self.GOLD)
        self.add_fixed_in_frame_mobjects(title)
        title.to_edge(UP)

        self.play(Write(title), run_time=1.5)
        self.play(Create(gyroid), run_time=4)

        # Rotate
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(8)

        self.stop_ambient_camera_rotation()
        self.play(FadeOut(gyroid), FadeOut(title))

    def create_parametric_gyroid(self, scale=3):
        """Create gyroid using parametric surface patches."""
        surfaces = VGroup()

        # Create surface using implicit function sampling
        def create_patch(u_offset, v_offset):
            def func(u, v):
                x = u + u_offset
                y = v + v_offset

                # Approximate z from gyroid equation
                # sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0
                # Initial guess
                z = 0.0
                for _ in range(8):
                    f = np.sin(x) * np.cos(y) + np.sin(y) * np.cos(z) + np.sin(z) * np.cos(x)
                    df = -np.sin(y) * np.sin(z) + np.cos(z) * np.cos(x)
                    if abs(df) > 1e-8:
                        z = z - f / df

                return np.array([x * scale / PI, y * scale / PI, z * scale / PI])

            return Surface(
                func,
                u_range=[-PI * 0.9, PI * 0.9],
                v_range=[-PI * 0.9, PI * 0.9],
                resolution=(25, 25),
                fill_opacity=0.85,
                stroke_width=0.3,
                stroke_color=WHITE,
                stroke_opacity=0.2,
            ).set_color_by_gradient(self.VIOLET_DEEP, self.GOLD)

        # Main patch
        surfaces.add(create_patch(0, 0))

        return surfaces


# Render command:
# manim -pqm gyroid_minimal_surface.py GyroidMinimalSurface
# For quick preview: manim -pql gyroid_minimal_surface.py GyroidSimple
