from manim import *
from manim.mobject.three_d.three_dimensions import Surface
import numpy as np

class StarField(VGroup):
    def __init__(self, is_3D=True, num_stars=400, **kwargs):
        super().__init__(**kwargs)
        colors = [WHITE, BLUE_E, YELLOW]
        for _ in range(num_stars):
            star = Dot3D(
                point=self.random_point(),
                color=np.random.choice(colors),
                radius=np.random.uniform(0.01, 0.05)
            )
            star.set_shade(0.5)
            self.add(star)
    
    def random_point(self):
        return np.array([
            np.random.uniform(-7, 7),
            np.random.uniform(-4, 4),
            np.random.uniform(-5, 5)
        ])

class QEDJourney(ThreeDScene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES, zoom=0.8)  # zoom < 1 makes view wider
        
        # Custom camera path
        camera_path = ParametricFunction(
            lambda t: np.array([3*np.cos(t), 3*np.sin(t), 0.5*t]),
            t_range=[0, 2*TAU]
        )
        
        # 1. Cosmic Introduction with dynamic camera
        star_field = StarField(num_stars=500)
        title = Text("Quantum Field Theory:\nA Journey into QED", 
                    font_size=48, gradient=(BLUE, YELLOW))
        subtitle = Text("From Maxwell to Feynman", font_size=36)
        title_group = VGroup(title, subtitle).arrange(DOWN)
        
        # Camera sweep through starfield
        self.move_camera(phi=75*DEGREES, theta=30*DEGREES, run_time=3)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.play(
            FadeIn(star_field, run_time=4),
            Write(title, run_time=2),
            FadeIn(subtitle, shift=UP),
            self.camera.frame.animate.move_to(ORIGIN + 2*OUT),
        )
        self.wait(2)
        
        # Keep text facing viewer function
        def always_facing_text(mob):
            mob.rotate(-self.camera.get_theta(), OUT)
            mob.rotate(-self.camera.get_phi(), RIGHT)
        
        # 2. Enhanced Spacetime Foundation
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
            fill_opacity=0.2,
            color=YELLOW,
            gloss=0.5
        )
        
        # Animated particles on light cone
        cone_particles = VGroup(*[
            Dot3D(color=RED, radius=0.05).move_to(
                light_cone.surface_point_from_coords(a, r)
            ).add_updater(lambda m, dt: m.rotate(0.2*dt, OUT))
            for a in np.linspace(0, TAU, 20)
            for r in np.linspace(0,3,8)
        ])
        
        self.play(
            Create(axes, run_time=2),
            Create(spacetime_grid, run_time=3),
            FadeIn(cone_particles, run_time=2),
            title_group.animate.scale(0.5).to_corner(UL),
            self.camera.frame.animate.set_euler_angles(theta=45*DEGREES),
        )
        self.play(Create(light_cone, run_time=3))
        self.wait(2)
        
        # 3. Enhanced EM Waves
        wave_group = VGroup()
        glow_group = VGroup()
        for direction in [LEFT, RIGHT]:
            wave = ParametricFunction(
                lambda t: axes.c2p(
                    direction[0]*t,
                    0,
                    np.sin(3*t)*0.5
                ),
                t_range=[0,5],
                color=RED
            )
            wave_glow = VGroup(*[
                Dot3D(
                    point=wave.point_from_proportion(p),
                    color=interpolate_color(RED, WHITE, 0.5*(1 + np.sin(p*TAU))),
                    radius=0.15
                ).set_opacity(0.3)
                for p in np.linspace(0,1,50)
            ])
            wave_group.add(wave)
            glow_group.add(wave_glow)
        
        # Dynamic vector field particles
        field_particles = VGroup(*[
            Dot3D(
                point=[x, 0, 0],
                color=BLUE,
                radius=0.08
            ).add_updater(lambda m, dt: m.shift(0.1*dt*OUT*np.sin(3*m.get_x() + 2*self.time)))
            for x in np.linspace(-5,5,20)
        ])
        
        maxwell_eq = MathTex(
            r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}",
            r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}"
        ).arrange(DOWN).to_edge(DR)
        maxwell_eq.add_updater(always_facing_text)
        
        self.play(
            Create(wave_group, run_time=3),
            FadeIn(glow_group),
            FadeIn(field_particles),
            Write(maxwell_eq),
        )
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(3)
        
        # 4. QED Lagrangian with morphing effect
        qed_lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            substrings_to_isolate=[r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu\nu}"]
        ).scale(0.8).to_corner(UR)
        qed_lagrangian.add_updater(always_facing_text)
        
        qed_lagrangian.set_color_by_tex(r"\psi", ORANGE)
        qed_lagrangian.set_color_by_tex(r"D_\mu", GREEN)
        qed_lagrangian.set_color_by_tex(r"\gamma^\mu", TEAL)
        qed_lagrangian.set_color_by_tex(r"F_{\mu\nu}", GOLD)
        
        self.play(
            TransformMatchingShapes(maxwell_eq, qed_lagrangian),
            run_time=3,
            path_arc=PI/2
        )
        self.wait(2)
        
        # 5. Animated Feynman Diagram
        feynman_diagram = VGroup(
            Line3D(LEFT*3, ORIGIN, color=BLUE, gloss=0.5),
            Line3D(ORIGIN, RIGHT*3, color=BLUE, gloss=0.5),
            ParametricFunction(
                lambda t: np.array([
                    3*np.cos(t) - 3,
                    0,
                    3*np.sin(t)
                ]),
                t_range=[-PI/2, PI/2],
                color=YELLOW
            )
        ).shift(UP*2)
        
        vertex_glow = Dot3D(color=WHITE, radius=0.3, gloss=1.0)
        vertex_glow.add_updater(lambda m: m.set_opacity(0.5*(1 + np.sin(2*self.time))))
        
        self.play(
            Create(feynman_diagram, run_time=3),
            FadeIn(vertex_glow),
            self.camera.frame.animate.move_to(ORIGIN + 3*OUT + 2*UP),
            run_time=3
        )
        self.wait(2)
        
        # 6. Enhanced Alpha Plot
        alpha_plot = Axes(
            x_range=[0, 20], y_range=[0.005, 0.03],
            x_length=6, y_length=4
        ).to_edge(DL)
        curve = alpha_plot.plot(
            lambda x: 0.007297 + 0.0001*x,
            color=RED
        )
        
        tracer = Dot(color=RED).move_to(curve.get_start())
        tracer.add_updater(lambda m: m.move_to(curve.point_from_proportion(
            (self.time % 5)/5
        )))
        
        self.play(
            Create(alpha_plot),
            Create(curve),
            FadeIn(tracer),
            self.camera.frame.animate.move_to(ORIGIN),
            run_time=3
        )
        self.wait(2)
        
        # 7. Finale with particle trails
        final_text = Text("QED: Light & Matter United", font_size=48)
        final_text.add_updater(always_facing_text)
        self.play(
            FadeIn(final_text, shift=UP),
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=5
        )
        self.wait(3)