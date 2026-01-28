"""
Fourier Transform as Epicycles - Manim Animation
Demonstrates how any shape can be drawn by stacking rotating circles (epicycles).
"""

from manim import *
import numpy as np

# Color Palette
BG_COLOR = "#F5F0E6"
PRIMARY = "#1A1A1A"
ORANGE = "#E85D04"
TEAL = "#0077B6"
PURPLE = "#7B2CBF"
LABEL_COLOR = "#555555"

# Font - use Consolas as fallback (available on Windows)
MONO_FONT = "Consolas"


class FourierEpicycles(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # Run all scenes
        self.scene1_circular_motion()
        self.scene2_sine_projection()
        self.scene3_complex_rotation()
        self.scene4_stacking_epicycles()
        self.scene5_drawing_shape()

    def scene1_circular_motion(self):
        """Scene 1: Circular Motion (0:00 - 0:25)"""
        # Set initial camera angle
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        # Create unit circle
        circle = Circle(radius=2, color=PRIMARY, stroke_width=3)
        circle.move_to(ORIGIN)

        self.play(Create(circle), run_time=1.5)

        # Create rotating dot and radius vector
        angle_tracker = ValueTracker(0)

        dot = always_redraw(
            lambda: Dot(
                point=circle.point_at_angle(angle_tracker.get_value()),
                color=ORANGE,
                radius=0.1
            )
        )

        radius_line = always_redraw(
            lambda: Line(
                ORIGIN,
                circle.point_at_angle(angle_tracker.get_value()),
                color=ORANGE,
                stroke_width=4
            )
        )

        self.play(FadeIn(dot), Create(radius_line))

        # Display equation
        equation = MathTex(r"e^{i\theta}", color=PRIMARY, font_size=48)
        equation.to_corner(UR)
        self.add_fixed_in_frame_mobjects(equation)
        self.play(Write(equation), run_time=1)

        # Frequency label
        freq_label = Text(
            "frequency = 1 revolution",
            font=MONO_FONT,
            font_size=20,
            color=LABEL_COLOR
        )
        freq_label.next_to(equation, DOWN)
        self.add_fixed_in_frame_mobjects(freq_label)
        self.play(FadeIn(freq_label))

        # Rotate the dot one full revolution
        self.play(
            angle_tracker.animate.set_value(TAU),
            run_time=4,
            rate_func=linear
        )

        self.wait(1)

        # Store for transition
        self.circle = circle
        self.dot = dot
        self.radius_line = radius_line
        self.angle_tracker = angle_tracker
        self.equation = equation
        self.freq_label = freq_label

    def scene2_sine_projection(self):
        """Scene 2: Sine Wave as Projection (0:25 - 0:50)"""
        # Move camera to side view
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=2)

        # Create axes for sine wave on the right
        axes = Axes(
            x_range=[0, 4 * PI, PI],
            y_range=[-2.5, 2.5, 1],
            x_length=6,
            y_length=4,
            axis_config={"color": PRIMARY, "stroke_width": 2},
        )
        axes.shift(RIGHT * 4)

        # Fade out old equation and label
        self.play(
            FadeOut(self.equation),
            FadeOut(self.freq_label),
        )
        self.remove_fixed_in_frame_mobjects(self.equation, self.freq_label)

        self.play(Create(axes), run_time=1)

        # Reset angle tracker
        self.angle_tracker.set_value(0)

        # Track the previous angle to avoid redrawing when not moving
        self.prev_sine_angle = 0

        # Create traced sine path with initial point
        sine_path = VMobject(color=ORANGE, stroke_width=3)
        initial_point = axes.c2p(0, 0)
        sine_path.start_new_path(initial_point)

        def update_sine(mob):
            angle = self.angle_tracker.get_value()
            # Only add points when angle has changed
            if angle > self.prev_sine_angle and angle <= 4 * PI:
                y_val = 2 * np.sin(angle)
                x_val = angle
                new_point = axes.c2p(x_val, y_val)
                mob.add_line_to(new_point)
                self.prev_sine_angle = angle

        sine_path.add_updater(update_sine)
        self.add(sine_path)

        # Projection line
        projection_line = always_redraw(
            lambda: DashedLine(
                self.circle.point_at_angle(self.angle_tracker.get_value()),
                axes.c2p(
                    min(self.angle_tracker.get_value(), 4 * PI),
                    2 * np.sin(self.angle_tracker.get_value())
                ),
                color=LABEL_COLOR,
                stroke_width=2
            )
        )
        self.add(projection_line)

        # Display sine equation
        sine_eq = MathTex(r"y = \sin(\theta)", color=PRIMARY, font_size=36)
        sine_eq.move_to(axes.get_top() + UP * 0.5)
        self.add_fixed_in_frame_mobjects(sine_eq)
        self.play(Write(sine_eq), run_time=1)

        # Projection label
        proj_label = Text(
            "projection of rotation",
            font=MONO_FONT,
            font_size=18,
            color=LABEL_COLOR
        )
        proj_label.next_to(axes, DOWN)
        self.add_fixed_in_frame_mobjects(proj_label)
        self.play(FadeIn(proj_label))

        # Rotate twice while drawing sine
        self.play(
            self.angle_tracker.animate.set_value(4 * PI),
            run_time=5,
            rate_func=linear
        )

        sine_path.remove_updater(update_sine)

        self.wait(2)

        # Fade out sine elements
        self.play(
            FadeOut(axes),
            FadeOut(sine_path),
            FadeOut(projection_line),
            FadeOut(sine_eq),
            FadeOut(proj_label),
        )
        self.remove_fixed_in_frame_mobjects(sine_eq, proj_label)

    def scene3_complex_rotation(self):
        """Scene 3: Complex Rotation & Multiple Frequencies (0:50 - 1:15)"""
        # Return to 3D view
        self.move_camera(phi=70 * DEGREES, theta=-60 * DEGREES, run_time=2)

        # Reset angle tracker
        self.angle_tracker.set_value(0)

        # Display complex exponential equation
        complex_eq = MathTex(r"z = r \cdot e^{i \cdot n \cdot t}", color=PRIMARY, font_size=42)
        complex_eq.to_edge(UP)
        self.add_fixed_in_frame_mobjects(complex_eq)
        self.play(Write(complex_eq), run_time=1)

        # Parameters for the two circles
        r1, r2 = 2, 1.2
        freq1, freq2 = 1, 2

        # Second circle (teal) attached to first vector's tip
        circle2 = always_redraw(
            lambda: Circle(
                radius=r2,
                color=TEAL,
                stroke_width=2
            ).move_to(self.circle.point_at_angle(self.angle_tracker.get_value()))
        )

        # Second dot on second circle
        dot2 = always_redraw(
            lambda: Dot(
                point=self.circle.point_at_angle(self.angle_tracker.get_value()) +
                      r2 * np.array([
                          np.cos(freq2 * self.angle_tracker.get_value()),
                          np.sin(freq2 * self.angle_tracker.get_value()),
                          0
                      ]),
                color=TEAL,
                radius=0.08
            )
        )

        # Second radius line
        radius2 = always_redraw(
            lambda: Line(
                self.circle.point_at_angle(self.angle_tracker.get_value()),
                self.circle.point_at_angle(self.angle_tracker.get_value()) +
                r2 * np.array([
                    np.cos(freq2 * self.angle_tracker.get_value()),
                    np.sin(freq2 * self.angle_tracker.get_value()),
                    0
                ]),
                color=TEAL,
                stroke_width=3
            )
        )

        self.play(Create(circle2), FadeIn(dot2), Create(radius2))

        # Create traced path for combined motion
        traced_path = TracedPath(
            dot2.get_center,
            stroke_color=PRIMARY,
            stroke_width=2
        )
        self.add(traced_path)

        # Animate both circles
        self.play(
            self.angle_tracker.animate.set_value(TAU),
            run_time=3,
            rate_func=linear
        )

        # Update equation
        new_eq = MathTex(r"z = r_1 e^{it} + r_2 e^{i \cdot 2t}", color=PRIMARY, font_size=42)
        new_eq.to_edge(UP)
        self.add_fixed_in_frame_mobjects(new_eq)
        self.play(
            FadeOut(complex_eq),
            FadeIn(new_eq),
            run_time=1
        )
        self.remove_fixed_in_frame_mobjects(complex_eq)

        self.wait(2)

        # Clear traced path
        self.play(FadeOut(traced_path))

        # Store elements for next scene
        self.circle2 = circle2
        self.dot2 = dot2
        self.radius2 = radius2
        self.r1, self.r2 = r1, r2
        self.current_eq = new_eq

    def scene4_stacking_epicycles(self):
        """Scene 4: Stacking Epicycles (1:15 - 1:40)"""
        # Reset angle
        self.angle_tracker.set_value(0)

        # Parameters for all 4 circles
        radii = [2, 1.2, 0.7, 0.4]
        freqs = [1, 2, 3, -2]
        colors = [ORANGE, TEAL, PURPLE, PURPLE]

        def get_epicycle_point(t, n_circles):
            """Get the position of the nth circle's dot"""
            pos = ORIGIN.copy()
            for i in range(n_circles):
                angle = freqs[i] * t
                pos = pos + radii[i] * np.array([np.cos(angle), np.sin(angle), 0])
            return pos

        # Create circles 3 and 4
        circle3 = always_redraw(
            lambda: Circle(
                radius=radii[2],
                color=PURPLE,
                stroke_width=2
            ).move_to(get_epicycle_point(self.angle_tracker.get_value(), 2))
        )

        circle4 = always_redraw(
            lambda: Circle(
                radius=radii[3],
                color=PURPLE,
                stroke_width=2,
                stroke_opacity=0.7
            ).move_to(get_epicycle_point(self.angle_tracker.get_value(), 3))
        )

        # Dots for circles 3 and 4
        dot3 = always_redraw(
            lambda: Dot(
                point=get_epicycle_point(self.angle_tracker.get_value(), 3),
                color=PURPLE,
                radius=0.06
            )
        )

        dot4 = always_redraw(
            lambda: Dot(
                point=get_epicycle_point(self.angle_tracker.get_value(), 4),
                color=PURPLE,
                radius=0.05
            )
        )

        # Radius lines for circles 3 and 4
        radius3 = always_redraw(
            lambda: Line(
                get_epicycle_point(self.angle_tracker.get_value(), 2),
                get_epicycle_point(self.angle_tracker.get_value(), 3),
                color=PURPLE,
                stroke_width=2
            )
        )

        radius4 = always_redraw(
            lambda: Line(
                get_epicycle_point(self.angle_tracker.get_value(), 3),
                get_epicycle_point(self.angle_tracker.get_value(), 4),
                color=PURPLE,
                stroke_width=2,
                stroke_opacity=0.7
            )
        )

        self.play(
            Create(circle3), Create(circle4),
            FadeIn(dot3), FadeIn(dot4),
            Create(radius3), Create(radius4),
            run_time=1
        )

        # Display Fourier series formula
        fourier_eq = MathTex(
            r"f(t) = \sum_{n} c_n \cdot e^{i \cdot n \cdot t}",
            color=PRIMARY,
            font_size=42
        )
        fourier_eq.to_edge(UP)
        self.add_fixed_in_frame_mobjects(fourier_eq)
        self.play(
            FadeOut(self.current_eq),
            Write(fourier_eq),
            run_time=2
        )
        self.remove_fixed_in_frame_mobjects(self.current_eq)

        # Fourier Series label
        fourier_label = Text(
            "Fourier Series",
            font=MONO_FONT,
            font_size=28,
            color=ORANGE,
            weight=BOLD
        )
        fourier_label.next_to(fourier_eq, DOWN)
        self.add_fixed_in_frame_mobjects(fourier_label)
        self.play(FadeIn(fourier_label))

        # Create traced path for the outermost dot
        traced_path = TracedPath(
            dot4.get_center,
            stroke_color=PRIMARY,
            stroke_width=2
        )
        self.add(traced_path)

        # Animate all circles with camera orbit
        # Note: move_camera must be called with added_anims, not directly in play()
        self.move_camera(
            theta=-120 * DEGREES,
            added_anims=[self.angle_tracker.animate(run_time=5, rate_func=linear).set_value(2 * TAU)],
            run_time=5
        )

        self.wait(1)

        # Clean up for final scene
        self.play(
            FadeOut(traced_path),
            FadeOut(self.circle), FadeOut(self.dot), FadeOut(self.radius_line),
            FadeOut(self.circle2), FadeOut(self.dot2), FadeOut(self.radius2),
            FadeOut(circle3), FadeOut(circle4),
            FadeOut(dot3), FadeOut(dot4),
            FadeOut(radius3), FadeOut(radius4),
            FadeOut(fourier_eq), FadeOut(fourier_label),
        )
        self.remove_fixed_in_frame_mobjects(fourier_eq, fourier_label)

    def scene5_drawing_shape(self):
        """Scene 5: Drawing a Shape (1:40 - 2:00)"""
        # Move to top-down view
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=1)

        # Display intro text
        intro_text = Text(
            "Any shape can be drawn with enough circles",
            font=MONO_FONT,
            font_size=24,
            color=PRIMARY
        )
        intro_text.to_edge(UP)
        self.add_fixed_in_frame_mobjects(intro_text)
        self.play(Write(intro_text), run_time=1.5)

        # Fourier coefficients for a square wave approximation
        # Using odd harmonics for square wave
        n_circles = 10
        coefficients = []
        for k in range(n_circles):
            if k == 0:
                coefficients.append((2.0, 1))  # (radius, frequency)
            else:
                # Square wave coefficients: 4/(pi*n) for odd n
                n = 2 * k + 1
                radius = 4 / (np.pi * n) * 2  # Scaled for visibility
                freq = n if k % 2 == 0 else -n
                coefficients.append((radius, freq))

        # Create color gradient
        def get_color(idx):
            if idx < n_circles // 3:
                return ORANGE
            elif idx < 2 * n_circles // 3:
                return TEAL
            else:
                return PURPLE

        # Angle tracker for this scene
        angle_tracker = ValueTracker(0)

        def get_epicycle_position(t, n):
            """Get position after n circles"""
            pos = ORIGIN.copy()
            for i in range(n):
                r, f = coefficients[i]
                angle = f * t
                pos = pos + r * np.array([np.cos(angle), np.sin(angle), 0])
            return pos

        # Create all circles and dots
        circles = []
        dots = []
        lines = []

        for i in range(n_circles):
            r, f = coefficients[i]
            color = get_color(i)
            opacity = 1 - (i / n_circles) * 0.5

            circle = always_redraw(
                lambda i=i, r=r, color=color, opacity=opacity: Circle(
                    radius=r,
                    color=color,
                    stroke_width=1.5,
                    stroke_opacity=opacity
                ).move_to(get_epicycle_position(angle_tracker.get_value(), i))
            )
            circles.append(circle)

            dot = always_redraw(
                lambda i=i, color=color: Dot(
                    point=get_epicycle_position(angle_tracker.get_value(), i + 1),
                    color=color,
                    radius=0.04
                )
            )
            dots.append(dot)

            line = always_redraw(
                lambda i=i, color=color, opacity=opacity: Line(
                    get_epicycle_position(angle_tracker.get_value(), i),
                    get_epicycle_position(angle_tracker.get_value(), i + 1),
                    color=color,
                    stroke_width=1.5,
                    stroke_opacity=opacity
                )
            )
            lines.append(line)

        # Add all circles
        for c, d, l in zip(circles, dots, lines):
            self.add(c, l, d)

        # Traced path for final shape
        traced_path = TracedPath(
            lambda: get_epicycle_position(angle_tracker.get_value(), n_circles),
            stroke_color=PRIMARY,
            stroke_width=3
        )
        self.add(traced_path)

        # Animate the drawing
        self.play(
            angle_tracker.animate.set_value(2 * TAU),
            run_time=6,
            rate_func=linear
        )

        # Fade out circles, keep traced path
        self.play(
            *[FadeOut(c) for c in circles],
            *[FadeOut(d) for d in dots],
            *[FadeOut(l) for l in lines],
            run_time=1
        )

        # Final equation
        final_eq = MathTex(
            r"\mathcal{F}\{f\} = \text{frequencies that draw } f",
            color=PRIMARY,
            font_size=32
        )
        final_eq.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(final_eq)
        self.play(Write(final_eq), run_time=1.5)

        self.wait(2)

        # Fade to background
        self.play(
            FadeOut(traced_path),
            FadeOut(intro_text),
            FadeOut(final_eq),
            run_time=1
        )
        self.remove_fixed_in_frame_mobjects(intro_text, final_eq)


# For rendering: manim -pqh fourier_epicycles.py FourierEpicycles
