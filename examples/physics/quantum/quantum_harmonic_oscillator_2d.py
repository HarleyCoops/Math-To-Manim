"""
Epic 2D Quantum Harmonic Oscillator Animation
==============================================
Visualizes the complete mathematical structure of the 2D quantum harmonic oscillator,
including wavefunctions, Hermite polynomials, energy levels, and degeneracy.

Features:
- Separation of variables visualization
- Hermite polynomial generation
- 3D wavefunction surface plots
- Energy level diagrams with degeneracy
- Beautiful color-coded mathematical notation
"""

from manim import *
import numpy as np
from scipy.special import hermite, factorial

class QuantumHarmonicOscillator2D(ThreeDScene):
    """Epic visualization of 2D quantum harmonic oscillator"""

    def construct(self):
        # Set dark background for better contrast
        self.camera.background_color = "#0a0a0a"

        # Scene 1: Title and Introduction
        self.intro_scene()
        self.wait(1)

        # Scene 2: Main formula reveal
        self.main_formula_scene()
        self.wait(1)

        # Scene 3: Separation of variables
        self.separation_scene()
        self.wait(1)

        # Scene 4: Hermite polynomials
        self.hermite_polynomial_scene()
        self.wait(1)

        # Scene 5: 1D Wavefunctions
        self.wavefunction_1d_scene()
        self.wait(1)

        # Scene 6: 2D Wavefunctions (Epic 3D visualization)
        self.wavefunction_2d_scene()
        self.wait(1)

        # Scene 7: Energy levels and degeneracy
        self.energy_degeneracy_scene()
        self.wait(1)

        # Scene 8: Grand finale
        self.finale_scene()
        self.wait(2)

    def intro_scene(self):
        """Beautiful introduction with title and context"""
        title = Tex(r"The 2D Quantum\\Harmonic Oscillator", font_size=72)
        title.set_color_by_gradient(BLUE, PURPLE, PINK)

        subtitle = Tex(r"A Journey Through Quantum Wavefunctions", font_size=36)
        subtitle.set_color(GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)

        # Animated particles in background
        particles = VGroup(*[
            Dot(point=np.array([
                np.random.uniform(-7, 7),
                np.random.uniform(-4, 4),
                0
            ]), radius=0.03, color=BLUE, fill_opacity=0.3)
            for _ in range(50)
        ])

        self.play(
            LaggedStart(*[FadeIn(p, scale=0.5) for p in particles], lag_ratio=0.02),
            run_time=2
        )
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=UP), run_time=1)
        self.wait(2)
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(particles),
            run_time=1
        )

    def main_formula_scene(self):
        """Reveal the main formula with dramatic effect"""
        header = Text("The Complete System", font_size=48, color=YELLOW)
        header.to_edge(UP)

        # Main wavefunction formula
        psi_2d = MathTex(
            r"\psi_{n_x,n_y}(x,y)", "=", r"\psi_{n_x}(x)", r"\cdot", r"\psi_{n_y}(y)",
            font_size=48
        )
        psi_2d.set_color_by_tex(r"\psi_{n_x,n_y}", BLUE)
        psi_2d.set_color_by_tex(r"\psi_{n_x}(x)", GREEN)
        psi_2d.set_color_by_tex(r"\psi_{n_y}(y)", PURPLE)

        # Energy formula
        energy = MathTex(
            r"E_{n_x,n_y}", "=", r"(n_x + n_y + 1)", r"\cdot", r"\hbar\omega",
            font_size=42
        )
        energy.set_color_by_tex(r"E_{n_x,n_y}", ORANGE)
        energy.set_color_by_tex(r"(n_x + n_y + 1)", YELLOW)
        energy.set_color_by_tex(r"\hbar\omega", RED)

        # Degeneracy formula
        degeneracy = MathTex(
            r"g_{n_x+n_y}", "=", r"n_x + n_y + 1",
            font_size=42
        )
        degeneracy.set_color_by_tex(r"g_{n_x+n_y}", PINK)
        degeneracy.set_color_by_tex(r"n_x + n_y + 1", YELLOW)

        formulas = VGroup(psi_2d, energy, degeneracy)
        formulas.arrange(DOWN, buff=0.8)
        formulas.move_to(ORIGIN)

        # Animate
        self.play(Write(header), run_time=1)
        self.wait(0.5)

        # Dramatic reveal
        for formula in formulas:
            self.play(
                Write(formula),
                Flash(formula.get_center(), color=YELLOW, flash_radius=0.5),
                run_time=1.5
            )
            self.wait(0.5)

        self.wait(2)
        self.play(
            FadeOut(header),
            FadeOut(formulas),
            run_time=1
        )

    def separation_scene(self):
        """Show separation of variables"""
        title = Text("Separation of Variables", font_size=42, color=YELLOW)
        title.to_edge(UP)

        # Show 2D -> 1D × 1D
        psi_2d = MathTex(r"\psi_{n_x,n_y}(x,y)", font_size=48, color=BLUE)

        equals = MathTex("=", font_size=48)

        psi_x = MathTex(r"\psi_{n_x}(x)", font_size=48, color=GREEN)
        times = MathTex(r"\cdot", font_size=48)
        psi_y = MathTex(r"\psi_{n_y}(y)", font_size=48, color=PURPLE)

        group = VGroup(psi_2d, equals, psi_x, times, psi_y)
        group.arrange(RIGHT, buff=0.3)
        group.move_to(ORIGIN)

        # Rectangles to highlight
        rect_2d = SurroundingRectangle(psi_2d, color=BLUE, buff=0.15)
        rect_x = SurroundingRectangle(psi_x, color=GREEN, buff=0.15)
        rect_y = SurroundingRectangle(psi_y, color=PURPLE, buff=0.15)

        # Labels
        label_2d = Text("2D Problem", font_size=24, color=BLUE)
        label_2d.next_to(rect_2d, UP, buff=0.3)

        label_1d = Text("Two 1D Problems!", font_size=24, color=YELLOW)
        label_1d.next_to(VGroup(rect_x, rect_y), DOWN, buff=0.3)

        self.play(Write(title), run_time=1)
        self.play(Write(psi_2d), Create(rect_2d), run_time=1)
        self.play(FadeIn(label_2d, shift=DOWN), run_time=0.5)
        self.wait(1)

        self.play(Write(equals), run_time=0.5)
        self.play(
            Write(psi_x), Write(times), Write(psi_y),
            Create(rect_x), Create(rect_y),
            run_time=1.5
        )
        self.play(FadeIn(label_1d, shift=UP), run_time=0.5)
        self.wait(2)

        self.play(
            FadeOut(title), FadeOut(group),
            FadeOut(rect_2d), FadeOut(rect_x), FadeOut(rect_y),
            FadeOut(label_2d), FadeOut(label_1d),
            run_time=1
        )

    def hermite_polynomial_scene(self):
        """Visualize Hermite polynomials"""
        title = Text("Hermite Polynomials", font_size=42, color=YELLOW)
        title.to_edge(UP)

        # Formula for Hermite polynomials
        hermite_formula = MathTex(
            r"H_n(x) = (-1)^n \cdot e^{x^2} \cdot \frac{d^n}{dx^n}\left[e^{-x^2}\right]",
            font_size=36
        )
        hermite_formula.next_to(title, DOWN, buff=0.5)
        hermite_formula.set_color_by_tex(r"H_n", YELLOW)

        self.play(Write(title), Write(hermite_formula), run_time=2)
        self.wait(1)

        # Create axes for plotting
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-15, 15, 5],
            x_length=10,
            y_length=4,
            axis_config={"color": GRAY}
        ).shift(DOWN * 0.5)

        axes_labels = axes.get_axis_labels(x_label="x", y_label="H_n(x)")

        self.play(Create(axes), Write(axes_labels), run_time=1)

        # Plot first few Hermite polynomials
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        hermite_graphs = VGroup()
        labels = VGroup()

        for n in range(6):
            # Create Hermite polynomial function
            hermite_poly = hermite(n)

            graph = axes.plot(
                lambda x: hermite_poly(x),
                x_range=[-2.5, 2.5],
                color=colors[n],
                stroke_width=3
            )

            label = MathTex(f"H_{n}", font_size=28, color=colors[n])
            label.next_to(graph.get_end(), RIGHT, buff=0.1)

            hermite_graphs.add(graph)
            labels.add(label)

            self.play(
                Create(graph),
                Write(label),
                run_time=0.8
            )
            self.wait(0.3)

        self.wait(2)
        self.play(
            FadeOut(title), FadeOut(hermite_formula),
            FadeOut(axes), FadeOut(axes_labels),
            FadeOut(hermite_graphs), FadeOut(labels),
            run_time=1
        )

    def wavefunction_1d_scene(self):
        """Show 1D wavefunctions"""
        title = Text("1D Wavefunctions", font_size=42, color=YELLOW)
        title.to_edge(UP)

        # Formula
        psi_formula = MathTex(
            r"\psi_n(x) = \frac{e^{-x^2/2} \cdot H_n(x)}{\sqrt{2^n \cdot n! \cdot \sqrt{\pi}}}",
            font_size=36
        )
        psi_formula.next_to(title, DOWN, buff=0.5)
        psi_formula.set_color_by_tex(r"\psi_n", GREEN)
        psi_formula.set_color_by_tex(r"H_n", YELLOW)

        self.play(Write(title), Write(psi_formula), run_time=2)
        self.wait(1)

        # Create axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-0.8, 0.8, 0.4],
            x_length=10,
            y_length=4,
            axis_config={"color": GRAY}
        ).shift(DOWN * 0.5)

        axes_labels = axes.get_axis_labels(x_label="x", y_label=r"\psi_n(x)")

        self.play(Create(axes), Write(axes_labels), run_time=1)

        # Plot wavefunctions
        def psi_n(x, n):
            """Calculate normalized harmonic oscillator wavefunction"""
            hermite_poly = hermite(n)
            norm = np.sqrt(2**n * factorial(n) * np.sqrt(np.pi))
            return np.exp(-x**2/2) * hermite_poly(x) / norm

        colors = [RED, ORANGE, YELLOW, GREEN]

        for n in range(4):
            graph = axes.plot(
                lambda x, n=n: psi_n(x, n),
                x_range=[-3.5, 3.5],
                color=colors[n],
                stroke_width=4
            )

            label = MathTex(f"n={n}", font_size=32, color=colors[n])
            label.next_to(axes, RIGHT, buff=0.5).shift(UP * (1.5 - n * 1))

            self.play(
                Create(graph),
                Write(label),
                run_time=1
            )
            self.wait(0.5)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)

    def wavefunction_2d_scene(self):
        """Epic 3D visualization of 2D wavefunctions"""
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        title = Text("2D Wavefunctions", font_size=48, color=YELLOW)
        title.to_corner(UL)
        title.fix_in_frame()

        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-0.5, 0.5, 0.25],
            x_length=6,
            y_length=6,
            z_length=4
        )

        labels = axes.get_axis_labels(
            x_label="x",
            y_label="y",
            z_label=r"\psi"
        )

        self.play(Create(axes), Write(labels), run_time=1.5)

        # Function for 2D wavefunction
        def psi_2d(x, y, nx, ny):
            """2D harmonic oscillator wavefunction"""
            def psi_1d(u, n):
                hermite_poly = hermite(n)
                norm = np.sqrt(2**n * factorial(n) * np.sqrt(np.pi))
                return np.exp(-u**2/2) * hermite_poly(u) / norm

            return psi_1d(x, nx) * psi_1d(y, ny)

        # Show different quantum states
        states = [(0, 0), (1, 0), (0, 1), (1, 1)]
        state_labels = [
            r"(n_x=0, n_y=0)",
            r"(n_x=1, n_y=0)",
            r"(n_x=0, n_y=1)",
            r"(n_x=1, n_y=1)"
        ]
        colors = [BLUE, GREEN, PURPLE, ORANGE]

        for idx, (nx, ny) in enumerate(states):
            # Create surface
            surface = Surface(
                lambda u, v: axes.c2p(
                    u, v, psi_2d(u, v, nx, ny)
                ),
                u_range=[-2.5, 2.5],
                v_range=[-2.5, 2.5],
                resolution=(30, 30),
                fill_opacity=0.7,
                checkerboard_colors=[colors[idx], colors[idx]],
                stroke_color=colors[idx],
                stroke_width=0.5
            )

            # Label
            state_label = MathTex(state_labels[idx], font_size=36, color=colors[idx])
            state_label.to_corner(UR)
            state_label.fix_in_frame()

            if idx == 0:
                self.add_fixed_in_frame_mobjects(state_label)
                self.play(
                    Create(surface),
                    Write(state_label),
                    run_time=2
                )
            else:
                old_label = self.mobjects[-1]
                self.play(
                    Transform(self.mobjects[-2], surface),
                    Transform(old_label, state_label),
                    run_time=2
                )

            # Rotate camera
            self.begin_ambient_camera_rotation(rate=0.3)
            self.wait(3)
            self.stop_ambient_camera_rotation()

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)

        # Reset camera
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

    def energy_degeneracy_scene(self):
        """Show energy levels and degeneracy"""
        title = Text("Energy Levels & Degeneracy", font_size=42, color=YELLOW)
        title.to_edge(UP)

        # Energy formula
        energy_formula = MathTex(
            r"E_{n_x,n_y} = (n_x + n_y + 1) \cdot \hbar\omega",
            font_size=36
        )
        energy_formula.next_to(title, DOWN, buff=0.3)
        energy_formula.set_color_by_tex(r"E_{n_x,n_y}", ORANGE)

        # Degeneracy formula
        deg_formula = MathTex(
            r"g_{n_x+n_y} = n_x + n_y + 1",
            font_size=36
        )
        deg_formula.next_to(energy_formula, DOWN, buff=0.3)
        deg_formula.set_color_by_tex(r"g_{n_x+n_y}", PINK)

        self.play(Write(title), run_time=1)
        self.play(Write(energy_formula), run_time=1)
        self.play(Write(deg_formula), run_time=1)
        self.wait(1)

        # Create energy level diagram
        diagram_group = VGroup()

        base_y = -2
        level_height = 0.8

        # Energy levels with states
        energy_data = [
            (0, [(0, 0)], 1),  # N=0, states, degeneracy
            (1, [(1, 0), (0, 1)], 2),  # N=1
            (2, [(2, 0), (1, 1), (0, 2)], 3),  # N=2
            (3, [(3, 0), (2, 1), (1, 2), (0, 3)], 4),  # N=3
        ]

        colors_deg = [RED, ORANGE, YELLOW, GREEN]

        for N, states, deg in energy_data:
            y_pos = base_y + N * level_height

            # Energy level line
            line = Line(LEFT * 3, RIGHT * 3, color=colors_deg[N], stroke_width=3)
            line.move_to(UP * y_pos)

            # Energy label
            energy_label = MathTex(f"E = {N+1}\\hbar\\omega", font_size=24, color=colors_deg[N])
            energy_label.next_to(line, LEFT, buff=0.3)

            # Degeneracy label
            deg_label = MathTex(f"g = {deg}", font_size=24, color=colors_deg[N])
            deg_label.next_to(line, RIGHT, buff=0.3)

            # State labels
            state_group = VGroup()
            for i, (nx, ny) in enumerate(states):
                state_text = MathTex(f"({nx},{ny})", font_size=20, color=WHITE)
                x_offset = -1.5 + i * (3 / deg)
                state_text.move_to(line.get_center() + RIGHT * x_offset + UP * 0.3)
                state_group.add(state_text)

            diagram_group.add(line, energy_label, deg_label, state_group)

        diagram_group.shift(DOWN * 0.5)

        # Animate
        for i in range(0, len(diagram_group), 4):
            group = VGroup(diagram_group[i:i+4])
            self.play(
                Create(group),
                Flash(group.get_center(), color=YELLOW),
                run_time=1
            )
            self.wait(0.5)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)

    def finale_scene(self):
        """Grand finale with all formulas"""
        title = Tex(
            r"The Complete\\2D Quantum Harmonic Oscillator",
            font_size=56
        )
        title.set_color_by_gradient(BLUE, PURPLE, PINK)
        title.to_edge(UP)

        # All key formulas
        formulas = VGroup(
            MathTex(r"\psi_{n_x,n_y}(x,y) = \psi_{n_x}(x) \cdot \psi_{n_y}(y)", font_size=32),
            MathTex(r"\psi_n(x) = \frac{e^{-x^2/2} \cdot H_n(x)}{\sqrt{2^n \cdot n! \cdot \sqrt{\pi}}}", font_size=32),
            MathTex(r"H_n(x) = (-1)^n \cdot e^{x^2} \cdot \frac{d^n}{dx^n}\left[e^{-x^2}\right]", font_size=32),
            MathTex(r"E_{n_x,n_y} = (n_x + n_y + 1) \cdot \hbar\omega", font_size=32),
            MathTex(r"g_{n_x+n_y} = n_x + n_y + 1", font_size=32),
        )

        formulas.arrange(DOWN, buff=0.4)
        formulas.move_to(ORIGIN)

        # Color the formulas
        formulas[0].set_color(BLUE)
        formulas[1].set_color(GREEN)
        formulas[2].set_color(YELLOW)
        formulas[3].set_color(ORANGE)
        formulas[4].set_color(PINK)

        # Background particles
        particles = VGroup(*[
            Dot(
                point=np.array([
                    np.random.uniform(-7, 7),
                    np.random.uniform(-4, 4),
                    0
                ]),
                radius=0.03,
                color=np.random.choice([BLUE, PURPLE, PINK]),
                fill_opacity=0.4
            )
            for _ in range(100)
        ])

        # Animate
        self.play(
            LaggedStart(*[FadeIn(p, scale=0.5) for p in particles], lag_ratio=0.01),
            run_time=2
        )

        self.play(Write(title), run_time=2)
        self.wait(1)

        for formula in formulas:
            self.play(
                Write(formula),
                Flash(formula.get_center(), color=YELLOW, flash_radius=0.3),
                run_time=1.2
            )
            self.wait(0.3)

        # Final animation - everything pulses
        self.play(
            *[p.animate.scale(1.5).set_opacity(0.8) for p in particles[:20]],
            run_time=1
        )
        self.play(
            *[p.animate.scale(0.67).set_opacity(0.4) for p in particles[:20]],
            run_time=1
        )

        # Final message
        end_text = Text(
            "The Beauty of Quantum Mechanics",
            font_size=36,
            gradient=(BLUE, PURPLE, PINK)
        )
        end_text.to_edge(DOWN, buff=0.5)

        self.play(FadeIn(end_text, shift=UP), run_time=1.5)
        self.wait(3)
