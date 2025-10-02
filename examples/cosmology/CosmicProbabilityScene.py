from manim import *
import numpy as np
from manim.mobject.geometry.tips import ArrowSquareTip

class CosmicProbabilityScene(ThreeDScene):
    def construct(self):
        self.setup_initial_scene()
        self.animate_cosmic_distributions()
        self.create_diffusion_bridge()
        self.show_optimal_transport()
        self.demonstrate_wasserstein()
        self.synthesize_benamou_brenier()
        
    def setup_initial_scene(self):
        self.camera.background_color = BLACK
        self.cosmic_void = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BLACK,
            fill_opacity=1,
            stroke_width=0
        )
        self.add(self.cosmic_void)
        
    def animate_cosmic_distributions(self):
        # Scene 1: Cosmic Distributions
        title_group = VGroup(
            Text("Diffusion Models", gradient=(BLUE, TEAL)),
            Text("Optimal Transport", gradient=(GOLD, ORANGE)),
            Text("Benamou-Brenier Theorem", gradient=(PURPLE, RED)),
            Text("Wasserstein Distance", gradient=(GREEN, YELLOW)),
        ).arrange(DOWN, buff=0.3).scale(0.8)
        
        self.play(
            Write(title_group),
            run_time=3,
            rate_func=smooth
        )
        self.wait(2)
        self.play(FadeOut(title_group))
        
        # Create spiral galaxies with different structures
        self.alpha0_dict = self.create_spiral_galaxy(
            spiral_arms=3, 
            particle_color=BLUE, 
            label=r"\alpha_0", 
            position=LEFT*3,
            arm_tightness=0.4
        )
        self.alpha1_dict = self.create_spiral_galaxy(
            spiral_arms=2, 
            particle_color=GOLD, 
            label=r"\alpha_1", 
            position=RIGHT*3,
            arm_tightness=0.6,
            rotation=PI/3
        )
        
        self.play(
            SpiralIn(self.alpha0_dict["particles"]),
            SpiralIn(self.alpha1_dict["particles"]),
            run_time=4
        )
        self.wait()
        
        # Add distribution labels with arrows
        alpha0_label = MathTex(r"\alpha_0 \text{ (Initial Distribution)}", color=BLUE)
        alpha1_label = MathTex(r"\alpha_1 \text{ (Target Distribution)}", color=GOLD)
        alpha0_label.next_to(self.alpha0_dict["particles"], DOWN)
        alpha1_label.next_to(self.alpha1_dict["particles"], DOWN)
        
        self.play(
            GrowFromCenter(alpha0_label),
            GrowFromCenter(alpha1_label),
            self.alpha0_dict["particles"].animate.set_opacity(0.7),
            self.alpha1_dict["particles"].animate.set_opacity(0.7)
        )
        self.wait(2)
        
    def create_spiral_galaxy(self, spiral_arms=2, particle_color=BLUE, 
                            label="", position=ORIGIN, arm_tightness=0.5,
                            rotation=0):
        galaxy_dict = {}
        galaxy = VGroup()
        n_particles = 1000  # Number of particles in the galaxy
        
        # Spiral parametric equations
        particles = VGroup()
        for i in range(n_particles):
            theta = TAU * np.random.rand()
            r = np.random.exponential(scale=2)
            x = r * np.cos(theta + rotation) + arm_tightness * np.cos(spiral_arms * theta)
            y = r * np.sin(theta + rotation) + arm_tightness * np.sin(spiral_arms * theta)
            particle = Dot(
                point=[x, y, 0],
                color=particle_color,
                radius=0.03 * np.random.normal(loc=1, scale=0.3),
                fill_opacity=0.8 * np.random.rand()
            )
            particles.add(particle)
        
        galaxy_dict["particles"] = particles
        galaxy.add(particles)
        galaxy.move_to(position)
        
        # Add rotating glow effect
        glow = Annulus(
            inner_radius=0.5,
            outer_radius=2,
            color=particle_color,
            fill_opacity=0.2
        ).rotate(rotation)
        galaxy_dict["glow"] = glow
        galaxy.add(glow)
        
        # Add label with custom arrow
        label_tex = MathTex(label, color=particle_color).scale(1.2)
        label_tex.next_to(galaxy, UP)
        arrow = CurvedArrow(
            label_tex.get_bottom(),
            galaxy.get_center(),
            color=particle_color,
            tip_shape=ArrowSquareTip
        )
        galaxy_dict["label"] = label_tex
        galaxy_dict["arrow"] = arrow
        galaxy.add(label_tex, arrow)
        
        return galaxy_dict

    def create_diffusion_bridge(self):
        # Scene 2: Blending Nebula
        t_tracker = ValueTracker(0)
        bridge = always_redraw(lambda: self.generate_bridge(
            self.alpha0_dict["particles"],
            self.alpha1_dict["particles"],
            t_tracker.get_value()
        ))
        
        # Create time indicator with label
        time_indicator = NumberLine(
            x_range=[0, 1, 0.1],
            length=6,
            include_numbers=True
        ).to_edge(DOWN)
        time_label = Text("Time t").next_to(time_indicator, DOWN)
        time_indicator_group = VGroup(time_indicator, time_label)
        
        time_dot = Dot(color=YELLOW).add_updater(
            lambda m: m.move_to(time_indicator.n2p(t_tracker.get_value()))
        )
        
        equation = MathTex(
            r"\alpha_t = ((1 - t)P_0 + tP_1)_{\#} (\alpha_0 \otimes \alpha_1)",
            font_size=36
        ).to_edge(UP)
        
        self.play(
            FadeOut(self.alpha0_dict["glow"]),
            FadeOut(self.alpha1_dict["glow"]),
            LaggedStart(
                FadeTransform(self.alpha0_dict["particles"].copy(), bridge),
                FadeTransform(self.alpha1_dict["particles"].copy(), bridge),
                lag_ratio=0.2
            ),
            run_time=3
        )
        self.add(time_indicator_group, time_dot, equation)
        self.play(
            t_tracker.animate.set_value(1),
            rate_func=linear,
            run_time=8
        )
        self.wait(2)
        
    def generate_bridge(self, source, target, t):
        bridge = VGroup()
        n = len(source)
        noise = 0.05  # Add perceptual randomness
        
        for s_dot, t_dot in zip(source, target):
            # Add Perlin-like noise to movement
            interp_point = interpolate(
                s_dot.get_center() + noise * np.random.randn(3),
                t_dot.get_center() + noise * np.random.randn(3),
                smooth(t)
            )
            color = interpolate_color(
                s_dot.get_color(), 
                t_dot.get_color(), 
                t + 0.1*np.sin(TAU*t)  # Add color oscillation
            )
            
            particle = Dot(
                interp_point,
                color=color,
                radius=s_dot.radius,
                fill_opacity=s_dot.fill_opacity
            )
            bridge.add(particle)
            
        return bridge

    def show_optimal_transport(self):
        # Scene 3: Optimal Transport River
        velocity_field = self.create_velocity_field()
        energy_diagram = self.create_energy_diagram()
        continuity_eq = MathTex(
            r"\text{div}(\alpha_t \nu_t) + \partial_t \alpha_t = 0",
            color=TEAL
        ).to_edge(UR)
        
        self.play(
            Create(velocity_field),
            FadeIn(energy_diagram),
            Write(continuity_eq),
            run_time=3
        )
        self.wait(3)
        
    def create_velocity_field(self):
        # Create dynamic streamlines with varying density
        streamlines = VGroup()
        n_lines = 50
        phase = ValueTracker(0)
        
        for i in range(n_lines):
            line = ParametricFunction(
                lambda t: self.velocity_path(i, phase.get_value(), t),
                t_range=[-PI, PI],
                color=interpolate_color(WHITE, BLUE_E, i/n_lines)
            )
            line.add_updater(lambda m, dt: m.become(
                ParametricFunction(
                    lambda t: self.velocity_path(i, phase.get_value(), t),
                    t_range=[-PI, PI],
                    color=m.color
                )
            ))
            streamlines.add(line)
        
        self.add(streamlines)
        self.play(phase.animate.set_value(TAU), run_time=5, rate_func=linear)
        return streamlines

    def velocity_path(self, seed, phase_val, t):
        np.random.seed(seed)
        return np.array([
            3 * np.cos(t + 0.5 * phase_val) + 0.5 * np.sin(3*t),
            2 * np.sin(t + 0.3 * phase_val) + 0.5 * np.cos(2*t),
            0
        ])
        
    def create_energy_diagram(self):
        # Animated energy minimization display
        axes = Axes(
            x_range=[0, 1],
            y_range=[0, 10, 2],
            axis_config={"color": WHITE}
        ).scale(0.5).to_edge(UL)
        
        labels = VGroup(
            axes.get_x_axis_label("t"),
            axes.get_y_axis_label("Energy")
        )
        
        # Simulated energy minimization curve
        curve = axes.plot(
            lambda x: 8 * np.exp(-3*x) + 0.5 * np.sin(20*x) + 1,
            color=RED
        )
        
        return VGroup(axes, labels, curve)

    def demonstrate_wasserstein(self):
        # Scene 4: Wasserstein Forge
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # Recreate original distributions
        alpha0 = self.alpha0_dict["particles"].copy()
        alpha1 = self.alpha1_dict["particles"].copy()
        grid = NumberPlane(
            x_range=[-5, 5],
            y_range=[-4, 4],
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_width": 1
            }
        )
        
        # Transport map visualization
        transport_eq = MathTex(
            r"W_2^2(\alpha_0, \alpha_1) = \inf_{T_1} \int \|x - T_1(x)\|^2 d\alpha_0(x)",
            font_size=36
        ).to_edge(UP)
        
        # Hammer animation
        hammer = Line(ORIGIN, UP, color=GREY)\
            .add_tip()\
            .rotate(-45*DEGREES)\
            .move_to(UP*3 + RIGHT*2)
        
        # Displacement vectors
        vectors = self.create_displacement_vectors(alpha0, alpha1)
        
        self.play(
            Create(grid),
            FadeIn(alpha0),
            Write(transport_eq)
        )
        self.wait()
        
        # Animate hammer strikes
        for _ in range(3):
            self.play(
                Rotate(hammer, 90*DEGREES, about_point=hammer.get_end()),
                rate_func=there_and_back,
                run_time=0.5
            )
            self.play(
                grid.animate.apply_function(lambda p: self.transport_map(p)),
                alpha0.animate.apply_function(lambda p: self.transport_map(p)),
                vectors.animate.set_opacity(1),
                run_time=2
            )
        
        self.wait(2)
        
    def transport_map(self, point):
        # Custom transport deformation
        x, y, z = point
        return [
            x + 0.5 * np.sin(x/2) * np.cos(y/3),
            y + 0.5 * np.cos(x/3) * np.sin(y/2),
            z
        ]
        
    def create_displacement_vectors(self, source, target):
        vectors = VGroup()
        sample_points = [m.get_center() for m in source[::50]]
        
        for point in sample_points:
            start = point
            end = self.transport_map(point)
            length = np.linalg.norm(end - start)
            color = interpolate_color(
                GREEN, RED, length/3
            )
            vector = Arrow(
                start, end,
                color=color,
                tip_length=0.2,
                stroke_width=2
            )
            vectors.add(vector)
            
        vectors.set_opacity(0)
        return vectors

    def synthesize_benamou_brenier(self):
        # Scene 5: Theorem Synthesis
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # Create combined visualization
        bridge = self.generate_bridge(self.alpha0_dict["particles"], self.alpha1_dict["particles"], 0.5)
        velocity_field = self.create_velocity_field()
        forge = self.demonstrate_wasserstein()
        
        # Theorem text
        theorem_text = VGroup(
            Text("Benamou-Brenier Theorem", font_size=48),
            MathTex(r"W_2^2(\alpha_0, \alpha_1) = \min \int_0^1 \|\nu_t\|_{L^2(\alpha_t)}^2 dt"),
            Text("In the calculus of shapes,\nWasserstein is the sculptor,\nand Benamou-Brenier the chisel...",
                 t2c={"sculptor": BLUE, "chisel": GOLD},
                 font_size=24)
        ).arrange(DOWN, buff=0.5)
        
        self.play(
            FadeIn(bridge),
            Create(velocity_field),
            FadeIn(forge),
            run_time=3
        )
        self.play(
            Write(theorem_text[0]),
            run_time=2
        )
        self.play(
            TransformFromCopy(theorem_text[0], theorem_text[1]),
            run_time=2
        )
        self.play(
            FadeIn(theorem_text[2], shift=UP),
            run_time=2
        )
        self.wait(3)

# Render with: manim -pqh -v WARNING --disable_caching your_file.py CosmicProbabilityScene