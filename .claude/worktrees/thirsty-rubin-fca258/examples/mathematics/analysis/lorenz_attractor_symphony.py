"""
Lorenz Attractor Symphony: A Journey Through Deterministic Chaos
================================================================

A spectacular 3D visualization of the Lorenz system featuring:
- The iconic "butterfly" strange attractor emerging from chaos
- Multiple trajectories showing sensitivity to initial conditions
- Color-coded particles by velocity (cool=slow, hot=fast)
- Real-time parameter exploration (sigma, rho, beta)
- Mathematical equations with LaTeX rendering
- Cinematic 3D camera movements through the attractor
- Phase space visualization and bifurcation hints

The Lorenz system:
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y  
    dz/dt = x * y - beta * z

With canonical parameters: sigma=10, rho=28, beta=8/3

Render with:
    manim -pqh lorenz_attractor_symphony.py LorenzAttractorSymphony

For 4K quality:
    manim -pqk lorenz_attractor_symphony.py LorenzAttractorSymphony

Author: Math-To-Manim - Celebrating 1400+ Stars!
"""

from manim import *
import numpy as np
from scipy.integrate import odeint

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Lorenz Parameters (canonical values)
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

# Visual Configuration
BACKGROUND_COLOR = "#0a0a1a"  # Deep space blue-black
ATTRACTOR_SCALE = 0.12  # Scale factor for visualization

# Color Palette - Fire to Ice gradient based on velocity
SLOW_COLOR = "#00b4d8"      # Cool cyan
MID_SLOW_COLOR = "#0077b6"  # Ocean blue
MID_COLOR = "#90e0ef"       # Light cyan
MID_FAST_COLOR = "#f77f00"  # Orange
FAST_COLOR = "#d62828"      # Hot red

# Particle Colors for Multiple Trajectories
TRAJECTORY_COLORS = [
    "#ff006e",  # Pink
    "#8338ec",  # Purple
    "#3a86ff",  # Blue
    "#06d6a0",  # Teal
    "#ffd60a",  # Gold
    "#ff5400",  # Orange
]

# ==============================================================================
# LORENZ SYSTEM MATHEMATICS
# ==============================================================================

def lorenz_system(state, t, sigma=SIGMA, rho=RHO, beta=BETA):
    """
    The Lorenz system of ordinary differential equations.
    
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z
    """
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


def generate_lorenz_trajectory(initial_condition, t_span, n_points=10000):
    """Generate a trajectory through the Lorenz attractor."""
    t = np.linspace(0, t_span, n_points)
    trajectory = odeint(lorenz_system, initial_condition, t)
    return trajectory, t


def compute_velocity(trajectory, t):
    """Compute velocity magnitude at each point for color mapping."""
    dt = t[1] - t[0]
    velocities = np.zeros(len(trajectory))
    for i in range(1, len(trajectory) - 1):
        dx = (trajectory[i+1, 0] - trajectory[i-1, 0]) / (2 * dt)
        dy = (trajectory[i+1, 1] - trajectory[i-1, 1]) / (2 * dt)
        dz = (trajectory[i+1, 2] - trajectory[i-1, 2]) / (2 * dt)
        velocities[i] = np.sqrt(dx**2 + dy**2 + dz**2)
    velocities[0] = velocities[1]
    velocities[-1] = velocities[-2]
    return velocities


def trajectory_to_manim_points(trajectory, scale=ATTRACTOR_SCALE, center_z=0):
    """Convert Lorenz trajectory to Manim 3D coordinates."""
    points = []
    # Center the attractor (z typically ranges 0-50, x/y around +/-20)
    z_offset = 25  # Center z around this value
    for x, y, z in trajectory:
        points.append([
            x * scale,
            y * scale,
            (z - z_offset) * scale + center_z
        ])
    return np.array(points)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def create_starfield(n_stars=2000, radius=50):
    """Create a 3D starfield background."""
    np.random.seed(42)
    stars = VGroup()
    
    for _ in range(n_stars):
        # Spherical distribution
        theta = np.random.uniform(0, TAU)
        phi = np.random.uniform(0, PI)
        r = np.random.uniform(radius * 0.5, radius)
        
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # Random star properties
        star_radius = np.random.uniform(0.01, 0.04)
        opacity = np.random.uniform(0.2, 0.8)
        
        star = Dot3D(point=[x, y, z], radius=star_radius, color=WHITE)
        star.set_opacity(opacity)
        stars.add(star)
    
    return stars


