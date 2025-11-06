from manim import *
import numpy as np
import random

class QuantumFieldTheoryJourney(ThreeDScene):
    def construct(self):
        # Set initial camera orientation
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        # ==================== 1. Star Field Backdrop ====================
        star_field = self.create_star_field()
        self.play(FadeIn(star_field, run_time=3))
        self.wait(0.5)
        
        # ==================== 2. Title and 3D Axis Frame ====================
        title = Text(
            "Quantum Field Theory:\nA Journey into the Electromagnetic Interaction",
            font_size=36,
            weight=BOLD,
            color=WHITE
        )
        title.to_edge(UP)
        
        # Create glowing effect for title
        title_glow = title.copy()
        title_glow.set_color(BLUE)
        title_glow.set_stroke(width=8, opacity=0.5)
        
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-5, 5, 1],
            x_length=10,
            y_length=10,
            z_length=10
        )
        
        self.play(FadeIn(title_glow), FadeIn(title), FadeIn(axes))
        self.wait(1)
        
        # Move title to upper-left corner
        title_target = title.copy().scale(0.5).to_corner(UL)
        title_glow_target = title_glow.copy().scale(0.5).to_corner(UL)
        
        self.play(
            Transform(title, title_target),
            Transform(title_glow, title_glow_target),
            run_time=2
        )
        self.wait(0.5)
        
        # ==================== 3. Wireframe Minkowski Spacetime ====================
        wireframe = self.create_wireframe()
        light_cone = self.create_light_cone()
        
        self.play(
            Create(wireframe, run_time=2),
            Create(light_cone, run_time=2)
        )
        self.wait(1)
        
        # Rotate wireframe
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(2)
        
        # ==================== 4. Relativistic Metric Equation ====================
        metric_eq = MathTex(
            r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2",
            font_size=36
        )
        metric_eq.to_edge(DOWN)
        metric_eq[0][0:3].set_color(WHITE)  # ds^2
        metric_eq[0][3:6].set_color(RED)    # -c^2
        metric_eq[0][6:10].set_color(YELLOW) # dt^2
        metric_eq[0][10:12].set_color(GREEN) # dx^2
        metric_eq[0][12:15].set_color(BLUE)  # dy^2
        metric_eq[0][15:18].set_color(PURPLE) # dz^2
        
        self.play(Write(metric_eq), run_time=3)
        self.wait(2)
        
        # ==================== 5. Zoom to Origin and EM Waves ====================
        # Stop rotation and zoom
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=1.5, run_time=2)
        
        # Create electromagnetic waves
        em_waves = self.create_em_waves()
        e_label = MathTex(r"\vec{E}", color=RED).shift(LEFT * 2)
        b_label = MathTex(r"\vec{B}", color=BLUE).shift(RIGHT * 2)
        
        self.play(
            FadeOut(metric_eq),
            FadeIn(em_waves),
            Write(e_label),
            Write(b_label)
        )
        self.wait(2)
        
        # Add rotating arrows for field directions
        e_arrow = Arrow(ORIGIN, UP, color=RED).next_to(e_label, DOWN)
        b_arrow = Arrow(ORIGIN, RIGHT, color=BLUE).next_to(b_label, DOWN)
        
        self.play(
            Rotate(e_arrow, angle=TAU, axis=RIGHT, run_time=3, rate_func=linear),
            Rotate(b_arrow, angle=TAU, axis=RIGHT, run_time=3, rate_func=linear),
        )
        self.wait(1)
        
        # Propagation arrow
        prop_arrow = Arrow(ORIGIN, OUT * 3, color=YELLOW)
        prop_label = Text("Propagation", font_size=24, color=YELLOW).next_to(prop_arrow, RIGHT)
        
        self.play(GrowArrow(prop_arrow), FadeIn(prop_label))
        self.wait(2)
        
        # ==================== 6. Maxwell's Equations Transformation ====================
        # Fade out current elements
        self.play(
            FadeOut(em_waves),
            FadeOut(e_label),
            FadeOut(b_label),
            FadeOut(e_arrow),
            FadeOut(b_arrow),
            FadeOut(prop_arrow),
            FadeOut(prop_label),
            FadeOut(wireframe),
            FadeOut(light_cone),
            FadeOut(axes)
        )
        
        # Classical form
        classical_maxwell = MathTex(
            r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}",
            r"\nabla \cdot \vec{B} = 0",
            r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}",
            r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}",
            font_size=28
        ).arrange(DOWN, aligned_edge=LEFT)
        
        # Relativistic form
        relativistic_maxwell = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu",
            font_size=36
        )
        
        self.play(Write(classical_maxwell), run_time=3)
        self.wait(1)
        
        # Transform to relativistic form
        self.play(
            ReplacementTransform(classical_maxwell, relativistic_maxwell),
            run_time=2
        )
        self.wait(2)
        self.play(FadeOut(relativistic_maxwell))
        
        # ==================== 7. QED Lagrangian ====================
        # Recreate wireframe background
        wireframe_bg = self.create_wireframe().set_opacity(0.3)
        self.add(wireframe_bg)
        
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            font_size=32
        )
        
        # Color coding
        lagrangian[0][0:6].set_color(WHITE)    # L_QED
        lagrangian[0][7:11].set_color(ORANGE)  # psi-bar
        lagrangian[0][12:14].set_color(TEAL)   # i
        lagrangian[0][14:18].set_color(BLUE)  # gamma^mu
        lagrangian[0][18:21].set_color(GREEN)  # D_mu
        lagrangian[0][22:23].set_color(ORANGE) # m
        lagrangian[0][24:26].set_color(ORANGE) # psi
        lagrangian[0][29:33].set_color(GOLD)   # F_mu nu
        
        # Semi-transparent plane
        plane = Rectangle(width=8, height=3, color=WHITE, fill_opacity=0.1, stroke_width=2)
        plane.to_edge(UP)
        
        lagrangian.move_to(plane.get_center())
        
        self.play(
            FadeIn(plane),
            Write(lagrangian),
            run_time=3
        )
        
        # Pulse animation for dynamic fields
        self.animate_pulsing_terms(lagrangian)
        self.wait(2)
        
        # ==================== 8. Gauge Invariance ====================
        gauge_text = Text("Gauge Invariance", font_size=28, color=YELLOW).to_edge(UP)
        phase_eq = MathTex(
            r"\psi \to e^{i\alpha(x)}\psi",
            font_size=32
        ).next_to(lagrangian, DOWN)
        
        gauge_eq = MathTex(
            r"D_\mu \to D_\mu - i\partial_\mu \alpha(x)",
            font_size=32
        ).next_to(phase_eq, DOWN)
        
        self.play(
            Write(gauge_text),
            Write(phase_eq),
            Write(gauge_eq),
            run_time=2
        )
        
        # Arrows and callouts
        arrow1 = Arrow(phase_eq.get_right(), lagrangian.get_bottom(), color=YELLOW)
        arrow2 = Arrow(gauge_eq.get_right(), lagrangian.get_bottom(), color=YELLOW)
        
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.wait(2)
        
        # ==================== 9. Feynman Diagram ====================
        # Clear previous elements
        self.play(
            FadeOut(lagrangian),
            FadeOut(plane),
            FadeOut(phase_eq),
            FadeOut(gauge_eq),
            FadeOut(gauge_text),
            FadeOut(arrow1),
            FadeOut(arrow2),
            FadeOut(wireframe_bg)
        )
        
        # Create Feynman diagram
        diagram = self.create_feynman_diagram()
        self.play(FadeIn(diagram), run_time=2)
        self.wait(2)
        
        # ==================== 10. Running Coupling Constant Graph ====================
        self.play(FadeOut(diagram))
        
        # Create 2D axes for the graph
        graph_axes = Axes(
            x_range=[0, 100, 20],
            y_range=[0.005, 0.01, 0.001],
            x_length=7,
            y_length=5,
            axis_config={"include_numbers": True}
        )
        
        x_label = graph_axes.get_x_axis_label("Energy Scale", edge=DOWN, buff=0.5)
        y_label = graph_axes.get_y_axis_label("Coupling Strength", edge=LEFT, buff=0.5)
        
        # Running coupling curve
        coupling_curve = graph_axes.plot(
            lambda x: 0.0073 + 0.0001 * np.log(x + 1),
            x_range=[0, 100],
            color=BLUE
        )
        
        graph_title = Text("Running of α", font_size=28).to_edge(UP)
        
        self.play(
            Create(graph_axes),
            Write(x_label),
            Write(y_label),
            Write(graph_title)
        )
        
        # Draw curve
        self.play(Create(coupling_curve), run_time=3)
        
        # Add data points
        data_points = VGroup(*[
            Dot(graph_axes.c2p(x, 0.0073 + 0.0001 * np.log(x + 1)), color=RED, radius=0.05)
            for x in [10, 30, 50, 70, 90]
        ])
        
        self.play(FadeIn(data_points))
        self.wait(2)
        
        # ==================== 11. Final Collage ====================
        # Fade out graph
        self.play(
            FadeOut(graph_axes),
            FadeOut(x_label),
            FadeOut(y_label),
            FadeOut(graph_title),
            FadeOut(coupling_curve),
            FadeOut(data_points)
        )
        
        # Recreate all elements at smaller scale
        final_wireframe = self.create_wireframe().scale(0.5).shift(LEFT * 3 + UP * 2)
        final_em_waves = self.create_em_waves().scale(0.5).shift(RIGHT * 3 + UP * 2)
        final_lagrangian = lagrangian.copy().scale(0.6).shift(DOWN * 1)
        final_diagram = self.create_feynman_diagram().scale(0.6).shift(LEFT * 3 + DOWN * 2)
        
        # Summary text
        summary = Text(
            "QED: Unifying Light and Matter Through Gauge Theory",
            font_size=36,
            weight=BOLD,
            color=YELLOW
        ).to_edge(UP)
        
        # Halo effect
        halo = summary.copy()
        halo.set_color(YELLOW)
        halo.set_stroke(width=10, opacity=0.3)
        
        self.play(
            FadeIn(final_wireframe),
            FadeIn(final_em_waves),
            FadeIn(final_lagrangian),
            FadeIn(final_diagram),
            Write(summary),
            FadeIn(halo)
        )
        self.wait(3)
        
        # ==================== 12. Fade Out ====================
        self.move_camera(zoom=0.5, run_time=3)
        
        # Fade everything
        self.play(
            FadeOut(final_wireframe),
            FadeOut(final_em_waves),
            FadeOut(final_lagrangian),
            FadeOut(final_diagram),
            FadeOut(summary),
            FadeOut(halo),
            FadeOut(title),
            FadeOut(title_glow)
        )
        
        # End with star field
        finis = Text("Finis", font_size=48, color=WHITE)
        self.play(Write(finis), run_time=2)
        self.wait(2)
        self.play(FadeOut(finis), FadeOut(star_field))
    
    def create_star_field(self, n_stars=200):
        """Create a star field background"""
        stars = VGroup()
        for _ in range(n_stars):
            star = Dot(
                point=[random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)],
                radius=random.uniform(0.01, 0.05),
                color=random.choice([WHITE, LIGHT_GRAY, BLUE])
            )
            star.set_opacity(random.uniform(0.5, 1.0))
            stars.add(star)
        return stars
    
    def create_wireframe(self):
        """Create 3D wireframe representation of spacetime"""
        wireframe = VGroup()
        
        # Grid lines
        for i in range(-5, 6, 2):
            # XZ plane lines
            line1 = Line3D([-5, i, -5], [5, i, -5], color=BLUE, stroke_width=1)
            line2 = Line3D([-5, i, 5], [5, i, 5], color=BLUE, stroke_width=1)
            line3 = Line3D([i, -5, -5], [i, 5, -5], color=BLUE, stroke_width=1)
            line4 = Line3D([i, -5, 5], [i, 5, 5], color=BLUE, stroke_width=1)
            
            # YZ plane lines
            line5 = Line3D([-5, -5, i], [-5, 5, i], color=GREEN, stroke_width=1)
            line6 = Line3D([5, -5, i], [5, 5, i], color=GREEN, stroke_width=1)
            line7 = Line3D([-5, i, -5], [-5, i, 5], color=GREEN, stroke_width=1)
            line8 = Line3D([5, i, -5], [5, i, 5], color=GREEN, stroke_width=1)
            
            wireframe.add(line1, line2, line3, line4, line5, line6, line7, line8)
        
        return wireframe
    
    def create_light_cone(self):
        """Create light cone visualization"""
        cone = Cone(
            base_radius=5,
            height=5,
            direction=UP,
            color=YELLOW,
            fill_opacity=0.3,
            stroke_width=2
        )
        cone_down = Cone(
            base_radius=5,
            height=5,
            direction=DOWN,
            color=YELLOW,
            fill_opacity=0.3,
            stroke_width=2
        )
        return VGroup(cone, cone_down)
    
    def create_em_waves(self):
        """Create animated electromagnetic waves"""
        waves = VGroup()
        
        # Electric field wave (red) - oscillates in Y direction, propagates in Z
        e_wave = ParametricFunction(
            lambda t: np.array([0, np.sin(t) * 0.5, t]),  # [x, y, z] - 3D coordinates
            t_range=[-3, 3, 0.1],
            color=RED,
            stroke_width=3
        )
        
        # Magnetic field wave (blue) - oscillates in X direction, propagates in Z
        b_wave = ParametricFunction(
            lambda t: np.array([np.sin(t) * 0.5, 0, t]),  # [x, y, z] - 3D coordinates
            t_range=[-3, 3, 0.1],
            color=BLUE,
            stroke_width=3
        )
        
        # Animated waves using updaters
        def update_e_wave(mob, dt):
            mob.become(
                ParametricFunction(
                    lambda t: np.array([0, np.sin(t + self.time * 2) * 0.5, t]),
                    t_range=[-3, 3, 0.1],
                    color=RED,
                    stroke_width=3
                )
            )
        
        def update_b_wave(mob, dt):
            mob.become(
                ParametricFunction(
                    lambda t: np.array([np.sin(t + self.time * 2) * 0.5, 0, t]),
                    t_range=[-3, 3, 0.1],
                    color=BLUE,
                    stroke_width=3
                )
            )
        
        e_wave.add_updater(update_e_wave)
        b_wave.add_updater(update_b_wave)
        
        waves.add(e_wave, b_wave)
        return waves
    
    def animate_pulsing_terms(self, lagrangian):
        """Animate pulsing effect on Lagrangian terms"""
        # Terms to pulse: psi, D_mu, gamma, F
        psi_terms = VGroup(lagrangian[0][7:11], lagrangian[0][24:26])
        d_terms = lagrangian[0][18:21]
        gamma_terms = lagrangian[0][14:18]
        f_terms = lagrangian[0][29:33]
        
        for _ in range(3):
            self.play(
                psi_terms.animate.scale(1.1).set_color(ORANGE),
                d_terms.animate.scale(1.1).set_color(GREEN),
                gamma_terms.animate.scale(1.1).set_color(BLUE),
                f_terms.animate.scale(1.1).set_color(GOLD),
                rate_func=there_and_back,
                run_time=0.5
            )
    
    def create_feynman_diagram(self):
        """Create simplified Feynman diagram"""
        diagram = VGroup()
        
        # Electron lines
        e1 = Line(LEFT * 3 + UP * 2, ORIGIN, color=BLUE, stroke_width=4)
        e2 = Line(LEFT * 3 + DOWN * 2, ORIGIN, color=BLUE, stroke_width=4)
        e3 = Line(ORIGIN, RIGHT * 3 + UP * 2, color=BLUE, stroke_width=4)
        e4 = Line(ORIGIN, RIGHT * 3 + DOWN * 2, color=BLUE, stroke_width=4)
        
        # Photon line
        photon = self.create_wavy_line(ORIGIN, UP * 0.5, color=YELLOW)
        
        # Labels
        e_label = MathTex(r"e^-", color=BLUE).next_to(e1, LEFT)
        photon_label = MathTex(r"\gamma", color=YELLOW).next_to(photon, RIGHT)
        
        # Coupling constant
        alpha = MathTex(r"\alpha \approx \frac{1}{137}", font_size=32).to_edge(UP)
        
        diagram.add(e1, e2, e3, e4, photon, e_label, photon_label, alpha)
        return diagram
    
    def create_wavy_line(self, start, end, color=YELLOW):
        """Create wavy photon line"""
        photon = VGroup()
        n_wiggles = 6
        for i in range(n_wiggles):
            t = i / (n_wiggles - 1)
            point1 = start + (end - start) * t + UP * 0.1 * np.sin(t * PI * 4)
            point2 = start + (end - start) * (t + 1/(n_wiggles - 1)) + UP * 0.1 * np.sin((t + 1/(n_wiggles - 1)) * PI * 4)
            photon.add(Line(point1, point2, color=color, stroke_width=3))
        return photon
