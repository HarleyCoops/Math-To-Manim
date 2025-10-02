from manim import *
import numpy as np
from manim.utils.color import interpolate_color

class QuantumFieldTheoryAnimation(ThreeDScene):
    def construct(self):
        # Set up the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        
        # Scene 1: Starfield and Title
        self.play_starfield_intro()
        
        # Scene 2: Minkowski Spacetime
        self.play_minkowski_spacetime()
        
        # Scene 3: Electromagnetic Fields
        self.play_electromagnetic_fields()
        
        # Scene 4: Maxwell's Equations
        self.play_maxwell_equations()
        
        # Scene 5: QED Lagrangian
        self.play_qed_lagrangian()
        
        # Scene 6: Gauge Invariance
        self.play_gauge_invariance()
        
        # Scene 7: Feynman Diagram
        self.play_feynman_diagram()
        
        # Scene 8: Running Coupling
        self.play_running_coupling()
        
        # Scene 9: Final Collage
        self.play_final_collage()
    
    def play_starfield_intro(self):
        """Create an animated starfield with the main title"""
        # Create starfield
        stars = VGroup()
        for _ in range(200):
            star = Dot(
                point=np.array([
                    np.random.uniform(-8, 8),
                    np.random.uniform(-5, 5),
                    np.random.uniform(-3, 3)
                ]),
                radius=np.random.uniform(0.01, 0.03),
                color=interpolate_color(YELLOW, WHITE, np.random.random())
            )
            star.set_opacity(np.random.uniform(0.3, 1))
            stars.add(star)
        
        # Fade in stars with twinkling effect
        self.play(
            LaggedStart(*[
                FadeIn(star, scale=np.random.uniform(0.5, 2))
                for star in stars
            ], lag_ratio=0.01),
            run_time=3
        )
        
        # Create main title with glow effect
        title = Text(
            "Quantum Field Theory:\nA Journey into the Electromagnetic Interaction",
            font_size=48,
            gradient=(BLUE, PURPLE, PINK)
        ).to_edge(UP)
        
        # Add glow effect
        title_glow = title.copy()
        title_glow.set_stroke(YELLOW, width=4, opacity=0.5)
        
        self.play(
            Write(title),
            Write(title_glow),
            run_time=3
        )
        
        # Shrink and move title
        mini_title = title.copy().scale(0.3).to_corner(UL)
        self.play(
            Transform(title, mini_title),
            FadeOut(title_glow),
            stars.animate.set_opacity(0.2),
            run_time=2
        )
        self.remove(title)
        self.add(mini_title)
        self.stars = stars
    
    def play_minkowski_spacetime(self):
        """Create animated Minkowski spacetime with light cone"""
        # Create 3D wireframe grid
        grid = VGroup()
        for i in range(-3, 4):
            for j in range(-3, 4):
                # Spatial grid lines
                line_x = Line3D(
                    start=np.array([i, j, -3]),
                    end=np.array([i, j, 3]),
                    color=BLUE,
                    stroke_width=1
                )
                line_y = Line3D(
                    start=np.array([i, -3, j]),
                    end=np.array([i, 3, j]),
                    color=BLUE,
                    stroke_width=1
                )
                grid.add(line_x, line_y)
        
        # Create light cone
        light_cone = VGroup()
        t_max = 3
        n_lines = 12
        for i in range(n_lines):
            angle = 2 * PI * i / n_lines
            # Future light cone
            future_line = ParametricFunction(
                lambda t: np.array([
                    t * np.cos(angle),
                    t * np.sin(angle),
                    t
                ]),
                t_range=[0, t_max],
                color=YELLOW,
                stroke_width=2
            )
            # Past light cone
            past_line = ParametricFunction(
                lambda t: np.array([
                    t * np.cos(angle),
                    t * np.sin(angle),
                    -t
                ]),
                t_range=[0, t_max],
                color=ORANGE,
                stroke_width=2
            )
            light_cone.add(future_line, past_line)
        
        # Animate grid and light cone
        self.play(
            Create(grid),
            run_time=3
        )
        self.play(
            Create(light_cone),
            Rotate(grid, angle=PI/4, axis=UP, rate_func=linear),
            run_time=4
        )
        
        # Add metric equation with color coding
        metric = MathTex(
            r"ds^2 = ",
            r"-c^2", r"dt^2",
            r" + ", r"dx^2",
            r" + ", r"dy^2",
            r" + ", r"dz^2"
        ).scale(0.8).to_corner(UR)
        
        # Color code the components
        metric[1].set_color(RED)  # Time component
        metric[4].set_color(BLUE)  # x component
        metric[6].set_color(GREEN)  # y component
        metric[8].set_color(PURPLE)  # z component
        
        self.play(Write(metric), run_time=2)
        
        # Continue rotation
        self.play(
            Rotate(grid, angle=PI/2, axis=UP, rate_func=linear),
            Rotate(light_cone, angle=PI/2, axis=UP, rate_func=linear),
            run_time=3
        )
        
        self.spacetime_grid = grid
        self.light_cone = light_cone
        self.metric = metric
    
    def play_electromagnetic_fields(self):
        """Visualize electromagnetic wave propagation"""
        # Zoom into origin using camera movement
        self.camera.set_euler_angles(phi=70 * DEGREES, theta=-45 * DEGREES, gamma=0)
        self.play(
            self.camera.set_x(0),
            self.camera.set_y(0),
            self.camera.set_z(0),
            run_time=2
        )
        
        # Create E and B field waves
        e_wave = ParametricFunction(
            lambda t: np.array([t, np.sin(2*t), 0]),
            t_range=[-4, 4],
            color=RED,
            stroke_width=3
        )
        b_wave = ParametricFunction(
            lambda t: np.array([t, 0, np.sin(2*t)]),
            t_range=[-4, 4],
            color=BLUE,
            stroke_width=3
        )
        
        # Add field labels
        e_label = MathTex(r"\vec{E}", color=RED).scale(0.7).next_to(e_wave, UP)
        b_label = MathTex(r"\vec{B}", color=BLUE).scale(0.7).next_to(b_wave, RIGHT)
        
        # Create propagation arrow
        prop_arrow = Arrow3D(
            start=ORIGIN,
            end=3*RIGHT,
            color=GREEN,
            stroke_width=4
        )
        prop_label = Text("k", color=GREEN).scale(0.6).next_to(prop_arrow, DOWN)
        
        # Animate fields
        self.play(
            Create(e_wave),
            Create(b_wave),
            Write(e_label),
            Write(b_label),
            run_time=3
        )
        
        # Add oscillating arrows
        e_arrows = VGroup()
        b_arrows = VGroup()
        for x in np.linspace(-3, 3, 7):
            e_arrow = Arrow3D(
                start=np.array([x, 0, 0]),
                end=np.array([x, 0.5*np.sin(2*x), 0]),
                color=RED,
                stroke_width=2
            )
            b_arrow = Arrow3D(
                start=np.array([x, 0, 0]),
                end=np.array([x, 0, 0.5*np.sin(2*x)]),
                color=BLUE,
                stroke_width=2
            )
            e_arrows.add(e_arrow)
            b_arrows.add(b_arrow)
        
        self.play(
            Create(e_arrows),
            Create(b_arrows),
            Create(prop_arrow),
            Write(prop_label),
            run_time=2
        )
        
        # Animate wave propagation
        def update_wave(mob, alpha):
            new_e = ParametricFunction(
                lambda t: np.array([t, np.sin(2*(t - 2*alpha)), 0]),
                t_range=[-4, 4],
                color=RED,
                stroke_width=3
            )
            new_b = ParametricFunction(
                lambda t: np.array([t, 0, np.sin(2*(t - 2*alpha))]),
                t_range=[-4, 4],
                color=BLUE,
                stroke_width=3
            )
            mob.become(VGroup(new_e, new_b))
        
        wave_group = VGroup(e_wave, b_wave)
        self.play(
            UpdateFromAlphaFunc(wave_group, update_wave),
            run_time=4,
            rate_func=linear
        )
        
        # Zoom back out
        self.play(
            self.camera.set_z(2),
            FadeOut(e_arrows),
            FadeOut(b_arrows),
            FadeOut(prop_arrow),
            FadeOut(prop_label),
            run_time=2
        )
        
        self.em_waves = VGroup(e_wave, b_wave, e_label, b_label)
    
    def play_maxwell_equations(self):
        """Transform Maxwell's equations from vector to tensor form"""
        # Classical Maxwell equations
        maxwell_classical = VGroup(
            MathTex(r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}"),
            MathTex(r"\nabla \cdot \vec{B} = 0"),
            MathTex(r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}"),
            MathTex(r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}")
        ).arrange(DOWN, buff=0.3).scale(0.6).to_edge(LEFT)
        
        # Tensor form
        maxwell_tensor = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu"
        ).scale(0.8).to_edge(RIGHT)
        
        # Animate transformation
        self.play(Write(maxwell_classical), run_time=3)
        self.wait(2)
        
        # Create morphing effect
        for eq in maxwell_classical:
            eq.generate_target()
            eq.target.move_to(maxwell_tensor)
            eq.target.set_opacity(0)
        
        self.play(
            *[MoveToTarget(eq) for eq in maxwell_classical],
            Write(maxwell_tensor),
            run_time=3
        )
        
        # Add field tensor visualization
        field_tensor = Matrix([
            ["0", "-E_x/c", "-E_y/c", "-E_z/c"],
            ["E_x/c", "0", "-B_z", "B_y"],
            ["E_y/c", "B_z", "0", "-B_x"],
            ["E_z/c", "-B_y", "B_x", "0"]
        ], h_buff=1.2).scale(0.5).next_to(maxwell_tensor, DOWN)
        
        field_label = MathTex(r"F^{\mu\nu} = ").scale(0.5).next_to(field_tensor, LEFT)
        
        self.play(
            Write(field_tensor),
            Write(field_label),
            run_time=3
        )
        
        self.maxwell_equations = VGroup(maxwell_tensor, field_tensor, field_label)
    
    def play_qed_lagrangian(self):
        """Display and explain QED Lagrangian with color coding"""
        # Clear some elements
        self.play(
            FadeOut(self.em_waves),
            FadeOut(self.maxwell_equations),
            run_time=2
        )
        
        # Create QED Lagrangian with color coding
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = ",
            r"\bar{\psi}",
            r"(i",
            r"\gamma^\mu",
            r"D_\mu",
            r" - m)",
            r"\psi",
            r" - \frac{1}{4}",
            r"F_{\mu\nu}",
            r"F^{\mu\nu}"
        ).scale(0.9)
        
        # Color code terms
        lagrangian[1].set_color(ORANGE)  # psi bar
        lagrangian[3].set_color(TEAL)     # gamma matrices
        lagrangian[4].set_color(GREEN)    # covariant derivative
        lagrangian[6].set_color(ORANGE)   # psi
        lagrangian[8].set_color(GOLD)     # F tensor
        lagrangian[9].set_color(GOLD)     # F tensor
        
        # Create transparent plane for Lagrangian
        plane = Rectangle(
            width=10, height=3,
            fill_opacity=0.1,
            fill_color=BLUE,
            stroke_color=BLUE
        )
        
        self.play(
            Create(plane),
            Write(lagrangian),
            run_time=3
        )
        
        # Add pulsing effect to show dynamic nature
        self.play(
            lagrangian.animate.set_stroke(WHITE, width=2, opacity=0.5),
            plane.animate.set_fill(opacity=0.2),
            run_time=1
        )
        
        # Add explanatory labels
        labels = VGroup(
            Text("Dirac Field", color=ORANGE, font_size=20).next_to(lagrangian[1], DOWN),
            Text("Interaction", color=GREEN, font_size=20).next_to(lagrangian[4], DOWN),
            Text("EM Field", color=GOLD, font_size=20).next_to(lagrangian[8], DOWN)
        )
        
        self.play(
            LaggedStart(*[Write(label) for label in labels], lag_ratio=0.3),
            run_time=2
        )
        
        self.qed_lagrangian = VGroup(lagrangian, plane, labels)
    
    def play_gauge_invariance(self):
        """Demonstrate gauge transformation"""
        # Create gauge transformation visualization
        gauge_text = Text("Gauge Invariance", font_size=36).to_edge(UP)
        
        # Field transformation equations
        psi_transform = MathTex(
            r"\psi \rightarrow e^{i\alpha(x)} \psi"
        ).scale(0.8).shift(2*UP)
        
        a_transform = MathTex(
            r"A_\mu \rightarrow A_\mu - \frac{1}{e}\partial_\mu \alpha(x)"
        ).scale(0.8).next_to(psi_transform, DOWN)
        
        self.play(
            Write(gauge_text),
            FadeOut(self.qed_lagrangian),
            run_time=2
        )
        
        self.play(
            Write(psi_transform),
            Write(a_transform),
            run_time=3
        )
        
        # Visualize phase rotation
        phase_circle = Circle(radius=1.5, color=YELLOW).shift(2*DOWN)
        phase_arrow = Arrow(
            start=phase_circle.get_center(),
            end=phase_circle.get_center() + 1.5*RIGHT,
            color=RED,
            stroke_width=4
        )
        phase_label = MathTex(r"e^{i\alpha}", color=RED).next_to(phase_arrow, RIGHT)
        
        self.play(
            Create(phase_circle),
            Create(phase_arrow),
            Write(phase_label),
            run_time=2
        )
        
        # Animate phase rotation
        self.play(
            Rotate(phase_arrow, angle=2*PI, about_point=phase_circle.get_center()),
            run_time=4,
            rate_func=linear
        )
        
        # Show charge conservation
        conservation = MathTex(
            r"\partial_\mu J^\mu = 0"
        ).scale(0.8).next_to(phase_circle, DOWN)
        conservation_label = Text(
            "Charge Conservation",
            font_size=24,
            color=GREEN
        ).next_to(conservation, DOWN)
        
        self.play(
            Write(conservation),
            Write(conservation_label),
            run_time=2
        )
        
        self.gauge_elements = VGroup(
            gauge_text, psi_transform, a_transform,
            phase_circle, phase_arrow, phase_label,
            conservation, conservation_label
        )
    
    def play_feynman_diagram(self):
        """Create animated Feynman diagram"""
        # Clear previous elements
        self.play(
            FadeOut(self.gauge_elements),
            FadeOut(self.spacetime_grid),
            FadeOut(self.light_cone),
            run_time=2
        )
        
        # Set 2D view
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        
        # Create Feynman diagram
        # Electron lines
        e1_start = 3*LEFT + UP
        e1_end = LEFT + 0.5*UP
        e2_start = 3*LEFT + DOWN
        e2_end = LEFT + 0.5*DOWN
        e3_start = RIGHT + 0.5*UP
        e3_end = 3*RIGHT + UP
        e4_start = RIGHT + 0.5*DOWN
        e4_end = 3*RIGHT + DOWN
        
        electron1 = Line(e1_start, e1_end, color=BLUE, stroke_width=3)
        electron2 = Line(e2_start, e2_end, color=BLUE, stroke_width=3)
        electron3 = Line(e3_start, e3_end, color=BLUE, stroke_width=3)
        electron4 = Line(e4_start, e4_end, color=BLUE, stroke_width=3)
        
        # Add arrows to electron lines
        e1_arrow = Arrow(
            start=e1_start + 0.3*(e1_end - e1_start),
            end=e1_start + 0.7*(e1_end - e1_start),
            color=BLUE,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.15
        )
        e2_arrow = Arrow(
            start=e2_start + 0.3*(e2_end - e2_start),
            end=e2_start + 0.7*(e2_end - e2_start),
            color=BLUE,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.15
        )
        e3_arrow = Arrow(
            start=e3_start + 0.3*(e3_end - e3_start),
            end=e3_start + 0.7*(e3_end - e3_start),
            color=BLUE,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.15
        )
        e4_arrow = Arrow(
            start=e4_start + 0.3*(e4_end - e4_start),
            end=e4_start + 0.7*(e4_end - e4_start),
            color=BLUE,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.15
        )
        
        # Photon line (wavy)
        photon = ParametricFunction(
            lambda t: np.array([
                t,
                0.5*UP[1] + 0.2*np.sin(8*t) - 0.5*t/2,
                0
            ]),
            t_range=[e1_end[0], e3_start[0]],
            color=YELLOW,
            stroke_width=3
        )
        
        # Labels
        e_label1 = MathTex(r"e^-", color=BLUE).scale(0.6).next_to(e1_start, LEFT)
        e_label2 = MathTex(r"e^-", color=BLUE).scale(0.6).next_to(e2_start, LEFT)
        e_label3 = MathTex(r"e^-", color=BLUE).scale(0.6).next_to(e3_end, RIGHT)
        e_label4 = MathTex(r"e^-", color=BLUE).scale(0.6).next_to(e4_end, RIGHT)
        photon_label = MathTex(r"\gamma", color=YELLOW).scale(0.8).next_to(photon, UP)
        
        # Animate diagram creation
        self.play(
            Create(electron1),
            Create(electron2),
            Create(e1_arrow),
            Create(e2_arrow),
            Write(e_label1),
            Write(e_label2),
            run_time=2
        )
        
        self.play(
            Create(photon),
            Write(photon_label),
            run_time=2
        )
        
        self.play(
            Create(electron3),
            Create(electron4),
            Create(e3_arrow),
            Create(e4_arrow),
            Write(e_label3),
            Write(e_label4),
            run_time=2
        )
        
        # Add coupling constant
        alpha_text = MathTex(
            r"\alpha \approx \frac{1}{137}",
            color=GREEN
        ).scale(0.8).shift(2*UP)
        
        alpha_full = MathTex(
            r"\alpha = \frac{e^2}{4\pi\epsilon_0\hbar c}",
            color=GREEN
        ).scale(0.8).shift(2*UP)
        
        self.play(Write(alpha_text), run_time=2)
        self.wait(1)
        self.play(Transform(alpha_text, alpha_full), run_time=2)
        
        # Add vertex factor
        vertex_text = Text(
            "Vertex Factor: ",
            font_size=24
        ).shift(2*DOWN)
        vertex_factor = MathTex(
            r"-ie\gamma^\mu",
            color=PURPLE
        ).scale(0.8).next_to(vertex_text, RIGHT)
        
        self.play(
            Write(vertex_text),
            Write(vertex_factor),
            run_time=2
        )
        
        self.feynman_diagram = VGroup(
            electron1, electron2, electron3, electron4,
            e1_arrow, e2_arrow, e3_arrow, e4_arrow,
            photon, e_label1, e_label2, e_label3, e_label4,
            photon_label, alpha_text, vertex_text, vertex_factor
        )
    
    def play_running_coupling(self):
        """Show running of coupling constant"""
        # Clear Feynman diagram
        self.play(FadeOut(self.feynman_diagram), run_time=2)
        
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0.006, 0.008, 0.0005],
            x_length=8,
            y_length=5,
            axis_config={
                "include_numbers": True,
                "font_size": 24,
            },
            tips=True
        )
        
        # Labels
        x_label = Text("Energy Scale (log Q²/GeV²)", font_size=24).next_to(axes.x_axis, DOWN)
        y_label = Text("α(Q²)", font_size=24).rotate(90*DEGREES).next_to(axes.y_axis, LEFT)
        
        # Running coupling function
        def alpha_running(q_squared):
            alpha_0 = 1/137
            return alpha_0 / (1 - (alpha_0/(3*PI)) * np.log(q_squared + 1))
        
        # Create graph
        graph = axes.plot(
            lambda x: alpha_running(x),
            x_range=[0, 10],
            color=YELLOW,
            stroke_width=3
        )
        
        # Add data points
        data_points = VGroup()
        experimental_data = [
            (1, 0.00729),
            (3, 0.00735),
            (5, 0.00741),
            (7, 0.00747),
            (9, 0.00753)
        ]
        
        for x, y in experimental_data:
            point = Dot(
                axes.coords_to_point(x, y),
                color=RED,
                radius=0.08
            )
            data_points.add(point)
        
        # Animate graph creation
        self.play(
            Create(axes),
            Write(x_label),
            Write(y_label),
            run_time=3
        )
        
        self.play(
            Create(graph),
            run_time=3
        )
        
        self.play(
            LaggedStart(*[Create(point) for point in data_points], lag_ratio=0.2),
            run_time=2
        )
        
        # Add explanation
        explanation = VGroup(
            Text("Vacuum Polarization", font_size=28, color=BLUE),
            Text("Virtual particle loops", font_size=20, color=WHITE),
            Text("screen the charge", font_size=20, color=WHITE)
        ).arrange(DOWN, buff=0.2).to_corner(UR)
        
        # Vacuum polarization diagram
        vac_pol = VGroup()
        center = 3*LEFT + 2*UP
        
        # Central charge
        charge = Dot(center, color=RED, radius=0.1)
        
        # Virtual loops
        for i in range(6):
            angle = i * PI / 3
            loop_center = center + 0.5 * np.array([np.cos(angle), np.sin(angle), 0])
            loop = Circle(radius=0.2, color=BLUE, stroke_width=2).move_to(loop_center)
            vac_pol.add(loop)
        
        vac_pol.add(charge)
        
        self.play(
            Write(explanation),
            Create(vac_pol),
            run_time=3
        )
        
        self.running_coupling = VGroup(
            axes, x_label, y_label, graph, data_points,
            explanation, vac_pol
        )
    
    def play_final_collage(self):
        """Create final summary collage"""
        # Set 3D view again
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        
        # Clear current elements
        self.play(FadeOut(self.running_coupling), run_time=2)
        
        # Bring back key elements in miniature
        # Mini spacetime
        mini_grid = self.spacetime_grid.copy().scale(0.3).shift(3*LEFT + 2*UP)
        mini_light_cone = self.light_cone.copy().scale(0.3).shift(3*LEFT + 2*UP)
        
        # Mini EM waves
        mini_em = VGroup(
            ParametricFunction(
                lambda t: np.array([t/3, 0.2*np.sin(4*t), 0]),
                t_range=[-2, 2],
                color=RED,
                stroke_width=2
            ),
            ParametricFunction(
                lambda t: np.array([t/3, 0, 0.2*np.sin(4*t)]),
                t_range=[-2, 2],
                color=BLUE,
                stroke_width=2
            )
        ).shift(3*RIGHT + 2*UP)
        
        # Mini Lagrangian
        mini_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}}",
            color=PURPLE
        ).scale(0.8).shift(3*LEFT + 2*DOWN)
        
        # Mini Feynman
        mini_feynman = VGroup(
            Line(LEFT, ORIGIN, color=BLUE, stroke_width=2),
            ParametricFunction(
                lambda t: np.array([t, 0.1*np.sin(10*t), 0]),
                t_range=[0, 1],
                color=YELLOW,
                stroke_width=2
            ),
            Line(RIGHT, ORIGIN, color=BLUE, stroke_width=2)
        ).scale(0.5).shift(3*RIGHT + 2*DOWN)
        
        # Central unifying text
        unity_text = Text(
            "QED: Unifying Light and Matter\nThrough Gauge Theory",
            font_size=36,
            gradient=(BLUE, PURPLE, GOLD)
        )
        
        # Halo effect
        halo = Circle(
            radius=4,
            stroke_color=YELLOW,
            stroke_width=4,
            stroke_opacity=0.5,
            fill_opacity=0
        )
        
        # Animate final collage
        self.play(
            FadeIn(mini_grid),
            FadeIn(mini_light_cone),
            run_time=2
        )
        
        self.play(
            Create(mini_em),
            Write(mini_lagrangian),
            Create(mini_feynman),
            run_time=3
        )
        
        self.play(
            Write(unity_text),
            Create(halo),
            run_time=3
        )
        
        # Final zoom out with everything
        self.play(
            self.camera.frame.animate.scale(1.5),
            halo.animate.scale(1.2).set_stroke(opacity=0.8),
            run_time=3
        )
        
        # Fade to stars
        self.play(
            *[FadeOut(mob) for mob in [
                mini_grid, mini_light_cone, mini_em,
                mini_lagrangian, mini_feynman, unity_text, halo
            ]],
            self.stars.animate.set_opacity(1),
            run_time=3
        )
        
        # Final text
        finis = Text("Finis", font_size=48, color=WHITE)
        self.play(
            Write(finis),
            run_time=2
        )
        
        self.wait(2)
        self.play(FadeOut(finis), FadeOut(self.stars), run_time=3)

# To render this animation, save this file and run:
# manim -pql quantum_field_theory.py QuantumFieldTheoryAnimation
# For high quality: manim -pqh quantum_field_theory.py QuantumFieldTheoryAnimation
# For 4K: manim -pqk quantum_field_theory.py QuantumFieldTheoryAnimation