def velocity_to_color(velocity, v_min, v_max):
    """Map velocity to color using a fire-ice gradient."""
    # Normalize velocity to [0, 1]
    t = (velocity - v_min) / (v_max - v_min + 1e-6)
    t = np.clip(t, 0, 1)
    
    # Convert hex strings to ManimColor objects
    slow = ManimColor(SLOW_COLOR)
    mid_slow = ManimColor(MID_SLOW_COLOR)
    mid = ManimColor(MID_COLOR)
    mid_fast = ManimColor(MID_FAST_COLOR)
    fast = ManimColor(FAST_COLOR)
    
    # Create gradient: cyan -> blue -> white -> orange -> red
    if t < 0.25:
        return interpolate_color(slow, mid_slow, t / 0.25)
    elif t < 0.5:
        return interpolate_color(mid_slow, mid, (t - 0.25) / 0.25)
    elif t < 0.75:
        return interpolate_color(mid, mid_fast, (t - 0.5) / 0.25)
    else:
        return interpolate_color(mid_fast, fast, (t - 0.75) / 0.25)


def create_velocity_colored_curve(trajectory, velocities, scale=ATTRACTOR_SCALE, 
                                   segment_length=50):
    """Create a curve colored by velocity with proper segments."""
    points = trajectory_to_manim_points(trajectory, scale)
    v_min, v_max = np.min(velocities), np.max(velocities)
    
    curves = VGroup()
    n_segments = len(points) // segment_length
    
    for i in range(n_segments):
        start_idx = i * segment_length
        end_idx = min((i + 1) * segment_length + 1, len(points))
        
        if end_idx - start_idx < 2:
            continue
            
        segment_points = points[start_idx:end_idx]
        avg_velocity = np.mean(velocities[start_idx:end_idx])
        color = velocity_to_color(avg_velocity, v_min, v_max)
        
        curve = VMobject()
        curve.set_points_smoothly(segment_points)
        curve.set_stroke(color, width=2.5, opacity=0.9)
        curves.add(curve)
    
    return curves


# ==============================================================================
# MAIN SCENE
# ==============================================================================

