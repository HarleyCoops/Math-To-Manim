"""
Single-Pixel Imaging: The Ghost Camera Symphony
================================================

A stunning 3D visualization of compressed sensing and single-pixel imaging,
demonstrating how a single photodetector can capture full images through
structured illumination and Fourier reconstruction.

Inspired by Jon Bumstead's single-pixel camera and the principles of
computational ghost imaging.

Key Concepts Visualized:
- Structured illumination with sinusoidal patterns
- Light reflection and detection by single photodetector
- Fourier transform reconstruction of hidden images
- The "ghost" emerging from mathematical inference

Render with:
    manim -pqh single_pixel_imaging.py SinglePixelImagingSymphony

For 4K quality:
    manim -pqk single_pixel_imaging.py SinglePixelImagingSymphony

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

# Scene Layout
PROJECTOR_POS = np.array([-6, 3, 2])
TARGET_POS = np.array([0, 0, 0])
DETECTOR_POS = np.array([5, 4, 1])

# Grid Resolution
PATTERN_RESOLUTION = 32
TARGET_SIZE = 3.0

# Particle Counts
LIGHT_RAY_COUNT = 50
PHOTON_PARTICLE_COUNT = 200
STAR_COUNT = 1500
FOURIER_WAVE_COUNT = 64

# Animation Timing
PATTERN_CYCLE_TIME = 0.5

# Color Palette - Ethereal Ghost Theme
VOID_BLACK = "#000000"
PROJECTOR_COLOR = "#00d4ff"       # Cyan beam
PATTERN_COLOR_1 = "#ff6b6b"       # Coral red
PATTERN_COLOR_2 = "#4ecdc4"       # Teal
PATTERN_COLOR_3 = "#ffe66d"       # Golden yellow
TARGET_COLOR = "#9d4edd"          # Purple
DETECTOR_COLOR = "#06ffa5"        # Neon green
GHOST_COLOR = "#e0aaff"           # Soft violet
FOURIER_COLOR = "#48cae4"         # Bright cyan
EQUATION_COLOR = WHITE
RECONSTRUCTION_COLOR = "#f72585"  # Magenta pink


# ==============================================================================
# HELPER CLASSES
# ==============================================================================

class PhotonParticle:
    """A photon traveling from projector to target to detector."""

    def __init__(self, start_pos: np.ndarray, target_pos: np.ndarray,
                 end_pos: np.ndarray, phase: float = 0.0):
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.end_pos = end_pos
        self.phase = phase
        self.progress = phase  # 0 to 2: 0-1 is projector->target, 1-2 is target->detector
        self.speed = uniform(0.8, 1.2)

        # Visual
        self.dot = Dot3D(
            point=self._get_position(),
            radius=0.03,
            color=PROJECTOR_COLOR
        )
        self.dot.set_opacity(0.8)

        # Trail
        self.trail_length = 8
        self.trail_points = [self._get_position() for _ in range(self.trail_length)]

    def _get_position(self) -> np.ndarray:
        """Calculate position along the photon path."""
        if self.progress < 1:
            # Projector to target
            t = self.progress
            return self.start_pos + t * (self.target_pos - self.start_pos)
        else:
            # Target to detector
            t = self.progress - 1
            return self.target_pos + t * (self.end_pos - self.target_pos)

    def update(self, dt: float):
        """Move photon along path."""
        self.progress += self.speed * dt * 0.5
        if self.progress > 2:
            self.progress = 0
            # Randomize slightly
            self.speed = uniform(0.8, 1.2)

        pos = self._get_position()
        self.dot.move_to(pos)

        # Update color based on leg of journey
        if self.progress < 1:
            self.dot.set_color(PROJECTOR_COLOR)
        else:
            # Transition to reflected color
            t = self.progress - 1
            self.dot.set_color(interpolate_color(TARGET_COLOR, DETECTOR_COLOR, t))


class SinusoidalPattern:
    """A sinusoidal pattern projected onto the target."""

    def __init__(self, frequency: float, orientation: float, phase: float = 0):
        self.frequency = frequency
        self.orientation = orientation
        self.phase = phase
        self.time = 0

    def get_intensity(self, x: float, y: float) -> float:
        """Calculate intensity at a point on the target."""
        # Rotate coordinates by orientation
        rx = x * cos(self.orientation) + y * sin(self.orientation)
        # Sinusoidal pattern
        return 0.5 + 0.5 * sin(2 * PI * self.frequency * rx + self.phase + self.time)

    def update(self, dt: float):
        """Animate the pattern."""
        self.time += dt * 2


class FourierComponent:
    """A single Fourier component in the reconstruction."""

    def __init__(self, kx: float, ky: float, amplitude: float, phase: float):
        self.kx = kx
        self.ky = ky
        self.amplitude = amplitude
        self.phase = phase
        self.revealed = False
        self.reveal_progress = 0.0

    def get_contribution(self, x: float, y: float) -> float:
        """Calculate this component's contribution to the image."""
        if not self.revealed:
            return 0
        return self.amplitude * self.reveal_progress * cos(
            2 * PI * (self.kx * x + self.ky * y) + self.phase
        )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def make_starfield(n: int = STAR_COUNT, radius: float = 60) -> VGroup:
    """Create a cosmic starfield background."""
    seed(42)
    stars = VGroup()

    for i in range(n):
        theta = uniform(0, TAU)
        phi = uniform(0, PI)
        r = uniform(radius * 0.4, radius)

        x = r * sin(phi) * cos(theta)
        y = r * sin(phi) * sin(theta)
        z = r * cos(phi)

        distance_factor = r / radius
        base_radius = 0.015 + 0.03 * (1 - distance_factor)

        star_colors = [WHITE, BLUE_A, YELLOW_A, "#e0aaff"]
        color = choice(star_colors) if uniform(0, 1) > 0.85 else WHITE

        dot = Dot3D(
            point=[x, y, z],
            radius=base_radius * uniform(0.5, 1.2),
            color=color
        )
        dot.set_opacity(uniform(0.2, 0.9) * (1 - distance_factor * 0.4))
        stars.add(dot)

    return stars


