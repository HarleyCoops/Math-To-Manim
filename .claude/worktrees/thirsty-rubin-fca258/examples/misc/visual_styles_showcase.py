"""
Manim 3D Visual Styles Showcase
================================

Demonstrates that Manim is NOT limited to black backgrounds and white text!
ALL scenes use ThreeDScene with 3D objects, camera movements, and lighting.

Features demonstrated:
- Custom background colors
- 3D geometric objects (spheres, tori, surfaces)
- Camera rotations and fly-throughs
- Gradient coloring on 3D objects
- Starfields and particle systems
- Mathematical surfaces (parametric, implicit)
- Custom lighting effects

Render with: manim -pqh visual_styles_showcase.py All3DStyles

Author: Math-To-Manim - Everything in glorious 3D!
"""

from manim import *
import numpy as np


# ==============================================================================
# STYLE 1: WARM SUNSET - 3D TORUS KNOT
# ==============================================================================

class SunsetTorus3D(ThreeDScene):
    """Warm sunset colors on a 3D torus knot with rotation."""
    
    def construct(self):
        self.camera.background_color = "#1a0a2e"  # Deep purple base
        
        # Set up 3D camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        
        # Create a torus
        torus = Torus(
            major_radius=2,
            minor_radius=0.6,
            resolution=(30, 30)
        )
        
        # Apply sunset gradient coloring
        torus.set_color_by_gradient("#ff6b6b", "#ffd93d", "#ff8c00", "#ff6b6b")
        torus.set_opacity(0.9)
        
        # Title
        title = Text(
            "Sunset Topology",
            font_size=56,
            weight=BOLD
        ).set_color_by_gradient("#ff6b6b", "#ffd93d", "#ff8c00")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Math label
        equation = MathTex(
            r"\mathbb{T}^2 = S^1 \times S^1",
            font_size=36
        ).set_color("#ffecd2")
        equation.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(equation)
        
        # Animate
        self.play(Write(title), run_time=1.5)
        self.play(Create(torus, run_time=3))
        self.play(Write(equation))
        
        # Rotate to show 3D structure
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.wait(1)


# ==============================================================================
# STYLE 2: OCEAN DEEP - 3D WAVE SURFACE
# ==============================================================================

class OceanWave3D(ThreeDScene):
    """Deep ocean blue with an animated 3D wave surface."""
    
    def construct(self):
        self.camera.background_color = "#001f3f"  # Deep navy
        
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES, zoom=0.7)
        
        # Create wave surface
        def wave_func(u, v):
            x = u
            y = v
            z = 0.3 * np.sin(2 * u) * np.cos(2 * v) + 0.2 * np.sin(3 * u + v)
            return np.array([x, y, z])
        
        wave_surface = Surface(
            wave_func,
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(40, 40)
        )
        wave_surface.set_color_by_gradient("#001f3f", "#0077b6", "#00b4d8", "#90e0ef")
        wave_surface.set_opacity(0.85)
        
        # Create "bubbles" as 3D spheres
        bubbles = VGroup()
        np.random.seed(42)
        for _ in range(30):
            x = np.random.uniform(-3, 3)
            y = np.random.uniform(-3, 3)
            z = np.random.uniform(-2, 0)
            r = np.random.uniform(0.05, 0.15)
            
            bubble = Sphere(radius=r, resolution=(8, 8))
            bubble.move_to([x, y, z])
            bubble.set_color("#80deea")
            bubble.set_opacity(0.5)
            bubbles.add(bubble)
        
        # Title
        title = Text(
            "Ocean Dynamics",
            font_size=56,
            weight=BOLD
        ).set_color_by_gradient("#80deea", "#00b4d8", "#0077b6")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Wave equation
        wave_eq = MathTex(
            r"\nabla^2 \psi = \frac{1}{c^2}\frac{\partial^2 \psi}{\partial t^2}",
            font_size=36
        ).set_color("#b2ebf2")
        wave_eq.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(wave_eq)
        
        # Animate
        self.play(Write(title))
        self.add(bubbles)
        self.play(Create(wave_surface, run_time=3))
        self.play(Write(wave_eq))
        
        # Bubble animation + camera rotation
        self.begin_ambient_camera_rotation(rate=0.15)
        self.play(
            *[b.animate.shift(UP * np.random.uniform(1, 3)) for b in bubbles],
            run_time=4
        )
        self.stop_ambient_camera_rotation()
        
        self.wait(1)


