"""
Black Hole Symphony: A Gravitational Ballet in Curved Spacetime
===============================================================

A spectacular 3D visualization of a Kerr (rotating) black hole featuring:
- Event horizon and ergosphere geometry
- Accretion disk with thousands of spiraling particles
- Gravitational lensing (Einstein ring effect)
- Relativistic jets from polar regions
- Spacetime curvature grid deformation
- Hawking radiation particle pairs
- Mathematical overlays (Schwarzschild/Kerr metrics)

Render with:
    manim -pqh black_hole_symphony.py BlackHoleSymphony

For 4K quality:
    manim -pqk black_hole_symphony.py BlackHoleSymphony

Author: Generated with Claude Opus 4 for Math-To-Manim
"""

from __future__ import annotations
from manim import *
import numpy as np
from random import uniform, seed, choice
from math import sin, cos, pi, sqrt, exp, atan2

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

# Physical Constants (scaled for visualization)
SCHWARZSCHILD_RADIUS = 1.0  # Event horizon radius
ERGOSPHERE_FACTOR = 1.5     # Ergosphere extends to 1.5 * r_s at equator
PHOTON_SPHERE = 1.5 * SCHWARZSCHILD_RADIUS  # Where light orbits
ISCO_RADIUS = 3.0 * SCHWARZSCHILD_RADIUS    # Innermost stable circular orbit

# Visual Constants
STAR_COUNT = 3000
STAR_SCATTER_RADIUS = 80
DISK_PARTICLE_COUNT = 800
JET_PARTICLE_COUNT = 200

# Color Palette - Cosmic Theme
VOID_BLACK = "#000000"
EVENT_HORIZON_COLOR = "#0a0a0a"
ERGOSPHERE_COLOR = "#1a0a2e"
DISK_INNER_COLOR = "#ff6b35"      # Hot orange-red
DISK_MIDDLE_COLOR = "#f7c59f"     # Golden yellow
DISK_OUTER_COLOR = "#2ec4b6"      # Cool teal
JET_COLOR = "#e0aaff"             # Violet plasma
LENSING_COLOR = "#48cae4"         # Bright cyan
HAWKING_PARTICLE_COLOR = "#ff006e"
HAWKING_ANTIPARTICLE_COLOR = "#3a86ff"
GRID_COLOR = BLUE_E
EQUATION_COLOR = WHITE


# ==============================================================================
# HELPER CLASSES
# ==============================================================================

class AccretionParticle:
    """A particle orbiting in the accretion disk with relativistic effects."""

    def __init__(self, radius: float, initial_angle: float,
                 vertical_scatter: float = 0.1, clockwise: bool = True):
        self.radius = radius
        self.angle = initial_angle
        self.z_offset = uniform(-vertical_scatter, vertical_scatter)
        self.clockwise = clockwise

        # Kepler's third law with relativistic correction near ISCO
        # Angular velocity decreases with radius, increases near black hole
        base_omega = 1.0 / (radius ** 1.5)
        relativistic_factor = 1.0 + 0.5 * (ISCO_RADIUS / max(radius, ISCO_RADIUS)) ** 2
        self.angular_velocity = base_omega * relativistic_factor
        if not clockwise:
            self.angular_velocity *= -1

        # Color based on temperature (hotter closer to center)
        self.color = self._compute_color(radius)

        # Brightness variation
        self.brightness = uniform(0.6, 1.0)

        # Create the visual representation
        self.dot = Dot3D(
            point=self._get_position(),
            radius=0.015 + 0.01 * (ISCO_RADIUS / radius),
            color=self.color
        )
        self.dot.set_opacity(self.brightness)

    def _compute_color(self, r: float) -> str:
        """Temperature-based color: hotter (white-blue) near center, cooler (red) at edge."""
        # Normalize radius
        t = (r - ISCO_RADIUS) / (8 * SCHWARZSCHILD_RADIUS - ISCO_RADIUS)
        t = np.clip(t, 0, 1)

        if t < 0.3:
            return interpolate_color(WHITE, DISK_INNER_COLOR, t / 0.3)
        elif t < 0.6:
            return interpolate_color(DISK_INNER_COLOR, DISK_MIDDLE_COLOR, (t - 0.3) / 0.3)
        else:
            return interpolate_color(DISK_MIDDLE_COLOR, DISK_OUTER_COLOR, (t - 0.6) / 0.4)

    def _get_position(self) -> np.ndarray:
        """Calculate 3D position from orbital parameters."""
        x = self.radius * cos(self.angle)
        y = self.radius * sin(self.angle)
        # Add slight wobble for realism
        z = self.z_offset * (1 + 0.2 * sin(3 * self.angle))
        return np.array([x, y, z])

    def update(self, dt: float):
        """Advance particle along its orbit."""
        self.angle += self.angular_velocity * dt
        self.dot.move_to(self._get_position())


