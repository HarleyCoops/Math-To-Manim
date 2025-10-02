from manim import *
from manim.mobject.three_d.three_dimensions import Surface
import numpy as np

# Enable caching explicitly
config.cache_dir = "./media/videos/cache"
config.disable_caching = False
config.save_last_frame = False

class StarField(VGroup):
    def __init__(self, is_3D=True, num_stars=600, **kwargs):  # Increased stars for epic feel
        super().__init__(**kwargs)
        colors = [WHITE, BLUE_E, YELLOW, PURPLE]  # Added purple for variety
        for _ in range(num_stars):
            star = Dot3D(
                point=self.random_point(),
                color=np.random.choice(colors),
                radius=np.random.uniform(0.02, 0.06)
            )
            star.set_shade(np.random.uniform(0.3, 0.7))  # Varied shading
            self.add(star)
    
    def random_point(self):
        return np.array([
            np.random.uniform(-8, 8),
            np.random.uniform(-5, 5),
            np.random.uniform(-6, 6)
        ])

class QEDJourney(ThreeDScene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES, zoom=0.7)  # Adjusted zoom for wider, epic view
        
        # 1. Cosmic Introduction with Enhanced Drama
        star_field = StarField(num_stars=600)
        title = Text("Quantum Field Theory:\nA Journey into QED", 
                    font_size=60, gradient=(BLUE, PURPLE)).scale(1.2)  # Bigger, gradient tweak
        subtitle = Text("From Maxwell to Feynman", font_size=40, color=GOLD)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        # Make text visible in 3D
        self.add_fixed_in_frame_mobjects(title_group)
        
        self.play(
            FadeIn(star_field, run_time=5),  # Slower fade for grandeur
            Write(title, run_time=2.5),
            FadeIn(subtitle, shift=UP*0.5),
            rate_func=smooth  # Changed from there_and_back for better flow
        )
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)

        # Keep text facing viewer
        def always_facing_text(mob):
            mob.rotate(-self.camera.get_theta(), OUT)
            mob.rotate(-self.camera.get_phi(), RIGHT)
        
        # 2. Spacetime Foundation with Labels
        axes = ThreeDAxes(x_range=[-6,6], y_range=[-6,6], z_range=[-5,5])
        spacetime_grid = Surface(
            lambda u,v: axes.c2p(u,v,0),
            u_range=[-6,6], v_range=[-6,6],
            resolution=(30,30),
            fill_opacity=0.15,
            stroke_width=1.5,
            stroke_color=BLUE_E
        )
        light_cone = Surface(
            lambda u,v: axes.c2p(v*np.cos(u), v*np.sin(u), v),
            u_range=[0,2*PI], v_range=[0,4],
            resolution=(30,15),
            fill_opacity=0.25,
            color=YELLOW
        )
        
        # Educational label for light cone
        light_cone_label = Text("Light Cone\n(Spacetime Boundary)", font_size=24, color=YELLOW)
        self.add_fixed_in_frame_mobjects(light_cone_label)
        light_cone_label.to_corner(UR)
        
        # Fixed cone_particles creation using direct parametric coordinates
        cone_particles = VGroup(*[
            Dot3D(color=RED, radius=0.06).move_to(
                np.array([
                    r * np.cos(a),  # x coordinate
                    r * np.sin(a),  # y coordinate
                    r               # z coordinate
                ])
            )
            for a in np.linspace(0, TAU, 25)
            for r in np.linspace(0.5, 4, 10)  # Starting from 0.5 to avoid clustering at origin
        ])
        
        self.play(
            Create(axes, run_time=2),
            Create(spacetime_grid, run_time=3),
            FadeIn(cone_particles, run_time=2),
            title_group.animate.scale(0.5).to_corner(UL)
        )
        self.play(Create(light_cone, run_time=3), FadeIn(light_cone_label))
        self.wait(2)
        
        # 3. Enhanced EM Waves with Explanation
        wave_group = VGroup()
        glow_group = VGroup()
        for direction in [LEFT, RIGHT]:
            wave = ParametricFunction(
                lambda t: axes.c2p(
                    direction[0]*t,
                    0,
                    np.sin(4*t)*0.7  # Increased amplitude and frequency
                ),
                t_range=[0,6],
                color=RED,
                stroke_width=3
            )
            wave_glow = VGroup(*[
                Dot3D(
                    point=wave.point_from_proportion(p),
                    color=interpolate_color(RED, WHITE, 0.6*(1 + np.sin(p*TAU))),
                    radius=0.2
                ).set_opacity(0.4)
                for p in np.linspace(0,1,60)
            ])
            wave_group.add(wave)
            glow_group.add(wave_glow)
        
        field_particles = VGroup(*[
            Dot3D(
                point=[x, 0, 0],
                color=BLUE,
                radius=0.1
            )
            for x in np.linspace(-6,6,25)
        ])
        
        maxwell_eq = MathTex(
            r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}",
            r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}"
        ).arrange(DOWN, buff=0.4).scale(0.9)
        maxwell_label = Text("Maxwell's Equations\n(Electromagnetic Fields)", font_size=24, color=RED)
        
        # Add equations to fixed frame
        self.add_fixed_in_frame_mobjects(maxwell_eq, maxwell_label)
        maxwell_eq.to_corner(DR)
        maxwell_label.next_to(maxwell_eq, UP)
        
        self.play(
            Create(wave_group, run_time=4),
            FadeIn(glow_group),
            FadeIn(field_particles),
            Write(maxwell_eq),
            FadeIn(maxwell_label)
        )
        self.wait(3)
        
        # 4. QED Lagrangian with Educational Morph
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            substrings_to_isolate=[r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu\nu}"]
        ).scale(0.9)
        qed_label = Text("QED Lagrangian\n(Quantum Electrodynamics)", font_size=24, color=GOLD)
        
        # Add to fixed frame
        self.add_fixed_in_frame_mobjects(qed_lagrangian, qed_label)
        qed_lagrangian.to_corner(UR)
        qed_label.next_to(qed_lagrangian, DOWN)
        
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu\nu}", GOLD)
        
        self.play(
            TransformMatchingShapes(maxwell_eq, qed_lagrangian),
            Transform(maxwell_label, qed_label),
            run_time=4
        )
        self.wait(2)
        
        # 5. Epic Feynman Diagram
        feynman_diagram = VGroup(
            Line3D(LEFT*4, ORIGIN, color=BLUE, stroke_width=4),
            Line3D(ORIGIN, RIGHT*4, color=BLUE, stroke_width=4),
            ParametricFunction(
                lambda t: np.array([
                    4*np.cos(t) - 4,
                    0,
                    4*np.sin(t)
                ]),
                t_range=[-PI/2, PI/2],
                color=YELLOW,
                stroke_width=3
            )
        ).shift(UP*2.5)
        
        vertex_glow = Dot3D(color=WHITE, radius=0.4)
        feynman_label = Text("Feynman Diagram\n(Electron-Photon Interaction)", font_size=24, color=YELLOW)
        
        # Add label to fixed frame
        self.add_fixed_in_frame_mobjects(feynman_label)
        feynman_label.to_edge(UP)
        
        self.play(
            Create(feynman_diagram, run_time=4),
            FadeIn(vertex_glow),
            FadeIn(feynman_label)
        )
        self.wait(2)
        
        # 6. Alpha Plot
        alpha_plot = Axes(
            x_range=[0, 20],
            y_range=[0.005, 0.03],
            x_length=7,
            y_length=5
        )
        curve = alpha_plot.plot(
            lambda x: 0.007297 + 0.0001*x,
            color=RED,
            stroke_width=3
        )
        
        tracer = Dot(color=RED, radius=0.1)
        alpha_label = Text("Fine-Structure Constant\n(Strength of EM Interaction)", font_size=24, color=RED)
        
        # Add to fixed frame
        self.add_fixed_in_frame_mobjects(alpha_plot, curve, tracer, alpha_label)
        alpha_plot.to_edge(DL)
        alpha_label.next_to(alpha_plot, UP)
        tracer.move_to(curve.get_start())
        
        self.play(
            Create(alpha_plot),
            Create(curve),
            FadeIn(tracer),
            FadeIn(alpha_label)
        )
        self.wait(2)
        
        # 7. Grand Finale
        final_text = Text("QED: Light & Matter United", font_size=60, gradient=(BLUE, GOLD))
        self.add_fixed_in_frame_mobjects(final_text)
        final_text.scale(1.5)
        
        particle_trails = VGroup(*[
            Dot3D(
                color=np.random.choice([RED, BLUE, YELLOW]),
                radius=0.05
            ).move_to(np.random.uniform(-5, 5, 3))
            for _ in range(50)
        ])
        
        self.play(
            FadeIn(particle_trails),
            FadeIn(final_text),
            *[FadeOut(mob) for mob in [feynman_diagram, vertex_glow, alpha_plot, curve, tracer, alpha_label]],
            run_time=6
        )
        
        self.wait(4)
        
        # Clean ending
        self.stop_ambient_camera_rotation()
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=3
        )