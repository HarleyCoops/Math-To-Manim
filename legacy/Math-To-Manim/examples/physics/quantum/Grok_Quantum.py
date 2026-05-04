from manim import *
import numpy as np

##############################################################################
# StarField utility
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
            star = Dot(point=[x, y, z], color=WHITE, radius=0.015 * np.random.uniform(0.5, 1.5))
            self.add(star)

##############################################################################
# CosmicOrigins main scene
##############################################################################
class CosmicOrigins(ThreeDScene):
    def construct(self):
        # Configure the camera with a 30-degree angle and zoomed-out view
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=30 * DEGREES, theta=0 * DEGREES, zoom=1.8)

        ############################################################################
        # 1. COSMIC DAWN: STARFIELD AND BIG BANG IGNITION
        ############################################################################
        star_field = StarField(is_3D=True, num_stars=500).set_opacity(0)
        singularity = Dot(radius=0.1, color=WHITE).set_glow_factor(2.5)
        main_title = Text(
            "From Void to Cosmos:\nQuantum Fields Shape the Universe",
            font_size=60,
            gradient=(PURPLE, GOLD),
            weight=BOLD
        ).set_glow_factor(0.6)
        subtitle = Text("A Journey Through Creation", font_size=36, color=WHITE)
        title_group = VGroup(main_title, subtitle).arrange(DOWN, buff=0.5)

        # Rotate title group 45 degrees left (counterclockwise) and position for diagonal zoom
        title_group.rotate(-45 * DEGREES, axis=OUT)  # Rotate around z-axis (OUT for 3D)
        initial_position = UR * 5  # Start far up-right for diagonal zoom
        title_group.move_to(initial_position)

        self.play(FadeIn(star_field, run_time=4), GrowFromCenter(singularity, run_time=2))
        self.play(Write(title_group, run_time=3))
        self.wait(3)  # Let the grandeur settle
        self.play(
            title_group.animate.scale(0.4).rotate(0 * DEGREES, axis=OUT).to_corner(UL, buff=0.5),  # Unrotate for final position
            singularity.animate.scale(15).set_opacity(0),  # Explosive expansion
            star_field.animate.set_opacity(1),
            run_time=3
        )

        ############################################################################
        # 2. SPACETIME EMERGES: MINKOWSKI WIREFRAME AND LIGHT CONE
        ############################################################################
        axes = ThreeDAxes(
            x_range=[-4, 4], y_range=[-4, 4], z_range=[-4, 4],
            x_length=8, y_length=8, z_length=8,
            axis_config={"color": GRAY_A}
        ).scale(0.8)
        spacetime_grid = Surface(
            lambda u, v: axes.c2p(u, v, 0),
            u_range=[-4, 4], v_range=[-4, 4],
            resolution=(30, 30),
            fill_opacity=0.1,
            stroke_width=0.5,
            stroke_color=BLUE_E
        )
        light_cone = Surface(
            lambda u, v: axes.c2p(v * np.cos(u), v * np.sin(u), v),
            u_range=[0, 2 * PI], v_range=[0, 2.5],
            resolution=(24, 12),
            fill_opacity=0.2,
            color=YELLOW
        )
        metric = MathTex(
            r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2",
            font_size=36
        ).to_edge(RIGHT, buff=0.5).shift(UP)
        metric.set_color_by_tex("-c^2 dt^2", RED).set_color_by_tex("dx^2", BLUE)

        self.play(Create(axes), Create(spacetime_grid), run_time=3)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.play(Create(light_cone), Write(metric), run_time=2)
        self.wait(5)  # Hold metric for understanding

        ############################################################################
        # 3. ELECTROMAGNETIC BIRTH: E AND B WAVES
        ############################################################################
        self.stop_ambient_camera_rotation()
        self.play(
            axes.animate.scale(0.6).shift(DOWN * 1.5),
            spacetime_grid.animate.scale(0.6).shift(DOWN * 1.5),
            light_cone.animate.scale(0.6).shift(DOWN * 1.5),
            FadeOut(metric),
            run_time=2
        )
        wave_length = 4
        e_wave = ParametricFunction(
            lambda t: axes.c2p(np.sin(2 * t) * 0.6, 0, t),
            t_range=[-wave_length, wave_length],
            color=RED
        ).scale(0.8)
        b_wave = ParametricFunction(
            lambda t: axes.c2p(0, np.sin(2 * t + PI/2) * 0.6, t),
            t_range=[-wave_length, wave_length],
            color=BLUE
        ).scale(0.8)
        label_E = MathTex(r"\vec{E}", color=RED, font_size=30).next_to(e_wave.get_end(), UP + RIGHT, buff=0.2)
        label_B = MathTex(r"\vec{B}", color=BLUE, font_size=30).next_to(b_wave.get_end(), DOWN + RIGHT, buff=0.2)
        propagation_arrow = Arrow3D(
            start=axes.c2p(0, 0, -wave_length * 0.5),
            end=axes.c2p(0, 0, wave_length * 0.5),
            color=YELLOW,
            thickness=0.02
        )
        prop_label = Tex("Propagation (z-axis)", color=YELLOW, font_size=24).next_to(propagation_arrow.get_end(), UP + RIGHT, buff=0.1)
        maxwell = MathTex(
            r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}",
            font_size=36
        ).to_edge(DR, buff=0.5)
        maxwell_rel = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu",
            font_size=36
        ).to_edge(DR, buff=0.5)

        self.play(
            LaggedStart(Create(e_wave), Create(b_wave), lag_ratio=0.5, run_time=3)
        )
        self.play(
            FadeIn(label_E, shift=RIGHT), FadeIn(label_B, shift=RIGHT),
            Create(propagation_arrow), Write(prop_label), Write(maxwell),
            run_time=3
        )
        self.wait(4)  # Classical Maxwell
        self.play(Transform(maxwell, maxwell_rel), run_time=2, path_arc=PI/4)
        self.wait(5)  # Relativistic form

        ############################################################################
        # 4. QED REVELATION: LAGRANGIAN AND GAUGE SYMMETRY
        ############################################################################
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi} (i \gamma^\mu D_\mu - m) \psi - \frac{1}{4} F_{\mu \nu} F^{\mu \nu}",
            substrings_to_isolate=[r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu \nu}"],
            font_size=40
        ).move_to(UP * 1.5)
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu \nu}", GOLD)
        plane = Rectangle(width=6, height=2, fill_opacity=0.15, color=GRAY).move_to(qed_lagrangian)
        gauge_transform = MathTex(r"\psi \to e^{i \alpha(x)} \psi", font_size=30).next_to(plane, DOWN, buff=0.2)
        gauge_note = Text("Gauge Symmetry Upholds Charge", font_size=20, color=WHITE).next_to(gauge_transform, DOWN, buff=0.1)

        self.play(FadeOut(maxwell), FadeIn(plane), Write(qed_lagrangian), run_time=3)
        self.wait(6)  # Let Lagrangian sink in
        self.play(Write(gauge_transform), FadeIn(gauge_note), run_time=2)
        self.wait(3)  # Gauge concept
        self.play(FadeOut(gauge_transform), FadeOut(gauge_note), run_time=1)

        ############################################################################
        # 5. FEYNMAN’S DANCE: INTERACTION VERTEX
        ############################################################################
        self.play(
            FadeOut(e_wave), FadeOut(b_wave), FadeOut(label_E), FadeOut(label_B),
            FadeOut(propagation_arrow), FadeOut(prop_label),
            axes.animate.shift(LEFT * 2.5),
            spacetime_grid.animate.shift(LEFT * 2.5),
            light_cone.animate.shift(LEFT * 2.5)
        )
        feynman = VGroup(
            Line(LEFT * 2, ORIGIN, color=BLUE),
            Line(ORIGIN, RIGHT * 2, color=BLUE),
            ParametricFunction(lambda t: np.array([t, np.sin(4 * t) * 0.5, 0]), t_range=[-1, 1], color=YELLOW)
        ).shift(DOWN)
        vertex = Dot(ORIGIN, color=WHITE, radius=0.1).set_glow_factor(1.5)
        labels = VGroup(
            MathTex(r"e^-", color=BLUE, font_size=30).next_to(feynman[0], LEFT),
            MathTex(r"e^-", color=BLUE, font_size=30).next_to(feynman[1], RIGHT),
            MathTex(r"\gamma", color=YELLOW, font_size=30).next_to(feynman[2], UP)
        )
        alpha = MathTex(r"\alpha \approx \frac{1}{137}", font_size=36).shift(UP * 2)
        alpha_sym = MathTex(r"\alpha = \frac{e^2}{4 \pi \epsilon_0 \hbar c}", font_size=36).shift(UP * 2)

        self.play(Create(feynman), GrowFromCenter(vertex), Write(labels), run_time=3)
        self.play(Write(alpha), run_time=1)
        self.wait(3)  # Numeric alpha
        self.play(Transform(alpha, alpha_sym), run_time=2)
        self.wait(5)  # Symbolic alpha

        ############################################################################
        # 6. RUNNING CONSTANT: COSMIC EVOLUTION
        ############################################################################
        alpha_plot = Axes(
            x_range=[0, 15], y_range=[0.005, 0.025], x_length=5, y_length=3,
            axis_config={"color": WHITE}
        ).to_edge(DL, buff=0.5)
        curve = alpha_plot.plot(lambda x: 0.007297 + 0.00009 * x, color=RED)
        plot_labels = VGroup(
            alpha_plot.get_x_axis_label(r"Energy Scale (GeV)", edge=DOWN, buff=0.2),
            alpha_plot.get_y_axis_label(r"\alpha", edge=LEFT, buff=0.2)
        )
        caption = Text("Quantum Vacuum Shapes Reality", font_size=20).to_edge(DOWN, buff=0.5)

        self.play(FadeOut(alpha), Create(alpha_plot), Create(curve), Write(plot_labels), run_time=3)
        self.play(Write(caption), run_time=1)
        self.wait(5)  # Reflect on evolution

        ############################################################################
        # 7. EPIC FINALE: UNITY OF CREATION
        ############################################################################
        self.play(
            axes.animate.scale(0.5).to_edge(LEFT, buff=0.5),
            spacetime_grid.animate.scale(0.5).to_edge(LEFT, buff=0.5),
            light_cone.animate.scale(0.5).to_edge(LEFT, buff=0.5),
            qed_lagrangian.animate.scale(0.7).to_edge(RIGHT, buff=0.5),
            plane.animate.scale(0.7).to_edge(RIGHT, buff=0.5),
            feynman.animate.scale(0.6).shift(RIGHT),
            FadeOut(alpha_plot), FadeOut(curve), FadeOut(plot_labels), FadeOut(caption)
        )
        final_text = Text(
            "QED: Crafting the Cosmos from Light and Matter",
            font_size=50,
            gradient=(BLUE, PURPLE),
            weight=BOLD
        ).set_stroke(width=1, color=WHITE).set_glow_factor(0.5)
        self.play(Write(final_text, run_time=3))
        self.wait(4)  # Grand statement
        self.play(
            FadeOut(final_text, shift=UP),
            *[FadeOut(mob, run_time=4) for mob in [axes, spacetime_grid, light_cone, qed_lagrangian, plane, feynman, vertex, labels]],
            star_field.animate.set_opacity(0.5),
            run_time=5
        )
        finis = Text("Finis", font_size=36, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(finis, run_time=2))
        self.wait(3)
        self.play(FadeOut(finis), star_field.animate.set_opacity(1), run_time=2)
        self.wait(3)

# Run with: manim -pql script.py CosmicOrigins