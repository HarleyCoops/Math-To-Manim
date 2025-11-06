from manim import *

class MinkowskiSpacetime(Scene):
    def construct(self):
        # Scene 1: Introduction to Newtonian Mechanics
        self.play(Write(Title("Newtonian Mechanics", color=WHITE).to_edge(UP)), 
                  Pendulum().animate(pendulum.swing), 
                  run_time=3)
        self.wait(1)

        # Scene 2: Maxwell's Equations
        maxwell_eq = [
            Tex(r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}"),
            Tex(r"\nabla \cdot \mathbf{B} = 0"),
            Tex(r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}"),
            Tex(r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}")
        ]
        for eq in maxwell_eq:
            self.play(Write(eq), run_time=1.5)
            self.wait(1)
        self.wait(3)

        # Scene 3: Speed of Light
        light_beam = Line(LEFT, RIGHT).set_color(WHITE)
        self.play(Create(light_beam), 
                  Write(Tex(r"c = \sqrt{1/(\mu_0 \epsilon_0)}").next_to(light_beam, RIGHT)), 
                  run_time=3)
        self.wait(1)

        # Scene 4: Special Relativity
        einstein = Circle(color=BLUE).move_to(UP)
        train1 = Line(LEFT, RIGHT).set_color(RED).next_to(einstein, LEFT)
        train2 = Line(LEFT, RIGHT).set_color(GREEN).next_to(einstein, RIGHT)
        self.play(Create(train1), 
                  Create(train2), 
                  Write(ThoughtBubble("Einstein's Special Relativity").next_to(einstein, UP)), 
                  run_time=6)
        self.wait(2)

        # Scene 5: Lorentz Transformations
        spacetime_grid = NumberPlane()
        lorentz_transform = spacetime_grid.copy()
        self.play(Create(spacetime_grid), 
                  Transform(spacetime_grid, lorentz_transform), 
                  run_time=9)
        self.wait(2)

        # Scene 6: Four-Vector
        four_vector = Arrow(LEFT, RIGHT).set_color(YELLOW)
        self.play(Create(four_vector), 
                  run_time=3)
        self.wait(1)

        # Scene 7: Minkowski Spacetime
        spacetime_3d = Cube()
        time_axis = Line(DOWN, UP).set_color(WHITE).next_to(spacetime_3d, UP)
        self.play(Create(spacetime_3d), 
                  Create(time_axis), 
                  run_time=9)
        self.wait(2)

        # Scene 8: Spacetime Interval
        interval_calculate = Tex(r"ds^2 = c^2dt^2 - dx^2 - dy^2 - dz^2").set_color(WHITE)
        self.play(Create(interval_calculate), 
                  run_time=3)
        self.wait(1)

        # Scene 9: Four-Dimensional Vectors
        vector_3d = Arrow(LEFT, RIGHT).set_color(RED)
        vector_4d = Arrow(LEFT, RIGHT).set_color(GREEN)
        self.play(Create(vector_3d).next_to(vector_4d, LEFT), 
                  Create(vector_4d), 
                  run_time=6)
        self.wait(2)

        # Scene 10: Conclusion
        final_spacetime = Cube()
        self.play(Create(final_spacetime), 
                  Write(Tex(r"ds^2 = c^2dt^2 - dx^2 - dy^2 - dz^2").next_to(final_spacetime, RIGHT)), 
                  run_time=3)
        self.wait(1)