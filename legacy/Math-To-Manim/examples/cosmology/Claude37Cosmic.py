from manim import *
import numpy as np
from typing import Callable

# Configuration
config.background_color = "#000000"

# Utility functions
def remap_interval(value, old_min, old_max, new_min, new_max):
    """Remaps a value from one interval to another."""
    old_range = old_max - old_min
    new_range = new_max - new_min
    return new_min + new_range * ((value - old_min) / old_range)

def rgb_to_hex(rgb):
    """Convert RGB values (0-1 scale) to hex color string."""
    r, g, b = [int(255 * c) for c in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"

def rgb_to_color(rgb):
    """Converts RGB values (0-1 scale) to a color."""
    return rgb_to_hex(rgb)

# Fix the Line3D class
class Line3D(VMobject):
    """A line in 3D space."""
    def __init__(self, start=ORIGIN, end=RIGHT, **kwargs):
        super().__init__(**kwargs)
        self.set_points_as_corners([start, end])

# Fix the Cone class
class Cone(Surface):
    """A cone in 3D space."""
    def __init__(self, base_radius=1, height=2, **kwargs):
        super().__init__(
            lambda u, v: np.array([
                v * base_radius * np.cos(u),
                v * base_radius * np.sin(u),
                height * (1 - v)
            ]),
            u_range=[0, TAU],
            v_range=[0, 1],
            **kwargs
        )

##############################################################################
#  Utility Classes
##############################################################################
class StarField(VGroup):
    """
    Creates a field of randomly placed small dots (stars) in either 2D or 3D.
    With twinkling effect option.
    """
    def __init__(self, is_3D=False, num_stars=500, twinkle=True, depth_based_scale=True, **kwargs):
        super().__init__(**kwargs)
        self.is_3D = is_3D
        self.twinkle = twinkle
        self.stars = []
        
        # Create stars with different sizes based on depth
        for _ in range(num_stars):
            x = np.random.uniform(-9, 9)
            y = np.random.uniform(-5, 5)
            z = np.random.uniform(-5, 5) if is_3D else 0
            
            # Vary star size based on z-position to create depth perception
            if depth_based_scale and is_3D:
                # Stars further away (negative z) are smaller
                size_factor = remap_interval(z, -5, 5, 0.005, 0.03)
            else:
                size_factor = np.random.uniform(0.005, 0.03)
                
            brightness = np.random.uniform(0.5, 1.0)
            star_color = rgb_to_color([brightness, brightness, brightness])
            
            star = Dot(point=[x, y, z], color=star_color, radius=size_factor)
            self.add(star)
            self.stars.append(star)
    
    def start_twinkling(self, scene):
        if self.twinkle:
            for _ in range(3):  # Twinkle a few times
                twinkle_anims = []
                for star in self.stars:
                    if np.random.random() < 0.1:  # Only 10% of stars twinkle
                        orig_opacity = star.get_fill_opacity()
                        target_opacity = max(0.1, orig_opacity - np.random.uniform(0.1, 0.5))
                        twinkle_anims.append(
                            star.animate.set_fill_opacity(target_opacity)
                        )
                
                if twinkle_anims:
                    scene.play(
                        *twinkle_anims,
                        rate_func=there_and_back,
                        run_time=1.0,
                    )

class GlowingText(Text):
    """Text with a glowing effect."""
    def __init__(self, text, glow_factor=1.0, **kwargs):
        super().__init__(text, **kwargs)
        self.glow_factor = glow_factor
        self.set_glow()
        
    def set_glow(self):
        self.original = self.copy()
        for i in range(3):
            glow = self.copy()
            glow.set_fill_opacity(0.3 - 0.1*i)
            glow.set_stroke(self.get_color(), width=5*(i+1)*self.glow_factor, opacity=0.3 - 0.1*i)
            self.add(glow)
        self.add(self.original)

class GlowingTex(Tex):
    """Tex with a glowing effect."""
    def __init__(self, *text, glow_factor=1.0, glow_color=None, **kwargs):
        super().__init__(*text, **kwargs)
        self.glow_factor = glow_factor
        self.glow_color = glow_color or self.get_color()
        self.set_glow()
        
    def set_glow(self):
        self.original = self.copy()
        for i in range(3):
            glow = self.copy()
            glow.set_fill_opacity(0.3 - 0.1*i)
            glow.set_stroke(self.glow_color, width=5*(i+1)*self.glow_factor, opacity=0.3 - 0.1*i)
            self.add(glow)
        self.add(self.original)

class GlowingMathTex(MathTex):
    """MathTex with a glowing effect."""
    def __init__(self, *text, glow_factor=1.0, glow_color=None, **kwargs):
        super().__init__(*text, **kwargs)
        self.glow_factor = glow_factor
        self.glow_color = glow_color or self.get_color()
        self.set_glow()
        
    def set_glow(self):
        self.original = self.copy()
        for i in range(3):
            glow = self.copy()
            glow.set_fill_opacity(0.3 - 0.1*i)
            glow.set_stroke(self.glow_color, width=5*(i+1)*self.glow_factor, opacity=0.3 - 0.1*i)
            self.add(glow)
        self.add(self.original)

class PulsatingVGroup(VGroup):
    """A VGroup that can pulsate."""
    def __init__(self, *vmobjects, pulsating_factor=0.1, **kwargs):
        super().__init__(*vmobjects, **kwargs)
        self.pulsating_factor = pulsating_factor
        self.original_scale = 1
        
    def start_pulsing(self, scene, run_time=2, rate_func=lambda t: np.sin(2 * np.pi * t) * 0.5 + 0.5):
        scene.play(
            self.animate.scale(1 + self.pulsating_factor),
            rate_func=rate_func,
            run_time=run_time
        )
        scene.play(
            self.animate.scale(1 / (1 + self.pulsating_factor)),
            rate_func=rate_func,
            run_time=run_time
        )

class Arrow3D(VGroup):
    """An arrow in 3D space, created using a line and a cone."""
    def __init__(self, start, end, thickness=0.02, tip_length=0.2, tip_radius=0.1, **kwargs):
        super().__init__(**kwargs)
        
        # Calculate direction and length
        direction = end - start
        length = np.linalg.norm(direction)
        
        # Prevent division by zero for zero-length vectors
        if length < 1e-6:
            unit_direction = np.array([0, 0, 1])  # Default direction if length is zero
        else:
            unit_direction = direction / length
        
        # Create the line
        line = Line3D(start=start, end=end - unit_direction * tip_length, **kwargs)
        
        # Create the tip (cone)
        tip = Cone(base_radius=tip_radius, height=tip_length, **kwargs)
        tip.shift(end - unit_direction * tip_length)
        
        # Rotate the tip to align with the direction
        axis = np.cross([0, 0, 1], unit_direction)
        angle = np.arccos(np.dot([0, 0, 1], unit_direction))
        # Only rotate if we have a valid rotation axis and non-zero angle
        if np.linalg.norm(axis) > 1e-6 and abs(angle) > 1e-6:
            tip.rotate(angle, axis=axis)
        
        self.add(line, tip)

##############################################################################
#  Wave Animations and Field Visualizations
##############################################################################
class ElectromagneticWave(VGroup):
    """
    Creates a 3D representation of an electromagnetic wave with E and B fields.
    """
    def __init__(
        self, 
        axes, 
        x_range=[-5, 5, 0.1], 
        amplitude=1.0, 
        wavelength=1.0,
        e_color=RED_E, 
        b_color=BLUE_E,
        propagation_axis=RIGHT,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Store the parameters
        self.axes = axes
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.e_color = e_color
        self.b_color = b_color
        self.propagation_axis = propagation_axis
        
        # Calculate wave parameters
        self.k = 2 * PI / wavelength  # Wave number
        
        # Create the E and B field representations
        e_points, b_points = self.get_wave_points(x_range)
        
        # Create the E and B field curves
        self.e_field = VMobject()
        self.e_field.set_points_smoothly(e_points)
        self.e_field.set_color(e_color)
        self.e_field.set_stroke(width=4)
        
        # Completely disable fill to avoid gradient issues
        self.e_field.set_fill(color=e_color, opacity=0)
        # Ensure no gradient is used
        self.e_field.set_sheen_direction(None)
        self.e_field.set_flat_stroke(True)
        
        self.b_field = VMobject()
        self.b_field.set_points_smoothly(b_points)
        self.b_field.set_color(b_color)
        self.b_field.set_stroke(width=4)
        
        # Completely disable fill to avoid gradient issues
        self.b_field.set_fill(color=b_color, opacity=0)
        # Ensure no gradient is used
        self.b_field.set_sheen_direction(None)
        self.b_field.set_flat_stroke(True)
        
        # Add the curves to the group
        self.add(self.e_field, self.b_field)
        
        # Create field vectors
        self.e_vectors = VGroup()
        self.b_vectors = VGroup()
        vector_spacing = 0.5  # Space between vectors
        
        for x in np.arange(x_range[0], x_range[1], vector_spacing):
            # Calculate field values at this point
            e_val = self.amplitude * np.sin(self.k * x)
            b_val = self.amplitude * np.sin(self.k * x)
            
            # Create E field vector (pointing up/down)
            e_vector = Arrow3D(
                start=self.axes.c2p(x, 0, 0),
                end=self.axes.c2p(x, e_val, 0),
                color=e_color,
                thickness=0.01,
                tip_length=0.1,
                tip_radius=0.05
            )
            
            # Create B field vector (pointing in/out)
            b_vector = Arrow3D(
                start=self.axes.c2p(x, 0, 0),
                end=self.axes.c2p(x, 0, b_val),
                color=b_color,
                thickness=0.01,
                tip_length=0.1,
                tip_radius=0.05
            )
            
            self.e_vectors.add(e_vector)
            self.b_vectors.add(b_vector)
        
        # Add the vectors to the group
        self.add(self.e_vectors, self.b_vectors)
        
        # Create labels
        self.e_label = GlowingMathTex(r"\vec{E}", color=e_color, glow_factor=0.5)
        self.e_label.move_to(self.axes.c2p(x_range[1] + 0.5, amplitude, 0))
        
        self.b_label = GlowingMathTex(r"\vec{B}", color=b_color, glow_factor=0.5)
        self.b_label.move_to(self.axes.c2p(x_range[1] + 0.5, 0, amplitude))
        
        # Add the labels to the group
        self.add(self.e_label, self.b_label)
    
    def get_wave_points(self, x_range):
        """Generate the points for the E and B field curves."""
        e_points = []
        b_points = []
        
        for x in np.arange(x_range[0], x_range[1], x_range[2]):
            # E field oscillates in y direction
            e_points.append(self.axes.c2p(x, self.amplitude * np.sin(self.k * x), 0))
            
            # B field oscillates in z direction
            b_points.append(self.axes.c2p(x, 0, self.amplitude * np.sin(self.k * x)))
        
        return e_points, b_points
    
    def update_wave(self, phase):
        """Update the wave with a new phase."""
        x_range = np.arange(-5, 5, 0.1)
        new_e_points = []
        new_b_points = []
        
        for x in x_range:
            # E field oscillates in y direction with phase
            new_e_points.append(self.axes.c2p(x, self.amplitude * np.sin(self.k * x - phase), 0))
            
            # B field oscillates in z direction with phase
            new_b_points.append(self.axes.c2p(x, 0, self.amplitude * np.sin(self.k * x - phase)))
        
        self.e_field.set_points_smoothly(new_e_points)
        self.b_field.set_points_smoothly(new_b_points)
        
        # Update vectors - this approach might cause issues, let's fix it
        new_e_vectors = VGroup()
        new_b_vectors = VGroup()
        
        for i, x in enumerate(np.arange(-5, 5, 0.5)):
            if i < len(self.e_vectors):
                # Calculate field values at this point
                e_val = self.amplitude * np.sin(self.k * x - phase)
                b_val = self.amplitude * np.sin(self.k * x - phase)
                
                # Create new vectors
                new_e_vector = Arrow3D(
                    start=self.axes.c2p(x, 0, 0),
                    end=self.axes.c2p(x, e_val, 0),
                    color=self.e_color,
                    thickness=0.01,
                    tip_length=0.1,
                    tip_radius=0.05
                )
                
                new_b_vector = Arrow3D(
                    start=self.axes.c2p(x, 0, 0),
                    end=self.axes.c2p(x, 0, b_val),
                    color=self.b_color,
                    thickness=0.01,
                    tip_length=0.1,
                    tip_radius=0.05
                )
                
                new_e_vectors.add(new_e_vector)
                new_b_vectors.add(new_b_vector)
        
        # Remove old vectors and add new ones
        self.remove(self.e_vectors, self.b_vectors)
        self.e_vectors = new_e_vectors
        self.b_vectors = new_b_vectors
        self.add(self.e_vectors, self.b_vectors)

class LightCone(Surface):
    """
    Creates a 3D light cone in Minkowski spacetime.
    """
    def __init__(self, height=4, resolution=(51, 51), **kwargs):
        super().__init__(
            self.func,
            u_range=[0, TAU],
            v_range=[0, height],
            resolution=resolution,
            **kwargs
        )
        self.set_stroke(width=1)
        self.set_stroke_opacity(0.5)
        
    def func(self, u, v):
        # u: angle around cone
        # v: height of cone
        return np.array([v * np.cos(u), v * np.sin(u), v])

##############################################################################
#  Feynman Diagram Visualization
##############################################################################
class FeynmanDiagram(VGroup):
    """
    Creates a Feynman diagram for electron-electron scattering via photon exchange.
    """
    def __init__(self, scale=1.0, **kwargs):
        super().__init__(**kwargs)
        
        # Create the electron lines
        e1_in = Line(ORIGIN, UP + LEFT, color=BLUE)
        e1_out = Line(ORIGIN, DOWN + LEFT, color=BLUE)
        e2_in = Line(RIGHT * 2, UP + RIGHT * 3, color=BLUE)
        e2_out = Line(RIGHT * 2, DOWN + RIGHT * 3, color=BLUE)
        
        # Create the photon line (wavy)
        photon = self.create_wavy_line(ORIGIN, RIGHT * 2, color=YELLOW)
        
        # Create the labels
        e1_label = MathTex("e^-", color=BLUE).scale(0.7).next_to(e1_in, UP + LEFT, buff=0.1)
        e2_label = MathTex("e^-", color=BLUE).scale(0.7).next_to(e2_in, UP + RIGHT, buff=0.1)
        photon_label = MathTex("\\gamma", color=YELLOW).scale(0.7).next_to(photon, UP, buff=0.2)
        
        # Add everything to the group
        self.add(e1_in, e1_out, e2_in, e2_out, photon, e1_label, e2_label, photon_label)
        
        # Scale the diagram
        self.scale(scale)
    
    def create_wavy_line(self, start, end, waves=5, color=YELLOW):
        """Creates a wavy line to represent a photon."""
        path = VMobject(color=color)
        direction = end - start
        length = np.linalg.norm(direction)
        unit_direction = direction / length
        
        # Perpendicular vector for wave amplitude
        if abs(unit_direction[0]) > abs(unit_direction[1]):
            perp = np.array([-unit_direction[1], unit_direction[0], 0])
        else:
            perp = np.array([unit_direction[1], -unit_direction[0], 0])
        perp = perp / np.linalg.norm(perp) * 0.2
        
        points = []
        wave_step = length / (waves * 2)
        for i in range(waves * 2 + 1):
            t = i / (waves * 2)
            if i % 2 == 0:
                points.append(start + direction * t + perp * np.sin(PI * i))
            else:
                points.append(start + direction * t - perp * np.sin(PI * i))
        
        path.set_points_as_corners(points)
        return path

##############################################################################
#  Main Animation Scenes
##############################################################################
class QEDJourney(ThreeDScene):
    def construct(self):
        # Initial camera settings
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)
        self.camera.background_color = "#000000"
        
        ############################################################################
        # 1. COSMIC STARFIELD FADE-IN
        ############################################################################
        # Create a 3D star field with depth-based scaling
        star_field = StarField(is_3D=True, num_stars=1000, twinkle=True, depth_based_scale=True)
        
        # Fade in the star field
        self.play(FadeIn(star_field, run_time=3))
        self.wait(1)
        
        # Add subtle twinkling to some stars (more efficient approach)
        for _ in range(3):  # Twinkle a few times
            twinkle_anims = []
            for star in star_field.stars:
                if np.random.random() < 0.1:  # Only 10% of stars twinkle
                    orig_opacity = star.get_fill_opacity()
                    target_opacity = max(0.1, orig_opacity - np.random.uniform(0.1, 0.5))
                    twinkle_anims.append(
                        star.animate.set_fill_opacity(target_opacity)
                    )
            
            if twinkle_anims:
                self.play(
                    *twinkle_anims,
                    rate_func=there_and_back,
                    run_time=1.0,
                )
        
        ############################################################################
        # 2. EPIC TITLE INTRODUCTION
        ############################################################################
        # Create a glowing, gradient title
        main_title = GlowingText(
            "Quantum Field Theory:",
            font="Helvetica Neue",
            font_size=60,
            color=BLUE,
            glow_factor=1.5
        )
        
        subtitle = GlowingText(
            "A Journey into the Electromagnetic Interaction",
            font="Helvetica Neue",
            font_size=48,
            color=YELLOW,
            glow_factor=1.0
        )
        
        title_group = VGroup(main_title, subtitle).arrange(DOWN, buff=0.3)
        
        # Add dramatic entry for the title - start from far away in 3D space
        title_group.move_to(OUT * 15 + UP * 5)
        title_group.rotate(60 * DEGREES, axis=RIGHT)
        
        # Fade in while moving the title toward camera
        self.play(
            FadeIn(title_group, run_time=1),
            title_group.animate.move_to(OUT * 10 + UP * 3).rotate(-30 * DEGREES, axis=RIGHT),
            run_time=3
        )
        
        # First animate the title group
        self.play(
            title_group.animate.move_to(ORIGIN),
            run_time=1.5
        )
        # Then move the camera
        self.move_camera(phi=65 * DEGREES, theta=-20 * DEGREES, run_time=1.5)
        
        # Hold for appreciation
        self.wait(2)
        
        # Shrink and move to upper left
        self.play(
            title_group.animate.scale(0.3).to_corner(UL, buff=0.5),
            run_time=2
        )
        
        ############################################################################
        # 3. 4D MINKOWSKI SPACETIME WIREFRAME
        ############################################################################
        # Create a 3D coordinate system to represent spacetime
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-4, 4, 1],
            x_length=8,
            y_length=8,
            z_length=8
        )
        
        # Axes labels
        x_label = axes.get_x_axis_label(Tex("x"), direction=RIGHT)
        y_label = axes.get_y_axis_label(Tex("y"), direction=UP)
        z_label = axes.get_z_axis_label(Tex("z"), direction=OUT)
        t_label = GlowingTex("ct", color=BLUE, glow_factor=0.5).next_to(axes.get_z_axis(), UP)
        
        axes_labels = VGroup(x_label, y_label, z_label, t_label)
        
        # Create a light cone
        light_cone = LightCone(height=3)
        light_cone.set_fill(BLUE, opacity=0.2)
        light_cone.set_stroke(BLUE_A, width=1, opacity=0.8)
        
        # Add a past light cone (inverted)
        past_light_cone = LightCone(height=3)
        past_light_cone.flip()  # Flip to point in the negative z direction
        past_light_cone.set_fill(RED, opacity=0.2)
        past_light_cone.set_stroke(RED_A, width=1, opacity=0.8)
        
        # Add grid lines to represent the space-time grid
        grid_lines = VGroup()
        
        # Horizontal time slices (x-y planes at different t)
        for t in np.linspace(-3, 3, 7):
            grid = NumberPlane(
                x_range=[-4, 4, 1],
                y_range=[-4, 4, 1],
                background_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 1,
                    "stroke_opacity": 0.3
                }
            )
            grid.shift(t * OUT)
            grid_lines.add(grid)
        
        # Group everything
        spacetime = VGroup(axes, axes_labels, light_cone, past_light_cone, grid_lines)
        
        # Fade in the axes and labels
        self.play(
            Create(axes, run_time=2),
            FadeIn(axes_labels, run_time=2)
        )
        
        # Introduce the light cone with a pulsing effect
        self.play(
            Create(light_cone),
            Create(past_light_cone),
            run_time=3
        )
        
        # Add in spacetime grid
        self.play(FadeIn(grid_lines, run_time=2))
        
        # Rotate the scene to appreciate 3D structure
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        
        # Add minkowski metric equation
        metric_eq = GlowingMathTex(
            r"ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2",
            glow_factor=0.5
        )
        metric_eq.to_corner(UR)
        
        # Color-code different terms
        metric_eq[0][0:4].set_color(YELLOW)  # ds^2
        metric_eq[0][5:13].set_color(RED)    # -c^2dt^2
        metric_eq[0][14:19].set_color(GREEN) # dx^2
        metric_eq[0][20:25].set_color(BLUE)  # dy^2
        metric_eq[0][26:31].set_color(PURPLE)# dz^2
        
        self.add_fixed_in_frame_mobjects(metric_eq)
        self.play(Write(metric_eq), run_time=2)
        self.wait(1)
        
        ############################################################################
        # 4. ZOOM INTO ORIGIN FOR ELECTROMAGNETIC WAVE
        ############################################################################
        # First set the camera orientation
        self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES, run_time=2)
        # Then fade out the objects
        self.play(
            FadeOut(grid_lines),
            FadeOut(light_cone),
            FadeOut(past_light_cone),
            run_time=2
        )
        
        # Create electromagnetic wave visualization
        em_wave = ElectromagneticWave(
            axes=axes,
            x_range=[-3, 3, 0.05],
            amplitude=1.5,
            wavelength=2,
            e_color=RED_E,
            b_color=BLUE_E
        )
        
        # Create a propagation axis arrow
        prop_arrow = Arrow3D(
            start=axes.c2p(-4, 0, 0),
            end=axes.c2p(4, 0, 0),
            color=YELLOW
        )
        prop_label = GlowingMathTex("\\text{Propagation}", color=YELLOW, glow_factor=0.5)
        prop_label.move_to(axes.c2p(4.5, 0, 0))
        
        # Fade in electromagnetic wave
        self.play(Create(em_wave), run_time=3)
        self.play(
            Create(prop_arrow),
            Write(prop_label),
            run_time=2
        )
        
        # Animate the wave propagation
        for i in range(20):
            phase = i * PI / 10
            em_wave.update_wave(phase)
            self.wait(0.1)
        
        # Display Maxwell's equations
        maxwell_classical = GlowingMathTex(
            r"\begin{aligned}"
            r"\nabla \cdot \vec{E} &= \frac{\rho}{\epsilon_0} \\"
            r"\nabla \cdot \vec{B} &= 0 \\"
            r"\nabla \times \vec{E} &= -\frac{\partial\vec{B}}{\partial t} \\"
            r"\nabla \times \vec{B} &= \mu_0\vec{J} + \mu_0\epsilon_0\frac{\partial\vec{E}}{\partial t}"
            r"\end{aligned}",
            color=WHITE,
            glow_factor=0.5
        )
        maxwell_classical.scale(0.8).to_edge(RIGHT)
        
        maxwell_relativistic = GlowingMathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu",
            color=WHITE,
            glow_factor=0.5
        )
        maxwell_relativistic.next_to(maxwell_classical, DOWN, buff=1)
        
        # Create the caption for the elegant relativistic form
        elegant_caption = GlowingText(
            "Elegant Relativistic Form",
            font_size=24,
            color=YELLOW,
            glow_factor=0.5
        )
        elegant_caption.next_to(maxwell_relativistic, DOWN, buff=0.2)
        
        # Add equations as fixed in frame to avoid 3D transformations
        self.add_fixed_in_frame_mobjects(maxwell_classical)
        self.play(Write(maxwell_classical), run_time=3)
        self.wait(1)
        
        # Transform to relativistic form with dissolve effect
        self.add_fixed_in_frame_mobjects(maxwell_relativistic, elegant_caption)
        self.play(
            FadeIn(maxwell_relativistic),
            FadeIn(elegant_caption),
            FadeOut(maxwell_classical),
            run_time=3
        )
        self.wait(2)
        
        # Clean up before next section
        try:
            self.play(
                FadeOut(em_wave),
                FadeOut(prop_arrow),
                FadeOut(prop_label),
                FadeOut(maxwell_relativistic),
                FadeOut(elegant_caption),
                run_time=2
            )
        except Exception as e:
            # If we're starting from a later animation, some objects might not exist
            # Just wait instead of trying to fade them out
            print(f"Skipping cleanup animation due to: {e}")
            self.wait(2)
        
        ############################################################################
        # 5. QED LAGRANGIAN
        ############################################################################
        # Create a semi-transparent plane for the Lagrangian
        lagrangian_plane = Rectangle(
            width=12,
            height=6,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.7
        )
        
        # Add QED Lagrangian
        qed_lagrangian = GlowingMathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            glow_factor=0.8
        ).scale(0.9)
        
        # Create a VGroup for the Lagrangian
        lagrangian_group = VGroup(lagrangian_plane, qed_lagrangian)
        
        # Color code the different terms
        # Dirac spinor terms
        qed_lagrangian[0][0:11].set_color(ORANGE)  # L_QED
        qed_lagrangian[0][12:14].set_color(ORANGE) # psi-bar
        qed_lagrangian[0][22:23].set_color(ORANGE) # psi
        
        # Gamma matrices
        qed_lagrangian[0][15:17].set_color(TEAL)   # gamma^mu
        
        # Covariant derivative
        qed_lagrangian[0][17:20].set_color(GREEN)  # D_mu
        
        # Field strength tensor
        qed_lagrangian[0][29:38].set_color(GOLD)   # F_μν F^μν
        
        # Add brief explanatory text for each term
        dirac_term_text = Tex("Dirac field term", color=ORANGE).scale(0.6)
        gauge_term_text = Tex("Gauge field term", color=GOLD).scale(0.6)
        interaction_text = Tex("Interaction via covariant derivative", color=GREEN).scale(0.6)
        
        term_texts = VGroup(dirac_term_text, gauge_term_text, interaction_text)
        
        # Position the explanatory texts
        dirac_term_text.next_to(qed_lagrangian, UP, aligned_edge=LEFT, buff=0.5)
        gauge_term_text.next_to(qed_lagrangian, DOWN, aligned_edge=RIGHT, buff=0.5)
        interaction_text.next_to(qed_lagrangian, DOWN, aligned_edge=LEFT, buff=0.5)
        
        # Add to group
        lagrangian_group.add(term_texts)
        
        # Add the lagrangian as fixed in frame
        self.add_fixed_in_frame_mobjects(lagrangian_group)
        
        # Create animations for the Lagrangian
        self.play(
            FadeIn(lagrangian_plane),
            Write(qed_lagrangian),
            run_time=3
        )
        
        # Fade in explanatory texts
        self.play(FadeIn(term_texts, lag_ratio=0.3, run_time=2))
        
        # Create pulsing animation for each term to emphasize
        for i, part in enumerate([
            qed_lagrangian[0][12:23],  # Dirac term
            qed_lagrangian[0][29:38],  # Gauge term
            qed_lagrangian[0][17:20]   # Interaction term
        ]):
            self.play(
                part.animate.scale(1.2).set_color(WHITE),
                run_time=1
            )
            self.play(
                part.animate.scale(1/1.2).set_color(part.get_color()),
                run_time=1
            )
        
        # Add gauge transformation explanation
        gauge_transform_title = Tex("Gauge Transformation", color=YELLOW).scale(0.8)
        gauge_transform_eq = MathTex(
            r"\psi \rightarrow e^{i\alpha(x)}\psi",
            r"\quad",
            r"A_\mu \rightarrow A_\mu - \frac{1}{e}\partial_\mu \alpha(x)"
        ).scale(0.7)
        
        gauge_transform_group = VGroup(gauge_transform_title, gauge_transform_eq)
        gauge_transform_group.arrange(DOWN, buff=0.3)
        gauge_transform_group.to_edge(DOWN, buff=1)
        
        # Add gauge transformation as fixed in frame
        self.add_fixed_in_frame_mobjects(gauge_transform_group)
        
        # Show gauge transformation
        self.play(
            Write(gauge_transform_title),
            Write(gauge_transform_eq),
            run_time=2
        )
        
        # Create a circular arrow to indicate gauge symmetry
        gauge_symmetry_arrow = Arc(
            radius=1.5,
            angle=330 * DEGREES,
            color=YELLOW
        )
        gauge_symmetry_arrow.add_tip(tip_length=0.2)
        gauge_symmetry_arrow.move_to(qed_lagrangian.get_center() + DOWN * 2)
        
        conservation_text = Tex("Enforces charge conservation", color=YELLOW).scale(0.6)
        conservation_text.next_to(gauge_symmetry_arrow, DOWN, buff=0.2)
        
        gauge_symmetry_group = VGroup(gauge_symmetry_arrow, conservation_text)
        
        # Add gauge symmetry as fixed in frame
        self.add_fixed_in_frame_mobjects(gauge_symmetry_group)
        
        # Show gauge symmetry animation
        self.play(
            Create(gauge_symmetry_arrow),
            Write(conservation_text),
            run_time=2
        )
        
        # Wait for a moment to appreciate
        self.wait(2)
        
        # Clean up before next section
        self.play(
            FadeOut(lagrangian_group),
            FadeOut(gauge_transform_group),
            FadeOut(gauge_symmetry_group),
            run_time=2
        )
        
        ############################################################################
        # 6. FEYNMAN DIAGRAM
        ############################################################################
        # Create background for Feynman diagram
        feynman_bg = Rectangle(
            width=12,
            height=6,
            fill_color=BLACK,
            fill_opacity=0.9,
            stroke_color=GRAY,
            stroke_width=1
        )
        
        # Title for the Feynman diagram section
        feynman_title = GlowingText(
            "Quantum Electrodynamics: Particle Interactions",
            font_size=36,
            color=BLUE,
            glow_factor=0.8
        )
        
        # Create the Feynman diagram
        feynman_diagram = FeynmanDiagram(scale=1.5)
        
        # Group elements
        feynman_group = VGroup(feynman_bg, feynman_title, feynman_diagram)
        feynman_group.arrange(DOWN, buff=0.5)
        
        # Add explanation text
        interaction_explanation = GlowingText(
            "Electron-electron scattering via virtual photon exchange",
            font_size=24,
            color=WHITE,
            glow_factor=0.3
        )
        interaction_explanation.next_to(feynman_diagram, DOWN, buff=0.5)
        feynman_group.add(interaction_explanation)
        
        # Add coupling constant
        coupling_title = Tex("Coupling Strength:", color=YELLOW).scale(0.8)
        coupling_numeric = MathTex(r"\alpha \approx \frac{1}{137}", color=WHITE).scale(0.8)
        coupling_symbolic = MathTex(r"\alpha = \frac{e^2}{4\pi\epsilon_0\hbar c}", color=WHITE).scale(0.8)
        
        coupling_group = VGroup(coupling_title, coupling_numeric, coupling_symbolic)
        coupling_group.arrange(RIGHT, buff=0.5)
        coupling_group.next_to(interaction_explanation, DOWN, buff=0.5)
        feynman_group.add(coupling_group)
        
        # Add as fixed in frame
        self.add_fixed_in_frame_mobjects(feynman_group)
        
        # Fade in the Feynman diagram section
        self.play(
            FadeIn(feynman_bg),
            Write(feynman_title),
            run_time=2
        )
        
        # Create the Feynman diagram with a building effect
        self.play(Create(feynman_diagram, run_time=3))
        
        # Add explanation
        self.play(Write(interaction_explanation, run_time=2))
        
        # Show coupling constant
        self.play(
            Write(coupling_title),
            Write(coupling_numeric),
            run_time=1.5
        )
        
        # Transform to symbolic form with flash
        self.play(
            coupling_numeric.animate.set_fill_opacity(0.5),
            TransformFromCopy(coupling_numeric, coupling_symbolic),
            Flash(coupling_symbolic, color=YELLOW, flash_radius=0.8),
            run_time=2
        )
        
        # Hold for a moment
        self.wait(2)
        
        # Clean up before next section
        self.play(FadeOut(feynman_group, run_time=2))
        
        ############################################################################
        # 7. RUNNING COUPLING VISUALIZATION
        ############################################################################
        # Create a graph to show running coupling
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 0.2, 0.05],
            axis_config={"include_tip": True, "numbers_to_exclude": [0]},
            y_axis_config={"include_numbers": True},
            x_axis_config={"include_numbers": True},
        )
        
        axes_labels = axes.get_axis_labels(
            x_label="\\text{Energy Scale (GeV)}",
            y_label="\\alpha(E)"
        )
        
        # Function for running coupling
        def alpha_running(x):
            a0 = 1/137.036
            return a0 * (1 + a0/(3*np.pi) * np.log(x/0.5 + 0.1))
        
        # Create the graph
        running_coupling_graph = axes.plot(
            alpha_running,
            x_range=[0.1, 10],
            color=YELLOW,
            stroke_width=3
        )
        
        # Add data points for experimental verification
        data_points = VGroup()
        for x, y in [(0.5, alpha_running(0.5)), (2, alpha_running(2)), (5, alpha_running(5)), (8, alpha_running(8))]:
            point = Dot(axes.c2p(x, y), color=RED)
            data_points.add(point)
        
        # Create graph title
        graph_title = GlowingText(
            "Running of the Electromagnetic Coupling Constant",
            font_size=36,
            color=BLUE, 
            glow_factor=0.5
        )
        
        # Create caption for vacuum polarization
        vac_pol_caption = Tex(
            "Due to vacuum polarization from virtual $e^+e^-$ pairs",
            color=WHITE
        ).scale(0.7)
        
        # Group everything
        graph_group = VGroup(
            graph_title,
            VGroup(axes, axes_labels, running_coupling_graph, data_points),
            vac_pol_caption
        )
        graph_group.arrange(DOWN, buff=0.5)
        
        # Add as fixed in frame
        self.add_fixed_in_frame_mobjects(graph_group)
        
        # Show the graph
        self.play(
            Write(graph_title),
            Create(axes),
            Write(axes_labels),
            run_time=2
        )
        
        # Draw the graph
        self.play(Create(running_coupling_graph, run_time=3))
        
        # Add data points one by one
        for point in data_points:
            self.play(
                FadeIn(point, scale=1.5),
                Flash(point, color=RED, flash_radius=0.3),
                run_time=0.5
            )
        
        # Add caption
        self.play(FadeIn(vac_pol_caption, run_time=1.5))
        
        # Wait to appreciate
        self.wait(2)
        
        # Clean up
        self.play(FadeOut(graph_group, run_time=2))
        
        ############################################################################
        # 8. FINAL COLLAGE AND CONCLUSION
        ############################################################################
        # Prepare for final collage by resetting camera
        self.move_camera(
            phi=70 * DEGREES,
            theta=-30 * DEGREES,
            run_time=2
        )
        
        # Create small versions of key elements
        mini_spacetime = VGroup(
            ThreeDAxes(
                x_range=[-2, 2],
                y_range=[-2, 2],
                z_range=[-2, 2],
                x_length=4,
                y_length=4,
                z_length=4
            ),
            LightCone(height=1.5, resolution=(21, 21))
        ).scale(0.6).to_edge(LEFT, buff=1)
        
        # Create a simpler version of the wave to avoid gradient issues
        mini_axes = ThreeDAxes(
            x_range=[-2, 2],
            y_range=[-2, 2],
            z_range=[-2, 2],
            x_length=4,
            y_length=4,
            z_length=4
        )
        
        # Create simple sine curves instead of full ElectromagneticWave
        e_curve = ParametricFunction(
            lambda t: mini_axes.c2p(t, 0.8 * np.sin(2*PI*t/1.5), 0),
            t_range=[-2, 2, 0.1],
            color=RED_E,
            stroke_width=2
        )
        
        b_curve = ParametricFunction(
            lambda t: mini_axes.c2p(t, 0, 0.8 * np.sin(2*PI*t/1.5)),
            t_range=[-2, 2, 0.1],
            color=BLUE_E,
            stroke_width=2
        )
        
        mini_wave = VGroup(mini_axes, e_curve, b_curve).scale(0.6).to_edge(RIGHT, buff=1)
        
        # Add elements one by one
        self.play(
            FadeIn(mini_spacetime),
            FadeIn(mini_wave),
            run_time=2
        )
        
        # Create simpler 2D versions of the lagrangian and feynman diagram for the fixed frame
        mini_lagrangian_2d = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}"
        ).scale(0.5)
        
        mini_feynman_2d = VGroup(
            Line(LEFT, ORIGIN, color=BLUE),
            Line(ORIGIN, DOWN+LEFT, color=BLUE),
            Line(RIGHT, ORIGIN, color=BLUE),
            Line(ORIGIN, DOWN+RIGHT, color=BLUE),
            Arc(start_angle=PI, angle=PI, radius=0.5, color=YELLOW)
        ).scale(0.8)
        
        # Create a frame to hold the 2D elements
        frame_2d = Rectangle(width=12, height=3, fill_color=BLACK, fill_opacity=0.5, stroke_width=0)
        frame_2d.to_edge(UP, buff=0.5)
        
        # Position the 2D elements
        mini_lagrangian_2d.move_to(frame_2d.get_center() + UP * 0.5)
        mini_feynman_2d.move_to(frame_2d.get_center() + DOWN * 0.5)
        
        # Group the 2D elements
        collage_2d_group = VGroup(frame_2d, mini_lagrangian_2d, mini_feynman_2d)
        
        # Add as fixed in frame
        self.add_fixed_in_frame_mobjects(collage_2d_group)
        self.play(
            FadeIn(collage_2d_group, run_time=2)
        )
        
        # Add unifying glow
        unified_glow = Circle(
            radius=5,
            stroke_width=1,  # Add a slight stroke
            stroke_color=BLUE_A,
            fill_color=BLUE,
            fill_opacity=0.1
        )
        unified_glow.move_to(ORIGIN)  # Ensure it's properly positioned
        
        # Add unifying glow animation - simplify to avoid rendering issues
        self.play(
            FadeIn(unified_glow),
            run_time=2
        )
        
        # Scale animation as a separate step
        self.play(
            unified_glow.animate.scale(1.2),
            rate_func=there_and_back,
            run_time=2
        )
        
        # Final title
        final_title = GlowingText(
            "QED: Unifying Light and Matter Through Gauge Theory",
            font_size=42,
            color=GOLD,
            glow_factor=1.2
        )
        
        # Conclusion text
        conclusion = Tex(
            "The triumph of quantum field theory:\\\\",
            "describing fundamental forces as gauge field interactions"
        ).scale(0.8)
        
        # Group and position
        final_group = VGroup(final_title, conclusion)
        final_group.arrange(DOWN, buff=0.7)
        final_group.to_edge(DOWN, buff=1)
        
        # Add final title and conclusion
        self.add_fixed_in_frame_mobjects(final_group)
        self.play(
            Write(final_title),
            FadeIn(conclusion),
            run_time=2
        )
        
        # Final camera movement - simplified to avoid rendering issues
        self.move_camera(phi=75 * DEGREES, theta=-20 * DEGREES, run_time=3)
        
        # Wait to appreciate the final scene
        self.wait(2)
        
        # Fade out elements in separate steps to avoid rendering issues
        self.play(
            FadeOut(mini_spacetime),
            FadeOut(mini_wave),
            run_time=1.5
        )
        
        self.play(
            FadeOut(unified_glow),
            FadeOut(collage_2d_group),
            run_time=1.5
        )
        
        self.play(
            FadeOut(final_group),
            run_time=1.5
        )
        
        # Add "Finis" at the end
        finis = GlowingText(
            "Finis",
            font_size=60,
            color=WHITE,
            glow_factor=1.0
        )
        
        self.add_fixed_in_frame_mobjects(finis)
        self.play(FadeIn(finis, run_time=2))


