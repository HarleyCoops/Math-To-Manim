from manim import *
import numpy as np

class StarField3D(VGroup):
    """3D starfield background with parallax effect"""
    def __init__(self, num_stars=200, depth_layers=5, **kwargs):
        super().__init__(**kwargs)
        for _ in range(num_stars):
            layer = np.random.randint(1, depth_layers+1)
            star = Dot3D(
                point=[np.random.uniform(-7,7), 
                      np.random.uniform(-4,4),
                      np.random.uniform(-5,5)],
                radius=0.01 + 0.005*layer,
                color=WHITE
            )
            star.set_opacity(0.3 + 0.1*layer)  # Set opacity after creation
            self.add(star)

class InformationGeometryScene(ThreeDScene):
    def construct(self):
        # Set better initial camera position and background
        self.camera.background_color = "#000000"
        self.set_camera_orientation(
            phi=75 * DEGREES,  # More overhead view
            theta=-30 * DEGREES,
            zoom=0.8,         # Zoom out slightly
            frame_center=[0, 0, 0]
        )
        
        # Add ambient light for better 3D visualization
        self.camera.light_source.move_to([20, -20, 20])
        
        ####################################################################
        # 1. COSMIC INTRODUCTION
        ####################################################################
        # Create starfield but don't add it yet
        star_field = StarField3D(num_stars=400, depth_layers=8)
        
        # Move title to better position
        title = Text("Information Geometry:\nThe Landscape of Probability", 
                    font_size=42, gradient=(PURPLE, TEAL))
        title.to_edge(UP).shift(DOWN * 0.5)
        
        # Fade in both elements
        self.play(
            Create(star_field),  # Changed from FadeIn to Create
            Write(title),
            run_time=2
        )
        
        self.play(
            title.animate.scale(0.5).to_corner(UL),
            run_time=1.5
        )
        
        # Adjust camera movement speed
        self.begin_ambient_camera_rotation(rate=0.1)
        self.move_camera(phi=60 * DEGREES, run_time=2)
        
        ####################################################################
        # 2. PROBABILITY MANIFOLDS VISUALIZATION
        ####################################################################
        # Create μ and ν as 3D probability surfaces
        def mu_func(u, v):
            return [u, v, np.exp(-(u**2 + v**2))]
        
        def nu_func(u, v):
            return [u, v, np.exp(-((u-1)**2 + (v-0.5)**2))]
        
        mu_surface = Surface(
            mu_func,
            u_range=[-3,3], v_range=[-3,3],
            resolution=(32,32),
            fill_opacity=0.3,
            stroke_width=1,
            color=BLUE
        )
        
        nu_surface = Surface(
            nu_func,
            u_range=[-3,3], v_range=[-3,3],
            resolution=(32,32),
            fill_opacity=0.3,
            stroke_width=1,
            color=RED
        )
        
        self.play(
            Create(mu_surface),
            Create(nu_surface),
            run_time=4
        )
        self.begin_ambient_camera_rotation(rate=0.05)
        
        ####################################################################
        # 3. KL DIVERGENCE COMPONENTS
        ####################################################################
        # Animate particles sampling from μ
        particles = VGroup(*[
            Dot3D(color=YELLOW, radius=0.05).move_to(
                mu_func(np.random.normal(0,1), np.random.normal(0,1))
            ) for _ in range(50)
        ])
        self.play(FadeIn(particles))
        
        # Show log-density ratio calculation
        kl_equation = MathTex(
            r"\text{KL}(\mu \parallel \nu) = \mathbb{E}_\mu\left[\log\frac{d\mu}{d\nu}\right]",
            font_size=40
        ).to_corner(DR)
        
        density_ratio = MathTex(
            r"\frac{d\mu}{d\nu}(x)", color=RED
        ).scale(1.2).next_to(kl_equation, UP)
        
        self.play(Write(kl_equation), Write(density_ratio))
        
        # Animate particles evaluating density ratio
        for particle in particles:
            x, y, _ = particle.get_center()
            mu_val = np.exp(-(x**2 + y**2))
            nu_val = np.exp(-((x-1)**2 + (y-0.5)**2))
            ratio = mu_val / nu_val
            label = DecimalNumber(ratio, num_decimal_places=2, color=RED) \
                .scale(0.5).next_to(particle, UP)
            self.add(label)
            self.play(
                particle.animate.set_color(RED if ratio > 1 else BLUE),
                run_time=0.1
            )
        self.wait(2)
        
        ####################################################################
        # 4. LOGARITHMIC LENS EFFECT
        ####################################################################
        # Create warping effect for log transform
        lens_group = VGroup()
        for particle in particles:
            x, y, z = particle.get_center()
            log_z = np.log(z/np.exp(-((x-1)**2 + (y-0.5)**2)))
            arrow = Arrow3D(
                start=particle.get_center(),
                end=[x, y, log_z],
                color=WHITE
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
        # Fisher information matrix visualization
        fisher_info = MathTex(
            r"\mathcal{I}(\theta) = \mathbb{E}\left[\left(\frac{\partial}{\partial\theta}\log p_\theta\right)^2\right]",
            font_size=40
        ).to_edge(UP)
        
        # Create curvature visualization on μ surface
        curvature_map = mu_surface.copy()
        curvature_map.set_color_by_gradient(BLUE, RED)
        self.play(
            Transform(mu_surface, curvature_map),
            Write(fisher_info),
            run_time=3
        )
        
        ####################################################################
        # 6. SUFFICIENCY & DATA REDUCTION
        ####################################################################
        # Animate data compression to sufficient statistics
        raw_data = VGroup(*[
            Dot3D(color=WHITE) for _ in range(100)
        ]).arrange_in_grid(10,10).scale(0.5)
        
        sufficient_stat = VGroup(*[
            Triangle(color=GREEN).scale(0.3) for _ in range(10)
        ]).arrange_in_grid(2,5).scale(1.5)
        
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
        self.move_camera(theta=0, phi=0, run_time=4)
        
        # Cosmic fade out
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=3
        )
        self.wait()