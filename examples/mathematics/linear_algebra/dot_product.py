from manim import *
import numpy as np


class DotProductExplained(Scene):
    """Complete dot product animation following project patterns."""

    def construct(self):
        # ========== PART 1: Title ==========
        title = Tex("The Dot Product", font_size=72)
        title_box = SurroundingRectangle(title, color=BLUE, buff=0.3, corner_radius=0.2)
        self.play(DrawBorderThenFill(title_box), Write(title))
        self.wait(1)

        subtitle = Tex("How to multiply vectors", font_size=36, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(subtitle))
        self.wait(1)

        self.play(
            FadeOut(subtitle),
            title.animate.scale(0.5).to_corner(UL),
            title_box.animate.scale(0.5).to_corner(UL)
        )
        self.wait(0.5)

        # ========== PART 2: Show Two Vectors ==========
        # Create coordinate plane
        plane = NumberPlane(
            x_range=[-1, 6, 1],
            y_range=[-1, 5, 1],
            x_length=8,
            y_length=6,
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        ).shift(DOWN * 0.3)

        self.play(FadeIn(plane, run_time=1))

        # Vector a = (4, 2)
        origin = plane.c2p(0, 0)
        vec_a_end = plane.c2p(4, 2)
        vec_a = Arrow(origin, vec_a_end, buff=0, color=RED, stroke_width=6)
        label_a = MathTex(r"\vec{a} = (4, 2)", color=RED, font_size=36)
        label_a.next_to(vec_a.get_end(), RIGHT, buff=0.2)

        # Vector b = (1, 3)
        vec_b_end = plane.c2p(1, 3)
        vec_b = Arrow(origin, vec_b_end, buff=0, color=GREEN, stroke_width=6)
        label_b = MathTex(r"\vec{b} = (1, 3)", color=GREEN, font_size=36)
        label_b.next_to(vec_b.get_end(), LEFT, buff=0.2)

        self.play(GrowArrow(vec_a), Write(label_a), run_time=1)
        self.play(GrowArrow(vec_b), Write(label_b), run_time=1)
        self.wait(1)

        # ========== PART 3: The Formula ==========
        formula_text = Tex("The dot product formula:", font_size=32)
        formula_text.to_edge(DOWN, buff=2)

        formula = MathTex(
            r"\vec{a} \cdot \vec{b} = a_x \cdot b_x + a_y \cdot b_y",
            font_size=44
        )
        formula.next_to(formula_text, DOWN, buff=0.3)

        self.play(Write(formula_text))
        self.play(Write(formula))
        self.wait(1)

        # ========== PART 4: Calculate Step by Step ==========
        calc_group = VGroup()

        step1 = MathTex(
            r"\vec{a} \cdot \vec{b} = (4)(1) + (2)(3)",
            font_size=40
        )
        step1.next_to(formula, DOWN, buff=0.5)

        step2 = MathTex(r"= 4 + 6", font_size=40)
        step2.next_to(step1, DOWN, buff=0.3)

        step3 = MathTex(r"= 10", font_size=48, color=YELLOW)
        step3.next_to(step2, DOWN, buff=0.3)

        self.play(Write(step1))
        self.wait(0.5)
        self.play(Write(step2))
        self.wait(0.5)
        self.play(Write(step3))

        result_box = SurroundingRectangle(step3, color=YELLOW, buff=0.15)
        self.play(Create(result_box))
        self.wait(2)

        # ========== PART 5: Clear and Show Geometric Meaning ==========
        self.play(
            FadeOut(formula_text),
            FadeOut(formula),
            FadeOut(step1),
            FadeOut(step2),
            FadeOut(step3),
            FadeOut(result_box)
        )

        geo_title = Tex("Geometric Interpretation", font_size=36, color=BLUE)
        geo_title.to_edge(DOWN, buff=2.5)
        self.play(Write(geo_title))

        # Show angle between vectors
        angle_arc = Angle(vec_a, vec_b, radius=0.6, color=YELLOW)
        angle_label = MathTex(r"\theta", color=YELLOW, font_size=32)
        angle_label.move_to(plane.c2p(0.8, 0.6))

        self.play(Create(angle_arc), Write(angle_label))
        self.wait(0.5)

        geo_formula = MathTex(
            r"\vec{a} \cdot \vec{b} = |\vec{a}| \, |\vec{b}| \cos\theta",
            font_size=40
        )
        geo_formula.next_to(geo_title, DOWN, buff=0.3)
        self.play(Write(geo_formula))
        self.wait(1)

        # Explanation
        meaning = Tex(
            "Measures how much vectors point in the same direction",
            font_size=28,
            color=GRAY
        )
        meaning.next_to(geo_formula, DOWN, buff=0.3)
        self.play(FadeIn(meaning))
        self.wait(2)

        # ========== PART 6: Show Projection ==========
        self.play(FadeOut(meaning), FadeOut(geo_title), FadeOut(geo_formula))

        proj_title = Tex("Projection Interpretation", font_size=36, color=BLUE)
        proj_title.to_edge(DOWN, buff=2.5)
        self.play(Write(proj_title))

        # Calculate projection of b onto a
        a_vec = np.array([4, 2])
        b_vec = np.array([1, 3])
        proj_scalar = np.dot(b_vec, a_vec) / np.dot(a_vec, a_vec)
        proj_point = proj_scalar * a_vec

        proj_end = plane.c2p(proj_point[0], proj_point[1])

        # Dashed line from b to projection
        dashed = DashedLine(vec_b_end, proj_end, color=BLUE, stroke_width=2)

        # Projection arrow
        proj_arrow = Arrow(origin, proj_end, buff=0, color=BLUE, stroke_width=5)
        proj_label = MathTex(r"\text{proj}_{\vec{a}} \vec{b}", color=BLUE, font_size=28)
        proj_label.next_to(proj_arrow.get_center(), DOWN, buff=0.3)

        self.play(Create(dashed))
        self.play(GrowArrow(proj_arrow), Write(proj_label))

        # Right angle marker
        right_angle = RightAngle(
            Line(origin, proj_end),
            Line(proj_end, vec_b_end),
            length=0.2,
            color=WHITE
        )
        self.play(Create(right_angle))
        self.wait(2)

        # ========== PART 7: Key Insight - Perpendicular ==========
        self.play(
            FadeOut(dashed),
            FadeOut(proj_arrow),
            FadeOut(proj_label),
            FadeOut(right_angle),
            FadeOut(angle_arc),
            FadeOut(angle_label),
            FadeOut(proj_title)
        )

        perp_title = Tex("Special Case: Perpendicular Vectors", font_size=36, color=GREEN)
        perp_title.to_edge(DOWN, buff=2.5)
        self.play(Write(perp_title))

        # Create new perpendicular vectors
        self.play(FadeOut(vec_a), FadeOut(vec_b), FadeOut(label_a), FadeOut(label_b))

        # New vectors that are perpendicular
        vec_p_end = plane.c2p(3, 1)
        vec_q_end = plane.c2p(-1, 3)

        vec_p = Arrow(origin, vec_p_end, buff=0, color=RED, stroke_width=6)
        vec_q = Arrow(origin, vec_q_end, buff=0, color=GREEN, stroke_width=6)

        label_p = MathTex(r"\vec{p} = (3, 1)", color=RED, font_size=32)
        label_p.next_to(vec_p.get_end(), RIGHT, buff=0.2)

        label_q = MathTex(r"\vec{q} = (-1, 3)", color=GREEN, font_size=32)
        label_q.next_to(vec_q.get_end(), LEFT, buff=0.2)

        self.play(GrowArrow(vec_p), Write(label_p))
        self.play(GrowArrow(vec_q), Write(label_q))

        # Show right angle
        perp_angle = RightAngle(vec_p, vec_q, length=0.3, color=YELLOW)
        self.play(Create(perp_angle))

        # Calculate: (3)(-1) + (1)(3) = -3 + 3 = 0
        perp_calc = MathTex(
            r"\vec{p} \cdot \vec{q} = (3)(-1) + (1)(3) = -3 + 3 = 0",
            font_size=36
        )
        perp_calc.next_to(perp_title, DOWN, buff=0.3)
        self.play(Write(perp_calc))

        conclusion = Tex(
            "Perpendicular vectors have dot product = 0",
            font_size=32,
            color=YELLOW
        )
        conclusion.next_to(perp_calc, DOWN, buff=0.3)
        conclusion_box = SurroundingRectangle(conclusion, color=YELLOW, buff=0.15)

        self.play(Write(conclusion), Create(conclusion_box))
        self.wait(2)

        # ========== PART 8: Summary ==========
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob != title and mob != title_box])

        summary_title = Tex("Summary: The Dot Product", font_size=48, color=BLUE)
        summary_title.to_edge(UP, buff=1)

        self.play(
            FadeOut(title),
            FadeOut(title_box),
            Write(summary_title)
        )

        points = VGroup(
            Tex(r"1. Algebraic: $\vec{a} \cdot \vec{b} = a_x b_x + a_y b_y$", font_size=32),
            Tex(r"2. Geometric: $\vec{a} \cdot \vec{b} = |\vec{a}||\vec{b}|\cos\theta$", font_size=32),
            Tex(r"3. Result is a scalar (number), not a vector", font_size=32),
            Tex(r"4. If dot product = 0, vectors are perpendicular", font_size=32),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        points.next_to(summary_title, DOWN, buff=0.8)

        for point in points:
            self.play(Write(point), run_time=0.8)
            self.wait(0.3)

        final_box = SurroundingRectangle(points, color=BLUE, buff=0.3)
        self.play(Create(final_box))
        self.wait(3)
