from manim import *
import numpy as np

class StarField(VGroup):
    def __init__(self, num_stars=400, seed=42, **kwargs):
        super().__init__(**kwargs)
        # Set random seed for deterministic star positions
        np.random.seed(seed)
        for _ in range(num_stars):
            x = np.random.uniform(-10, 10)
            y = np.random.uniform(-6, 6)
            z = np.random.uniform(-5, 5)
            brightness = np.random.uniform(0.2, 1.0)
            star = Dot3D(point=[x, y, z], color=WHITE).set_opacity(brightness)
            self.add(star)
        # Reset random seed to not affect other random operations
        np.random.seed(None)

class QuantumFieldTheoryScene(ThreeDScene):
    def construct(self):
        # Initial camera setup
        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=60*DEGREES, theta=30*DEGREES)
        
        # Step 1: Create 3D star field instead of image
        star_field = StarField()
        self.play(FadeIn(star_field, run_time=3))
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(1)
        
        # Step 2: Introduce a 3D axis frame
        axes = ThreeDAxes(
            x_range=[-5, 5],
            y_range=[-5, 5],
            z_range=[-5, 5],
            x_length=8,
            y_length=8,
            z_length=8,
            axis_config={"include_tip": True}
        )
        self.play(Create(axes), run_time=3)
        self.move_camera(phi=45*DEGREES, theta=60*DEGREES, run_time=2)
        self.wait(1)
        
        # Step 3: Add a large title
        title = Tex(r"\textbf{Quantum Field Theory: A Journey into the Electromagnetic Interaction}", 
                    color=YELLOW, font_size=60)
        title.set_stroke(WHITE, width=2)  # Glow effect
        self.add_fixed_in_frame_mobjects(title)  # Keep title facing camera
        self.play(Write(title, run_time=3))
        self.wait(6)  # Keep title visible for 6 seconds
        self.play(FadeOut(title), run_time=1)  # Fade out title
        
        # Move the title to the upper-left corner
        title.scale(0.5).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.wait(1)
        
        # Step 4: Introduce a rotating wireframe of 4D Minkowski spacetime
        light_cone = Surface(
            lambda u, v: np.array([
                u * np.cos(v),
                u * np.sin(v),
                u
            ]),
            u_range=[0, 2],
            v_range=[0, TAU],
            checkerboard_colors=[BLUE_D, BLUE_E],
            resolution=(15, 32)
        )
        self.play(Create(light_cone), run_time=3)
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES, zoom=0.8, run_time=2)
        self.wait(2)
        
        # Step 5: Display the relativistic metric equation
        metric_eq = MathTex(r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2", color=WHITE, font_size=40)
        metric_eq.set_color_by_tex("-c^2", RED)
        metric_eq.set_color_by_tex("dx^2", GREEN)
        metric_eq.set_color_by_tex("dy^2", BLUE)
        metric_eq.set_color_by_tex("dz^2", ORANGE)
        self.add_fixed_in_frame_mobjects(metric_eq)  # Keep equation facing camera
        metric_eq.to_edge(DOWN)
        # Move camera to focus on equation
        self.move_camera(phi=45*DEGREES, zoom=1.2, run_time=2)
        self.play(Write(metric_eq, run_time=3))
        self.wait(6)  # Keep equation visible for 6 seconds
        self.play(FadeOut(metric_eq), run_time=1)  # Fade out equation
        self.wait(2)
        
        # Step 6: Zoom into the origin and introduce quantum fields
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES, zoom=1.5, run_time=3)
        self.wait(1)
        
        # Electric and magnetic fields
        e_field = ParametricFunction(
            lambda t: np.array([t, np.sin(t), 0]),
            t_range=[-PI, PI],
            color=RED,
            stroke_width=4  # Make it more visible in 3D
        )
        b_field = ParametricFunction(
            lambda t: np.array([0, np.cos(t), t]),
            t_range=[-PI, PI],
            color=BLUE,
            stroke_width=4  # Make it more visible in 3D
        )
        e_label = MathTex(r"\vec{E}", color=RED)
        b_label = MathTex(r"\vec{B}", color=BLUE)
        self.add_fixed_in_frame_mobjects(e_label, b_label)
        # Position labels better in 3D space
        e_label.move_to(e_field.point_from_proportion(0.7) + RIGHT * 0.5)
        b_label.move_to(b_field.point_from_proportion(0.7) + UP * 0.5)
        # Move camera to better view the fields
        self.move_camera(phi=70*DEGREES, theta=30*DEGREES, zoom=1.2, run_time=2)
        self.play(Create(e_field), Create(b_field), Write(e_label), Write(b_label), run_time=3)
        self.wait(6)  # Keep fields visible for 6 seconds
        self.play(FadeOut(e_field), FadeOut(b_field), FadeOut(e_label), FadeOut(b_label), run_time=1)  # Fade out fields
        self.wait(1)
        
        # Wave propagation along the z-axis with better 3D visualization
        wave_arrow = Arrow3D(
            start=ORIGIN, 
            end=2 * OUT,
            color=YELLOW,
            thickness=0.02  # Make arrow thicker for better visibility
        )
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES, zoom=1.3, run_time=2)
        self.play(Create(wave_arrow), run_time=2)
        self.wait(6)  # Keep arrow visible for 6 seconds
        self.play(FadeOut(wave_arrow), run_time=1)  # Fade out arrow
        self.wait(1)
        
        # Step 7: Transition to Maxwell's equations
        maxwell_classical = MathTex(
            r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}",
            r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}"
        ).arrange(DOWN, buff=0.5)
        maxwell_relativistic = MathTex(r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu")
        # Keep equations facing camera and position them
        self.add_fixed_in_frame_mobjects(maxwell_classical)
        maxwell_classical.to_edge(UP)
        self.move_camera(phi=45*DEGREES, theta=30*DEGREES, zoom=1.0, run_time=2)
        self.play(Write(maxwell_classical, run_time=3))
        self.wait(6)  # Keep classical equations visible for 6 seconds
        self.play(FadeOut(maxwell_classical), run_time=1)  # Fade out classical equations
        self.wait(2)
        
        # Transform to relativistic form
        self.add_fixed_in_frame_mobjects(maxwell_relativistic)
        maxwell_relativistic.to_edge(UP)
        self.play(ReplacementTransform(maxwell_classical.copy(), maxwell_relativistic), run_time=3)
        self.wait(6)  # Keep relativistic equation visible for 6 seconds
        self.play(FadeOut(maxwell_relativistic), run_time=1)  # Fade out relativistic equation
        self.wait(2)
        
        # Step 8: Present the QED Lagrangian with improved visibility
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}"
        ).scale(0.8)
        self.add_fixed_in_frame_mobjects(qed_lagrangian)
        qed_lagrangian.to_edge(DOWN)
        # Color the terms
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu\nu}", GOLD)
        # Move camera to focus on the Lagrangian
        self.move_camera(phi=50*DEGREES, theta=30*DEGREES, zoom=1.4, run_time=2)
        self.play(Write(qed_lagrangian, run_time=4))
        self.wait(6)  # Keep Lagrangian visible for 6 seconds
        self.play(FadeOut(qed_lagrangian), run_time=1)  # Fade out Lagrangian
        self.wait(2)
        
        # Step 9: Illustrate gauge invariance
        gauge_text = Tex(r"Gauge Invariance: $\psi \to e^{i \alpha(x)} \psi$", color=WHITE).scale(0.7)
        self.add_fixed_in_frame_mobjects(gauge_text)
        gauge_text.next_to(qed_lagrangian, UP)
        self.play(Write(gauge_text), run_time=3)
        self.wait(6)  # Keep gauge text visible for 6 seconds
        self.play(FadeOut(gauge_text), run_time=1)  # Fade out gauge text
        self.wait(2)
        
        # Step 10: Feynman diagram in 3D
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES, zoom=1.0, run_time=2)
        feynman_diagram = VGroup(
            Line3D(start=LEFT * 3, end=ORIGIN, color=BLUE),
            Line3D(start=ORIGIN, end=RIGHT * 3, color=BLUE),
            ParametricFunction(
                lambda t: np.array([1.5 * np.cos(t), 1.5 * np.sin(t), 0.5 * np.sin(2*t)]),
                t_range=[0, PI],
                color=YELLOW
            )
        )
        # Add labels to the Feynman diagram
        electron_labels = VGroup(
            MathTex(r"e^-", color=BLUE),
            MathTex(r"e^-", color=BLUE),
            MathTex(r"\gamma", color=YELLOW)
        )
        self.add_fixed_in_frame_mobjects(electron_labels)
        electron_labels[0].next_to(feynman_diagram[0], LEFT)
        electron_labels[1].next_to(feynman_diagram[1], RIGHT)
        electron_labels[2].next_to(feynman_diagram[2], UP)
        # Create the diagram with a nice camera angle
        self.move_camera(phi=70*DEGREES, theta=30*DEGREES, zoom=1.2, run_time=2)
        self.play(
            Create(feynman_diagram),
            Write(electron_labels),
            run_time=3
        )
        self.wait(6)  # Keep Feynman diagram visible for 6 seconds
        self.play(FadeOut(feynman_diagram), FadeOut(electron_labels), run_time=1)  # Fade out Feynman diagram
        self.wait(2)
        
        # Step 11: Coupling constant visualization
        coupling_axes = ThreeDAxes(
            x_range=[0, 10],
            y_range=[0, 1],
            z_range=[0, 1],
            x_length=6,
            y_length=4,
            z_length=4
        )
        # Create the coupling constant curve
        coupling_curve = ParametricFunction(
            lambda t: np.array([t, 0.1 + 0.05 * np.log(t + 1), 0]),
            t_range=[0, 10],
            color=GREEN
        )
        # Add labels
        coupling_label = MathTex(r"\alpha \approx \frac{1}{137}", color=WHITE)
        self.add_fixed_in_frame_mobjects(coupling_label)
        coupling_label.to_corner(UR)
        # Show the coupling visualization
        self.move_camera(phi=60*DEGREES, theta=45*DEGREES, zoom=0.9, run_time=2)
        self.play(
            Create(coupling_axes),
            Create(coupling_curve),
            Write(coupling_label),
            run_time=3
        )
        self.wait(6)  # Keep coupling constant visible for 6 seconds
        self.play(FadeOut(coupling_axes), FadeOut(coupling_curve), FadeOut(coupling_label), run_time=1)  # Fade out coupling constant
        self.wait(2)
        
        # Final sequence
        self.move_camera(phi=60*DEGREES, theta=30*DEGREES, zoom=0.8, run_time=3)
        final_text = Text("QED: Unifying Light & Matter", color=YELLOW, font_size=48)
        self.add_fixed_in_frame_mobjects(final_text)
        final_text.move_to(ORIGIN)
        # Fade out everything except stars and show final text
        self.play(
            [FadeOut(mob) for mob in self.mobjects if not isinstance(mob, StarField)],
            FadeIn(final_text),
            run_time=3
        )
        self.wait(6)  # Keep final text visible for 6 seconds
        # End with fading star field
        finis = Text("Finis", color=WHITE, font_size=60)
        self.add_fixed_in_frame_mobjects(finis)
        self.play(
            FadeOut(final_text),
            ReplacementTransform(final_text.copy(), finis),  # Use ReplacementTransform here
            run_time=3
        )
        self.wait(6)  # Keep "Finis" visible for 6 seconds
        self.play(FadeOut(finis), run_time=3)  # Fade out "Finis"
        self.wait(3)