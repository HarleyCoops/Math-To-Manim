from manim import *
import numpy as np

class StarField3D(VGroup):
    """3D starfield with depth-based scaling"""
    def __init__(self, num_stars=400, depth_layers=8, **kwargs):
        super().__init__(**kwargs)
        for _ in range(num_stars):
            layer = np.random.randint(1, depth_layers+1)
            star = Dot3D(
                point=[np.random.uniform(-7,7), 
                      np.random.uniform(-4,4),
                      np.random.uniform(-5,5)],
                radius=0.005,
                color=WHITE
            ).scale(0.5/layer)
            star.set_opacity(0.3 + 0.1*layer)
            self.add(star)

class InformationGeometryScene(ThreeDScene):
    def construct(self):
        # Configure 3D lighting properly
        self.renderer.camera.light_source.move_to([5, -5, 10])
        self.camera.background_color = "#000000"
        
        # Set initial camera orientation
        self.set_camera_orientation(
            phi=75 * DEGREES,
            theta=-30 * DEGREES,
            zoom=0.8,
        )

        ####################################################################
        # 1. COSMIC INTRODUCTION
        ####################################################################
        star_field = StarField3D()
        title = Text("Information Geometry:\nThe Landscape of Probability", 
                    font_size=42, gradient=(PURPLE, TEAL))
        title.to_edge(UP).shift(DOWN * 0.5)
        
        self.play(
            Create(star_field),
            Write(title),
            run_time=2
        )
        
        self.play(
            title.animate.scale(0.5).to_corner(UL),
            run_time=1.5
        )
        
        self.begin_ambient_camera_rotation(rate=0.1)
        self.move_camera(phi=60 * DEGREES, run_time=2)
        
        ####################################################################
        # 2. PROBABILITY MANIFOLDS VISUALIZATION
        ####################################################################
        def mu_func(u, v):
            return [u, v, np.exp(-(u**2 + v**2))]
        
        def nu_func(u, v):
            return [u, v, np.exp(-((u-1)**2 + (v-0.5)**2))]
        
        mu_surface = Surface(
            mu_func,
            u_range=[-3,3], v_range=[-3,3],
            resolution=(32,32),
            fill_opacity=0.3,
            color=BLUE
        )
        
        nu_surface = Surface(
            nu_func,
            u_range=[-3,3], v_range=[-3,3],
            resolution=(32,32),
            fill_opacity=0.3,
            color=RED
        )
        
        self.play(
            Create(mu_surface),
            Create(nu_surface),
            run_time=4
        )
        self.begin_ambient_camera_rotation(rate=0.05)
        
        ####################################################################
        # 3. KL DIVERGENCE COMPONENTS (OPTIMIZED)
        ####################################################################
        particles = VGroup()
        particle_data = []
        for _ in range(50):
            u, v = np.random.normal(0,1), np.random.normal(0,1)
            particle = Dot3D(
                color=YELLOW,
                radius=0.05
            ).move_to(mu_func(u, v))
            particles.add(particle)
            particle_data.append((u, v, particle))
        
        self.play(FadeIn(particles))
        
        kl_equation = MathTex(
            r"\text{KL}(\mu \parallel \nu) = \mathbb{E}_\mu\left[\log\frac{d\mu}{d\nu}\right]",
            font_size=40
        ).to_corner(DR)
        
        density_ratio = MathTex(
            r"\frac{d\mu}{d\nu}(x)", color=RED
        ).scale(1.2).next_to(kl_equation, UP)
        
        self.play(Write(kl_equation), Write(density_ratio))
        
        # Optimized particle animation
        labels = VGroup()
        color_anims = []
        for u, v, particle in particle_data:
            mu_val = np.exp(-(u**2 + v**2))
            nu_val = np.exp(-((u-1)**2 + (v-0.5)**2))
            ratio = mu_val / nu_val
            label = DecimalNumber(ratio, num_decimal_places=2, color=RED) \
                .scale(0.5).next_to(particle, UP)
            labels.add(label)
            color_anims.append(particle.animate.set_color(RED if ratio > 1 else BLUE))
        
        self.play(
            LaggedStart(*color_anims, lag_ratio=0.02),
            FadeIn(labels),
            run_time=2
        )
        self.wait(2)
        
        ####################################################################
        # 4. LOGARITHMIC LENS EFFECT (USING CONES)
        ####################################################################
        lens_group = VGroup()
        for u, v, particle in particle_data:
            x, y, z = particle.get_center()
            log_z = np.log(z/np.exp(-((x-1)**2 + (y-0.5)**2)))
            arrow = Cone(
                direction=UP,
                base_radius=0.05,
                height=0.5,
                color=WHITE
            ).put_start_and_end_on(
                particle.get_center(),
                [x, y, log_z]
            )
            lens_group.add(arrow)
        
        self.play(
            LaggedStart(*[Create(a) for a in lens_group], lag_ratio=0.1),
            run_time=3
        )
        self.wait(2)
        
        ####################################################################
        # 5. INFORMATION GEOMETRY CONNECTIONS
        ####################################################################
        fisher_info = MathTex(
            r"\mathcal{I}(\theta) = \mathbb{E}\left[\left(\frac{\partial}{\partial\theta}\log p_\theta\right)^2\right]",
            font_size=40
        ).to_edge(UP)
        
        # Create curvature visualization using proper surface coloring
        curvature_map = mu_surface.copy()
        curvature_map.set_color_by_gradient(BLUE, RED)
        self.play(
            Transform(mu_surface, curvature_map),
            Write(fisher_info),
            run_time=3
        )
        
        ####################################################################
        # 6. SUFFICIENCY & DATA REDUCTION (3D VERSION)
        ####################################################################
        raw_data = VGroup(*[
            Dot3D(color=WHITE, radius=0.03) 
            for _ in range(100)
        ]).arrange_in_grid(10,10, buff=0.15).scale(0.5)
        
        sufficient_stat = VGroup(*[
            Cone(
                color=GREEN,
                height=0.4,
                base_radius=0.15,
                direction=np.random.uniform(-1,1,3)
            ) for _ in range(10)
        ]).arrange_in_grid(2,5, buff=0.5)
        
        self.play(
            FadeIn(raw_data.next_to(mu_surface, OUT)),
            run_time=2
        )
        self.play(
            Transform(raw_data, sufficient_stat),
            run_time=3
        )
        
        ####################################################################
        # 7. FINAL SYNTHESIS
        ####################################################################
        final_eq = MathTex(
            r"\underbrace{\text{KL}(\mu \parallel \nu)}_{\text{Information Gain}} = ",
            r"\underbrace{\mathbb{E}_\mu[\log d\mu]}_{\text{Entropy}} - ",
            r"\underbrace{\mathbb{E}_\mu[\log d\nu]}_{\text{Cross-Entropy}}",
            font_size=36
        ).to_edge(DOWN)
        
        self.play(
            FadeIn(final_eq),
            run_time=4
        )
        self.camera.set_euler_angles(theta=0, phi=0)
        self.wait(3)
        
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=3
        )
        self.wait()