def create_projector() -> VGroup:
    """Create the light projector device."""
    projector = VGroup()

    # Main body - cone shape
    body = Cone(
        base_radius=0.4,
        height=0.8,
        direction=TARGET_POS - PROJECTOR_POS,
        resolution=24
    )
    body.move_to(PROJECTOR_POS)
    body.set_color(PROJECTOR_COLOR)
    body.set_opacity(0.8)

    # Lens glow
    lens = Sphere(radius=0.15, resolution=(16, 16))
    lens.move_to(PROJECTOR_POS)
    lens.set_color(WHITE)
    lens.set_opacity(0.9)

    # Housing
    housing = Cylinder(
        radius=0.35,
        height=0.5,
        direction=TARGET_POS - PROJECTOR_POS,
        resolution=24
    )
    housing.move_to(PROJECTOR_POS + 0.4 * normalize(PROJECTOR_POS - TARGET_POS))
    housing.set_color(BLUE_E)
    housing.set_opacity(0.7)

    projector.add(housing, body, lens)
    return projector


def create_target_surface() -> VGroup:
    """Create the target object being imaged."""
    target = VGroup()

    # Main surface - a tilted plane
    surface = Surface(
        lambda u, v: np.array([
            u - TARGET_SIZE/2,
            v - TARGET_SIZE/2,
            0.1 * sin(2 * u) * cos(2 * v)  # Slight texture
        ]),
        u_range=[0, TARGET_SIZE],
        v_range=[0, TARGET_SIZE],
        resolution=(32, 32),
        fill_color=TARGET_COLOR,
        fill_opacity=0.6,
        stroke_color=PURPLE_A,
        stroke_width=0.5
    )
    surface.move_to(TARGET_POS)
    surface.set_shade_in_3d(True)

    # Border frame
    frame = Square(side_length=TARGET_SIZE)
    frame.move_to(TARGET_POS)
    frame.set_stroke(PURPLE_A, width=3)
    frame.set_fill(opacity=0)

    target.add(surface, frame)
    return target


def create_detector() -> VGroup:
    """Create the single-pixel photodetector."""
    detector = VGroup()

    # Detector surface - small square
    sensor = Square(side_length=0.5)
    sensor.move_to(DETECTOR_POS)
    sensor.set_fill(DETECTOR_COLOR, opacity=0.8)
    sensor.set_stroke(WHITE, width=2)

    # Look at target
    sensor.rotate(PI/6, axis=UP)
    sensor.rotate(-PI/8, axis=RIGHT)

    # Glow effect
    glow = Circle(radius=0.4)
    glow.move_to(DETECTOR_POS)
    glow.set_fill(DETECTOR_COLOR, opacity=0.3)
    glow.set_stroke(width=0)

    # Housing box
    housing = Cube(side_length=0.6)
    housing.move_to(DETECTOR_POS + np.array([0.3, 0, 0]))
    housing.set_color(BLUE_E)
    housing.set_opacity(0.5)

    detector.add(housing, glow, sensor)
    return detector


