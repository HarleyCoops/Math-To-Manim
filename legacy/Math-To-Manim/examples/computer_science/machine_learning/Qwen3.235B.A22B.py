from manim import *
import numpy as np
from manim.mobject.opengl.opengl_surface import ParametricSurface

class QEDJourney(ThreeDScene):
    def construct(self):
        # Step 1: Cosmic Background
        stars = VGroup(*[
            Dot(point=np.array([np.random.uniform(-8, 8), np.random.uniform(-8, 8), np.random.uniform(-2, 2)]), 
                radius=0.03, color=WHITE).set_opacity(np.random.uniform(0.5, 1))
            for _ in range(150)
        ])
        self.add(stars)
        self.wait(0.5)

        # Title
        title = Tex(r"Quantum Field Theory: A Journey into the Electromagnetic Interaction")
        title.scale(0.9).set_color_by_gradient(BLUE, PURPLE, YELLOW)
        title.set_stroke(width=1.2)
        self.play(Write(title), run_time=2)
        self.wait(1)
        self.play(title.animate.to_corner(UL).scale(0.6))

        # Step 2: Spacetime Grid & Light Cone
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-4, 4, 1],
            axis_config={"color": WHITE}
        )

        # Light cone (future)
        def light_cone(u, v):
            return np.array([
                u * np.cos(v),
                u * np.sin(v),
                u
            ])

        light_cone_future = ParametricSurface(
            light_cone, u_range=[0, 2], v_range=[0, TAU], resolution=(10, 32),
            fill_opacity=0.2, color=YELLOW
        )
        light_cone_past = ParametricSurface(
            lambda u, v: np.array([-u * np.cos(v), -u * np.sin(v), -u]),
            u_range=[0, 2], v_range=[0, TAU], resolution=(10, 32),
            fill_opacity=0.1, color=YELLOW
        )

        spacetime = VGroup(axes, light_cone_future, light_cone_past)
        self.play(Create(spacetime), run_time=3)
        self.begin_ambient_camera_rotation(rate=0.25)

        # Metric Tensor Equation
        metric = MathTex(
            r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2",
            substrings_to_isolate=[
                r"-c^2 dt^2", r"dx^2", r"dy^2", r"dz^2"
            ]
        ).set_color_by_tex("-c^2 dt^2", RED).set_color_by_tex("dx^2", BLUE_C).set_color_by_tex("dy^2", GREEN_C).set_color_by_tex("dz^2", GOLD_E)
        metric.to_corner(UR).scale(0.8)
        self.play(Write(metric), run_time=2)

        # Step 3: Electric and Magnetic Fields (Plane Waves)
        self.play(self.camera.frame.animate.set_width(6).shift(IN * 2))

        # E-field wave (Red, X-direction)
        def field_x(t): return np.array([np.sin(4 * t), 0, t])
        wave_E = ParametricFunction(field_x, t_range=[-TAU, TAU], color=RED)
        wave_E.set_stroke(width=2)

        # B-field wave (Blue, Y-direction)
        def field_y(t): return np.array([0, np.sin(4 * t + PI / 2), t])
        wave_B = ParametricFunction(field_y, t_range=[-TAU, TAU], color=BLUE)
        wave_B.set_stroke(width=2)

        self.play(Create(wave_E), Create(wave_B), run_time=2)

        # Field labels
        E_label = Tex(r"\vec{E}").next_to(wave_E.get_end(), UP, buff=0.2).set_color(RED)
        B_label = Tex(r"\vec{B}").next_to(wave_B.get_end(), OUT, buff=0.2).set_color(BLUE)
        self.play(Write(E_label), Write(B_label))

        # Wave propagation vector
        wave_dir = Arrow(start=ORIGIN, end=OUT * 2, color=WHITE, buff=0.1)
        self.play(GrowArrow(wave_dir))

        # Step 4: Maxwell's Equations
        maxwell_classical = MathTex(
            r"\nabla \cdot \vec{E} &= \frac{\rho}{\varepsilon_0}", r"\\",
            r"\nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t}"
        ).arrange(DOWN).to_edge(LEFT).shift(UP)
        maxwell_relativistic = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu"
        ).to_edge(RIGHT).shift(UP)

        self.play(
            TransformMatchingTex(maxwell_classical, maxwell_relativistic),
            FadeOut(wave_dir, E_label, B_label, wave_E, wave_B)
        )

        # Step 5: QED Lagrangian
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            substrings_to_isolate=[
                r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu\nu}"
            ]
        ).set_color_by_tex("psi", ORANGE).set_color_by_tex("D_", GREEN).set_color_by_tex("gamma", TEAL_A).set_color_by_tex("F_", GOLD)
        lag_plane = RoundedRectangle(height=1.5, width=8, color=GRAY, fill_opacity=0.2)
        lag_plane.next_to(maxwell_relativistic, DOWN)
        lagrangian.move_to(lag_plane.get_center())

        self.play(FadeIn(lag_plane), Write(lagrangian))

        # Step 6: Gauge Transformation
        gauge_group = VGroup(
            MathTex(r"\psi \rightarrow e^{i \alpha(x)} \psi"),
            MathTex(r"A_\mu \rightarrow A_\mu - \partial_\mu \alpha(x)")
        ).arrange(DOWN).next_to(lag_plane, DOWN, buff=0.5)

        self.play(Write(gauge_group))

        # Step 7: Feynman Diagram
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )
        self.remove(*self.mobjects)

        diag_base = VGroup(
            Line(LEFT * 2.5 + DOWN * 1, LEFT * 0.5 + DOWN * 1, color=BLUE),
            Line(RIGHT * 2.5 + DOWN * 1, RIGHT * 0.5 + DOWN * 1, color=BLUE),
            WavedLine(LEFT * 0.5 + DOWN * 1, RIGHT * 0.5 + DOWN * 1, color=YELLOW, amplitude=0.3, n_waves=3)
        )
        diag_labels = VGroup(
            Tex(r"$e^-$", color=BLUE).next_to(diag_base[0].get_start(), LEFT),
            Tex(r"$e^-$", color=BLUE).next_to(diag_base[1].get_start(), RIGHT),
            Tex(r"$\gamma$", color=YELLOW).next_to(diag_base[2].get_top(), UP)
        )

        self.play(Create(diag_base), Write(diag_labels))

        # Step 8: Coupling Constant
        alpha_num = MathTex(r"\alpha \approx \frac{1}{137}").to_edge(UP)
        alpha_sym = MathTex(r"\alpha = \frac{e^2}{4 \pi \varepsilon_0 \hbar c}").to_edge(UP)
        self.play(Write(alpha_num))
        self.wait()
        self.play(TransformMatchingTex(alpha_num, alpha_sym))

        # Step 9: RG Flow Graph
        graph_axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 0.1, 0.02],
            tips=True,
            axis_config={"include_numbers": True},
            x_axis_config={"label_direction": DR},
            y_axis_config={"label_direction": UL}
        )
        label_energy = Tex("Energy Scale").next_to(graph_axes.x_axis.get_end(), RIGHT)
        label_coupling = Tex("Coupling Strength").rotate(PI / 2).next_to(graph_axes.y_axis.get_end(), UP)
        curve = graph_axes.plot(lambda x: 0.005 + 0.0004 * x**2, color=ORANGE)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )
        self.play(
            Create(graph_axes),
            Write(label_energy),
            Write(label_coupling),
            Create(curve),
            run_time=3
        )

        # Step 10: Final Montage
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )
        self.play(
            FadeIn(spacetime, metric, lag_plane, lagrangian),
            run_time=2
        )

        final_title = Tex("QED: Unifying Light and Matter Through Gauge Theory")
        final_title.set_color_by_gradient(PURPLE, GOLD, BLUE).scale(1.1)
        halo = Annulus(inner_radius=final_title.width / 2, outer_radius=final_title.width / 2 + 0.3, color=GOLD, fill_opacity=0.2)
        halo.move_to(final_title.get_center())

        self.play(
            FadeIn(halo),
            Write(final_title),
            self.camera.frame.animate.set_width(20).shift(OUT * 3),
            run_time=3
        )

        self.wait(2)

        # Finale
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=2
        )
        self.add(stars)
        finis = Tex("Finis").scale(2).set_color(WHITE)
        self.play(Write(finis), run_time=2)
        self.wait(2)