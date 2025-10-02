from manim import *
import numpy as np
import random

class GravitationalWaveSymphony(ThreeDScene):
    def construct(self):
        # Total animation duration: 180 seconds (3 minutes)
        self.camera.background_color = "#01001a"  # Deep space blue
        self.camera.set_focal_distance(10)

        # ======================
        # Section 1: Cosmic Overture (0:00-0:30)
        # ======================
        # Starfield with varying brightness and twinkling effect
        stars = VGroup(*[
            Dot(radius=0.002*(1+np.random.rand()**3),
                color=interpolate_color(WHITE, BLUE_E, random.random()))
            .shift(15*(np.random.rand(3)-0.5))
            for _ in range(1000)
        ])

        # Add twinkling effect
        for star in stars:
            star.add_updater(lambda m, dt: m.set_opacity(0.5 + 0.5*np.sin(dt*5)))

        # Slow panning camera movement
        initial_center = ORIGIN
        self.move_camera(frame_center=UP*2 + LEFT*3, run_time=0.1)  # Small but non-zero duration

        # Gradual star appearance
        star_anim = LaggedStartMap(
            FadeIn, stars,
            lag_ratio=0.01,
            run_time=12,
            rate_func=linear
        )

        # Play the star animation
        self.play(star_anim)

        # Title sequence
        title = Text("Cosmic Ripples", font_size=72).set_color_by_gradient(BLUE_B, TEAL)
        subtitle = Text("A Gravitational Wave Journey", font_size=36).next_to(title, DOWN)

        # First move the camera back
        self.move_camera(frame_center=initial_center, run_time=2)
        # Then play the text animations
        self.play(
            Write(title, run_time=3),
            FadeIn(subtitle, shift=DOWN),
            run_time=3
        )
        self.wait(5)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=3)

        # ======================
        # Section 2: Spacetime Ballet (0:30-1:30)
        # ======================
        # Create spacetime grid with depth and dynamic color
        spacetime = NumberPlane(
            x_range=[-10,10], y_range=[-6,6],
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1.5},
            faded_line_ratio=3
        ).set_opacity(0.8).rotate(20*DEGREES, axis=RIGHT)

        # Add glow effect
        spacetime.add(spacetime.copy().set_opacity(0.3).set_color(WHITE))

        # Wave parameters with smooth transitions
        wave_tracker = ValueTracker(0)
        resonance = ValueTracker(0)

        # Complex grid deformation with multiple frequency components
        def spacetime_warp(mob):
            t = wave_tracker.get_value()
            r = resonance.get_value()
            points = mob.get_points().copy()  # Create a copy of points
            for i, point in enumerate(points):
                x, y, _ = point
                d = np.sqrt(x**2 + y**2)

                # Base wave
                dx1 = (0.3/(d+0.5)) * np.cos(3*t - 0.7*d)
                dy1 = (0.3/(d+0.5)) * np.sin(3*t - 0.7*d)

                # Harmonic component
                dx2 = (0.15*r/(d+1)) * np.cos(5*t - 1.2*d)
                dy2 = (0.15*r/(d+1)) * np.sin(5*t - 1.2*d)

                # Nonlinear resonance
                dx3 = 0.1*r**2 * np.exp(-d/4) * np.sin(2*t)

                points[i] = point + np.array([dx1 + dx2 + dx3, dy1 + dy2, 0])
            mob.set_points(points)

        spacetime.add_updater(spacetime_warp)

        # Animate spacetime awakening
        self.play(
            FadeIn(spacetime, shift=DOWN),
            wave_tracker.animate.set_value(2*PI),
            resonance.animate.set_value(1),
            rate_func=there_and_back,
            run_time=25  # Extended spacetime sequence
        )

        # ======================
        # Section 3: Wave Propagation (1:30-2:15)
        # ======================
        # Multilayered pulse with different speeds and colors
        pulse_layers = VGroup(*[
            Annulus(inner_radius=0.5, outer_radius=1, color=color, fill_opacity=0.2)
            .set_style(stroke_width=3) for color in [TEAL_A, PINK, BLUE_B]
        ])

        # Pulse animation with dispersion effect
        def pulse_update(mob, alpha):
            for i, layer in enumerate(mob):
                layer.set_width(4 + 3*i + 8*alpha)
                layer.set_opacity(0.3/(i+1) * (1 - alpha))
                layer.rotate(0.1*alpha * (-1)**i)

        # Synchronized pulse emission
        self.play(
            UpdateFromAlphaFunc(
                pulse_layers, pulse_update,
                rate_func=rate_functions.ease_in_out_sine,
                run_time=15
            ),
            resonance.animate.set_value(2),
            spacetime.animate.set_color(interpolate_color(BLUE_E, PURPLE_A, 0.5)),
            run_time=15
        )

        # ======================
        # Section 4: Celestial Cartography (2:15-3:00)
        # ======================
        # Mollweide projection with animated contours and constellations
        sky_map = ParametricSurface(
            lambda u,v: self.mollweide_projection(u,v),
            u_range=[-PI, PI],
            v_range=[-PI/2, PI/2],
            resolution=(40,20)
        ).set_style(fill_opacity=0.2, stroke_color=WHITE, stroke_width=1)

        # Add constellation lines
        constellations = VGroup(*[
            Line(start, end).set_color(WHITE).set_opacity(0.5)
            for start, end in self.get_constellation_lines()
        ])

        # Animated probability contours
        contour = always_redraw(lambda:
            ParametricSurface(
                lambda u,v: self.mollweide_projection(u,v) + 0.05*np.array([
                    0,
                    0,
                    np.exp(-((u-0.3)**2 + (v-0.2)**2)/0.5) * np.sin(3*wave_tracker.get_value())
                ]),
                u_range=[-PI, PI],
                v_range=[-PI/2, PI/2],
                resolution=(40,20)
            ).set_color(interpolate_color(GREEN, YELLOW, 0.5))
        )

        # Final reveal with multiple elements
        self.play(
            FadeIn(sky_map.shift(RIGHT*4)),
            FadeIn(contour),
            FadeIn(constellations),
            pulse_layers.animate.set_opacity(0)
        )
        self.wait(15)

    def mollweide_projection(self, u, v):
        # Mollweide projection formula with bounds checking
        # Ensure inputs are within valid ranges
        u = np.clip(u, -PI, PI)
        v = np.clip(v, -PI/2, PI/2)

        theta = u
        # Add numerical stability to phi calculation
        arg = (2*v + np.sin(2*v)) / np.pi
        arg = np.clip(arg, -1, 1)  # Ensure argument is in valid range for arcsin
        phi = np.arcsin(arg)

        x = 2 * np.sqrt(2) * (theta - np.pi) * np.cos(phi) / np.pi
        y = np.sqrt(2) * np.sin(phi)
        z = 0
        return np.array([x, y, z])

    def get_constellation_lines(self):
        # Define constellation lines (example data)
        return [
            (np.array([-1, 1, 0]), np.array([-1.5, 1.5, 0])),
            (np.array([-1.5, 1.5, 0]), np.array([-2, 2, 0])),
            # Add more lines as needed
        ]

# To render the scene, use the following command in your terminal:
# python -m manim -pql Mistral_gravity_wave.py GravitationalWaveSymphony
# For higher quality:
# python -m manim -pqh Mistral_gravity_wave.py GravitationalWaveSymphony  # 1080p60
