from manim import *

class GaleShapleyVisualization(Scene):
    def construct(self):
        # Initialize sets, formulas, and animations
        self.camera.background_color = "#1e1e1e"
        
        # 1. Bipartite Graphs
        colleges = VGroup(*[Circle(radius=0.2, fill_color=BLUE, fill_opacity=1).shift(LEFT*3 + UP*i) for i in range(-2, 3)])
        applicants = VGroup(*[Circle(radius=0.2, fill_color=GREEN, fill_opacity=1).shift(RIGHT*3 + UP*i) for i in range(-2, 3)])
        
        bipartite_formula = MathTex(r"C = \{c_1, c_2, \dots, c_m\},\ A = \{a_1, a_2, \dots, a_n\}", r"E \subseteq C \times A").arrange(DOWN)
        
        self.play(
            LaggedStart(
                *[Create(col) for col in colleges] + [Create(app) for app in applicants],
                lag_ratio=0.2
            )
        )
        self.play(Write(bipartite_formula))
        self.wait(1)
        self.play(FadeOut(bipartite_formula))
        
        # 2. Preference Orderings
        pref_applicant = MathTex(r"a_k: c_{\sigma(1)} \succ c_{\sigma(2)} \succ \dots \succ c_{\sigma(m)}").next_to(applicants[2], RIGHT)
        pref_college = MathTex(r"c_i: a_{\tau(1)} \succ a_{\tau(2)} \succ \dots \succ a_{\tau(n)}").next_to(colleges[2], LEFT)
        
        self.play(
            TransformFromCopy(colleges[2], pref_college),
            TransformFromCopy(applicants[2], pref_applicant),
            run_time=2
        )
        self.wait(1)
        
        # 3. Combinatorics Grid
        grid = NumberPlane(x_range=[0,5], y_range=[0,5]).scale(0.4).shift(DOWN)
        self.play(Create(grid))
        crosses = VGroup(*[Cross(scale_factor=0.3).move_to(grid.c2p(i, j)).set_color(RED) for i, j in [(i,j) for i in range(5) for j in range(5) if (i+j)%2 != 0]])
        self.play(LaggedStart(*[Create(cross) for cross in crosses], lag_ratio=0.05))
        self.wait(1)
        self.play(FadeOut(grid), FadeOut(crosses))
        
        # 4. Stability Condition
        blocking_formula = MathTex(r"\nexists (a, c): a \text{ prefers } c \succ c' \land c \text{ prefers } a \succ a'").scale(0.8)
        self.play(Write(blocking_formula))
        self.play(blocking_formula.animate.set_color(GREEN).scale(1.2), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(blocking_formula))
        
        # 5. Algorithm Steps
        algo_steps = VGroup(
            Tex(r"While there exists an unfilled college $c$:"),
            Tex(r"1. $c$ proposes to highest-ranked unmatched $a$"),
            Tex(r"2. If $a$ prefers $c$ to current match:"),
            Tex(r"3. \quad Accept $c$ (reject previous if needed)")
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.7).to_edge(LEFT)
        
        self.play(Write(algo_steps))
        
        arrow = Arrow(colleges[1].get_right(), applicants[1].get_left(), color=YELLOW)
        check = Tex(r"\checkmark", color=GREEN).next_to(applicants[1], UP)
        
        self.play(GrowArrow(arrow), run_time=1)
        self.play(FadeIn(check))
        self.wait(1)
        self.play(FadeOut(arrow), FadeOut(check))
        
        # 6. Quotas
        quota_text = MathTex(r"\forall c \in C,\, |M(c)| \leq q_c").to_edge(DOWN)
        counters = [Tex(f"0/3").next_to(col, DOWN) for col in colleges]
        self.play(Write(quota_text), *[Write(c) for c in counters])
        for i in range(3):  # Simulate filling quotas
            self.play(counters[i].animate.become(Tex(f"{i+1}/3", color=GOLD).next_to(colleges[i], DOWN)))
        self.wait(2)
        
        # Finalize
        self.play(*[FadeOut(mob) for mob in self.mobjects])
