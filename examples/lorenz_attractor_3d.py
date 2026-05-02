"""
Lorenz Attractor — 3D Manim visualization with color-changing particle trails.
Render: manim -pqh examples/lorenz_attractor_3d.py LorenzAttractor3D
"""
from manim import *
import numpy as np

class LorenzAttractor3D(ThreeDScene):
    def construct(self):
        # Lorenz parameters
        sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
        dt = 0.005
        num_steps = 8000

        # Integrate Lorenz system
        points = np.zeros((num_steps, 3))
        points[0] = [1.0, 1.0, 1.0]
        for i in range(1, num_steps):
            x, y, z = points[i - 1]
            dx = sigma * (y - x) * dt
            dy = (x * (rho - z) - y) * dt
            dz = (x * y - beta * z) * dt
            points[i] = [x + dx, y + dy, z + dz]

        # Scale to fit scene
        points = points / 15.0

        # Camera setup
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.6)
        self.begin_ambient_camera_rotation(rate=0.15)

        # Build colored segments
        colors = color_gradient([BLUE, TEAL, GREEN, YELLOW, ORANGE, RED, PURPLE], num_steps)

        # Draw trail in chunks for animation
        chunk_size = 200
        trail = VGroup()

        for start in range(0, num_steps - 1, chunk_size):
            end = min(start + chunk_size, num_steps - 1)
            segment_points = [
                np.array([points[i][0], points[i][2] - 1.5, points[i][1]])
                for i in range(start, end + 1)
            ]
            if len(segment_points) < 2:
                continue

            line = VMobject()
            line.set_points_smoothly(segment_points)
            line.set_stroke(
                color=colors[start],
                width=1.5,
                opacity=0.9
            )
            trail.add(line)

        # Title
        title = Text("Lorenz Attractor", font_size=36, color=WHITE)
        title.to_corner(UL)
        title.fix_in_frame()

        subtitle = Text("dx/dt = σ(y-x),  dy/dt = x(ρ-z)-y,  dz/dt = xy-βz",
                        font_size=18, color=GREY_B)
        subtitle.next_to(title, DOWN, aligned_edge=LEFT)
        subtitle.fix_in_frame()

        # Axes
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-1, 4, 1],
            z_range=[-2.5, 2.5, 1],
            x_length=5, y_length=5, z_length=5,
        ).set_stroke(opacity=0.2)

        self.add(axes)
        self.play(Write(title), Write(subtitle), run_time=1)

        # Animate trail drawing
        for segment in trail:
            self.play(Create(segment), run_time=0.08, rate_func=linear)

        # Hold and rotate
        self.wait(3)

        # Fade out
        self.play(
            FadeOut(trail),
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(axes),
            run_time=2
        )
        self.wait(0.5)
