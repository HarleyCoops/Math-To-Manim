from manim import *
import numpy as np

class DiffusionOptimalTransport(Scene):
    def construct(self):
        self.setup_particles()
        self.animate_diffusion()
        self.show_velocity_field()
        self.show_continuity_equation()
        self.show_wasserstein()
        self.final_scene()

    def setup_particles(self):
        np.random.seed(42)
        num_particles = 50
        
        # Initialize particle positions
        alpha0_pos = np.column_stack([
            np.random.normal(-3, 0.7, num_particles),
            np.random.normal(0, 1, num_particles)
        ])
        alpha1_pos = np.column_stack([
            np.random.normal(3, 0.7, num_particles),
            np.random.normal(0, 1, num_particles)
        ])

        # Sort for ordered pairing
        alpha0_pos = alpha0_pos[alpha0_pos[:, 0].argsort()]
        alpha1_pos = alpha1_pos[alpha1_pos[:, 0].argsort()]

        # Create particle mobjects - convert NumPy points to Manim points by adding z-coordinate
        self.alpha0 = VGroup(*[
            Dot(point=np.array([x, y, 0]), color=BLUE, radius=0.08) 
            for x, y in alpha0_pos
        ])
        self.alpha1 = VGroup(*[
            Dot(point=np.array([x, y, 0]), color=GOLD, radius=0.08) 
            for x, y in alpha1_pos
        ])

        self.play(
            LaggedStart(
                *[FadeIn(p) for p in self.alpha0],
                *[FadeIn(p) for p in self.alpha1],
                lag_ratio=0.1
            ),
            run_time=2
        )
        self.wait()

    def animate_diffusion(self):
        self.tracker = ValueTracker(0)
        equation = MathTex(
            r"\alpha_t = ((1 - t)P_0 + tP_1)_\# (\alpha_0 \otimes \alpha_1)",
            font_size=36
        ).to_edge(UP)

        # Create interpolated particles
        self.alpha_t = VGroup()
        for p0, p1 in zip(self.alpha0, self.alpha1):
            particle = p0.copy()
            particle.add_updater(lambda m: m.move_to(
                interpolate(p0.get_center(), p1.get_center(), self.tracker.get_value())
            ).set_color(interpolate_color(
                BLUE, GOLD, self.tracker.get_value()
            )))
            self.alpha_t.add(particle)

        self.play(Write(equation))
        self.add(self.alpha_t)
        self.play(self.tracker.animate.set_value(1), run_time=3)
        self.wait()
        self.play(FadeOut(equation))

    def show_velocity_field(self):
        arrows = VGroup()
        for p0, p1 in zip(self.alpha0, self.alpha1):
            # Get the vector between positions using get_center()
            start_pos = p0.get_center()
            end_pos = p1.get_center()
            direction = end_pos - start_pos  # Now we're subtracting numpy arrays, not Dots
            
            arrow = Arrow(
                start=start_pos,
                end=start_pos + direction * 0.5,  # Scale the direction vector
                buff=0,
                color=WHITE,
                max_tip_length=0.1
            )
            arrow.add_updater(lambda a, p0=p0, p1=p1: a.put_start_and_end_on(
                interpolate(p0.get_center(), p1.get_center(), self.tracker.get_value()),
                interpolate(p0.get_center(), p1.get_center(), self.tracker.get_value()) 
                + (p1.get_center() - p0.get_center()) * 0.5
            ))
            arrows.add(arrow)

        equation = MathTex(
            r"\min_{\nu_t} \int \|\nu_t\|_{L^2(\alpha_t)}^2 dt",
            r"\text{div}(\alpha_t \nu_t) + \partial_t \alpha_t = 0",
            font_size=36
        ).arrange(DOWN).to_edge(UP)

        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1))
        self.play(Write(equation))
        self.wait(2)
        self.play(FadeOut(arrows), FadeOut(equation))

    def show_continuity_equation(self):
        grid = NumberPlane(
            x_range=[-5,5,1], y_range=[-3,3,1],
            background_line_style={"stroke_opacity":0.3}
        )

        def deform_grid(mob, alpha):
            for line in mob.get_lines():
                new_points = []
                for x, y, _ in line.get_points():
                    dx = 0.5 * np.sin(x/2 + alpha*PI) * (1 - abs(x)/5)
                    dy = 0.5 * np.cos(y/2 + alpha*PI) * (1 - abs(y)/3)
                    new_points.append([x + dx, y + dy, 0])
                line.set_points(new_points)

        equation = MathTex(
            r"\text{div}(\alpha_t \nu_t) + \partial_t \alpha_t = 0",
            font_size=36
        ).to_edge(UP)

        self.play(Create(grid), Write(equation))
        self.play(UpdateFromAlphaFunc(grid, deform_grid), run_time=3)
        self.wait()
        self.play(FadeOut(grid), FadeOut(equation))

    def show_wasserstein(self):
        equation = MathTex(
            r"W_2^2(\alpha_0, \alpha_1) = \inf_{T_1} \int \|x - T_1(x)\|^2 d\alpha_0(x)",
            font_size=36
        ).to_edge(UP)
        
        # Create transport map visualization
        grid = NumberPlane(x_range=[-5,5,1], y_range=[-3,3,1])
        grid.prepare_for_nonlinear_transform()
        grid.apply_function(lambda p: [
            p[0] + 0.5*(p[0]+3)*(1 if p[0]>-3 else 0),
            p[1] + 0.3*np.sin(p[0]),
            0
        ])

        self.play(Write(equation))
        self.play(Create(grid), run_time=2)
        self.wait(2)
        self.play(FadeOut(grid), FadeOut(equation))

    def final_scene(self):
        final_eq = MathTex(
            r"W_2^2(\alpha_0, \alpha_1) = \inf \int_0^1 \|\nu_t\|_{L^2(\alpha_t)}^2 dt",
            font_size=36
        ).to_edge(UP)

        self.play(
            self.alpha0.animate.set_opacity(0.3),
            self.alpha1.animate.set_opacity(0.3),
            self.alpha_t.animate.set_opacity(0.7)
        )
        self.play(Write(final_eq))
        self.wait(3)