class JetParticle:
    """A particle in a relativistic jet, moving along magnetic field lines."""

    def __init__(self, is_north: bool = True, initial_progress: float = 0.0):
        self.is_north = is_north
        self.progress = initial_progress  # 0 to 1 along jet
        self.radial_offset = uniform(0, 0.3)
        self.twist_angle = uniform(0, TAU)
        self.speed = uniform(0.3, 0.6)  # Relativistic but varied

        # Visual
        self.dot = Dot3D(
            point=self._get_position(),
            radius=0.02,
            color=JET_COLOR
        )
        self.dot.set_opacity(uniform(0.5, 0.9))

    def _get_position(self) -> np.ndarray:
        """Helical path along the jet axis."""
        z_sign = 1 if self.is_north else -1
        z = z_sign * (0.5 + self.progress * 8)  # Jets extend far

        # Jet widens as it goes
        jet_radius = 0.2 + self.progress * 1.5

        # Helical motion
        twist = self.twist_angle + self.progress * 4 * PI
        x = jet_radius * self.radial_offset * cos(twist)
        y = jet_radius * self.radial_offset * sin(twist)

        return np.array([x, y, z])

    def update(self, dt: float):
        """Move particle along jet."""
        self.progress += self.speed * dt * 0.1
        if self.progress > 1:
            self.progress = 0  # Reset at base
            self.twist_angle = uniform(0, TAU)
        self.dot.move_to(self._get_position())
        # Fade as particle moves away
        opacity = max(0.1, 0.9 - 0.8 * self.progress)
        self.dot.set_opacity(opacity)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def make_deep_starfield(n: int = STAR_COUNT, radius: float = STAR_SCATTER_RADIUS) -> VGroup:
    """Create a 3D starfield with depth variation and different star types."""
    seed(42)
    stars = VGroup()

    for i in range(n):
        # Spherical distribution
        theta = uniform(0, TAU)
        phi = uniform(0, PI)
        r = uniform(radius * 0.3, radius)

        x = r * sin(phi) * cos(theta)
        y = r * sin(phi) * sin(theta)
        z = r * cos(phi)

        # Star properties based on "distance"
        distance_factor = r / radius
        base_radius = 0.01 + 0.04 * (1 - distance_factor)

        # Different star colors (blue giants, yellow dwarfs, red giants)
        star_colors = [WHITE, BLUE_A, YELLOW_A, ORANGE, RED_A]
        color = choice(star_colors) if uniform(0, 1) > 0.8 else WHITE

        dot = Dot3D(
            point=[x, y, z],
            radius=base_radius * uniform(0.5, 1.5),
            color=color
        )
        dot.set_opacity(uniform(0.3, 1.0) * (1 - distance_factor * 0.5))
        stars.add(dot)

    return stars


