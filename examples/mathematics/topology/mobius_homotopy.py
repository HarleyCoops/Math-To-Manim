"""
Möbius Strip Homotopy Equivalence Visualization

Demonstrates the deformation retraction proving that a Möbius band
is homotopy equivalent to a circle (S¹). The animation shows how
the strip continuously contracts to its central circle using the
deformation retraction formula:

    f_t(x, y) = ((1/2 - x)t + x, y)

This visualization helps understand one of topology's fundamental
examples of homotopy equivalence.

Features:
- 3D parametric Möbius surface with always_redraw for smooth deformation
- Camera-facing S¹ label that follows ambient rotation
- Visual fiber lines to show the retraction clearly
- Enhanced visuals with grid lines and opacity
"""

from manim import *
import numpy as np


class MobiusHomotopyProof(ThreeDScene):
    def construct(self):
        # 1. Setup Scene and Camera
        # Start with a slightly higher view to see the band structure better
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        # Slow rotation to show 3D structure
        self.begin_ambient_camera_rotation(rate=0.08)

        # 2. Text and Formula Setup
        title = Text("Homotopy Equivalence: Möbius Band ≃ Circle", font_size=32)
        title.to_corner(UL)
        # Fix text to screen so it doesn't rotate with the camera
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))

        formula_text = VGroup(
            Text("Deformation Retraction:", font_size=24),
            MathTex(
                r"f_t(x, y) = \left( \left(\frac{1}{2} - x\right)t + x, \; y \right)",
                font_size=30
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        formula_text.to_corner(DL).shift(RIGHT * 0.5)

        self.add_fixed_in_frame_mobjects(formula_text)
        self.play(FadeIn(formula_text))

        # 3. Create the 3D Mobius Strip and controls
        # This tracker controls the "width" multiplier of the strip.
        # 1.0 = full width, 0.0 = collapsed to line.
        width_tracker = ValueTracker(1.0)

        # The central radius of the strip
        R = 3.0

        # We define the surface generation function depending on the tracker value.
        # We use always_redraw so Manim regenerates it every frame.
        mobius_strip = always_redraw(lambda: Surface(
            lambda u, v: np.array([
                # The standard parametric equation for a Mobius strip embedded in 3D
                # u goes around the ring (0 to 2pi)
                # v is the width (-1 to 1)
                # width_tracker.get_value() scales v, controlling the total width
                (R + width_tracker.get_value() * v * np.cos(u / 2)) * np.cos(u),
                (R + width_tracker.get_value() * v * np.cos(u / 2)) * np.sin(u),
                width_tracker.get_value() * v * np.sin(u / 2)
            ]),
            u_range=[0, 2 * PI],
            v_range=[-0.7, 0.7],  # Slightly narrower range for better visuals
            checkerboard_colors=[BLUE_D, BLUE_E],
            resolution=(50, 16),  # Higher resolution for smoother deformation
            stroke_width=0.5,  # Add thin lines to see the grid better
            stroke_color=BLUE_A,
            fill_opacity=0.8
        ))

        self.play(Create(mobius_strip), run_time=3)
        self.wait(0.5)

        # 4. Highlight the Central Circle (The core S1)
        # This is where width v = 0
        central_circle = ParametricFunction(
            lambda u: np.array([
                R * np.cos(u),
                R * np.sin(u),
                0
            ]),
            t_range=[0, 2 * PI + 0.1],  # Slight overlap to close the loop nicely
            color=RED_E,
            stroke_width=8
        )
        self.play(Create(central_circle))

        # Label the central circle - fixed in frame for readability
        circle_label = MathTex("S^1", color=RED_E).scale(1.5)
        circle_label.to_corner(UR)
        self.add_fixed_in_frame_mobjects(circle_label)
        self.play(Write(circle_label))

        # VISUAL HELPER: Add "fibers" (lines across the width) to see them shrink
        # Fiber at angle u=0
        fiber1 = always_redraw(lambda: Line(
            start=np.array([R + width_tracker.get_value() * 0.7, 0, 0]),
            end=np.array([R - width_tracker.get_value() * 0.7, 0, 0]),
            color=RED_B, stroke_width=5
        ))
        # Fiber at angle u=pi (showing the twist, as z coordinate is involved)
        fiber2 = always_redraw(lambda: Line(
            start=np.array([-(R + 0), 0, width_tracker.get_value() * 0.7]),
            end=np.array([-(R - 0), 0, -width_tracker.get_value() * 0.7]),
            color=RED_B, stroke_width=5
        ))
        self.play(Create(fiber1), Create(fiber2))
        self.wait(1)

        # 5. Animate the Retraction (Homotopy)
        # Because we used always_redraw on the strip and fibers,
        # animating the tracker will automatically animate the geometry.
        self.play(
            width_tracker.animate.set_value(0),
            run_time=6,
            rate_func=smooth
        )

        # 6. Conclusion
        # The strip has collapsed onto the circle
        conclusion = Text("Strip retracted to central circle S¹", font_size=24, color=YELLOW)
        conclusion.next_to(formula_text, UP, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(conclusion)
        self.play(Write(conclusion))

        self.wait(4)