def create_light_cone(progress: float = 1.0) -> VGroup:
    """Create the cone of light from projector to target."""
    cone = VGroup()

    direction = TARGET_POS - PROJECTOR_POS
    dist = np.linalg.norm(direction)

    # Create multiple beam lines
    n_beams = 12
    for i in range(n_beams):
        angle = i * TAU / n_beams

        # Start point at projector
        start = PROJECTOR_POS

        # End point spread across target
        spread = 1.5 * progress
        end_offset = np.array([
            spread * cos(angle),
            spread * sin(angle),
            0
        ])
        end = TARGET_POS + end_offset

        # Create gradient line
        line = Line3D(
            start=start,
            end=start + progress * (end - start),
            color=PROJECTOR_COLOR,
            thickness=0.02
        )
        line.set_opacity(0.4)
        cone.add(line)

    return cone


def create_sinusoidal_surface(pattern: SinusoidalPattern, size: float = TARGET_SIZE) -> Surface:
    """Create a 3D surface showing the sinusoidal pattern on target."""
    def pattern_func(u, v):
        x = (u - 0.5) * size
        y = (v - 0.5) * size
        intensity = pattern.get_intensity(x, y)

        # Height based on intensity
        z = 0.3 * intensity

        return np.array([x, y, z])

    surface = Surface(
        pattern_func,
        u_range=[0, 1],
        v_range=[0, 1],
        resolution=(PATTERN_RESOLUTION, PATTERN_RESOLUTION),
        fill_opacity=0.8,
        stroke_width=0.5,
        stroke_opacity=0.3
    )
    surface.move_to(TARGET_POS)

    # Color based on intensity
    surface.set_fill_by_value(
        axes=Axes(),
        colorscale=[
            (PATTERN_COLOR_2, 0),
            (PATTERN_COLOR_3, 0.5),
            (PATTERN_COLOR_1, 1.0)
        ],
        axis=2
    )
    surface.set_shade_in_3d(True)

    return surface


def create_fourier_space_visualization() -> VGroup:
    """Create the Fourier transform frequency space visualization."""
    fourier_vis = VGroup()

    # Central plane
    plane = Square(side_length=4)
    plane.set_fill(VOID_BLACK, opacity=0.8)
    plane.set_stroke(FOURIER_COLOR, width=2)

    # Frequency grid
    grid = NumberPlane(
        x_range=[-2, 2, 0.5],
        y_range=[-2, 2, 0.5],
        background_line_style={
            "stroke_color": FOURIER_COLOR,
            "stroke_width": 1,
            "stroke_opacity": 0.3
        }
    )
    grid.scale(0.5)

    # Frequency components as dots
    components = VGroup()
    for kx in np.linspace(-1.5, 1.5, 7):
        for ky in np.linspace(-1.5, 1.5, 7):
            if abs(kx) + abs(ky) > 0.1:  # Skip DC
                r = sqrt(kx**2 + ky**2)
                amp = exp(-r * 0.5)  # Amplitude falls off

                dot = Dot(
                    point=[kx, ky, 0],
                    radius=0.08 * amp + 0.02,
                    color=interpolate_color(FOURIER_COLOR, WHITE, amp)
                )
                dot.set_opacity(0.5 + 0.5 * amp)
                components.add(dot)

    fourier_vis.add(plane, grid, components)
    return fourier_vis