# ==============================================================================
# STYLE 3: NEON CYBERPUNK - 3D WIREFRAME POLYHEDRON
# ==============================================================================

class NeonPolyhedron3D(ThreeDScene):
    """Neon cyberpunk with rotating wireframe polyhedra."""
    
    def construct(self):
        self.camera.background_color = "#0d0221"  # Very dark purple
        
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES, zoom=0.7)
        
        # Create wireframe grid floor
        grid = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": "#ff00ff",
                "stroke_width": 1,
                "stroke_opacity": 0.3
            },
            axis_config={
                "stroke_color": "#00ffff",
                "stroke_opacity": 0.5
            }
        )
        grid.rotate(PI/2, axis=RIGHT)
        grid.shift(DOWN * 2)
        
        # Create glowing icosahedron
        icosa = Icosahedron(edge_length=2)
        icosa.set_color("#00ffff")
        icosa.set_stroke("#ff00ff", width=3)
        icosa.set_fill(opacity=0.2)
        
        # Create outer dodecahedron
        dodeca = Dodecahedron(edge_length=1.5)
        dodeca.set_color("#ff00ff")
        dodeca.set_stroke("#00ffff", width=2)
        dodeca.set_fill(opacity=0.1)
        dodeca.scale(1.8)
        
        # Title with glow effect
        title = Text(
            "CYBERHEDRA",
            font_size=64,
            weight=BOLD
        ).set_color_by_gradient("#ff00ff", "#00ffff")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Euler's polyhedron formula
        euler = MathTex(
            r"V - E + F = 2",
            font_size=42
        ).set_color("#00ffff")
        euler.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(euler)
        
        # Animate
        self.add(grid)
        self.play(Write(title))
        self.play(
            Create(icosa, run_time=2),
            Create(dodeca, run_time=2)
        )
        self.play(Write(euler))
        
        # Counter-rotating polyhedra
        self.play(
            Rotate(icosa, angle=TAU, axis=UP, run_time=4),
            Rotate(dodeca, angle=-TAU, axis=UP + RIGHT, run_time=4),
            rate_func=linear
        )
        
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(3)
        self.stop_ambient_camera_rotation()


# ==============================================================================
# STYLE 4: MINIMALIST WHITE - 3D MOBIUS STRIP
# ==============================================================================

class MinimalistMobius3D(ThreeDScene):
    """Clean white background with elegant Mobius strip."""
    
    def construct(self):
        self.camera.background_color = WHITE
        
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        
        # Create Mobius strip parametric surface
        def mobius_func(u, v):
            # u goes around the strip, v is width
            x = (1 + v/2 * np.cos(u/2)) * np.cos(u)
            y = (1 + v/2 * np.cos(u/2)) * np.sin(u)
            z = v/2 * np.sin(u/2)
            return np.array([x, y, z])
        
        mobius = Surface(
            mobius_func,
            u_range=[0, TAU],
            v_range=[-0.5, 0.5],
            resolution=(50, 10)
        )
        mobius.set_color_by_gradient("#3498db", "#2c3e50", "#34495e")
        mobius.set_opacity(0.9)
        mobius.scale(1.5)
        
        # Edge curve for emphasis
        edge_points = []
        for u in np.linspace(0, TAU, 100):
            v = 0.5
            x = (1 + v/2 * np.cos(u/2)) * np.cos(u)
            y = (1 + v/2 * np.cos(u/2)) * np.sin(u)
            z = v/2 * np.sin(u/2)
            edge_points.append([x * 1.5, y * 1.5, z * 1.5])
        
        edge = VMobject()
        edge.set_points_smoothly(edge_points)
        edge.set_stroke("#e74c3c", width=4)
        
        # Title
        title = Text(
            "Elegant Topology",
            font_size=56,
            color="#2c3e50",
            weight=LIGHT
        )
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Mathematical notation
        notation = MathTex(
            r"\chi(\mathcal{M}) = 0",
            font_size=36,
            color="#34495e"
        )
        notation.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(notation)
        
        # Animate
        self.play(Write(title))
        self.play(Create(mobius, run_time=4))
        self.play(Create(edge, run_time=2))
        self.play(Write(notation))
        
        # Gentle rotation
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(5)
        self.stop_ambient_camera_rotation()


