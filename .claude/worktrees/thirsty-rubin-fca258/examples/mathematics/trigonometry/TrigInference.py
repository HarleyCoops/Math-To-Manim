import numpy as np
from manim import *

# These colors are chosen to closely match the ones in the provided image.
IMAGE_COLORS = ["#8be9fd", "#ffb86c", "#f1fa8c", "#50fa7b", "#ff79c6", "#bd93f9"]

class FourierSeriesSquareWave(Scene):
    """
    This Manim script creates a visualization of the Fourier series for a square wave,
    emulating the style of the provided image.

    The visualization consists of two main parts:
    1.  The upper part shows a series of rotating vectors (phasors) on a complex plane.
        Each vector represents a term in the Fourier series. They are chained together
        to form epicycles, visualizing the summation of complex terms.
    2.  The lower part plots the vertical component (imaginary part) of the final
        vector's tip against time. This reveals how the sum of sine waves builds up
        the target square wave.

    Note: The provided image is a static snapshot. This script recreates the overall
    mechanism using the standard Fourier sine series for an odd square wave. The final
    frame of the animation, including the faint trace lines, will capture the essence
    of the original still image.
    """

    # --- Configuration ---
    N_TERMS = 6
    # The animation will stop at t = 3*pi, matching the end-point in the image.
    T_MAX = 3 * PI
    ANIMATION_RUN_TIME = 10
    
    # Position of the two coordinate systems
    EPICYCLE_CENTER = 2.5 * UP
    WAVE_CENTER = 2.0 * DOWN

    # Scaling factor for radii to make them visually appealing
    FOURIER_SCALE_FACTOR = 1.2

    def setup(self):
        """Set up the scene's state variables."""
        self.time_tracker = ValueTracker(0)

    def construct(self):
        """Construct the animation objects and play the animation."""
        # 1. Create the two sets of axes for epicycles and the wave graph
        axes_epi = self.get_epicycle_axes()
        axes_wave = self.get_wave_axes()
        self.add(axes_epi, axes_wave)

        # 2. Get Fourier series coefficients (amplitudes for the sine series)
        amplitudes = self.get_fourier_amplitudes(self.N_TERMS)

        # 3. Create the epicycles (circles and vectors), which update with time
        epicycles_group = self.create_epicycles(axes_epi, amplitudes)

        # 4. Create the waveforms for each partial sum of the series
        waves = self.create_waveforms(axes_wave, amplitudes)
        
        # 5. Create the connecting line and dots that track the wave's creation
        final_vector_dot = epicycles_group.get_family()[-1] # The dot on the last vector tip
        projection_line, final_wave_dot = self.create_connecting_mobjects(
            axes_wave, amplitudes, final_vector_dot
        )
        
        # 6. Add all mobjects to the scene
        self.add(waves, epicycles_group, projection_line, final_wave_dot)

        # 7. Animate by advancing the time parameter
        self.play(
            self.time_tracker.animate.set_value(self.T_MAX),
            run_time=self.ANIMATION_RUN_TIME,
            rate_func=linear
        )
        self.wait(0.5)

        # 8. Add the final trace lines seen in the static image
        trace_lines = self.create_final_trace_lines(axes_wave, epicycles_group)
        self.play(Create(trace_lines))
        
        self.wait(3)

    def get_epicycle_axes(self):
        """Creates the Axes for the epicycles in the upper part."""
        axes = Axes(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1],
            x_length=4.5, y_length=4.5,
            axis_config={"color": WHITE, "stroke_width": 2},
            tips=True
        ).move_to(self.EPICYCLE_CENTER)
        return axes

    def get_wave_axes(self):
        """Creates the Axes for the waveform in the lower part."""
        axes = Axes(
            x_range=[0, 4.5 * PI, PI / 2], y_range=[-2, 2, 1],
            x_length=13, y_length=4,
            axis_config={"color": RED, "stroke_width": 3, "include_tip": False},
        ).move_to(self.WAVE_CENTER)

        # Add x-axis labels to match the image
        x_labels_map = {
            # r"2\pi": 2 * PI,  # Omitted as it's at the start in the image
            r"\frac{5\pi}{2}": 5 * PI / 2,
            r"3\pi": 3 * PI,
            r"\frac{7\pi}{2}": 7 * PI / 2,
            r"4\pi": 4 * PI,
            r"\frac{9\pi}{2}": 9 * PI / 2,
        }
        
        labels_vgroup = VGroup()
        for tex, val in x_labels_map.items():
            if tex == r"3\pi": # Special handling for the '3' label in the image
                label = Tex("3").next_to(axes.c2p(val, 0), DOWN, buff=0.25).shift(LEFT * 1.2)
            else:
                label = MathTex(tex).next_to(axes.c2p(val, 0), DOWN, buff=0.25)
            labels_vgroup.add(label)

        axes.add(labels_vgroup)
        return axes
    
    def get_fourier_amplitudes(self, n_terms):
        """Calculates amplitudes for the Fourier sine series of an odd square wave."""
        return [
            (4 / (PI * (2 * n + 1))) * self.FOURIER_SCALE_FACTOR
            for n in range(n_terms)
        ]

    def get_complex_sum(self, t, amplitudes, n_terms=None):
        """Computes the sum of complex vectors at a given time."""
        if n_terms is None:
            n_terms = len(amplitudes)
        
        return sum(
            amp * np.exp(1j * (2 * n + 1) * t)
            for n, amp in enumerate(amplitudes[:n_terms])
        )

    def create_epicycles(self, axes, amplitudes):
        """Creates a VGroup of updating circles, vectors, and dots."""
        circles, vectors, dots = VGroup(), VGroup(), VGroup()
        
        for i, amp in enumerate(amplitudes):
            radius = abs(amp) * axes.x_axis.get_unit_size()
            color = IMAGE_COLORS[i]
            circles.add(Circle(radius=radius, color=color, stroke_width=2))
            vectors.add(Line(stroke_color=color, stroke_width=4))
            dots.add(Dot(color=color, radius=0.06))

        epicycles = VGroup(circles, vectors, dots)
        
        def updater(mob):
            t = self.time_tracker.get_value()
            current_center_complex = 0j
            for i, amp in enumerate(amplitudes):
                term_vector_complex = amp * np.exp(1j * (2 * i + 1) * t)
                
                start_point = axes.c2p(current_center_complex.real, current_center_complex.imag)
                end_pos_complex = current_center_complex + term_vector_complex
                end_point = axes.c2p(end_pos_complex.real, end_pos_complex.imag)
                
                circles[i].move_to(start_point)
                vectors[i].put_start_and_end_on(start_point, end_point)
                dots[i].move_to(end_point)
                current_center_complex = end_pos_complex
                
        epicycles.add_updater(updater)
        return epicycles

    def create_waveforms(self, axes, amplitudes):
        """Creates the waveforms for each partial sum."""
        waves = VGroup()
        for n in range(self.N_TERMS):
            wave_plot = axes.plot(
                lambda t, n_cap=n: self.get_complex_sum(t, amplitudes, n + 1).imag,
                x_range=[0, self.T_MAX, 0.01],
                color=IMAGE_COLORS[n],
                stroke_width=2.5,
            )
            waves.add(wave_plot)
        return waves

    def create_connecting_mobjects(self, axes_wave, amplitudes, final_epi_dot):
        """Creates the projection line and the dot on the final wave."""
        wave_dot = Dot(color=IMAGE_COLORS[-1], radius=0.06)
        wave_dot.add_updater(lambda d: d.move_to(
            axes_wave.c2p(
                self.time_tracker.get_value(),
                self.get_complex_sum(self.time_tracker.get_value(), amplitudes).imag
            )
        ))
        
        proj_line = always_redraw(
            lambda: Line(
                final_epi_dot.get_center(), wave_dot.get_center(),
                stroke_color=GREY_B, stroke_width=1.5, stroke_opacity=0.8
            )
        )
        return proj_line, wave_dot

    def create_final_trace_lines(self, axes_wave, epicycles):
        """Creates the faint white lines seen in the image at the final time step."""
        t_final = self.time_tracker.get_value()
        amplitudes = self.get_fourier_amplitudes(self.N_TERMS)
        
        final_y = self.get_complex_sum(t_final, amplitudes).imag
        wave_final_point = axes_wave.c2p(t_final, final_y)
        
        epicycle_dots = epicycles[2] # The VGroup containing the dots
        
        return VGroup(*(
            Line(
                wave_final_point, dot.get_center(), 
                stroke_color=WHITE, stroke_width=1, stroke_opacity=0.4
            )
            for dot in epicycle_dots
        ))