def create_ghost_image_surface(reveal_progress: float = 0.0) -> Surface:
    """Create the reconstructed 'ghost' image emerging from Fourier data."""
    def ghost_func(u, v):
        x = (u - 0.5) * TARGET_SIZE
        y = (v - 0.5) * TARGET_SIZE

        # Simulate a simple reconstructed image (e.g., a face or pattern)
        # Using superposition of Fourier components
        z = 0

        # Low frequency components (overall shape)
        z += 0.3 * cos(PI * x / TARGET_SIZE) * cos(PI * y / TARGET_SIZE)

        # Medium frequency (features)
        z += 0.15 * cos(2 * PI * x / TARGET_SIZE) * cos(PI * y / TARGET_SIZE)
        z += 0.1 * cos(PI * x / TARGET_SIZE) * cos(2 * PI * y / TARGET_SIZE)

        # High frequency (details)
        z += 0.05 * cos(4 * PI * x / TARGET_SIZE) * cos(4 * PI * y / TARGET_SIZE)

        # Apply reveal
        z *= reveal_progress

        return np.array([x, y, z])

    surface = Surface(
        ghost_func,
        u_range=[0, 1],
        v_range=[0, 1],
        resolution=(48, 48),
        fill_opacity=0.7 * reveal_progress,
        stroke_width=1,
        stroke_opacity=0.5 * reveal_progress
    )
    surface.move_to(TARGET_POS + np.array([0, 0, 0.5]))

    surface.set_fill_by_value(
        axes=Axes(),
        colorscale=[
            (VOID_BLACK, -0.5),
            (GHOST_COLOR, 0),
            (WHITE, 0.5)
        ],
        axis=2
    )
    surface.set_shade_in_3d(True)

    return surface


def create_data_stream_particles(n: int = 30) -> VGroup:
    """Create particles representing data flowing from detector."""
    particles = VGroup()

    for i in range(n):
        t = i / n

        # Helical path from detector
        angle = t * 4 * PI
        radius = 0.3 + 0.2 * t

        x = DETECTOR_POS[0] + 1 + t * 3
        y = DETECTOR_POS[1] + radius * cos(angle)
        z = DETECTOR_POS[2] + radius * sin(angle)

        dot = Dot3D(
            point=[x, y, z],
            radius=0.04 - 0.02 * t,
            color=interpolate_color(DETECTOR_COLOR, RECONSTRUCTION_COLOR, t)
        )
        dot.set_opacity(0.8 - 0.5 * t)
        particles.add(dot)

    return particles


# ==============================================================================
# MAIN SCENE
# ==============================================================================