# Define additional scenes if needed for complex sequences
class QEDEquationTransformations(Scene):
    """Standalone scene focusing just on equation transformations"""
    def construct(self):
        # Maxwell's equations transformation
        maxwell_div_e = MathTex(r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}")
        maxwell_div_b = MathTex(r"\nabla \cdot \vec{B} = 0")
        maxwell_curl_e = MathTex(r"\nabla \times \vec{E} = -\frac{\partial\vec{B}}{\partial t}")
        maxwell_curl_b = MathTex(r"\nabla \times \vec{B} = \mu_0\vec{J} + \mu_0\epsilon_0\frac{\partial\vec{E}}{\partial t}")
        
        maxwell_classical = VGroup(
            maxwell_div_e,
            maxwell_div_b,
            maxwell_curl_e,
            maxwell_curl_b
        ).arrange(DOWN, buff=0.5)
        
        # Intermediate form with four-vectors
        maxwell_tensor_components = MathTex(
            r"F^{\mu\nu} = \begin{pmatrix} 0 & -E_x/c & -E_y/c & -E_z/c \\ E_x/c & 0 & -B_z & B_y \\ E_y/c & B_z & 0 & -B_x \\ E_z/c & -B_y & B_x & 0 \end{pmatrix}"
        )
        
        # Final relativistic form
        maxwell_relativistic = MathTex(r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu")
        
        # Title
        title = Text("From Maxwell to Relativistic Electrodynamics")
        title.to_edge(UP)
        
        # Transformation animation
        self.play(Write(title))
        self.play(Write(maxwell_classical))
        self.wait(1)
        
        self.play(
            maxwell_classical.animate.scale(0.7).to_edge(LEFT)
        )
        
        maxwell_tensor_components.scale(0.7).next_to(maxwell_classical, RIGHT, buff=1)
        self.play(FadeIn(maxwell_tensor_components))
        
        maxwell_relativistic.scale(1.2).next_to(maxwell_tensor_components, DOWN, buff=1)
        self.play(
            Write(maxwell_relativistic),
            maxwell_relativistic.animate.set_color(YELLOW)
        )
        
        # Highlight the beauty of the compact form
        elegant_box = SurroundingRectangle(maxwell_relativistic, color=GOLD, buff=0.2)
        elegant_text = Text("Elegant 4D formulation", color=GOLD).scale(0.8)
        elegant_text.next_to(elegant_box, DOWN)
        
        self.play(
            Create(elegant_box),
            Write(elegant_text)
        )