def create_event_horizon() -> VGroup:
    """Create the black hole's event horizon as a perfect black sphere."""
    horizon = Sphere(
        radius=SCHWARZSCHILD_RADIUS,
        resolution=(32, 32)
    )
    horizon.set_color(EVENT_HORIZON_COLOR)
    horizon.set_opacity(1.0)
    horizon.set_shade_in_3d(True)

    # Add subtle glow rim
    glow = Sphere(
        radius=SCHWARZSCHILD_RADIUS * 1.02,
        resolution=(16, 16)
    )
    glow.set_color(LENSING_COLOR)
    glow.set_opacity(0.1)

    return VGroup(horizon, glow)


def create_ergosphere() -> Surface:
    """Create the ergosphere - the region where spacetime is dragged."""
    def ergosphere_func(u, v):
        # Ergosphere radius varies with latitude (polar angle)
        # r_ergo = r_s * (1 + sqrt(1 - a^2 * cos^2(theta))) for Kerr
        # Simplified: larger at equator, touches horizon at poles
        theta = v  # polar angle
        phi = u    # azimuthal angle

        # Ergosphere shape
        equatorial_factor = abs(sin(theta))
        r = SCHWARZSCHILD_RADIUS * (1 + 0.5 * equatorial_factor)

        x = r * sin(theta) * cos(phi)
        y = r * sin(theta) * sin(phi)
        z = r * cos(theta)

        return np.array([x, y, z])

    ergosphere = Surface(
        ergosphere_func,
        u_range=[0, TAU],
        v_range=[0, PI],
        resolution=(32, 32),
        fill_color=ERGOSPHERE_COLOR,
        fill_opacity=0.15,
        stroke_color=PURPLE_A,
        stroke_width=0.5,
        stroke_opacity=0.3
    )
    ergosphere.set_shade_in_3d(True)

    return ergosphere


def create_photon_sphere() -> VMobject:
    """Create the photon sphere where light orbits the black hole."""
    # Draw as a thin ring at the equator to indicate the photon sphere
    photon_ring = ParametricFunction(
        lambda t: np.array([
            PHOTON_SPHERE * cos(t),
            PHOTON_SPHERE * sin(t),
            0
        ]),
        t_range=[0, TAU],
        color=YELLOW_A,
        stroke_width=2
    )
    photon_ring.set_opacity(0.6)

    return photon_ring


def create_spacetime_grid(time_val: float = 0) -> VGroup:
    """Create a 2D grid that shows spacetime curvature around the black hole."""
    grid_lines = VGroup()

    # Radial lines
    for angle in np.linspace(0, TAU, 24, endpoint=False):
        points = []
        for r in np.linspace(SCHWARZSCHILD_RADIUS * 1.5, 12, 50):
            # Gravitational time dilation factor
            dilation = sqrt(1 - SCHWARZSCHILD_RADIUS / r) if r > SCHWARZSCHILD_RADIUS else 0.1

            # Warp the z-coordinate based on distance (gravitational well)
            z_warp = -2 * SCHWARZSCHILD_RADIUS / max(r, SCHWARZSCHILD_RADIUS * 1.1)

            x = r * cos(angle)
            y = r * sin(angle)
            z = z_warp - 3  # Shift down

            points.append([x, y, z])

        line = VMobject()
        line.set_points_smoothly(points)
        line.set_stroke(GRID_COLOR, width=1, opacity=0.4)
        grid_lines.add(line)

    # Circular lines
    for r in np.linspace(2, 12, 8):
        points = []
        for angle in np.linspace(0, TAU, 64):
            z_warp = -2 * SCHWARZSCHILD_RADIUS / max(r, SCHWARZSCHILD_RADIUS * 1.1)

            x = r * cos(angle)
            y = r * sin(angle)
            z = z_warp - 3

            points.append([x, y, z])
        points.append(points[0])  # Close the loop

        circle = VMobject()
        circle.set_points_smoothly(points)
        circle.set_stroke(GRID_COLOR, width=1, opacity=0.3)
        grid_lines.add(circle)

    return grid_lines


