from manim import *

class EnhancedPythagorean(Scene):
    def construct(self):
        # Title animation with background
        title = Tex("The Pythagorean Theorem", font_size=48)
        title_box = SurroundingRectangle(title, color=BLUE, buff=0.3, corner_radius=0.2)
        self.play(DrawBorderThenFill(title_box), Write(title))
        self.wait(0.5)
        self.play(title.animate.set_color(YELLOW), title_box.animate.set_color(GREEN))
        self.wait(1)

        # Create coordinate system
        grid = NumberPlane(x_range=[-7, 7], y_range=[-5, 5], background_line_style={
            "stroke_color": TEAL,
            "stroke_width": 2,
            "stroke_opacity": 0.3
        })
        self.play(FadeIn(grid, run_time=1, lag_ratio=0.1))
        self.wait(0.5)

        # Right triangle construction
        A = [-3, 0, 0]
        B = [1, 0, 0]
        C = [-3, 3, 0]
        triangle = Polygon(A, B, C, color=BLUE, fill_opacity=0.3)
        
        # Animate triangle drawing with labels
        self.play(
            Create(triangle),
            title.animate.scale(0.7).to_corner(UL),
            title_box.animate.scale(0.7).to_corner(UL)
        )
        a_label = MathTex("a", color=RED).next_to(Line(A, C), LEFT, buff=0.15)
        b_label = MathTex("b", color=GREEN).next_to(Line(A, B), DOWN, buff=0.15)
        c_label = MathTex("c", color=YELLOW).next_to(Line(B, C), UR, buff=0.15)
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(0.5)

        # Create squares on each side with proper geometric positioning
        square_a = Square(side_length=3, color=RED, fill_opacity=0.2).shift(LEFT*6 + DOWN*1.5)
        square_a_label = MathTex("a^2", color=WHITE).move_to(square_a)
        
        square_b = Square(side_length=4, color=GREEN, fill_opacity=0.2).shift(RIGHT*1 + DOWN*4)
        square_b_label = MathTex("b^2", color=WHITE).move_to(square_b)
        
        # Calculate hypotenuse square position using rotation
        hypotenuse = Line(B, C)
        square_c = Square(side_length=5, color=YELLOW, fill_opacity=0.2)
        square_c.rotate(hypotenuse.get_angle()).next_to(hypotenuse, OUT, buff=0)
        square_c_label = MathTex("c^2", color=WHITE).move_to(square_c)

        # Animate squares appearing with transformation effects
        self.play(
            triangle.animate.set_fill(BLUE, 0.8),
            LaggedStart(
                TransformFromCopy(Line(A, C), square_a),
                TransformFromCopy(Line(A, B), square_b),
                TransformFromCopy(hypotenuse, square_c),
                lag_ratio=0.3
            ),
            run_time=2
        )
        self.play(Write(square_a_label), Write(square_b_label), Write(square_c_label))
        self.wait(1)

        # Area calculation animation
        area_equation = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=72)
        area_equation.set_color_by_tex("a^2", RED)
        area_equation.set_color_by_tex("b^2", GREEN)
        area_equation.set_color_by_tex("c^2", YELLOW)
        area_equation.to_edge(DOWN).shift(UP*0.5)
        
        self.play(
            square_a.animate.scale(1.2),
            square_a_label.animate.scale(1.2),
            run_time=0.5
        )
        self.play(
            square_b.animate.scale(1.2),
            square_b_label.animate.scale(1.2),
            run_time=0.5
        )
        self.play(
            square_c.animate.scale(1.2),
            square_c_label.animate.scale(1.2),
            run_time=0.5
        )
        self.play(
            LaggedStart(
                ReplacementTransform(square_a_label.copy(), area_equation[0]),
                Write(area_equation[1]),
                ReplacementTransform(square_b_label.copy(), area_equation[2]),
                Write(area_equation[3]),
                ReplacementTransform(square_c_label.copy(), area_equation[4]),
                lag_ratio=0.3
            ),
            run_time=2
        )
        self.wait(1)

        # Visual proof animation
        area_box = SurroundingRectangle(area_equation, color=BLUE, buff=0.3)
        self.play(Create(area_box))
        self.play(
            area_equation.animate.set_color(WHITE),
            area_box.animate.set_stroke(width=3),
            Flash(area_box, color=BLUE, line_length=0.3)
        )
        self.wait(2)

        # Cleanup and final emphasis
        self.play(
            FadeOut(Group(grid, triangle, square_a, square_b, square_c,
                          a_label, b_label, c_label,
                          square_a_label, square_b_label, square_c_label)),
            title.animate.move_to(ORIGIN).scale(2),
            title_box.animate.move_to(ORIGIN).scale(2),
            area_equation.animate.scale(1.5).move_to(ORIGIN).shift(DOWN*2),
            area_box.animate.scale(1.5).move_to(ORIGIN).shift(DOWN*2)
        )
        self.play(
            Flash(title, line_length=0.5, num_lines=30, color=BLUE),
            Flash(area_equation, line_length=0.4, num_lines=20, color=YELLOW)
        )
        self.wait(2)