class LorenzAttractorSymphony(ThreeDScene):
    """
    A spectacular visualization of the Lorenz strange attractor.
    
    Features:
    - Mathematical equations introducing the system
    - Emergence of chaos from simple ODEs
    - Multiple trajectories showing sensitivity to initial conditions
    - Velocity-based color mapping
    - Cinematic 3D camera movements
    """
    
    def construct(self):
        # =====================================================================
        # SETUP
        # =====================================================================
        self.camera.background_color = BACKGROUND_COLOR
        
        # Initial camera - wide view
        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.5,
            frame_center=ORIGIN
        )
        
        # Create starfield
        stars = create_starfield()
        self.add(stars)
        
        # =====================================================================
        # PHASE 1: TITLE AND INTRODUCTION
        # =====================================================================
        
        title = Text(
            "The Lorenz Attractor",
            font_size=72,
            weight=BOLD
        ).set_color_by_gradient("#ff006e", "#8338ec", "#3a86ff")
        
        subtitle = Text(
            "A Symphony of Deterministic Chaos",
            font_size=36
        ).set_color_by_gradient(GRAY_A, WHITE)
        
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        title_group.to_edge(UP, buff=1)
        
        self.add_fixed_in_frame_mobjects(title_group)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1.5)
        self.wait(2)
        
        # Shrink title to corner
        small_title = title.copy().scale(0.25).to_corner(UL, buff=0.3)
        self.play(
            Transform(title, small_title),
            FadeOut(subtitle),
            run_time=2
        )
        
        # =====================================================================
        # PHASE 2: THE MATHEMATICS - LORENZ EQUATIONS
        # =====================================================================
        
        # The Lorenz system equations
        equations_title = Text("The Lorenz System (1963)", font_size=32, color=WHITE)
        equations_title.to_edge(UP, buff=0.8)
        
        # Individual equations
        eq1 = MathTex(
            r"\frac{dx}{dt} = \sigma (y - x)",
            font_size=38
        )
        eq2 = MathTex(
            r"\frac{dy}{dt} = x(\rho - z) - y",
            font_size=38
        )
        eq3 = MathTex(
            r"\frac{dz}{dt} = xy - \beta z",
            font_size=38
        )
        
        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.4)
        equations.next_to(equations_title, DOWN, buff=0.5)
        
        # Color code the parameters
        eq1[0][4:5].set_color("#ff006e")  # sigma
        eq2[0][5:6].set_color("#3a86ff")  # rho
        eq3[0][6:7].set_color("#06d6a0")  # beta
        
        self.add_fixed_in_frame_mobjects(equations_title, equations)
        self.play(Write(equations_title), run_time=1)
        self.play(
            Write(eq1, run_time=1.5),
            Write(eq2, run_time=1.5),
            Write(eq3, run_time=1.5),
            lag_ratio=0.3
        )
        self.wait(1)
        
        # Parameter values
        params = MathTex(
            r"\sigma = 10, \quad \rho = 28, \quad \beta = \frac{8}{3}",
            font_size=32
        )
        params[0][0:1].set_color("#ff006e")
        params[0][5:6].set_color("#3a86ff")
        params[0][11:12].set_color("#06d6a0")
        params.to_corner(UR, buff=0.5)
        
        self.add_fixed_in_frame_mobjects(params)
        self.play(Write(params), run_time=1.5)
        self.wait(2)
        
        # Move equations to corner
        equations_small = VGroup(eq1, eq2, eq3).copy().scale(0.5)
        equations_small.to_corner(DR, buff=0.3)
        
        self.play(
            FadeOut(equations_title),
            Transform(equations, equations_small),
            run_time=2
        )
        
        # =====================================================================
        # PHASE 3: BIRTH OF THE ATTRACTOR - SINGLE TRAJECTORY
        # =====================================================================
        
        # Generate first trajectory
        initial_1 = [1.0, 1.0, 1.0]
        trajectory_1, t = generate_lorenz_trajectory(initial_1, t_span=50, n_points=15000)
        velocities_1 = compute_velocity(trajectory_1, t)
        
        # Create the colored curve
        attractor_curve = create_velocity_colored_curve(trajectory_1, velocities_1)
        
        # Emergence text
        emergence_text = Text(
            "From simple equations...",
            font_size=28,
            color=WHITE
        ).to_edge(DOWN, buff=0.5)
        
        self.add_fixed_in_frame_mobjects(emergence_text)
        self.play(FadeIn(emergence_text))
        
        # Camera adjustment for better view
        self.move_camera(
            phi=65 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.6,
            run_time=2
        )
        
        # Draw the attractor emerging - this is the money shot
        self.play(
            Create(attractor_curve, lag_ratio=0.001, run_time=12),
            rate_func=linear
        )
        
        # Update text
        emergence_text_2 = Text(
            "...emerges infinite complexity",
            font_size=28,
            color=WHITE
        ).to_edge(DOWN, buff=0.5)
        
        self.play(
            FadeOut(emergence_text),
            FadeIn(emergence_text_2)
        )
        
        # Begin rotation to show 3D structure
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        
        self.play(FadeOut(emergence_text_2))
        
        # =====================================================================
        # PHASE 4: BUTTERFLY EFFECT - MULTIPLE TRAJECTORIES
        # =====================================================================
        
        butterfly_text = Text(
            "The Butterfly Effect: Sensitivity to Initial Conditions",
            font_size=32,
            color=WHITE
        ).to_edge(UP, buff=0.3)
        
        self.add_fixed_in_frame_mobjects(butterfly_text)
        self.play(FadeIn(butterfly_text))
        
        # Create multiple trajectories with slightly different initial conditions
        epsilon = 0.001  # Tiny perturbation
        initial_conditions = [
            [1.0, 1.0, 1.0],
            [1.0 + epsilon, 1.0, 1.0],
            [1.0, 1.0 + epsilon, 1.0],
            [1.0, 1.0, 1.0 + epsilon],
        ]
        
        additional_curves = VGroup()
        
        for i, ic in enumerate(initial_conditions[1:]):  # Skip first (already drawn)
            traj, t_arr = generate_lorenz_trajectory(ic, t_span=40, n_points=10000)
            points = trajectory_to_manim_points(traj)
            
            curve = VMobject()
            curve.set_points_smoothly(points)
            curve.set_stroke(
                TRAJECTORY_COLORS[(i + 1) % len(TRAJECTORY_COLORS)],
                width=1.5,
                opacity=0.7
            )
            additional_curves.add(curve)
        
        # Fade the original slightly and add new trajectories
        self.play(
            attractor_curve.animate.set_opacity(0.3),
            run_time=1
        )
        
        self.play(
            *[Create(c, run_time=8) for c in additional_curves],
            rate_func=linear
        )
        
        # Divergence annotation
        diverge_note = MathTex(
            r"\Delta x_0 = 10^{-3} \Rightarrow \text{Divergent Futures}",
            font_size=28,
            color=YELLOW
        ).to_edge(DOWN, buff=0.5)
        
        self.add_fixed_in_frame_mobjects(diverge_note)
        self.play(Write(diverge_note))
        
        # Cinematic camera sweep
        self.move_camera(
            phi=80 * DEGREES,
            theta=45 * DEGREES,
            zoom=0.5,
            run_time=4
        )
        self.wait(2)
        
        self.move_camera(
            phi=50 * DEGREES,
            theta=-90 * DEGREES,
            zoom=0.7,
            run_time=4
        )
        self.wait(2)
        
        # =====================================================================
        # PHASE 5: FLY-THROUGH THE ATTRACTOR
        # =====================================================================
        
        self.play(
            FadeOut(butterfly_text),
            FadeOut(diverge_note)
        )
        
        flythrough_text = Text(
            "Journey Through the Strange Attractor",
            font_size=32,
            color=WHITE
        ).to_edge(UP, buff=0.3)
        
        self.add_fixed_in_frame_mobjects(flythrough_text)
        self.play(FadeIn(flythrough_text))
        
        # Dramatic zoom into the attractor
        self.move_camera(
            phi=70 * DEGREES,
            theta=0,
            zoom=1.2,
            frame_center=[0, 0, 0.5],
            run_time=4
        )
        
        # Fly around inside
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        
        # Pull back out
        self.move_camera(
            phi=65 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.5,
            frame_center=ORIGIN,
            run_time=3
        )
        
        self.play(FadeOut(flythrough_text))
        
        # =====================================================================
        # PHASE 6: THE MATHEMATICS OF CHAOS
        # =====================================================================
        
        # Clear trajectories for cleaner view
        self.play(
            FadeOut(additional_curves),
            attractor_curve.animate.set_opacity(0.8),
            run_time=2
        )
        
        # Lyapunov exponent
        lyapunov_title = Text(
            "The Lyapunov Exponent: Quantifying Chaos",
            font_size=32,
            color=WHITE
        ).to_edge(UP, buff=0.3)
        
        lyapunov_eq = MathTex(
            r"\lambda = \lim_{t \to \infty} \frac{1}{t} \ln \frac{|\delta \mathbf{x}(t)|}{|\delta \mathbf{x}_0|}",
            font_size=36
        )
        lyapunov_eq.next_to(lyapunov_title, DOWN, buff=0.3)
        
        lyapunov_value = MathTex(
            r"\lambda_{\max} \approx 0.906 > 0 \implies \text{Chaos}",
            font_size=30,
            color=YELLOW
        )
        lyapunov_value.next_to(lyapunov_eq, DOWN, buff=0.2)
        
        self.add_fixed_in_frame_mobjects(lyapunov_title, lyapunov_eq, lyapunov_value)
        self.play(Write(lyapunov_title), run_time=1)
        self.play(Write(lyapunov_eq), run_time=2)
        self.play(Write(lyapunov_value), run_time=1.5)
        
        # Gentle rotation while showing math
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.play(
            FadeOut(lyapunov_title),
            FadeOut(lyapunov_eq),
            FadeOut(lyapunov_value)
        )
        
        # =====================================================================
        # PHASE 7: GRAND FINALE - FULL SPECTACLE
        # =====================================================================
        
        finale_text = Text(
            "Deterministic Yet Unpredictable",
            font_size=42,
            weight=BOLD
        ).set_color_by_gradient("#ff006e", "#3a86ff", "#06d6a0")
        finale_text.to_edge(DOWN, buff=0.8)
        
        self.add_fixed_in_frame_mobjects(finale_text)
        self.play(Write(finale_text), run_time=2)
        
        # Bring back all trajectories at full opacity
        self.play(
            attractor_curve.animate.set_opacity(1.0),
            FadeIn(additional_curves.set_opacity(0.8)),
            run_time=2
        )
        
        # Epic camera rotation
        self.move_camera(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.45,
            run_time=3
        )
        
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(10)
        self.stop_ambient_camera_rotation()
        
        # =====================================================================
        # PHASE 8: FADE TO COSMOS
        # =====================================================================
        
        # Quote
        quote = Text(
            '"Does the flap of a butterfly\'s wings in Brazil\nset off a tornado in Texas?"',
            font_size=24,
            slant=ITALIC
        ).set_color(GRAY_A)
        quote.to_edge(UP, buff=0.5)
        
        attribution = Text(
            "- Edward Lorenz, 1972",
            font_size=20,
            color=GRAY_B
        )
        attribution.next_to(quote, DOWN, buff=0.2)
        
        self.play(FadeOut(finale_text))
        self.add_fixed_in_frame_mobjects(quote, attribution)
        self.play(
            FadeIn(quote),
            FadeIn(attribution),
            run_time=2
        )
        
        self.wait(4)
        
        # Fade everything
        self.play(
            *[FadeOut(mob) for mob in [attractor_curve, additional_curves, 
                                        quote, attribution, title, equations, params]],
            stars.animate.set_opacity(0.3),
            run_time=4
        )
        
        # Final title
        finis = Text(
            "Chaos",
            font_size=96,
            weight=BOLD
        ).set_color_by_gradient("#ff006e", "#8338ec", "#3a86ff")
        
        self.add_fixed_in_frame_mobjects(finis)
        self.play(Write(finis), run_time=2)
        self.wait(2)
        self.play(FadeOut(finis), FadeOut(stars), run_time=3)


