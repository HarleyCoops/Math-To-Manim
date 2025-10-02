from manim import *
from manim.mobject.three_d.three_dimensions import Surface
import numpy as np

class StarField(VGroup):
    def __init__(self, is_3D=False, num_stars=200, **kwargs):
        super().__init__(**kwargs)
        for _ in range(num_stars):
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)
            z = np.random.uniform(-3, 3) if is_3D else 0
            star = Dot(point=[x, y, z], color=WHITE, radius=0.02)
            self.add(star)

class QEDJourney(ThreeDScene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=70*DEGREES, theta=-30*DEGREES)

        # 1. Cosmic Introduction
        star_field = StarField(is_3D=True)
        title = Text("Quantum Field Theory:\nA Journey into QED", 
                    font_size=48, gradient=(BLUE, YELLOW))
        subtitle = Text("From Maxwell to Feynman", font_size=36)
        title_group = VGroup(title, subtitle).arrange(DOWN)

        self.play(FadeIn(star_field), run_time=2)
        self.play(Write(title), FadeIn(subtitle))
        self.wait(2)
        self.play(title_group.animate.scale(0.5).to_corner(UL), run_time=2)

        # 2. Spacetime Foundation
        axes = ThreeDAxes(x_range=[-5,5], y_range=[-5,5], z_range=[-4,4])
        spacetime_grid = Surface(
            lambda u,v: axes.c2p(u,v,0),
            u_range=[-5,5], v_range=[-5,5],
            resolution=(25,25),
            fill_opacity=0.1,
            stroke_width=1,
            stroke_color=BLUE_E
        )
        light_cone = Surface(
            lambda u,v: axes.c2p(v*np.cos(u), v*np.sin(u), v),
            u_range=[0,2*PI], v_range=[0,3],
            resolution=(24,12),
            fill_opacity=0.15,
            color=YELLOW
        )

        self.play(
            Create(axes), 
            Create(spacetime_grid),
            run_time=3
        )
        self.begin_ambient_camera_rotation(rate=0.1)
        self.play(Create(light_cone), run_time=2)
        self.wait(2)

        # 3. Electromagnetic Waves Visualization
        wave_group = VGroup()
        for direction in [LEFT, RIGHT]:
            em_wave = ParametricFunction(
                lambda t: axes.c2p(
                    direction[0]*t,
                    0,
                    np.sin(3*t)*0.5
                ),
                t_range=[0,5],
                color=RED
            )
            wave_group.add(em_wave)
        
        b_field = ArrowVectorField(
            lambda p: [0, np.sin(3*p[0]),0],
            x_range=[-5,5], y_range=[-5,5], z_range=[-4,4],
            colors=[BLUE]
        )

        maxwell_eq = MathTex(
            r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}",
            r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}"
        ).arrange(DOWN).to_edge(DR)

        self.play(
            Create(wave_group),
            Create(b_field),
            Write(maxwell_eq),
            run_time=4
        )
        self.wait(3)

        # 4. QED Lagrangian Revelation
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            substrings_to_isolate=[r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu\nu}"]
        ).scale(0.8).to_corner(UR)
        
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu\nu}", GOLD)

        self.play(
            Transform(maxwell_eq, qed_lagrangian),
            run_time=3,
            path_arc=PI/2
        )
        self.wait(2)

        # 5. Feynman Diagram Unfoldment
        feynman_diagram = VGroup(
            Line(LEFT*3, ORIGIN, color=BLUE),
            Line(ORIGIN, RIGHT*3, color=BLUE),
            ArcBetweenPoints(LEFT*3, RIGHT*3, angle=PI/2, color=YELLOW)
        ).shift(UP*2)

        vertex_dot = Dot(color=WHITE).scale(1.5)
        labels = VGroup(
            MathTex(r"e^-", color=BLUE).next_to(feynman_diagram[0], LEFT),
            MathTex(r"e^-", color=BLUE).next_to(feynman_diagram[1], RIGHT),
            MathTex(r"\gamma", color=YELLOW).next_to(feynman_diagram[2], UP)
        )

        self.play(
            Create(feynman_diagram),
            GrowFromCenter(vertex_dot),
            FadeIn(labels),
            run_time=3
        )
        self.wait(2)

        # 6. Coupling Constant Evolution
        alpha_plot = Axes(
            x_range=[0, 20], y_range=[0.005, 0.03],
            x_length=6, y_length=4
        ).to_edge(DL)
        curve = alpha_plot.plot(
            lambda x: 0.007297 + 0.0001*x,
            color=RED
        )
        plot_labels = VGroup(
            alpha_plot.get_x_axis_label(r"\text{Energy Scale (GeV)}"),
            alpha_plot.get_y_axis_label(r"\alpha")
        )

        self.play(
            Create(alpha_plot),
            Create(curve),
            Write(plot_labels),
            run_time=3
        )
        self.wait(2)

        # 7. Grand Finale
        self.stop_ambient_camera_rotation()
        final_text = Text("QED: Light & Matter United", font_size=48)
        self.play(
            FadeIn(final_text, shift=UP),
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=5
        )
        self.wait(3)
