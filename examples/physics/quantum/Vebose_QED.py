from manim import *
import numpy as np

##############################################################################
#  StarField utility
##############################################################################
class StarField(VGroup):
    """
    Creates a field of randomly placed small dots (stars) in either 2D or 3D.
    """
    def __init__(self, is_3D=False, num_stars=400, **kwargs):
        super().__init__(**kwargs)
        for _ in range(num_stars):
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)
            z = np.random.uniform(-3, 3) if is_3D else 0
            star = Dot(point=[x, y, z], color=WHITE, radius=0.015)
            self.add(star)

##############################################################################
#  QEDJourney main scene
##############################################################################
class QEDJourney(ThreeDScene):
    def construct(self):
        """
        This scene contains:
          1. Cosmic Starfield Fade-In
          2. Title & Sub-Title Introduction
          3. Rotating Minkowski Spacetime Wireframe + Light Cone
          4. Metric Equation (ds^2...) in color-coded form
          5. Zoom to Origin & E/B Wave Visualization
          6. Maxwell Equations: Classical -> Relativistic Notation
          7. QED Lagrangian (Color-coded) + Gauge Invariance
          8. Feynman Diagram w/ electron lines & photon
          9. Coupling Constant alpha (~1/137) + symbolic form
          10. 2D Graph of Running Coupling
          11. Final Zoom Out & Collage with "Finis"
        """

        # CONFIGURE THE CAMERA to have a slight tilt/angle:
        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)

        ############################################################################
        # 1. COSMIC STARFIELD FADE-IN
        ############################################################################
        star_field = StarField(is_3D=True, num_stars=400)
        self.play(FadeIn(star_field, run_time=3))
        self.wait()

        ############################################################################
        # 2. TITLE INTRODUCTION
        ############################################################################
        main_title = Text(
            "Quantum Field Theory:\nA Journey into the Electromagnetic Interaction",
            font_size=52,
            gradient=(BLUE, YELLOW),
            weight=BOLD
        ).scale(1.0)
        main_title.set_glow_factor(0.4)  # subtle "glow" effect in newer Manim builds

        # Move title to center first
        self.play(Write(main_title), run_time=3)
        self.wait(2)

        # Then shrink and move to upper-left
        self.play(
            main_title.animate.scale(0.5).to_corner(UL),
            run_time=2
        )
        self.wait(1)

        ############################################################################
        # 3. 4D MINKOWSKI SPACETIME WIREFRAME + LIGHT CONE
        ############################################################################
        # We'll represent Minkowski space as a 3D wireframe grid plus a light cone.
        axes = ThreeDAxes(
            x_range=[-4, 4], y_range=[-4, 4], z_range=[-4, 4],
            x_length=8, y_length=8, z_length=8
        )
        wireframe_surface = Surface(
            # Minkowski 3D representation is purely symbolic here.
            lambda u, v: axes.c2p(u, v, 0),
            u_range=[-4, 4],
            v_range=[-4, 4],
            fill_opacity=0.0,
            stroke_color=BLUE_E,
            stroke_width=1
        )
        # Light Cone representation
        light_cone = Surface(
            lambda u, v: axes.c2p(
                v * np.cos(u), 
                v * np.sin(u), 
                v  # upward in z for the "future" light cone
            ),
            u_range=[0, 2 * PI],
            v_range=[0, 3],
            fill_opacity=0.1,
            checkerboard_colors=[YELLOW, YELLOW],
            stroke_color=YELLOW
        )

        # Animate the creation
        self.play(
            Create(axes),
            Create(wireframe_surface),
            run_time=3
        )
        self.play(Create(light_cone), run_time=2)

        # Slowly rotate the wireframe in the background
        self.begin_ambient_camera_rotation(rate=0.05)

        ############################################################################
        # 4. METRIC EQUATION ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2
        ############################################################################
        # Color-coded to highlight negative time vs. positive spatial parts
        metric_eq = MathTex(
            r"ds^2",
            r"=",
            r"-\,c^2\,dt^2",
            r"+\,dx^2",
            r"+\,dy^2",
            r"+\,dz^2",
            font_size=50
        )
        metric_eq.set_color_by_tex("ds^2", GOLD)
        metric_eq.set_color_by_tex("c^2", RED)
        metric_eq.set_color_by_tex("dt^2", RED)
        metric_eq.set_color_by_tex("dx^2", GREEN)
        metric_eq.set_color_by_tex("dy^2", BLUE)
        metric_eq.set_color_by_tex("dz^2", TEAL)

        metric_eq.to_corner(DR).shift(UP*0.5)
        self.play(Write(metric_eq), run_time=3)
        self.wait(2)

        ############################################################################
        # 5. ZOOM INTO ORIGIN + E/B WAVE VISUALIZATION
        ############################################################################
        # We'll move the camera to the origin for a close-up on wave fields
        self.stop_ambient_camera_rotation()
        self.move_camera(frame_center=self.camera.frame_center + UP * 2 + IN * 5)
        self.wait(2)

        # Create a wave for E and B fields in 3D
        # We use ParametricFunction for a sine wave traveling along z-axis,
        # with E field in x, B field in y, for instance.
        wave_length = 5
        # Electric field in red
        e_wave = ParametricFunction(
            lambda t: axes.c2p(
                np.sin(2 * t),  # E field amplitude along x
                0,             # (y = 0, but we'll visually offset for clarity)
                t              # wave traveling along z
            ),
            t_range=[-wave_length, wave_length],
            color=RED
        )
        # Magnetic field in blue
        b_wave = ParametricFunction(
            lambda t: axes.c2p(
                0,
                np.sin(2 * t),  # B field amplitude along y
                t
            ),
            t_range=[-wave_length, wave_length],
            color=BLUE
        )

        # Label vectors E and B
        label_E = MathTex(r"\vec{E}", color=RED).move_to(e_wave.get_end())
        label_B = MathTex(r"\vec{B}", color=BLUE).move_to(b_wave.get_end())

        # 3D Arrow for direction of propagation (z-axis)
        propagation_arrow = Arrow3D(
            start=axes.c2p(0, 0, -wave_length),
            end=axes.c2p(0, 0, wave_length),
            color=YELLOW
        ).set_stroke(width=4)
        prop_label = Tex("Propagation (z-axis)").set_color(YELLOW)
        prop_label.next_to(propagation_arrow.get_end(), UP + RIGHT)

        self.play(
            LaggedStart(
                Create(e_wave),
                Create(b_wave),
                lag_ratio=0.5,
                run_time=3
            )
        )
        self.play(
            FadeIn(label_E, shift=RIGHT),
            FadeIn(label_B, shift=RIGHT),
            GrowArrow(propagation_arrow),
            FadeIn(prop_label),
            run_time=3
        )
        self.wait(2)

        ############################################################################
        # 6. MAXWELL EQUATIONS: CLASSICAL -> 4-VECTOR NOTATION
        ############################################################################
        # We'll show the classical form, then morph to the relativistic form.

        # Classical Maxwell
        maxwell_classical = VGroup(
            MathTex(r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}", font_size=36),
            MathTex(
                r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0 \frac{\partial \mathbf{E}}{\partial t}",
                font_size=36
            ),
            MathTex(r"\nabla \cdot \mathbf{B} = 0", font_size=36),
            MathTex(r"\nabla \times \mathbf{E} = - \frac{\partial \mathbf{B}}{\partial t}", font_size=36)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR)

        # Relativistic compact form
        maxwell_relativistic = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu", font_size=38
        )

        self.play(
            FadeIn(maxwell_classical, shift=RIGHT, run_time=3)
        )
        self.wait(2)

        # Morph to the relativistic form:
        self.play(
            ReplacementTransform(maxwell_classical, maxwell_relativistic),
            run_time=4
        )
        self.wait(2)

        ############################################################################
        # 7. QED LAGRANGIAN (COLOR-CODED) + GAUGE INVARIANCE
        ############################################################################
        # QED Lagrangian
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi \;-\; \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            font_size=40
        )
        qed_lagrangian.to_edge(UP)

        # Color the terms:
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu\nu}", GOLD)

        # Animate Lagrangian appearing
        plane_bg = Rectangle(
            width=10,
            height=3.5,
            fill_color=BLACK,
            fill_opacity=0.6,
            stroke_opacity=0.2
        ).move_to(UP*2).set_z_index(-1)

        self.play(
            FadeIn(plane_bg),
            FadeIn(qed_lagrangian, shift=UP),
            run_time=3
        )
        self.wait(1)

        # Gauge invariance: let psi -> psi e^{i alpha(x)}, gauge field transforms, etc.
        gauge_text = Tex(
            r"Gauge Invariance: $\psi \;\to\; e^{i\alpha(x)}\psi$, "
            r"Gauge Fields $\;\to\;$ shift accordingly",
            font_size=36
        ).next_to(qed_lagrangian, DOWN)

        self.play(FadeIn(gauge_text, shift=RIGHT), run_time=3)
        self.wait(2)

        # Make the psi term flash with a phase factor
        gauge_phase = MathTex(
            r"e^{i \alpha(x)}",
            color=YELLOW
        ).scale(1.2)
        gauge_phase.move_to(qed_lagrangian.get_part_by_tex(r"\psi").get_right() + RIGHT*0.3)

        self.play(
            FadeIn(gauge_phase, scale=0.5),
            Flash(qed_lagrangian.get_part_by_tex(r"\psi"), color=YELLOW, run_time=2),
        )
        self.wait(2)
        self.play(FadeOut(gauge_phase, shift=LEFT))

        ############################################################################
        # 8. FEYNMAN DIAGRAM: e- e- gamma
        ############################################################################
        # Move camera left so we can show a Feynman diagram on a black background
        self.play(self.camera.animate.move_to([5, -2, 5]), run_time=2)

        # Dark rectangle behind
        diag_bg = Rectangle(
            width=8,
            height=4,
            fill_color=BLACK,
            fill_opacity=0.8,
            stroke_opacity=0
        ).to_edge(LEFT).shift(UP*0.5)
        self.play(FadeIn(diag_bg))

        # Electron lines + photon
        left_e_line = Line(LEFT*3, ORIGIN, color=BLUE)
        right_e_line = Line(ORIGIN, RIGHT*3, color=BLUE)
        photon_arc = ArcBetweenPoints(
            LEFT*3, RIGHT*3, angle=PI/2, color=YELLOW
        )

        feynman_diagram = VGroup(left_e_line, right_e_line, photon_arc).scale(0.8)
        feynman_diagram.move_to(diag_bg.get_center())

        e_label_left = MathTex(r"e^{-}", color=BLUE).next_to(left_e_line, LEFT)
        e_label_right = MathTex(r"e^{-}", color=BLUE).next_to(right_e_line, RIGHT)
        gamma_label = MathTex(r"\gamma", color=YELLOW).next_to(photon_arc, UP)

        self.play(
            Create(left_e_line),
            Create(right_e_line),
            Create(photon_arc),
            run_time=3
        )
        self.play(
            FadeIn(e_label_left),
            FadeIn(e_label_right),
            FadeIn(gamma_label),
            run_time=2
        )
        self.wait(1)

        # Show the coupling constant alpha ~ 1/137
        alpha_num = MathTex(r"\alpha \approx \frac{1}{137}", font_size=40)
        alpha_num.next_to(feynman_diagram, DOWN)
        self.play(Write(alpha_num))
        self.wait(1)

        # Transition alpha numeric -> symbolic
        alpha_symbolic = MathTex(
            r"\alpha = \frac{e^2}{4\pi \epsilon_0 \hbar c}",
            font_size=40
        ).move_to(alpha_num)
        self.play(
            Transform(alpha_num, alpha_symbolic),
            run_time=3
        )
        self.wait(2)

        ############################################################################
        # 9. 2D GRAPH OF RUNNING COUPLING
        ############################################################################
        # Shift camera or fade out diagram to reveal a 2D graph
        self.play(
            FadeOut(diag_bg),
            FadeOut(feynman_diagram),
            FadeOut(e_label_left),
            FadeOut(e_label_right),
            FadeOut(gamma_label),
            FadeOut(alpha_num),
            run_time=2
        )

        # Bring the camera back to a more central vantage
        self.play(self.camera.animate.move_to([0, 0, 10]), run_time=2)

        # Axes for coupling vs energy
        alpha_axes = Axes(
            x_range=[0, 20, 5],
            y_range=[0.005, 0.03, 0.005],
            x_length=6,
            y_length=3,
            axis_config={"color": GREY_A},
            tips=True
        )
        alpha_axes_labels = alpha_axes.get_axis_labels(
            Tex("Energy Scale"),
            Tex("Coupling Strength")
        )
        alpha_curve = alpha_axes.plot(
            lambda x: 0.007297 + 0.0006*x,  # simple slope to show growth
            x_range=[0, 20],
            color=RED
        )

        alpha_plot_group = VGroup(alpha_axes, alpha_axes_labels, alpha_curve)
        alpha_plot_group.to_edge(DOWN)

        # Some "data points" to illustrate measurement
        data_points = VGroup()
        energies = [2, 5, 10, 15]
        for e in energies:
            y_val = 0.007297 + 0.0006 * e
            dot = Dot(alpha_axes.coords_to_point(e, y_val), color=ORANGE)
            data_points.add(dot)

        plot_caption = Tex(
            "Running of \\( \\alpha \\) due to vacuum polarization",
            font_size=34
        ).next_to(alpha_plot_group, UP)

        self.play(
            Create(alpha_axes),
            Write(alpha_axes_labels),
            Create(alpha_curve),
            run_time=3
        )
        self.play(FadeIn(plot_caption, shift=UP), *[FadeIn(dot) for dot in data_points])
        self.wait(2)

        ############################################################################
        # 10. FINAL ZOOM OUT & COLLAGE (ALL ELEMENTS)
        ############################################################################
        # We'll bring back the Minkowski wireframe, fields, QED Lagr., etc.
        # Then fade into a cosmic star field. End with "Finis".
        self.stop_ambient_camera_rotation()

        final_text = Text(
            "QED: Unifying Light and Matter Through Gauge Theory",
            font_size=48
        ).set_color(YELLOW)
        final_text.set_glow_factor(0.3)
        final_text.to_edge(UP)

        self.play(
            # Everything else fades or transforms into a collage
            FadeIn(final_text, shift=UP),
            run_time=4
        )
        self.wait(2)

        # Pan camera out so we can see the entire "scene" in a wide shot
        self.play(
            self.camera.animate.move_to([0, 0, 20]),
            self.camera.animate.set_euler_angles(
                phi=70 * DEGREES, theta=-30 * DEGREES
            ),
            run_time=3
        )

        # Fade out all objects except star_field
        all_but_stars = VGroup(*[m for m in self.mobjects if m is not star_field])
        self.play(
            FadeOut(all_but_stars, run_time=4),
        )
        self.wait(1)

        # Concluding subtitle "Finis" over star field
        finis_text = Text("Finis", font_size=40, slant=ITALIC).to_edge(DOWN).set_color(GRAY_B)
        self.play(FadeIn(finis_text, shift=UP), run_time=3)
        self.wait(3)

        # Finally fade to star field only
        self.play(
            FadeOut(finis_text, run_time=3),
            star_field.animate.set_opacity(0.2)
        )
        self.wait(2)

        # End
        self.play(FadeOut(star_field, run_time=3))
        self.wait()