# ==============================================================================
# ADDITIONAL EDUCATIONAL SCENES
# ==============================================================================

class LorenzBifurcation(ThreeDScene):
    """
    Visualize how the Lorenz attractor changes with the rho parameter.
    Shows transition from fixed point to limit cycle to strange attractor.
    """
    
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.6)
        
        title = Text("Bifurcation: The Road to Chaos", font_size=48)
        title.set_color_by_gradient("#ff006e", "#3a86ff")
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Different rho values showing different behaviors
        rho_values = [0.5, 13.9, 24.74, 28]
        labels = ["Fixed Point", "Limit Cycle", "Transient Chaos", "Strange Attractor"]
        
        for rho_val, label in zip(rho_values, labels):
            # Generate trajectory
            def lorenz_custom(state, t):
                x, y, z = state
                return [
                    SIGMA * (y - x),
                    x * (rho_val - z) - y,
                    x * y - BETA * z
                ]
            
            t = np.linspace(0, 50, 10000)
            traj = odeint(lorenz_custom, [1, 1, 1], t)
            points = trajectory_to_manim_points(traj)
            
            curve = VMobject()
            curve.set_points_smoothly(points)
            curve.set_stroke(TRAJECTORY_COLORS[rho_values.index(rho_val) % len(TRAJECTORY_COLORS)],
                           width=2, opacity=0.9)
            
            # Label
            rho_label = MathTex(f"\\rho = {rho_val}", font_size=36)
            rho_label.to_corner(UR)
            behavior_label = Text(label, font_size=28, color=WHITE)
            behavior_label.to_edge(DOWN)
            
            self.add_fixed_in_frame_mobjects(rho_label, behavior_label)
            self.play(
                FadeIn(rho_label),
                FadeIn(behavior_label),
                Create(curve, run_time=6),
                rate_func=linear
            )
            
            self.begin_ambient_camera_rotation(rate=0.1)
            self.wait(3)
            self.stop_ambient_camera_rotation()
            
            self.play(
                FadeOut(curve),
                FadeOut(rho_label),
                FadeOut(behavior_label)
            )
        
        self.play(FadeOut(title))


class LorenzPhaseSpace(ThreeDScene):
    """
    Show the Lorenz attractor with 3D axes and labeled coordinates.
    Educational view for understanding the phase space.
    """
    
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.5)
        
        # 3D Axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            z_length=6,
        )
        
        # Labels
        x_label = MathTex("x", font_size=36).next_to(axes.x_axis, RIGHT)
        y_label = MathTex("y", font_size=36).next_to(axes.y_axis, UP)
        z_label = MathTex("z", font_size=36).next_to(axes.z_axis, OUT)
        
        labels = VGroup(x_label, y_label, z_label)
        
        self.play(Create(axes), Write(labels))
        
        # Generate trajectory
        traj, t = generate_lorenz_trajectory([1, 1, 1], t_span=50, n_points=12000)
        velocities = compute_velocity(traj, t)
        attractor = create_velocity_colored_curve(traj, velocities)
        
        title = Text("Lorenz Phase Space", font_size=48, color=WHITE)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        self.play(Create(attractor, lag_ratio=0.001, run_time=10), rate_func=linear)
        
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(8)
        self.stop_ambient_camera_rotation()
        
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=3
        )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    scene = LorenzAttractorSymphony()
    scene.render()
