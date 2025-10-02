from manim import *
import numpy as np
import random

config.background_color = "#1a1a1a"
config.frame_rate = 60

class BrownToEinstein(ThreeDScene):
    def construct(self):
        # Scene 1: Brownian Motion Introduction
        self.set_camera_orientation(phi=0, theta=0)
        
        # Create pollen particle swarm
        particles = VGroup(*[Dot(color=interpolate_color(BLUE_E, GREEN_E, random.random()), 
                                radius=0.08) for _ in range(20)])
        paths = VGroup(*[VMobject() for _ in particles])
        for p, path in zip(particles, paths):
            path.set_points_as_corners([p.get_center(), p.get_center()])  # Initialize with two identical points
            path.set_color(p.get_color())
        
        # Brownian motion path updater
        def update_path(path):
            points = path.points
            if len(points) > 0:
                new_point = points[-1] + np.random.normal(0, 0.1, 3)
                path.add_points_as_corners([new_point])
        
        # Animated Brownian motion
        self.play(LaggedStart(*[Create(p) for p in particles], lag_ratio=0.1))
        self.add(*paths)
        particles.save_state()
        self.play(
            particles.animate.shift(UR * 0.5).set_opacity(0.8),
            UpdateFromFunc(paths, lambda m: m.set_stroke(width=1.5)),
            run_time=4,
            rate_func=linear
        )
        for _ in range(30):
            self.play(
                *[p.animate.shift(np.random.normal(0, 0.15, 3)) for p in particles],
                *[UpdateFromFunc(path, update_path) for path in paths],
                run_time=0.5
            )
        
        # Scene 2: Transition to Einstein's Equation
        heat_eq = MathTex(
            r"\frac{\partial \rho}{\partial t} ", r"= ", r"D", r"\nabla^2 \rho"
        ).scale(1.5)
        heat_eq[0].set_color(YELLOW)  # partial rho/partial t
        heat_eq[2].set_color(ORANGE)  # D
        heat_eq[3].set_color(BLUE)    # nabla^2 rho
        
        msd_eq = MathTex(
            r"\langle x^2(t) \rangle ", r"= ", r"2D", r"t"
        ).next_to(heat_eq, DOWN, buff=1)
        msd_eq[0].set_color(GREEN)   # <x^2(t)>
        msd_eq[2].set_color(ORANGE)  # 2D
        msd_eq[3].set_color(WHITE)   # t
        
        # Transform particles to equation elements
        self.play(
            particles.animate.set_opacity(0.2).set_height(0.3),
            paths.animate.set_stroke(width=0.5, opacity=0.3),
            run_time=2
        )
        # Move camera separately
        self.set_camera_orientation(frame_center=ORIGIN)
        
        equation_group = VGroup(heat_eq, msd_eq)
        self.play(
            TransformFromCopy(particles[:3], heat_eq[0]),  # Transform particles to partial rho/partial t
            TransformFromCopy(particles[3:6], heat_eq[2]),  # Transform to D
            Write(heat_eq),
            run_time=3
        )
        
        # Scene 3: Heat Equation Visualization
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 2, 0.5],
            axis_config={"color": BLUE_D},
            x_axis_config={"numbers_to_include": np.arange(0, 6, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 2.5, 0.5)}
        ).shift(DOWN)
        
        D = ValueTracker(0.1)
        
        def gaussian(x, t):
            # Add small epsilon to prevent division by zero
            t = max(t, 1e-6)
            return np.exp(-x**2/(4*D.get_value()*t))/np.sqrt(4*np.pi*D.get_value()*t)
        
        graph = always_redraw(lambda: axes.plot(
            lambda x: gaussian(x, 1.0), color=YELLOW, stroke_width=3
        ))
        
        self.play(
            FadeIn(axes),
            FadeOut(particles),
            FadeOut(paths),
            heat_eq.animate.to_edge(UP),
            run_time=2
        )
        self.add(graph)
        self.play(
            D.animate.set_value(0.5),
            run_time=4,
            rate_func=there_and_back
        )
        
        # Scene 4: MSD Visualization
        msd_axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 5, 1],
            axis_config={"color": GREEN_D}
        ).shift(DOWN)
        
        # Add labels separately
        x_label = MathTex("t").next_to(msd_axes.x_axis, RIGHT)
        y_label = MathTex(r"\langle x^2 \rangle").next_to(msd_axes.y_axis, UP)
        msd_axes_group = VGroup(msd_axes, x_label, y_label)
        
        line = msd_axes.plot(lambda x: 2*0.3*x, color=ORANGE)
        dot = Dot(color=RED).move_to(msd_axes.c2p(0,0))
        
        # First create and show the new axes
        self.play(
            FadeOut(graph),
            ReplacementTransform(axes, msd_axes),
            Write(x_label),
            Write(y_label),
            run_time=2
        )
        
        # Then add the line and equation
        self.play(
            Create(line),
            FadeTransform(heat_eq, msd_eq),
            run_time=2
        )
        
        # Add and animate the dot
        self.play(Create(dot))
        self.play(
            MoveAlongPath(dot, line),
            run_time=3,
            rate_func=linear
        )
        
        # Final synthesis
        final_group = VGroup(msd_axes_group, line, dot, msd_eq)
        restored_particles = particles.copy().restore().shift(RIGHT*3)
        
        # First move camera
        self.move_camera(phi=30*DEGREES, theta=45*DEGREES)
        # Then do the other animations
        self.play(
            final_group.animate.shift(LEFT*3),
            FadeIn(restored_particles),
            run_time=4
        )
        self.wait(2)