def create_lensing_ring() -> VGroup:
    """Create the Einstein ring / gravitational lensing effect."""
    rings = VGroup()

    # Multiple concentric rings representing lensed light
    for i, r in enumerate([2.2, 2.5, 2.8]):
        ring = ParametricFunction(
            lambda t, r=r: np.array([
                r * cos(t),
                r * sin(t),
                0.1 * sin(4 * t)  # Slight wobble
            ]),
            t_range=[0, TAU],
            color=LENSING_COLOR,
            stroke_width=3 - i
        )
        ring.set_opacity(0.7 - i * 0.2)
        rings.add(ring)

    return rings


def create_accretion_disk_base() -> Surface:
    """Create the base accretion disk surface with color gradient."""
    def disk_func(u, v):
        # u: angle (0 to 2pi)
        # v: radius (ISCO to outer edge)
        r = v
        theta = u

        # Slight vertical structure (thicker at edge, thin at center)
        thickness = 0.05 * (r / 8) ** 0.5
        z = thickness * sin(theta * 3)  # Warps

        x = r * cos(theta)
        y = r * sin(theta)

        return np.array([x, y, z])

    disk = Surface(
        disk_func,
        u_range=[0, TAU],
        v_range=[ISCO_RADIUS, 8 * SCHWARZSCHILD_RADIUS],
        resolution=(64, 32)
    )

    # Radial color gradient
    disk.set_fill_by_value(
        axes=Axes(),
        colorscale=[
            (WHITE, 0),
            (DISK_INNER_COLOR, 0.2),
            (DISK_MIDDLE_COLOR, 0.5),
            (DISK_OUTER_COLOR, 1.0)
        ],
        axis=2  # Color by radial distance approximated by z calculation
    )
    disk.set_opacity(0.6)
    disk.set_shade_in_3d(True)

    return disk


# ==============================================================================
# MAIN SCENE
# ==============================================================================