class SinglePixelImagingSymphony(ThreeDScene):
    """
    A spectacular visualization of single-pixel imaging through
    compressed sensing and Fourier reconstruction.

    The animation shows how a single photodetector, combined with
    structured illumination patterns, can reconstruct full 2D images
    through the magic of mathematics.
    """

    def construct(self):
        # ====================================================================
        # PHASE 0: SETUP
        # ====================================================================
        self.camera.background_color = VOID_BLACK
        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.45,
            frame_center=ORIGIN
        )

        # ====================================================================
        # PHASE 1: COSMIC AWAKENING
        # ====================================================================
        stars = make_starfield()
        self.add(stars)

        # Title
        title = Text(
            "THE GHOST CAMERA",
            font_size=64,
            color=WHITE,
            weight=BOLD
        )
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)

        subtitle = Text(
            "Single-Pixel Imaging Through Structured Light",
            font_size=32,
            color=GHOST_COLOR
        )
        subtitle.next_to(title, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(subtitle)

        self.play(
            FadeIn(title, shift=DOWN),
            FadeIn(subtitle, shift=DOWN),
            run_time=2
        )
        self.wait(1)

        # ====================================================================
        # PHASE 2: THE IMPOSSIBLE QUESTION
        # ====================================================================
        question = Text(
            "Can you capture an image with a single pixel?",
            font_size=36,
            color=FOURIER_COLOR
        )
        question.next_to(subtitle, DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(question)

        self.play(Write(question), run_time=2)
        self.wait(1.5)

        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(question),
            run_time=1.5
        )
        self.remove_fixed_in_frame_mobjects(title, subtitle, question)

        # ====================================================================
        # PHASE 3: THE HARDWARE - PROJECTOR, TARGET, DETECTOR
        # ====================================================================
        hardware_title = Text(
            "The Setup: Projector + Target + Single Detector",
            font_size=36,
            color=WHITE
        )
        hardware_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(hardware_title)
        self.play(FadeIn(hardware_title), run_time=1)

        # Create hardware components
        projector = create_projector()
        target = create_target_surface()
        detector = create_detector()

        # Labels
        proj_label = Text("PROJECTOR", font_size=20, color=PROJECTOR_COLOR)
        proj_label.next_to(projector, UP, buff=0.3)

        target_label = Text("TARGET", font_size=20, color=TARGET_COLOR)
        target_label.next_to(target, DOWN, buff=0.3)

        det_label = Text("SINGLE PIXEL", font_size=20, color=DETECTOR_COLOR)
        det_label.next_to(detector, UP, buff=0.3)

        # Animate hardware appearance
        self.play(
            FadeIn(projector, scale=0.5),
            run_time=1.5
        )
        self.add(proj_label)

        self.play(
            FadeIn(target, scale=0.5),
            run_time=1.5
        )
        self.add(target_label)

        self.play(
            FadeIn(detector, scale=0.5),
            run_time=1.5
        )
        self.add(det_label)

        self.wait(1)

        # Move camera to better view
        self.move_camera(phi=60 * DEGREES, theta=-30 * DEGREES, zoom=0.5, run_time=2)

        # ====================================================================
        # PHASE 4: THE SECRET - STRUCTURED ILLUMINATION
        # ====================================================================
        self.play(FadeOut(hardware_title), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(hardware_title)

        secret_title = Text(
            "The Secret: Sinusoidal Pattern Projection",
            font_size=36,
            color=PATTERN_COLOR_3
        )
        secret_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(secret_title)
        self.play(FadeIn(secret_title), run_time=1)

        # Create light cone
        light_cone = create_light_cone(1.0)
        self.play(Create(light_cone), run_time=2)

        # Create initial sinusoidal pattern
        pattern = SinusoidalPattern(frequency=2, orientation=0)
        pattern_surface = create_sinusoidal_surface(pattern)

        # Remove plain target, add patterned surface
        self.play(
            FadeOut(target),
            FadeIn(pattern_surface),
            run_time=2
        )

        # ====================================================================
        # PHASE 5: ANIMATING PATTERNS
        # ====================================================================
        # Create photon particles
        photons = []
        photon_group = VGroup()

        for i in range(PHOTON_PARTICLE_COUNT):
            # Randomize starting position slightly around projector
            offset = np.array([uniform(-0.2, 0.2), uniform(-0.2, 0.2), uniform(-0.1, 0.1)])
            start = PROJECTOR_POS + offset

            # Random point on target
            target_offset = np.array([
                uniform(-TARGET_SIZE/2, TARGET_SIZE/2),
                uniform(-TARGET_SIZE/2, TARGET_SIZE/2),
                0
            ])
            target_pt = TARGET_POS + target_offset

            photon = PhotonParticle(
                start_pos=start,
                target_pos=target_pt,
                end_pos=DETECTOR_POS,
                phase=uniform(0, 2)
            )
            photons.append(photon)
            photon_group.add(photon.dot)

        def update_photons(mob, dt):
            for p in photons:
                p.update(dt)

        photon_group.add_updater(update_photons)
        self.add(photon_group)

        # Equation for sinusoidal pattern
        pattern_eq = MathTex(
            r"I(x, y) = \frac{1}{2}\left[1 + \cos(2\pi f_x x + 2\pi f_y y + \phi)\right]",
            font_size=28,
            color=EQUATION_COLOR
        )
        pattern_eq.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(pattern_eq)
        self.play(Write(pattern_eq), run_time=2)

        # Animate pattern changes
        def update_pattern_surface(surface, dt):
            pattern.update(dt)

        pattern_surface.add_updater(update_pattern_surface)

        self.wait(3)

        # Change pattern frequency
        pattern_surface.remove_updater(update_pattern_surface)

        new_pattern = SinusoidalPattern(frequency=4, orientation=PI/4)
        new_pattern_surface = create_sinusoidal_surface(new_pattern)

        freq_text = Text(
            "Varying frequency and orientation...",
            font_size=24,
            color=PATTERN_COLOR_3
        )
        freq_text.next_to(pattern_eq, UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(freq_text)

        self.play(
            Transform(pattern_surface, new_pattern_surface),
            FadeIn(freq_text),
            run_time=2
        )

        self.wait(2)

        # ====================================================================
        # PHASE 6: THE MEASUREMENT - TOTAL INTENSITY
        # ====================================================================
        self.play(FadeOut(secret_title), FadeOut(freq_text), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(secret_title, freq_text)

        measure_title = Text(
            "The Measurement: One Number Per Pattern",
            font_size=36,
            color=DETECTOR_COLOR
        )
        measure_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(measure_title)
        self.play(FadeIn(measure_title), run_time=1)

        # Highlight detector
        detector_highlight = Circle(radius=0.8)
        detector_highlight.move_to(DETECTOR_POS)
        detector_highlight.set_stroke(DETECTOR_COLOR, width=4)
        detector_highlight.set_fill(DETECTOR_COLOR, opacity=0.2)

        self.play(Create(detector_highlight), run_time=1)

        # Show measurement equation
        self.play(FadeOut(pattern_eq), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(pattern_eq)

        measure_eq = MathTex(
            r"m_k = \iint_{\text{target}} I_k(x,y) \cdot R(x,y) \, dx \, dy",
            font_size=28,
            color=EQUATION_COLOR
        )
        measure_eq.to_edge(DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(measure_eq)
        self.play(Write(measure_eq), run_time=2)

        # Data values appearing near detector
        data_values = VGroup()
        for i in range(8):
            val = Text(f"{uniform(0.3, 0.9):.3f}", font_size=16, color=DETECTOR_COLOR)
            val.move_to(DETECTOR_POS + np.array([1 + i * 0.5, 0.5 - i * 0.1, 0]))
            data_values.add(val)

        self.play(
            LaggedStartMap(FadeIn, data_values, lag_ratio=0.2),
            run_time=2
        )

        self.wait(2)

        # ====================================================================
        # PHASE 7: THE MAGIC - FOURIER RECONSTRUCTION
        # ====================================================================
        self.play(
            FadeOut(measure_title),
            FadeOut(detector_highlight),
            FadeOut(data_values),
            run_time=1
        )
        self.remove_fixed_in_frame_mobjects(measure_title)

        fourier_title = Text(
            "The Magic: Fourier Transform Reconstruction",
            font_size=36,
            color=FOURIER_COLOR
        )
        fourier_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(fourier_title)
        self.play(FadeIn(fourier_title), run_time=1)

        # Move camera for dramatic reveal
        self.move_camera(phi=50 * DEGREES, theta=-60 * DEGREES, zoom=0.55, run_time=2)

        # Fourier equation
        self.play(FadeOut(measure_eq), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(measure_eq)

        fourier_eq = MathTex(
            r"\hat{R}(f_x, f_y) = \mathcal{F}\{R(x,y)\} = \sum_{k} m_k \cdot e^{-2\pi i (f_{x,k} x + f_{y,k} y)}",
            font_size=26,
            color=EQUATION_COLOR
        )
        fourier_eq.to_edge(DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(fourier_eq)
        self.play(Write(fourier_eq), run_time=2)

        # Create data stream particles flowing to reconstruction
        data_stream = create_data_stream_particles()
        self.play(FadeIn(data_stream), run_time=1.5)

        # Animate data stream
        def update_data_stream(mob, dt):
            for i, dot in enumerate(mob):
                current_pos = dot.get_center()
                # Spiral motion
                angle = dt * 3
                new_x = current_pos[0] + dt * 0.5
                new_y = current_pos[1] + 0.1 * sin(new_x * 2)
                new_z = current_pos[2] + 0.1 * cos(new_x * 2)

                if new_x > 12:
                    new_x = DETECTOR_POS[0] + 1

                dot.move_to([new_x, new_y, new_z])

        data_stream.add_updater(update_data_stream)

        self.wait(3)

        # ====================================================================
        # PHASE 8: THE GHOST EMERGES
        # ====================================================================
        self.play(FadeOut(fourier_title), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(fourier_title)

        ghost_title = Text(
            "THE GHOST EMERGES",
            font_size=48,
            color=GHOST_COLOR,
            weight=BOLD
        )
        ghost_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(ghost_title)
        self.play(FadeIn(ghost_title, scale=1.2), run_time=1)

        # Remove pattern surface, prepare for ghost
        photon_group.remove_updater(update_photons)
        data_stream.remove_updater(update_data_stream)

        self.play(
            FadeOut(pattern_surface),
            FadeOut(photon_group),
            FadeOut(data_stream),
            FadeOut(light_cone),
            run_time=1.5
        )

        # Create ghost image surfaces at increasing reveal levels
        ghost_surfaces = []
        for i, progress in enumerate([0.2, 0.4, 0.6, 0.8, 1.0]):
            ghost = create_ghost_image_surface(progress)
            ghost_surfaces.append(ghost)

        # Animate ghost revelation
        current_ghost = ghost_surfaces[0]
        self.play(FadeIn(current_ghost), run_time=2)

        for i in range(1, len(ghost_surfaces)):
            self.play(
                Transform(current_ghost, ghost_surfaces[i]),
                run_time=1.5
            )

        # Add reveal text
        reveal_text = Text(
            "Image reconstructed from single-pixel measurements!",
            font_size=28,
            color=WHITE
        )
        reveal_text.next_to(fourier_eq, UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(reveal_text)
        self.play(Write(reveal_text), run_time=2)

        # Dramatic camera rotation
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(5)
        self.stop_ambient_camera_rotation()

        # ====================================================================
        # PHASE 9: THE INVERSE EQUATION
        # ====================================================================
        self.play(FadeOut(fourier_eq), FadeOut(reveal_text), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(fourier_eq, reveal_text)

        inverse_eq = MathTex(
            r"R(x,y) = \mathcal{F}^{-1}\{\hat{R}(f_x, f_y)\}",
            font_size=32,
            color=RECONSTRUCTION_COLOR
        )
        inverse_eq.to_edge(DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(inverse_eq)
        self.play(Write(inverse_eq), run_time=2)

        # Final explanation
        explanation = VGroup(
            Text("No lens. No array.", font_size=24, color=FOURIER_COLOR),
            Text("Just math and light.", font_size=24, color=GHOST_COLOR),
        )
        explanation.arrange(DOWN, buff=0.2)
        explanation.next_to(inverse_eq, UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(explanation)

        self.play(
            FadeIn(explanation[0], shift=UP),
            run_time=1
        )
        self.play(
            FadeIn(explanation[1], shift=UP),
            run_time=1
        )

        self.wait(2)

        # ====================================================================
        # PHASE 10: GRAND FINALE
        # ====================================================================
        self.play(FadeOut(ghost_title), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(ghost_title)

        final_title = Text(
            "SINGLE-PIXEL IMAGING",
            font_size=56,
            color=WHITE,
            weight=BOLD
        )
        final_subtitle = Text(
            "Seeing without looking",
            font_size=32,
            color=GHOST_COLOR
        )
        final_group = VGroup(final_title, final_subtitle)
        final_group.arrange(DOWN, buff=0.4)
        final_group.to_edge(UP, buff=1)

        self.add_fixed_in_frame_mobjects(final_title, final_subtitle)

        self.play(
            FadeIn(final_title, scale=1.1),
            FadeIn(final_subtitle),
            run_time=2
        )

        # Zoom out to cosmic view
        self.move_camera(phi=45 * DEGREES, theta=-45 * DEGREES, zoom=0.35, run_time=3)

        # Final ambient rotation
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # Fade to void
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=3
        )

        self.wait(1)


# ==============================================================================
# ADDITIONAL VISUALIZATION SCENES
# ==============================================================================

class PatternSequenceVisualization(ThreeDScene):
    """
    Focused visualization of the sinusoidal pattern sequence
    sweeping across the target object.
    """

    def construct(self):
        self.camera.background_color = VOID_BLACK
        self.set_camera_orientation(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.7
        )

        # Create target
        target = create_target_surface()
        self.add(target)

        # Title
        title = Text("Structured Illumination Patterns", font_size=36, color=WHITE)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        # Create patterns with varying frequencies and orientations
        patterns = [
            SinusoidalPattern(frequency=1, orientation=0),
            SinusoidalPattern(frequency=2, orientation=0),
            SinusoidalPattern(frequency=2, orientation=PI/4),
            SinusoidalPattern(frequency=3, orientation=PI/2),
            SinusoidalPattern(frequency=4, orientation=PI/3),
        ]

        current_surface = create_sinusoidal_surface(patterns[0])
        self.play(FadeIn(current_surface), run_time=2)

        for i, pattern in enumerate(patterns[1:], 1):
            # Update label
            freq_label = Text(
                f"f = {pattern.frequency}, θ = {int(pattern.orientation * 180 / PI)}°",
                font_size=24,
                color=PATTERN_COLOR_3
            )
            freq_label.to_edge(DOWN)
            self.add_fixed_in_frame_mobjects(freq_label)

            new_surface = create_sinusoidal_surface(pattern)
            self.play(
                Transform(current_surface, new_surface),
                run_time=2
            )
            self.wait(1)

            self.remove_fixed_in_frame_mobjects(freq_label)

        self.wait(2)


class FourierReconstructionVisualization(ThreeDScene):
    """
    Detailed visualization of how Fourier components
    build up to form the final image.
    """

    def construct(self):
        self.camera.background_color = VOID_BLACK
        self.set_camera_orientation(
            phi=55 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.6
        )

        # Title
        title = Text("Fourier Component Summation", font_size=36, color=FOURIER_COLOR)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        # Base surface
        base = Square(side_length=TARGET_SIZE)
        base.set_fill(VOID_BLACK, opacity=0.5)
        base.set_stroke(PURPLE_A, width=2)
        self.add(base)

        # Equation
        eq = MathTex(
            r"R(x,y) = \sum_{n,m} A_{nm} \cos(2\pi n x / L) \cos(2\pi m y / L)",
            font_size=24
        )
        eq.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(eq)

        # Build up image from components
        components_text = []
        surfaces = []

        # DC component (average)
        def dc_surface(u, v):
            x = (u - 0.5) * TARGET_SIZE
            y = (v - 0.5) * TARGET_SIZE
            return np.array([x, y, 0.2])

        # (1,0) component
        def comp_10(u, v):
            x = (u - 0.5) * TARGET_SIZE
            y = (v - 0.5) * TARGET_SIZE
            z = 0.2 + 0.15 * cos(PI * x)
            return np.array([x, y, z])

        # (0,1) component
        def comp_01(u, v):
            x = (u - 0.5) * TARGET_SIZE
            y = (v - 0.5) * TARGET_SIZE
            z = 0.2 + 0.15 * cos(PI * x) + 0.1 * cos(PI * y)
            return np.array([x, y, z])

        # (1,1) component
        def comp_11(u, v):
            x = (u - 0.5) * TARGET_SIZE
            y = (v - 0.5) * TARGET_SIZE
            z = 0.2 + 0.15 * cos(PI * x) + 0.1 * cos(PI * y) + 0.08 * cos(PI * x) * cos(PI * y)
            return np.array([x, y, z])

        # Higher frequency
        def final_surface(u, v):
            x = (u - 0.5) * TARGET_SIZE
            y = (v - 0.5) * TARGET_SIZE
            z = (0.2 + 0.15 * cos(PI * x) + 0.1 * cos(PI * y) +
                 0.08 * cos(PI * x) * cos(PI * y) +
                 0.05 * cos(2 * PI * x) + 0.05 * cos(2 * PI * y))
            return np.array([x, y, z])

        funcs = [dc_surface, comp_10, comp_01, comp_11, final_surface]
        labels = ["DC (Average)", "+ cos(πx)", "+ cos(πy)", "+ cos(πx)cos(πy)", "+ Higher frequencies"]

        current = Surface(
            funcs[0],
            u_range=[0, 1], v_range=[0, 1],
            resolution=(32, 32),
            fill_color=GHOST_COLOR,
            fill_opacity=0.7
        )
        current.set_shade_in_3d(True)
        self.play(FadeIn(current), run_time=2)

        for i, (func, label) in enumerate(zip(funcs[1:], labels[1:]), 1):
            label_text = Text(label, font_size=24, color=FOURIER_COLOR)
            label_text.next_to(title, DOWN)
            self.add_fixed_in_frame_mobjects(label_text)

            new_surface = Surface(
                func,
                u_range=[0, 1], v_range=[0, 1],
                resolution=(32, 32),
                fill_color=GHOST_COLOR,
                fill_opacity=0.7
            )
            new_surface.set_shade_in_3d(True)

            self.play(Transform(current, new_surface), run_time=2)
            self.wait(1)

            self.remove_fixed_in_frame_mobjects(label_text)

        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
        self.stop_ambient_camera_rotation()


# ==============================================================================
# RUN INSTRUCTIONS
# ==============================================================================
"""
To render the main animation:
    manim -pqh single_pixel_imaging.py SinglePixelImagingSymphony

To render the pattern sequence:
    manim -pqh single_pixel_imaging.py PatternSequenceVisualization

To render Fourier reconstruction:
    manim -pqh single_pixel_imaging.py FourierReconstructionVisualization

For 4K quality:
    manim -pqk single_pixel_imaging.py SinglePixelImagingSymphony
"""