# ==============================================================================
# STYLE 5: FOREST NATURE - 3D GOLDEN SPIRAL SHELL
# ==============================================================================

class ForestSpiral3D(ThreeDScene):
    """Nature-inspired with 3D golden spiral shell."""
    
    def construct(self):
        self.camera.background_color = "#1a2f1a"  # Dark forest green
        
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES, zoom=0.7)
        
        # Create 3D golden spiral shell (nautilus-like)
        def spiral_shell(u, v):
            # Golden ratio-based spiral
            phi_gr = (1 + np.sqrt(5)) / 2
            r = np.exp(0.2 * u)
            
            x = r * np.cos(u) * (1 + 0.3 * np.cos(v))
            y = r * np.sin(u) * (1 + 0.3 * np.cos(v))
            z = r * 0.3 * np.sin(v) + u * 0.15
            return np.array([x, y, z]) * 0.4
        
        shell = Surface(
            spiral_shell,
            u_range=[0, 4 * PI],
            v_range=[0, TAU],
            resolution=(60, 20)
        )
        shell.set_color_by_gradient("#8bc34a", "#4caf50", "#2e7d32", "#1b5e20")
        shell.set_opacity(0.9)
        
        # Floating "leaves" (small green spheres)
        leaves = VGroup()
        np.random.seed(123)
        for _ in range(25):
            x = np.random.uniform(-4, 4)
            y = np.random.uniform(-4, 4)
            z = np.random.uniform(-2, 3)
            r = np.random.uniform(0.08, 0.2)
            
            leaf = Sphere(radius=r, resolution=(6, 6))
            leaf.move_to([x, y, z])
            color = np.random.choice(["#8bc34a", "#4caf50", "#81c784"])
            leaf.set_color(color)
            leaf.set_opacity(np.random.uniform(0.3, 0.6))
            leaves.add(leaf)
        
        # Title
        title = Text(
            "Nature's Mathematics",
            font_size=56,
            weight=BOLD
        ).set_color_by_gradient("#8bc34a", "#4caf50", "#2e7d32")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Golden ratio
        phi_eq = MathTex(
            r"\phi = \frac{1 + \sqrt{5}}{2}",
            font_size=42
        ).set_color("#a5d6a7")
        phi_eq.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(phi_eq)
        
        # Animate
        self.add(leaves)
        self.play(Write(title))
        self.play(Create(shell, run_time=5))
        self.play(Write(phi_eq))
        
        # Rotation
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(5)
        self.stop_ambient_camera_rotation()


# ==============================================================================
# STYLE 6: COSMIC SPACE - 3D GRAVITATIONAL WELL
# ==============================================================================

class CosmicGravity3D(ThreeDScene):
    """Deep space with 3D gravitational well visualization."""
    
    def construct(self):
        self.camera.background_color = "#050510"  # Very dark blue-black
        
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.6)
        
        # Create starfield
        stars = VGroup()
        np.random.seed(77)
        for _ in range(200):
            theta = np.random.uniform(0, TAU)
            phi = np.random.uniform(0, PI)
            r = np.random.uniform(8, 15)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            star_r = np.random.uniform(0.02, 0.06)
            star = Dot3D(point=[x, y, z], radius=star_r, color=WHITE)
            star.set_opacity(np.random.uniform(0.3, 1.0))
            stars.add(star)
        
        # Create gravitational well (curved spacetime)
        def gravity_well(u, v):
            r = np.sqrt(u**2 + v**2) + 0.01
            z = -2 / (r + 0.5) + 0.5
            return np.array([u, v, z])
        
        spacetime = Surface(
            gravity_well,
            u_range=[-4, 4],
            v_range=[-4, 4],
            resolution=(40, 40)
        )
        spacetime.set_color_by_gradient("#4a148c", "#7b1fa2", "#9c27b0", "#e040fb")
        spacetime.set_opacity(0.7)
        
        # Central "black hole" sphere
        black_hole = Sphere(radius=0.3, resolution=(20, 20))
        black_hole.move_to([0, 0, -2.5])
        black_hole.set_color("#000000")
        black_hole.set_opacity(1)
        
        # Accretion ring
        ring = Torus(major_radius=0.8, minor_radius=0.1)
        ring.move_to([0, 0, -1.5])
        ring.rotate(PI/6, axis=RIGHT)
        ring.set_color_by_gradient("#ff6f00", "#ff8f00", "#ffa000")
        ring.set_opacity(0.8)
        
        # Title
        title = Text(
            "SPACETIME CURVATURE",
            font_size=56,
            weight=BOLD
        ).set_color_by_gradient("#e040fb", "#7c4dff", "#448aff")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        # Einstein equation
        einstein = MathTex(
            r"G_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}",
            font_size=36
        ).set_color_by_gradient("#ce93d8", "#b39ddb")
        einstein.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(einstein)
        
        # Animate
        self.add(stars)
        self.play(Write(title))
        self.play(
            Create(spacetime, run_time=4),
            FadeIn(black_hole),
            Create(ring, run_time=2)
        )
        self.play(Write(einstein))
        
        # Cosmic rotation
        self.begin_ambient_camera_rotation(rate=0.1)
        self.play(
            Rotate(ring, angle=TAU, axis=OUT, run_time=5),
            rate_func=linear
        )
        self.stop_ambient_camera_rotation()
        
        self.wait(1)