class BlackHoleSymphony(ThreeDScene):
    """
    A spectacular visualization of a Kerr black hole with full relativistic effects.

    SCENE CONTROL PHILOSOPHY:
    - All objects exist within a defined 3D bounding volume: [-15, 15] in all axes
    - Camera is positioned far enough to see the entire scene
    - Zoom values are carefully calibrated (0.3-0.5 for wide views)
    - Camera distance of 25+ units ensures everything is visible
    """

    def construct(self):
        # =====================================================================
        # SCENE CONTROL: Define our 3D workspace
        # =====================================================================
        # The scene operates in a cubic volume:
        # - X: -15 to 15 (left/right)
        # - Y: -15 to 15 (front/back)
        # - Z: -10 to 10 (down/up)
        # - Black hole at origin
        # - Accretion disk in XY plane
        # - Jets along Z axis
        # - Spacetime grid at Z = -5

        SCENE_RADIUS = 15  # Maximum extent of objects from origin
        CAMERA_DISTANCE = 30  # Far enough to see everything

        # =====================================================================
        # PHASE 1: COSMIC AWAKENING - Starfield and Introduction
        # =====================================================================

        self.camera.background_color = VOID_BLACK

        # CRITICAL: Set camera far back with low zoom to see entire scene
        self.set_camera_orientation(
            phi=70 * DEGREES,      # Angle from Z axis (70° = looking slightly down)
            theta=-45 * DEGREES,   # Rotation around Z axis
            zoom=0.35,             # LOW zoom = wide field of view
            frame_center=ORIGIN    # Center on the black hole
        )

        # Create deep space starfield (stars are far away, in background)
        stars = make_deep_starfield()

        # Optional: Add 3D reference axes to show the space (can be removed for final render)
        # This helps verify camera positioning during development
        reference_axes = ThreeDAxes(
            x_range=[-SCENE_RADIUS, SCENE_RADIUS, 5],
            y_range=[-SCENE_RADIUS, SCENE_RADIUS, 5],
            z_range=[-10, 10, 5],
            x_length=SCENE_RADIUS * 2,
            y_length=SCENE_RADIUS * 2,
            z_length=20,
            tips=False,
        )
        reference_axes.set_stroke(opacity=0.15, width=1)

        # Fade in the cosmos
        self.play(FadeIn(stars, run_time=4))
        self.add(reference_axes)  # Add axes for reference (subtle)
        self.wait(1)

        # Title sequence
        title = Text(
            "Black Hole Symphony",
            font_size=72,
            weight=BOLD
        ).set_color_by_gradient(PURPLE_A, BLUE_A, TEAL_A)

        subtitle = Text(
            "A Gravitational Ballet in Curved Spacetime",
            font_size=36
        ).set_color_by_gradient(GRAY_A, WHITE)

        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        title_group.to_edge(UP, buff=1)

        self.add_fixed_in_frame_mobjects(title_group)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1.5)
        self.wait(2)

        # Shrink title to corner
        small_title = title.copy().scale(0.3).to_corner(UL, buff=0.3)
        self.play(
            Transform(title, small_title),
            FadeOut(subtitle),
            run_time=2
        )

        # =====================================================================
        # PHASE 2: THE ABYSS FORMS - Black Hole Emergence
        # =====================================================================

        # Camera adjustment - still keeping wide view (zoom stays low!)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.4,  # Slightly closer but still wide
            run_time=3
        )

        # Event horizon emerges from darkness
        event_horizon = create_event_horizon()
        event_horizon.scale(0.01)

        self.play(
            event_horizon.animate.scale(100),  # Scale up from tiny
            run_time=4,
            rate_func=smooth
        )

        # Add subtle rotation to the black hole
        rotation_tracker = ValueTracker(0)

        # Schwarzschild metric equation
        metric_eq = MathTex(
            r"ds^2 = -\left(1 - \frac{r_s}{r}\right)c^2 dt^2 + "
            r"\frac{dr^2}{1 - \frac{r_s}{r}} + r^2 d\Omega^2",
            font_size=32,
            color=EQUATION_COLOR
        )
        metric_eq.to_corner(UR, buff=0.5)

        self.add_fixed_in_frame_mobjects(metric_eq)
        self.play(Write(metric_eq), run_time=3)
        self.wait(1)

        # =====================================================================
        # PHASE 3: ERGOSPHERE AND FRAME DRAGGING
        # =====================================================================

        ergosphere = create_ergosphere()

        # Gentle camera shift while maintaining wide view
        self.play(
            Create(ergosphere, run_time=3),
        )
        self.move_camera(
            phi=65 * DEGREES,
            theta=-60 * DEGREES,
            zoom=0.4,  # Maintain wide zoom
            run_time=2
        )

        # Kerr metric annotation
        kerr_note = MathTex(
            r"\text{Kerr: } g_{t\phi} \neq 0 \implies \text{Frame Dragging}",
            font_size=28,
            color=PURPLE_A
        )
        kerr_note.next_to(metric_eq, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(kerr_note)
        self.play(FadeIn(kerr_note), run_time=1)

        # Photon sphere
        photon_sphere = create_photon_sphere()
        self.play(Create(photon_sphere), run_time=2)

        # =====================================================================
        # PHASE 4: SPACETIME CURVATURE VISUALIZATION
        # =====================================================================

        spacetime_grid = create_spacetime_grid()

        # Camera angle to show the curved grid below the black hole
        self.move_camera(
            phi=55 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.35,  # Wide view to see the full grid
            run_time=2
        )
        self.play(Create(spacetime_grid, lag_ratio=0.02), run_time=4)
        self.wait(1)

        # =====================================================================
        # PHASE 5: THE ACCRETION DISK IGNITES
        # =====================================================================

        # Move to better angle for disk viewing
        self.move_camera(
            phi=70 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.4,  # Still wide to see full disk
            run_time=2
        )

        # Create particle system
        seed(123)
        disk_particles = []
        for _ in range(DISK_PARTICLE_COUNT):
            # Power-law distribution: more particles near ISCO
            r = ISCO_RADIUS + (uniform(0, 1) ** 0.5) * (7 * SCHWARZSCHILD_RADIUS)
            angle = uniform(0, TAU)
            particle = AccretionParticle(r, angle, vertical_scatter=0.15)
            disk_particles.append(particle)

        particle_dots = VGroup(*[p.dot for p in disk_particles])

        # Gravitational lensing rings
        lensing = create_lensing_ring()

        self.play(
            FadeIn(particle_dots, lag_ratio=0.002),
            Create(lensing),
            run_time=4
        )

        # Add disk dynamics updater
        def update_disk(mob, dt):
            for p in disk_particles:
                p.update(dt)

        particle_dots.add_updater(update_disk)

        # Let the disk spin
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # PHASE 6: RELATIVISTIC JETS ERUPT
        # =====================================================================

        # Camera angle to see vertical jets (more side view)
        self.move_camera(
            phi=80 * DEGREES,      # Looking more from the side
            theta=-30 * DEGREES,
            zoom=0.35,             # Wide to see full jet extent
            run_time=2
        )

        # Create jet particles
        jet_particles_north = [JetParticle(is_north=True, initial_progress=uniform(0, 1))
                               for _ in range(JET_PARTICLE_COUNT // 2)]
        jet_particles_south = [JetParticle(is_north=False, initial_progress=uniform(0, 1))
                               for _ in range(JET_PARTICLE_COUNT // 2)]

        jet_dots = VGroup(
            *[p.dot for p in jet_particles_north],
            *[p.dot for p in jet_particles_south]
        )

        # Jet axis indicator
        jet_axis = Line3D(
            start=[0, 0, -10],
            end=[0, 0, 10],
            color=JET_COLOR,
            stroke_width=1,
            stroke_opacity=0.3
        )

        self.play(
            FadeIn(jet_dots, lag_ratio=0.01),
            Create(jet_axis),
            run_time=3
        )

        # Jet dynamics
        def update_jets(mob, dt):
            for p in jet_particles_north + jet_particles_south:
                p.update(dt)

        jet_dots.add_updater(update_jets)

        # Jet equation
        jet_eq = MathTex(
            r"P_{\text{jet}} \sim \dot{M} c^2 \cdot \epsilon_{\text{BZ}}",
            font_size=28,
            color=JET_COLOR
        )
        jet_eq.to_corner(DL, buff=0.5)
        self.add_fixed_in_frame_mobjects(jet_eq)
        self.play(Write(jet_eq), run_time=2)

        # =====================================================================
        # PHASE 7: HAWKING RADIATION (Quantum Effects)
        # =====================================================================

        hawking_note = MathTex(
            r"T_H = \frac{\hbar c^3}{8\pi G M k_B}",
            font_size=28,
            color=HAWKING_PARTICLE_COLOR
        )
        hawking_note.next_to(jet_eq, UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(hawking_note)
        self.play(Write(hawking_note), run_time=2)

        # Create Hawking pair animations
        hawking_pairs = VGroup()
        for i in range(8):
            angle = i * TAU / 8
            r = SCHWARZSCHILD_RADIUS * 1.3

            # Particle escapes
            particle = Dot3D(
                point=[r * cos(angle), r * sin(angle), 0],
                radius=0.03,
                color=HAWKING_PARTICLE_COLOR
            )
            # Antiparticle falls in
            antiparticle = Dot3D(
                point=[r * cos(angle), r * sin(angle), 0],
                radius=0.03,
                color=HAWKING_ANTIPARTICLE_COLOR
            )
            hawking_pairs.add(particle, antiparticle)

        self.play(FadeIn(hawking_pairs))

        # Animate pair separation
        particle_anims = []
        for i in range(0, len(hawking_pairs), 2):
            angle = (i // 2) * TAU / 8
            # Particle escapes outward
            escape_point = np.array([5 * cos(angle), 5 * sin(angle), uniform(-1, 1)])
            particle_anims.append(
                hawking_pairs[i].animate.move_to(escape_point).set_opacity(0)
            )
            # Antiparticle falls to horizon
            particle_anims.append(
                hawking_pairs[i+1].animate.move_to(ORIGIN).set_opacity(0)
            )

        self.play(*particle_anims, run_time=4, rate_func=smooth)

        # =====================================================================
        # PHASE 8: GRAND FINALE - FULL COSMIC VIEW
        # =====================================================================

        # Pull camera back for epic wide view - see EVERYTHING
        self.move_camera(
            phi=65 * DEGREES,      # Good elevated angle
            theta=-45 * DEGREES,
            zoom=0.3,              # WIDEST zoom - see entire scene
            run_time=4
        )

        # Begin majestic rotation
        self.begin_ambient_camera_rotation(rate=0.08)

        # Summary text
        finale_text = Text(
            "Where Gravity Bends Light, Time, and Space",
            font_size=42,
            weight=BOLD
        ).set_color_by_gradient(BLUE_A, PURPLE_A, GOLD_A)
        finale_text.to_edge(DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(finale_text)
        self.play(Write(finale_text), run_time=3)

        # Let everything spin majestically
        self.wait(8)

        self.stop_ambient_camera_rotation()

        # =====================================================================
        # PHASE 9: FADE TO THE VOID
        # =====================================================================

        # Remove all fixed frame mobjects
        self.remove_fixed_in_frame_mobjects(title, metric_eq, kerr_note,
                                            jet_eq, hawking_note, finale_text)

        # Fade everything to black
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=5
        )

        # Final title
        finis = Text(
            "Finis",
            font_size=64,
            weight=BOLD
        ).set_color_by_gradient(WHITE, GRAY_A)
        self.add_fixed_in_frame_mobjects(finis)
        self.play(Write(finis), run_time=2)
        self.wait(2)
        self.play(FadeOut(finis), run_time=3)


# ==============================================================================
# ADDITIONAL SCENES FOR EDUCATIONAL DEEP DIVES
# ==============================================================================

class GeodesicVisualization(ThreeDScene):
    """
    Visualize null and timelike geodesics around a Schwarzschild black hole.
    Shows how light and matter follow curved paths in spacetime.
    """

    def construct(self):
        self.camera.background_color = VOID_BLACK
        # Wide camera setup to see all geodesic paths
        self.set_camera_orientation(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.4  # Wide view
        )

        # Create black hole
        horizon = create_event_horizon()
        stars = make_deep_starfield(n=500, radius=30)

        self.add(stars)
        self.play(FadeIn(horizon), run_time=2)

        # Title
        title = Text("Geodesics in Curved Spacetime", font_size=48)
        title.set_color_by_gradient(BLUE_A, TEAL_A)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))

        # Geodesic equation
        geodesic_eq = MathTex(
            r"\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}"
            r"\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0",
            font_size=32
        )
        geodesic_eq.to_corner(UR)
        self.add_fixed_in_frame_mobjects(geodesic_eq)
        self.play(Write(geodesic_eq))

        # Create various geodesics
        geodesics = VGroup()

        # 1. Circular orbit (at photon sphere)
        circular = ParametricFunction(
            lambda t: np.array([
                PHOTON_SPHERE * cos(t),
                PHOTON_SPHERE * sin(t),
                0
            ]),
            t_range=[0, TAU],
            color=YELLOW,
            stroke_width=3
        )

        # 2. Plunging orbit
        plunge_points = []
        for i in range(100):
            t = i / 99
            r = 5 - 4 * t  # Starts at r=5, ends at r=1
            angle = t * 3 * PI  # Spirals in
            if r > SCHWARZSCHILD_RADIUS:
                plunge_points.append([r * cos(angle), r * sin(angle), 0])

        plunging = VMobject()
        plunging.set_points_smoothly(plunge_points)
        plunging.set_stroke(RED, width=3)

        # 3. Scattered geodesic (comes close, escapes)
        scatter_points = []
        for i in range(100):
            t = (i - 50) / 25  # -2 to 2
            # Hyperbolic-like path
            r = 2 + sqrt(1 + t ** 2)
            angle = 0.5 * np.arctan(t)
            scatter_points.append([r * cos(angle), r * sin(angle), 0])

        scattered = VMobject()
        scattered.set_points_smoothly(scatter_points)
        scattered.set_stroke(GREEN, width=3)

        # Animate geodesics
        self.play(Create(circular), run_time=3)
        self.wait(1)
        self.play(Create(plunging), run_time=3)
        self.wait(1)
        self.play(Create(scattered), run_time=3)

        # Labels
        labels = VGroup(
            Text("Circular (unstable)", font_size=20, color=YELLOW),
            Text("Plunging", font_size=20, color=RED),
            Text("Scattered", font_size=20, color=GREEN)
        ).arrange(DOWN, aligned_edge=LEFT)
        labels.to_corner(DL)
        self.add_fixed_in_frame_mobjects(labels)
        self.play(FadeIn(labels))

        # Camera rotation
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=3)


class TimeDilationVisualization(ThreeDScene):
    """
    Visualize gravitational time dilation near a black hole.
    Shows clocks ticking at different rates based on gravitational potential.
    """

    def construct(self):
        self.camera.background_color = VOID_BLACK
        # Wide view to see all clocks at different radii
        self.set_camera_orientation(
            phi=75 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.4  # Wide view to see clocks at r=2, 4, 8
        )

        # Black hole
        horizon = create_event_horizon()
        stars = make_deep_starfield(n=800, radius=40)

        self.add(stars)
        self.play(FadeIn(horizon), run_time=2)

        # Title
        title = Text("Gravitational Time Dilation", font_size=48)
        title.set_color_by_gradient(PURPLE_A, BLUE_A)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))

        # Time dilation formula
        dilation_eq = MathTex(
            r"\frac{d\tau}{dt} = \sqrt{1 - \frac{r_s}{r}}",
            font_size=36
        )
        dilation_eq.to_corner(UR)
        self.add_fixed_in_frame_mobjects(dilation_eq)
        self.play(Write(dilation_eq))

        # Create "clocks" at different radii
        clock_radii = [2, 4, 8]
        clocks = VGroup()
        clock_hands = []

        for r in clock_radii:
            # Clock face
            clock_face = Circle(radius=0.3, color=WHITE, stroke_width=2)
            clock_face.move_to([r, 0, 0])

            # Clock hand
            hand = Line(ORIGIN, UP * 0.25, color=YELLOW, stroke_width=3)
            hand.move_to(clock_face.get_center())

            clocks.add(clock_face, hand)
            clock_hands.append((hand, r))

        self.play(Create(clocks), run_time=2)

        # Time tracker
        time_tracker = ValueTracker(0)

        # Update clock hands based on time dilation
        def update_clocks(mob, dt):
            t = time_tracker.get_value()
            for hand, r in clock_hands:
                # Time dilation factor
                dilation = sqrt(1 - SCHWARZSCHILD_RADIUS / r)
                local_time = t * dilation
                angle = -local_time * 2 * PI  # One rotation per unit time

                center = np.array([r, 0, 0])
                hand.put_start_and_end_on(
                    center,
                    center + 0.25 * np.array([sin(angle), cos(angle), 0])
                )

        clocks.add_updater(update_clocks)

        # Animate time passing
        self.play(
            time_tracker.animate.set_value(3),
            run_time=10,
            rate_func=linear
        )

        # Explanation
        explanation = Text(
            "Clocks tick slower in stronger gravitational fields",
            font_size=28
        )
        explanation.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(explanation)
        self.play(Write(explanation))

        self.wait(2)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=3)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Render the main scene
    scene = BlackHoleSymphony()
    scene.render()
