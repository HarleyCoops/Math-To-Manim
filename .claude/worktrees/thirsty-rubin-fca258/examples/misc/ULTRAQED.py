"""
ULTRA QED - The Ultimate Quantum Electrodynamics Visualization
A comprehensive multi-minute journey through the electromagnetic interaction
Maximizing Manim v0.19.0 capabilities for visual storytelling
"""

from manim import *
import numpy as np

# Ultra High Quality Color Palette
COSMIC_BLUE = "#1a1a2e"
ELECTRIC_CRIMSON = "#ff0055"
MAGNETIC_SAPPHIRE = "#0066ff"
PHOTON_GOLD = "#ffd700"
SPACETIME_SILVER = "#c0c0c0"
FERMION_ORANGE = "#ff6b35"
GAUGE_EMERALD = "#00d9a3"
QUANTUM_VIOLET = "#9d4edd"

class ULTRAQEDComplete(ThreeDScene):
    """Single unified scene for the complete QED journey"""

    def construct(self):
        # Initialize with cosmic background
        self.camera.background_color = BLACK

        # Scene 1: Cosmic Introduction
        self.scene_1_cosmic_opening()

        # Scene 2: Spacetime Arena
        self.scene_2_spacetime_foundations()

        # Scene 3: Quantum Fields Emerge
        self.scene_3_quantum_fields()

        # Scene 4: Maxwell Evolution
        self.scene_4_maxwell_transformation()

        # Scene 5: QED Lagrangian Heart
        self.scene_5_qed_lagrangian()

        # Scene 6: Feynman Diagrams
        self.scene_6_feynman_interactions()

        # Scene 7: Coupling Constant Deep Dive
        self.scene_7_fine_structure()

        # Scene 8: Renormalization Journey
        self.scene_8_running_coupling()

        # Scene 9: Vacuum Polarization
        self.scene_9_vacuum_structure()

        # Scene 10: Grand Synthesis
        self.scene_10_synthesis()

        # Scene 11: Cosmic Finale
        self.scene_11_finale()

    def scene_1_cosmic_opening(self):
        """Epic opening with starfield and cosmic scale"""
        self.set_camera_orientation(phi=70*DEGREES, theta=-45*DEGREES)

        # Create static starfield - much more efficient
        stars = VGroup(*[
            Dot(
                point=np.random.randn(3) * 8,
                radius=np.random.uniform(0.02, 0.08),
                color=interpolate_color(WHITE, BLUE, np.random.random())
            ).set_opacity(np.random.uniform(0.3, 1.0))
            for _ in range(150)  # Reduced from 300 to 150
        ])

        self.play(FadeIn(stars), run_time=2)

        # Grand title emergence
        title_main = Text(
            "QUANTUM FIELD THEORY",
            font_size=72,
            weight=BOLD,
            gradient=(ELECTRIC_CRIMSON, PHOTON_GOLD)
        )
        title_sub = Text(
            "A Journey into the Electromagnetic Interaction",
            font_size=36,
            slant=ITALIC
        ).next_to(title_main, DOWN)

        title_group = VGroup(title_main, title_sub)

        # Dramatic entrance with light burst
        self.play(
            FadeIn(title_group, scale=0.8),
            Flash(ORIGIN, color=PHOTON_GOLD, line_length=1.5,
                  num_lines=24, flash_radius=3),
            run_time=3
        )

        # Pulsing glow effect
        for _ in range(2):
            self.play(
                title_main.animate.set_color(PHOTON_GOLD),
                rate_func=there_and_back,
                run_time=1
            )

        self.wait(2)

        # Title moves to corner
        self.play(
            title_group.animate.scale(0.3).to_corner(UL),
            run_time=2
        )

        # Fade stars partially
        self.play(
            stars.animate.set_opacity(0.15),
            run_time=1.5
        )

        self.stars = stars
        self.title_group = title_group

    def scene_2_spacetime_foundations(self):
        """4D Minkowski spacetime with light cone"""

        # Create sophisticated 3D axes
        axes = ThreeDAxes(
            x_range=[-6, 6, 1],
            y_range=[-6, 6, 1],
            z_range=[-4, 4, 1],
            x_length=12,
            y_length=12,
            z_length=8,
            axis_config={
                "stroke_width": 2,
                "include_tip": True,
                "tip_length": 0.2
            }
        )

        # Axis labels with physics notation
        x_label = MathTex("x", font_size=36, color=RED).next_to(axes.x_axis.get_end(), RIGHT)
        y_label = MathTex("y", font_size=36, color=GREEN).next_to(axes.y_axis.get_end(), UP)
        z_label = MathTex("t", font_size=36, color=BLUE).next_to(axes.z_axis.get_end(), OUT)

        axes_labels = VGroup(x_label, y_label, z_label)

        self.play(
            Create(axes),
            Write(axes_labels),
            run_time=3
        )

        # Intricate light cone structure
        # Upper cone
        light_cone_upper = Surface(
            lambda u, v: axes.c2p(
                u * np.cos(v),
                u * np.sin(v),
                u
            ),
            u_range=[0, 3],
            v_range=[0, TAU],
            resolution=(32, 64),
            fill_opacity=0.25,
            checkerboard_colors=[BLUE_E, BLUE_D],
            stroke_width=0.5,
            stroke_color=SPACETIME_SILVER
        )

        # Lower cone
        light_cone_lower = Surface(
            lambda u, v: axes.c2p(
                u * np.cos(v),
                u * np.sin(v),
                -u
            ),
            u_range=[0, 3],
            v_range=[0, TAU],
            resolution=(32, 64),
            fill_opacity=0.25,
            checkerboard_colors=[BLUE_E, BLUE_D],
            stroke_width=0.5,
            stroke_color=SPACETIME_SILVER
        )

        light_cone = VGroup(light_cone_upper, light_cone_lower)

        self.play(Create(light_cone), run_time=4)

        # Add rotation dynamics
        light_cone.add_updater(lambda m, dt: m.rotate(0.15 * dt, axis=UP))
        self.wait(4)

        # Relativistic metric - expanded form
        metric_title = Text("Minkowski Metric", font_size=32).to_edge(UP, buff=1.5)

        metric_eq = MathTex(
            "ds^2", "=", "-c^2", "dt^2", "+", "dx^2", "+", "dy^2", "+", "dz^2",
            font_size=48
        ).next_to(metric_title, DOWN)

        # Color coding with sophistication
        metric_eq[0].set_color(WHITE)
        metric_eq[2:4].set_color(ELECTRIC_CRIMSON)  # Time component
        metric_eq[5].set_color(RED)  # dx^2
        metric_eq[7].set_color(GREEN)  # dy^2
        metric_eq[9].set_color(BLUE)  # dz^2

        self.add_fixed_in_frame_mobjects(metric_title, metric_eq)

        self.play(
            Write(metric_title),
            run_time=1.5
        )
        self.play(
            Write(metric_eq),
            run_time=3
        )

        # Dramatic emphasis on time component
        time_box = SurroundingRectangle(
            VGroup(metric_eq[2], metric_eq[3]),
            color=ELECTRIC_CRIMSON,
            buff=0.15
        )
        time_annotation = Text(
            "Signature: (-, +, +, +)",
            font_size=24,
            color=ELECTRIC_CRIMSON
        ).next_to(metric_eq, DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(time_box, time_annotation)

        self.play(
            Create(time_box),
            FadeIn(time_annotation, shift=UP),
            Flash(VGroup(metric_eq[2], metric_eq[3]), color=ELECTRIC_CRIMSON),
            run_time=2
        )

        self.wait(3)

        # Clean up for next scene
        light_cone.clear_updaters()

        self.play(
            FadeOut(time_box),
            FadeOut(time_annotation),
            metric_eq.animate.scale(0.6).to_corner(UR, buff=0.5),
            metric_title.animate.scale(0.6).next_to(metric_eq, UP, buff=0.2, aligned_edge=RIGHT),
            run_time=2
        )

        self.axes = axes
        self.axes_labels = axes_labels
        self.light_cone = light_cone
        self.metric_eq = metric_eq
        self.metric_title = metric_title

    def scene_3_quantum_fields(self):
        """Electromagnetic field visualization with dynamic waves"""

        # Zoom into origin
        self.move_camera(
            phi=70*DEGREES,
            theta=-45*DEGREES,
            frame_center=self.axes.c2p(0, 0, 0),
            zoom=0.7,
            run_time=3
        )

        # Create sophisticated E and B field waves
        # Electric field (oscillating in x-direction)
        E_wave = always_redraw(lambda: self.axes.plot_parametric_curve(
            lambda t: self.axes.c2p(
                0.5 * np.sin(5 * t - self.renderer.time * 2),
                0,
                t
            ),
            t_range=[-3, 3, 0.05],
            color=ELECTRIC_CRIMSON,
            stroke_width=6
        ))

        # Magnetic field (oscillating in y-direction, 90 degrees out of phase)
        B_wave = always_redraw(lambda: self.axes.plot_parametric_curve(
            lambda t: self.axes.c2p(
                0,
                0.5 * np.sin(5 * t - self.renderer.time * 2 + PI/2),
                t
            ),
            t_range=[-3, 3, 0.05],
            color=MAGNETIC_SAPPHIRE,
            stroke_width=6
        ))

        # Propagation arrow
        prop_arrow = Arrow3D(
            start=self.axes.c2p(0, 0, -3),
            end=self.axes.c2p(0, 0, 3),
            color=PHOTON_GOLD,
            thickness=0.03,
            base_radius=0.08
        )

        # Field labels with enhanced styling
        E_label = MathTex(
            r"\vec{E}(z,t)",
            color=ELECTRIC_CRIMSON,
            font_size=48
        ).rotate(PI/2, axis=RIGHT).move_to(self.axes.c2p(1, 0, 0))

        B_label = MathTex(
            r"\vec{B}(z,t)",
            color=MAGNETIC_SAPPHIRE,
            font_size=48
        ).rotate(PI/2, axis=RIGHT).move_to(self.axes.c2p(0, 1, 0))

        k_label = MathTex(
            r"\vec{k}",
            color=PHOTON_GOLD,
            font_size=48
        ).next_to(prop_arrow, RIGHT)

        # Animate field emergence
        self.play(
            Create(E_wave),
            Create(B_wave),
            Create(prop_arrow),
            run_time=3
        )

        self.play(
            Write(E_label),
            Write(B_label),
            Write(k_label),
            run_time=2
        )

        # Let fields oscillate
        self.wait(6)

        # Add wave equation
        wave_eq = MathTex(
            r"\nabla^2 \vec{E} - \frac{1}{c^2}\frac{\partial^2 \vec{E}}{\partial t^2} = 0",
            font_size=36
        ).to_edge(DOWN, buff=1.5)

        self.add_fixed_in_frame_mobjects(wave_eq)
        self.play(Write(wave_eq), run_time=2)
        self.wait(3)

        # Store for next scene
        self.E_wave = E_wave
        self.B_wave = B_wave
        self.field_labels = VGroup(E_label, B_label, k_label, prop_arrow)
        self.wave_eq = wave_eq

    def scene_4_maxwell_transformation(self):
        """Transform Maxwell equations to relativistic form"""

        # Classical Maxwell equations
        maxwell_classical = VGroup(
            MathTex(r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}", font_size=32),
            MathTex(r"\nabla \cdot \vec{B} = 0", font_size=32),
            MathTex(r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}", font_size=32),
            MathTex(r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)

        maxwell_title = Text("Maxwell's Equations", font_size=36, weight=BOLD).next_to(maxwell_classical, UP, buff=0.5)

        maxwell_group = VGroup(maxwell_title, maxwell_classical).move_to(ORIGIN + LEFT * 3)

        self.add_fixed_in_frame_mobjects(maxwell_group)

        # Remove wave equation
        self.remove(self.wave_eq)

        self.play(
            Write(maxwell_title),
            LaggedStart(*[Write(eq) for eq in maxwell_classical], lag_ratio=0.4),
            run_time=5
        )

        self.wait(2)

        # Introduce field strength tensor
        tensor_intro = MathTex(
            r"F^{\mu\nu} = \begin{pmatrix} 0 & -E_x/c & -E_y/c & -E_z/c \\ E_x/c & 0 & -B_z & B_y \\ E_y/c & B_z & 0 & -B_x \\ E_z/c & -B_y & B_x & 0 \end{pmatrix}",
            font_size=28
        ).move_to(ORIGIN + RIGHT * 3)

        tensor_title = Text("Electromagnetic Tensor", font_size=32, weight=BOLD).next_to(tensor_intro, UP, buff=0.5)

        tensor_group = VGroup(tensor_title, tensor_intro)

        self.add_fixed_in_frame_mobjects(tensor_group)

        self.play(
            FadeIn(tensor_title, shift=RIGHT),
            Write(tensor_intro),
            run_time=4
        )

        self.wait(3)

        # Transform to compact form with particle dissolution effect
        self.play(
            *[FadeOut(eq, target_position=ORIGIN) for eq in maxwell_classical],
            FadeOut(maxwell_title),
            FadeOut(tensor_intro),
            FadeOut(tensor_title),
            run_time=2
        )

        # Compact relativistic form
        maxwell_compact = MathTex(
            r"\partial_\mu F^{\mu\nu} = \mu_0 J^\nu",
            font_size=64,
            color=PHOTON_GOLD
        )

        self.add_fixed_in_frame_mobjects(maxwell_compact)

        # Dramatic emergence with light rays
        self.play(
            Write(maxwell_compact),
            Flash(ORIGIN, color=PHOTON_GOLD, line_length=2, num_lines=32),
            run_time=3
        )

        # Pulsing emphasis
        for _ in range(3):
            self.play(
                maxwell_compact.animate.scale(1.1).set_color(WHITE),
                rate_func=there_and_back,
                run_time=0.8
            )

        self.wait(3)

        # Move to corner
        self.play(
            maxwell_compact.animate.scale(0.5).to_corner(UL, buff=1),
            run_time=2
        )

        self.maxwell_compact = maxwell_compact

    def scene_5_qed_lagrangian(self):
        """The heart of QED - Lagrangian density"""

        # Reset camera
        self.move_camera(
            phi=0,
            theta=-90*DEGREES,
            zoom=1,
            run_time=2
        )

        # Clear 3D elements
        self.play(
            FadeOut(self.axes),
            FadeOut(self.axes_labels),
            FadeOut(self.light_cone),
            FadeOut(self.E_wave),
            FadeOut(self.B_wave),
            FadeOut(self.field_labels),
            run_time=2
        )

        # Grand Lagrangian reveal
        lagrangian_title = Text(
            "QED Lagrangian Density",
            font_size=48,
            weight=BOLD,
            gradient=(FERMION_ORANGE, PHOTON_GOLD)
        ).to_edge(UP, buff=0.5)

        # Full Lagrangian with careful color coding
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}}", "=",
            r"\bar{\psi}", r"\left(", "i", r"\gamma^\mu", r"D_\mu", "-", "m", r"\right)", r"\psi",
            "-", r"\frac{1}{4}", r"F_{\mu\nu}", r"F^{\mu\nu}",
            font_size=56
        )

        # Sophisticated color mapping
        lagrangian[0].set_color(WHITE)  # L_QED
        lagrangian[2].set_color(FERMION_ORANGE)  # psi_bar
        lagrangian[5].set_color(QUANTUM_VIOLET)  # gamma
        lagrangian[6].set_color(GAUGE_EMERALD)  # D_mu
        lagrangian[8].set_color(WHITE)  # mass
        lagrangian[10].set_color(FERMION_ORANGE)  # psi
        lagrangian[13].set_color(PHOTON_GOLD)  # F_munu
        lagrangian[14].set_color(PHOTON_GOLD)  # F^munu

        # Beautiful background plane
        lag_bg = Rectangle(
            width=lagrangian.width + 1,
            height=lagrangian.height + 0.8,
            fill_color=COSMIC_BLUE,
            fill_opacity=0.85,
            stroke_color=PHOTON_GOLD,
            stroke_width=3
        ).move_to(lagrangian)

        lagrangian_group = VGroup(lag_bg, lagrangian)

        self.add_fixed_in_frame_mobjects(lagrangian_title, lagrangian_group)

        self.play(
            Write(lagrangian_title),
            run_time=2
        )

        self.play(
            FadeIn(lag_bg, scale=0.9),
            run_time=1.5
        )

        # Write Lagrangian term by term
        self.play(
            LaggedStart(*[Write(term) for term in lagrangian], lag_ratio=0.15),
            run_time=6
        )

        self.wait(2)

        # Highlight each term with explanation
        # Fermion term
        fermion_terms = VGroup(*lagrangian[2:11])
        fermion_box = SurroundingRectangle(fermion_terms, color=FERMION_ORANGE, buff=0.15)
        fermion_label = Text("Dirac Fermion + Interaction", font_size=28, color=FERMION_ORANGE).next_to(fermion_box, DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(fermion_box, fermion_label)

        self.play(
            Create(fermion_box),
            FadeIn(fermion_label, shift=UP),
            run_time=2
        )
        self.wait(2)

        # Field term
        field_terms = VGroup(*lagrangian[11:])
        field_box = SurroundingRectangle(field_terms, color=PHOTON_GOLD, buff=0.15)
        field_label = Text("Electromagnetic Field", font_size=28, color=PHOTON_GOLD).next_to(field_box, DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(field_box, field_label)

        self.play(
            FadeOut(fermion_box),
            FadeOut(fermion_label),
            Create(field_box),
            FadeIn(field_label, shift=UP),
            run_time=2
        )
        self.wait(2)

        # Covariant derivative expansion
        D_mu = lagrangian[6]
        D_mu_expanded = MathTex(
            r"D_\mu = \partial_\mu + ieA_\mu",
            font_size=48,
            color=GAUGE_EMERALD
        ).next_to(lagrangian_group, DOWN, buff=1)

        gauge_annotation = Text(
            "Gauge covariant derivative - Minimal coupling",
            font_size=24,
            color=GAUGE_EMERALD
        ).next_to(D_mu_expanded, DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(D_mu_expanded, gauge_annotation)

        self.play(
            FadeOut(field_box),
            FadeOut(field_label),
            Indicate(D_mu, color=GAUGE_EMERALD, scale_factor=1.5),
            run_time=1
        )

        self.play(
            Write(D_mu_expanded),
            FadeIn(gauge_annotation),
            run_time=3
        )

        self.wait(3)

        # Gauge invariance demonstration
        gauge_title = Text("U(1) Gauge Symmetry", font_size=36, weight=BOLD, color=QUANTUM_VIOLET).to_edge(LEFT, buff=0.5).shift(DOWN)

        gauge_transforms = VGroup(
            MathTex(r"\psi(x) \to e^{i\alpha(x)} \psi(x)", font_size=32),
            MathTex(r"A_\mu(x) \to A_\mu(x) - \frac{1}{e}\partial_\mu \alpha(x)", font_size=32),
            MathTex(r"\mathcal{L}_{\text{QED}} \text{ unchanged}", font_size=32, color=PHOTON_GOLD)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(gauge_title, DOWN, buff=0.4)

        gauge_group = VGroup(gauge_title, gauge_transforms)

        self.add_fixed_in_frame_mobjects(gauge_group)

        self.play(
            Write(gauge_title),
            run_time=1.5
        )

        self.play(
            LaggedStart(*[Write(eq) for eq in gauge_transforms], lag_ratio=0.6),
            run_time=4
        )

        self.wait(4)

        # Clean up
        self.play(
            FadeOut(gauge_group),
            FadeOut(D_mu_expanded),
            FadeOut(gauge_annotation),
            run_time=2
        )

        self.lagrangian_group = lagrangian_group
        self.lagrangian = lagrangian
        self.lagrangian_title = lagrangian_title

    def scene_6_feynman_interactions(self):
        """Feynman diagrams with multiple processes"""

        self.play(
            self.lagrangian_group.animate.scale(0.5).to_corner(UR, buff=0.5),
            self.lagrangian_title.animate.scale(0.5).next_to(self.lagrangian_group, UP, buff=0.2, aligned_edge=RIGHT),
            run_time=2
        )

        # Title
        feynman_title = Text("QED Interactions: Feynman Diagrams", font_size=42, weight=BOLD).to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(feynman_title)
        self.play(Write(feynman_title), run_time=2)

        # Create multiple diagrams showing different processes

        # Diagram 1: Electron-electron scattering (left)
        def create_scattering_diagram(position, scale=1.0):
            v1 = np.array([-1, -0.7, 0]) * scale + position
            v2 = np.array([1, 0.7, 0]) * scale + position

            e_in1 = Arrow(v1 + LEFT*1.5*scale, v1, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)
            e_in2 = Arrow(v2 + LEFT*1.5*scale, v2, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)

            photon = ParametricFunction(
                lambda t: v1 + (v2-v1)*t + 0.2*scale*np.sin(PI*t*6)*RIGHT,
                t_range=[0, 1],
                color=PHOTON_GOLD,
                stroke_width=5
            )

            e_out1 = Arrow(v1, v1 + RIGHT*1.5*scale + UP*0.3*scale, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)
            e_out2 = Arrow(v2, v2 + RIGHT*1.5*scale + DOWN*0.3*scale, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)

            labels = VGroup(
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_in1.get_start(), LEFT, buff=0.1),
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_in2.get_start(), LEFT, buff=0.1),
                MathTex(r"\gamma", font_size=28, color=PHOTON_GOLD).move_to(photon.get_center() + DOWN*0.5*scale),
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_out1.get_end(), RIGHT, buff=0.1),
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_out2.get_end(), RIGHT, buff=0.1)
            )

            title = Text("e-e Scattering", font_size=24, weight=BOLD).next_to(VGroup(e_in1, e_in2, e_out1, e_out2), UP, buff=0.4)

            return VGroup(e_in1, e_in2, photon, e_out1, e_out2, labels, title)

        # Diagram 2: Pair annihilation (center)
        def create_annihilation_diagram(position, scale=1.0):
            v = position

            e_in = Arrow(v + LEFT*1.5*scale + DOWN*0.5*scale, v, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)
            p_in = Arrow(v + LEFT*1.5*scale + UP*0.5*scale, v, buff=0, stroke_width=4, color=RED, max_tip_length_to_length_ratio=0.15)

            photon_out = ParametricFunction(
                lambda t: v + RIGHT*t*1.5*scale + 0.15*scale*np.sin(PI*t*8)*UP,
                t_range=[0, 1],
                color=PHOTON_GOLD,
                stroke_width=5
            )

            labels = VGroup(
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_in.get_start(), LEFT, buff=0.1),
                MathTex("e^+", font_size=24, color=RED).next_to(p_in.get_start(), LEFT, buff=0.1),
                MathTex(r"\gamma", font_size=28, color=PHOTON_GOLD).next_to(photon_out.get_end(), RIGHT, buff=0.1)
            )

            title = Text("Pair Annihilation", font_size=24, weight=BOLD).next_to(VGroup(e_in, p_in, photon_out), UP, buff=0.4)

            return VGroup(e_in, p_in, photon_out, labels, title)

        # Diagram 3: Pair creation (right)
        def create_pair_creation_diagram(position, scale=1.0):
            v = position

            photon_in = ParametricFunction(
                lambda t: v + LEFT*(1.5-t*1.5)*scale + 0.15*scale*np.sin(PI*t*8)*UP,
                t_range=[0, 1],
                color=PHOTON_GOLD,
                stroke_width=5
            )

            e_out = Arrow(v, v + RIGHT*1.5*scale + DOWN*0.5*scale, buff=0, stroke_width=4, color=BLUE, max_tip_length_to_length_ratio=0.15)
            p_out = Arrow(v, v + RIGHT*1.5*scale + UP*0.5*scale, buff=0, stroke_width=4, color=RED, max_tip_length_to_length_ratio=0.15)

            labels = VGroup(
                MathTex(r"\gamma", font_size=28, color=PHOTON_GOLD).next_to(photon_in.get_start(), LEFT, buff=0.1),
                MathTex("e^-", font_size=24, color=BLUE).next_to(e_out.get_end(), RIGHT, buff=0.1),
                MathTex("e^+", font_size=24, color=RED).next_to(p_out.get_end(), RIGHT, buff=0.1)
            )

            title = Text("Pair Creation", font_size=24, weight=BOLD).next_to(VGroup(e_out, p_out, photon_in), UP, buff=0.4)

            return VGroup(photon_in, e_out, p_out, labels, title)

        # Position diagrams
        diagram_scattering = create_scattering_diagram(LEFT*4 + DOWN*0.5, scale=0.8)
        diagram_annihilation = create_annihilation_diagram(ORIGIN + DOWN*0.5, scale=0.8)
        diagram_creation = create_pair_creation_diagram(RIGHT*4 + DOWN*0.5, scale=0.8)

        all_diagrams = VGroup(diagram_scattering, diagram_annihilation, diagram_creation)

        self.add_fixed_in_frame_mobjects(all_diagrams)

        # Animate diagrams appearing
        self.play(
            LaggedStart(*[FadeIn(diag, shift=UP) for diag in all_diagrams], lag_ratio=0.5),
            run_time=5
        )

        self.wait(3)

        # Store for next scene
        self.feynman_diagrams = all_diagrams
        self.feynman_title = feynman_title

    def scene_7_fine_structure(self):
        """Deep dive into the fine structure constant"""

        # Fade diagrams slightly
        self.play(
            self.feynman_diagrams.animate.set_opacity(0.3),
            run_time=1
        )

        # Alpha constant emergence
        alpha_title = Text(
            "The Fine Structure Constant",
            font_size=42,
            weight=BOLD,
            color=PHOTON_GOLD
        ).to_edge(UP, buff=2)

        alpha_value = MathTex(
            r"\alpha = \frac{e^2}{4\pi\epsilon_0\hbar c} \approx \frac{1}{137.036}",
            font_size=56
        )

        alpha_value[0][0].set_color(PHOTON_GOLD)  # alpha symbol

        alpha_group = VGroup(alpha_title, alpha_value).arrange(DOWN, buff=0.6)

        self.add_fixed_in_frame_mobjects(alpha_group)

        self.play(
            FadeOut(self.feynman_title),
            Write(alpha_title),
            run_time=2
        )

        self.play(
            Write(alpha_value),
            Flash(alpha_value.get_center(), color=PHOTON_GOLD, line_length=1.5, num_lines=20),
            run_time=3
        )

        # Emphasize the value
        value_box = SurroundingRectangle(alpha_value, color=PHOTON_GOLD, buff=0.2)

        self.add_fixed_in_frame_mobjects(value_box)

        self.play(Create(value_box), run_time=1.5)

        self.wait(2)

        # Physical interpretations
        interpretations = VGroup(
            Text("Coupling strength of electromagnetic interaction", font_size=24),
            Text("Dimensionless fundamental constant", font_size=24),
            Text("Determines atomic spectra fine structure", font_size=24),
            Text("Probability amplitude for photon emission", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(DOWN, buff=1)

        self.add_fixed_in_frame_mobjects(interpretations)

        self.play(
            LaggedStart(*[FadeIn(text, shift=UP) for text in interpretations], lag_ratio=0.4),
            run_time=4
        )

        self.wait(4)

        # Clean up
        self.play(
            FadeOut(interpretations),
            FadeOut(value_box),
            alpha_group.animate.scale(0.6).to_corner(UL, buff=0.5),
            run_time=2
        )

        self.alpha_group = alpha_group

    def scene_8_running_coupling(self):
        """Renormalization and energy-dependent coupling"""

        # Restore feynman diagrams opacity
        self.play(
            self.feynman_diagrams.animate.set_opacity(0.15),
            run_time=1
        )

        # Title
        renorm_title = Text(
            "Renormalization: Running of α",
            font_size=42,
            weight=BOLD
        ).to_edge(UP, buff=0.5)

        self.add_fixed_in_frame_mobjects(renorm_title)
        self.play(Write(renorm_title), run_time=2)

        # Create running coupling plot
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[0.006, 0.010, 0.001],
            x_length=8,
            y_length=5,
            axis_config={
                "include_tip": True,
                "numbers_to_include": []
            }
        ).shift(DOWN*0.5)

        # Axis labels
        x_label = MathTex(r"\log_{10}(Q/\text{GeV})", font_size=32).next_to(axes.x_axis, DOWN)
        y_label = MathTex(r"\alpha(Q)", font_size=32).next_to(axes.y_axis, LEFT)

        # Running coupling function (simplified QED)
        def alpha_running(logQ):
            alpha_0 = 1/137.036
            # Simplified one-loop running
            beta = 2 * alpha_0 / (3 * PI)
            return alpha_0 / (1 - beta * logQ * 2)

        # Create smooth curve
        running_curve = axes.plot(
            alpha_running,
            x_range=[0, 5.5],
            color=PHOTON_GOLD,
            stroke_width=5
        )

        # Energy scale markers
        markers = VGroup()
        scales = [
            (0, "m_e", BLUE),
            (2, "M_W", GREEN),
            (3, "M_Z", RED),
            (5, "M_{Planck}", PURPLE)
        ]

        for logQ, label, color in scales:
            if logQ <= 5.5:
                point = axes.c2p(logQ, alpha_running(logQ))
                dot = Dot(point, color=color, radius=0.1)
                label_tex = MathTex(label, font_size=24, color=color).next_to(dot, UP, buff=0.2)
                markers.add(VGroup(dot, label_tex))

        graph_group = VGroup(axes, x_label, y_label, running_curve, markers)

        self.add_fixed_in_frame_mobjects(graph_group)

        self.play(
            Create(axes),
            Write(x_label),
            Write(y_label),
            run_time=2
        )

        self.play(
            Create(running_curve),
            run_time=4
        )

        self.play(
            LaggedStart(*[FadeIn(marker) for marker in markers], lag_ratio=0.4),
            run_time=3
        )

        self.wait(2)

        # Explanation
        explanation = Text(
            "Coupling increases with energy due to vacuum polarization",
            font_size=28
        ).to_edge(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(explanation)

        self.play(FadeIn(explanation, shift=UP), run_time=2)

        self.wait(4)

        # Store for next scene
        self.running_graph = graph_group
        self.renorm_title = renorm_title
        self.renorm_explanation = explanation

    def scene_9_vacuum_structure(self):
        """Vacuum polarization and virtual particles"""

        # Fade previous elements
        self.play(
            FadeOut(self.running_graph),
            FadeOut(self.renorm_explanation),
            FadeOut(self.feynman_diagrams),
            run_time=2
        )

        # New title
        vacuum_title = Text(
            "Quantum Vacuum Structure",
            font_size=42,
            weight=BOLD,
            gradient=(QUANTUM_VIOLET, PHOTON_GOLD)
        ).to_edge(UP, buff=0.5)

        self.add_fixed_in_frame_mobjects(vacuum_title)

        self.play(
            FadeOut(self.renorm_title),
            Write(vacuum_title),
            run_time=2
        )

        # Virtual particle pairs visualization
        def create_virtual_pair(position, scale=0.3):
            electron = Circle(radius=scale, color=BLUE, fill_opacity=0.7).shift(position + LEFT*scale*1.5)
            positron = Circle(radius=scale, color=RED, fill_opacity=0.7).shift(position + RIGHT*scale*1.5)

            e_label = MathTex("e^-", font_size=16).move_to(electron)
            p_label = MathTex("e^+", font_size=16).move_to(positron)

            return VGroup(electron, e_label, positron, p_label)

        # Create multiple virtual pairs
        vacuum_pairs = VGroup(*[
            create_virtual_pair(
                np.array([
                    np.random.uniform(-5, 5),
                    np.random.uniform(-3, 2),
                    0
                ]),
                scale=np.random.uniform(0.15, 0.35)
            )
            for _ in range(20)
        ])

        self.add_fixed_in_frame_mobjects(vacuum_pairs)

        # Pairs bubble up
        self.play(
            LaggedStart(*[
                FadeIn(pair, scale=0.1, shift=UP*np.random.uniform(0.1, 0.5))
                for pair in vacuum_pairs
            ], lag_ratio=0.1),
            run_time=5
        )

        # Add shimmer effect
        self.play(
            *[pair.animate.set_opacity(np.random.uniform(0.3, 1.0)) for pair in vacuum_pairs],
            rate_func=there_and_back,
            run_time=2
        )

        self.wait(2)

        # Explanatory text
        vacuum_explanation = VGroup(
            Text("Virtual electron-positron pairs constantly appear and disappear", font_size=26),
            Text("They screen the bare charge, modifying the effective coupling", font_size=26),
            Text("This is the origin of charge renormalization", font_size=26)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(DOWN, buff=0.8)

        self.add_fixed_in_frame_mobjects(vacuum_explanation)

        self.play(
            LaggedStart(*[FadeIn(text, shift=UP) for text in vacuum_explanation], lag_ratio=0.5),
            run_time=4
        )

        self.wait(4)

        # Fade for finale
        self.play(
            FadeOut(vacuum_pairs),
            FadeOut(vacuum_explanation),
            run_time=2
        )

        self.vacuum_title = vacuum_title

    def scene_10_synthesis(self):
        """Grand synthesis bringing everything together"""

        cleanup_targets = [
            "vacuum_title",
            "lagrangian_group",
            "lagrangian_title",
            "maxwell_compact",
            "metric_eq",
            "metric_title",
            "alpha_group",
            "running_graph",
            "renorm_title",
            "renorm_explanation",
            "feynman_diagrams",
        ]
        to_fade = [getattr(self, name) for name in cleanup_targets if hasattr(self, name)]
        if to_fade:
            self.play(*[FadeOut(mob) for mob in to_fade], run_time=2)
            for mob in to_fade:
                self.remove_fixed_in_frame_mobjects(mob)

        # Final synthesis title
        synthesis_title = Text(
            "QED: The Complete Picture",
            font_size=48,
            weight=BOLD,
            gradient=(ELECTRIC_CRIMSON, PHOTON_GOLD),
        ).to_edge(UP, buff=0.4)

        self.add_fixed_in_frame_mobjects(synthesis_title)

        self.play(
            Write(synthesis_title),
            Flash(synthesis_title.get_center(), color=PHOTON_GOLD, line_length=2, num_lines=32),
            run_time=3,
        )

        # Central Lagrangian hub
        mini_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            font_size=34,
        ).scale(0.95)
        mini_lagrangian.shift(DOWN * 0.2)
        mini_lagrangian.set_color_by_tex_to_color_map({
            r"\psi": FERMION_ORANGE,
            r"\bar{\psi}": FERMION_ORANGE,
            r"D_\mu": GAUGE_EMERALD,
            r"F": PHOTON_GOLD,
        })

        # Supporting elements positioned with generous spacing
        mini_maxwell = MathTex(
            r"\partial_\mu F^{\mu\nu} = \mu_0 J^\nu",
            font_size=30,
        ).scale(0.9)
        mini_alpha = MathTex(
            r"\alpha \approx \frac{1}{137}",
            font_size=30,
            color=PHOTON_GOLD,
        ).scale(0.9)
        mini_gauge = MathTex(
            r"U(1)",
            font_size=36,
            color=QUANTUM_VIOLET,
        ).scale(0.9)

        mini_feynman_parts = VGroup(
            Line(LEFT * 0.5, ORIGIN, stroke_width=3, color=BLUE),
            Line(ORIGIN, RIGHT * 0.5 + UP * 0.3, stroke_width=3, color=BLUE),
            ParametricFunction(
                lambda t: UP * 0.3 * t + RIGHT * 0.1 * np.sin(PI * t * 4),
                t_range=[0, 1],
                color=PHOTON_GOLD,
                stroke_width=3,
            ).move_to(ORIGIN + UP * 0.15),
        ).scale(1.0)

        left_column = VGroup(mini_maxwell, mini_feynman_parts).arrange(
            DOWN, buff=1.5, aligned_edge=LEFT
        )
        left_column.move_to(LEFT * 4 + DOWN * 0.3)

        right_column = VGroup(mini_alpha, mini_gauge).arrange(
            DOWN, buff=1.5, aligned_edge=RIGHT
        )
        right_column.move_to(RIGHT * 4 + DOWN * 0.3)

        synthesis_elements = VGroup(
            mini_lagrangian,
            mini_maxwell,
            mini_alpha,
            mini_feynman_parts,
            mini_gauge,
        )

        self.add_fixed_in_frame_mobjects(synthesis_elements)

        self.play(
            LaggedStart(*[FadeIn(elem, scale=0.5) for elem in synthesis_elements], lag_ratio=0.25),
            run_time=4,
        )
        self.wait(2)

        # Connections with gentle curvature to avoid crowding
        connections = VGroup(
            CurvedArrow(mini_maxwell.get_right(), mini_lagrangian.get_left(), angle=PI / 4, color=PHOTON_GOLD),
            CurvedArrow(mini_alpha.get_left(), mini_lagrangian.get_right(), angle=-PI / 4, color=PHOTON_GOLD),
            CurvedArrow(
                mini_lagrangian.get_bottom() + LEFT * 0.2,
                mini_feynman_parts.get_top(),
                angle=-PI / 5,
                color=FERMION_ORANGE,
            ),
            CurvedArrow(
                mini_lagrangian.get_bottom() + RIGHT * 0.2,
                mini_gauge.get_top(),
                angle=PI / 5,
                color=QUANTUM_VIOLET,
            ),
        )

        self.add_fixed_in_frame_mobjects(connections)
        self.play(
            LaggedStart(*[Create(arrow) for arrow in connections], lag_ratio=0.2),
            run_time=3,
        )
        self.wait(3)

        summary_text = VGroup(
            Text("Gauge Theory of Electromagnetism", font_size=30, weight=BOLD),
            Text("Predicts anomalous magnetic moment to 10 decimal places", font_size=22),
            Text("Most precisely tested theory in physics", font_size=22),
            Text("Foundation for electroweak and QCD", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(DOWN, buff=0.7)

        self.add_fixed_in_frame_mobjects(summary_text)
        self.play(
            LaggedStart(*[FadeIn(text, shift=UP) for text in summary_text], lag_ratio=0.35),
            run_time=4,
        )
        self.wait(4)

        self.synthesis_title = synthesis_title
        self.synthesis_elements = synthesis_elements
        self.connections = connections
        self.summary_text = summary_text

    def scene_11_finale(self):
        """Epic cosmic finale"""

        # Fade all synthesis elements
        self.play(
            FadeOut(self.synthesis_title),
            FadeOut(self.synthesis_elements),
            FadeOut(self.connections),
            FadeOut(self.summary_text),
            FadeOut(self.lagrangian_group),
            FadeOut(self.lagrangian_title),
            FadeOut(self.maxwell_compact),
            FadeOut(self.metric_eq),
            FadeOut(self.metric_title),
            FadeOut(self.alpha_group),
            run_time=3
        )

        # Bring back stars with increased opacity
        self.play(
            self.stars.animate.set_opacity(0.8),
            run_time=2
        )

        # Pull camera way back
        self.move_camera(
            phi=70*DEGREES,
            theta=-45*DEGREES,
            zoom=0.3,
            run_time=4
        )

        # Final message
        final_message = VGroup(
            Text(
                "QED",
                font_size=96,
                weight=BOLD,
                gradient=(ELECTRIC_CRIMSON, PHOTON_GOLD, QUANTUM_VIOLET)
            ),
            Text(
                "Unifying Light and Matter",
                font_size=48,
                slant=ITALIC
            ),
            Text(
                "Through Gauge Symmetry",
                font_size=48,
                slant=ITALIC
            )
        ).arrange(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(final_message)

        self.play(
            FadeIn(final_message, scale=0.7),
            Flash(ORIGIN, color=PHOTON_GOLD, line_length=3, num_lines=48, flash_radius=4),
            run_time=4
        )

        # Hold with subtle glow
        for _ in range(3):
            self.play(
                final_message[0].animate.set_color(WHITE),
                rate_func=there_and_back,
                run_time=1.5
            )

        self.wait(3)

        # Fade to stars
        self.play(
            FadeOut(final_message),
            self.stars.animate.set_opacity(1.0),
            run_time=3
        )

        self.wait(2)

        # Finis
        finis = Text(
            "Finis",
            font_size=72,
            weight=BOLD,
            color=PHOTON_GOLD
        )

        self.add_fixed_in_frame_mobjects(finis)

        self.play(
            FadeIn(finis),
            run_time=2
        )

        self.wait(4)

        self.play(
            FadeOut(finis),
            FadeOut(self.stars),
            run_time=4
        )

        self.wait(2)