# ==============================================================================
# COMBINED SHOWCASE - ALL STYLES
# ==============================================================================

class All3DStyles(ThreeDScene):
    """Quick showcase of all 3D visual styles."""
    
    def construct(self):
        self.camera.background_color = "#0a0a14"
        
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.6)
        
        # Create starfield background
        stars = VGroup()
        np.random.seed(99)
        for _ in range(150):
            theta = np.random.uniform(0, TAU)
            phi = np.random.uniform(0, PI)
            r = np.random.uniform(10, 20)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            star = Dot3D(point=[x, y, z], radius=0.03, color=WHITE)
            star.set_opacity(np.random.uniform(0.3, 0.8))
            stars.add(star)
        
        self.add(stars)
        
        # Title
        title = Text(
            "3D Visual Styles",
            font_size=72,
            weight=BOLD
        ).set_color_by_gradient("#ff6b6b", "#ffd93d", "#4fc3f7", "#00ff88")
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        
        self.play(Write(title, run_time=2))
        
        # Style objects
        styles = [
            ("Sunset", Torus(major_radius=1, minor_radius=0.3), "#ff6b6b"),
            ("Ocean", Sphere(radius=0.8), "#00b4d8"),
            ("Cyber", Icosahedron(edge_length=1.2), "#00ffff"),
            ("Minimal", Cube(side_length=1.2), "#3498db"),
            ("Nature", Cone(base_radius=0.8, height=1.5), "#4caf50"),
            ("Cosmic", Dodecahedron(edge_length=0.8), "#9c27b0"),
        ]
        
        objects = VGroup()
        positions = [
            [-3, 1, 0], [0, 1, 0], [3, 1, 0],
            [-3, -1.5, 0], [0, -1.5, 0], [3, -1.5, 0]
        ]
        
        for i, (name, obj, color) in enumerate(styles):
            obj.set_color(color)
            obj.set_opacity(0.9)
            obj.move_to(positions[i])
            obj.scale(0.7)
            objects.add(obj)
        
        # Animate objects appearing
        self.play(
            *[Create(obj, run_time=1.5) for obj in objects],
            lag_ratio=0.2
        )
        
        # Labels
        labels = VGroup()
        for i, (name, _, color) in enumerate(styles):
            label = Text(name, font_size=24, color=color)
            label.move_to(positions[i])
            label.shift(DOWN * 1)
            labels.add(label)
        
        self.add_fixed_in_frame_mobjects(*labels)
        self.play(*[FadeIn(l) for l in labels])
        
        # Rotate all objects
        self.begin_ambient_camera_rotation(rate=0.15)
        self.play(
            *[Rotate(obj, angle=TAU, axis=UP, run_time=5) for obj in objects],
            rate_func=linear
        )
        self.stop_ambient_camera_rotation()
        
        # Final message
        self.play(
            FadeOut(objects),
            *[FadeOut(l) for l in labels]
        )
        
        message = Text(
            "Everything in 3D!",
            font_size=64,
            weight=BOLD
        ).set_color_by_gradient("#ff6b6b", "#00ffff", "#00ff88")
        message.to_edge(DOWN, buff=1)
        self.add_fixed_in_frame_mobjects(message)
        self.play(Write(message))
        
        self.wait(2)


if __name__ == "__main__":
    scene = All3DStyles()
    scene.render()
