from manim import *
import numpy as np


class MOEHyperparameterScaling(Scene):
    """Artistic exploration of MoE loss scaling between total and active parameters."""

    def construct(self):
        self.camera.background_color = "#0f172a"

        self.next_section("Question framing")
        opening = self.show_opening_question()
        self.fade_out_scene(opening)

        self.next_section("MoE routing intuition")
        routing = self.show_moe_routing()
        self.fade_out_scene(routing)

        self.next_section("Token budget tradeoff")
        tradeoff = self.token_budget_tradeoff()
        self.fade_out_scene(tradeoff)

        self.next_section("Scaling landscapes")
        landscapes = self.stepfun_landscapes()
        self.fade_out_scene(landscapes)

        self.next_section("Ant group findings")
        ant_group = self.ant_group_heatmap()
        self.fade_out_scene(ant_group)

        self.next_section("Loss function equation")
        equation_scene = self.present_loss_equation()
        self.fade_out_scene(equation_scene)

        self.next_section("Loss cross sections")
        cross_sections = self.animate_loss_cross_sections()
        self.fade_out_scene(cross_sections)

        self.next_section("Synthesis")
        self.closing_synthesis()

    def fade_out_scene(self, group: VGroup | Mobject):
        if group is None:
            return
        mob_group = group if isinstance(group, Mobject) else VGroup(*group)
        if len(mob_group) == 0:
            return
        self.play(FadeOut(mob_group, shift=DOWN * 0.4), run_time=0.8)
        self.wait(0.2)

    def show_opening_question(self):
        title = Text(
            "Mixture-of-Experts Scaling Intuition",
            font_size=58,
            weight=BOLD,
            gradient=(BLUE_B, PURPLE_B),
        )
        subtitle = Text(
            "How many tokens should each parameter really see?",
            font_size=36,
            t2c={"tokens": YELLOW, "parameter": ORANGE},
        )
        framing = Text(
            "Total parameters  vs  Active parameters  vs  Both?",
            font_size=30,
            t2c={"Total": BLUE, "Active": GREEN, "Both": GOLD},
        )
        question_group = VGroup(title, subtitle, framing).arrange(DOWN, buff=0.4)
        question_group.to_edge(UP)

        glow = Circle(radius=3.5, color=BLUE_E).set_z_index(-2)
        glow.set_fill(color=BLUE_E, opacity=0.25)
        glow.shift(LEFT * 4 + UP * 0.5)

        ribbon = Line(LEFT * 6, RIGHT * 6, stroke_width=6, color=BLUE_E).set_z_index(-1)
        ribbon.shift(DOWN * 3)

        prompt = Paragraph(
            "Sparsity promises efficiency, but scaling laws emerge from data.",
            "Where should we anchor our intuition when estimators disagree?",
            alignment="left",
            font_size=26,
        ).next_to(ribbon, UP, buff=0.6)

        self.play(FadeIn(glow, scale=1.3), Create(ribbon))
        self.play(Write(title), run_time=1.6)
        self.play(LaggedStart(FadeIn(subtitle, shift=DOWN * 0.3), FadeIn(framing)), run_time=1.6)
        self.wait(0.8)
        self.play(Write(prompt))
        self.wait(1.2)

        return VGroup(question_group, glow, ribbon, prompt)

    def show_moe_routing(self):
        router = RoundedRectangle(
            width=2.4, height=1.4, corner_radius=0.3, color=BLUE_B
        ).shift(LEFT * 2.5)
        router_label = Text("Router", font_size=28).move_to(router)

        experts = VGroup(
            *[
                RoundedRectangle(
                    width=2.7,
                    height=1.2,
                    corner_radius=0.25,
                    color=GREEN_B,
                )
                for _ in range(4)
            ]
        ).arrange(DOWN, buff=0.35).shift(RIGHT * 2.8)
        expert_labels = VGroup(
            *[
                Text(f"Expert {i+1}", font_size=24, color=WHITE).move_to(box)
                for i, box in enumerate(experts)
            ]
        )

        token_stream = VGroup(
            *[
                Circle(radius=0.16, color=YELLOW, fill_opacity=0.85)
                .shift(LEFT * 5 + UP * (i - 2) * 0.7)
                for i in range(5)
            ]
        )
        token_label = Text("Incoming tokens", font_size=22, color=GRAY_B).next_to(
            token_stream, LEFT, buff=0.4
        )

        ingress_arrows = VGroup(
            *[
                Arrow(
                    start=token.get_right(),
                    end=router.get_left(),
                    buff=0.1,
                    stroke_width=3,
                    color=YELLOW,
                )
                for token in token_stream
            ]
        )
        egress_arrows = VGroup(
            *[
                Arrow(
                    start=router.get_right(),
                    end=expert.get_left(),
                    buff=0.1,
                    stroke_width=3,
                    color=BLUE,
                )
                for expert in experts
            ]
        )

        capacity_text = Text(
            "Capacity = total parameters of all experts (B)",
            font_size=26,
            t2c={"total parameters": BLUE_B, "B": BLUE_B},
        ).to_edge(DOWN)
        active_text = Text(
            "Active parameters per token = those experts actually used",
            font_size=26,
            t2c={"Active parameters": GREEN_B},
        ).next_to(capacity_text, UP, buff=0.3)

        self.play(LaggedStart(*[FadeIn(token) for token in token_stream], lag_ratio=0.2))
        self.play(FadeIn(token_label, shift=LEFT * 0.2))
        self.play(Create(router), FadeIn(router_label))
        self.play(LaggedStart(*[GrowArrow(arr) for arr in ingress_arrows], lag_ratio=0.1))
        self.play(LaggedStart(*[GrowArrow(arr) for arr in egress_arrows], lag_ratio=0.1))
        self.play(LaggedStart(*[Create(box) for box in experts], lag_ratio=0.15), FadeIn(expert_labels))
        self.wait(0.6)
        self.play(Write(active_text), Write(capacity_text))
        self.wait(1.2)

        return VGroup(
            token_stream,
            token_label,
            router,
            router_label,
            ingress_arrows,
            egress_arrows,
            experts,
            expert_labels,
            active_text,
            capacity_text,
        )

    def token_budget_tradeoff(self):
        axes = Axes(
            x_range=[1, 9, 1],
            y_range=[0, 640, 80],
            x_length=5.4,
            y_length=3.2,
            axis_config={"color": GRAY_B},
        ).shift(LEFT * 3.5 + DOWN * 0.5)
        labels = axes.get_axis_labels(
            Tex("Number of experts", color=WHITE),
            Tex("Tokens per expert", color=WHITE),
        )

        total_tokens = 512
        graph = axes.plot(
            lambda x: total_tokens / x,
            color=YELLOW,
            x_range=[1.2, 8.5],
        )
        graph.set_stroke(width=6)

        curve_glow = graph.copy().set_stroke(color=TEAL_E, width=14, opacity=0.15)

        highlight_point = Dot(color=ORANGE).move_to(axes.c2p(4, total_tokens / 4))
        highlight_label = Text(
            "Sparser routing ↓ tokens per expert",
            font_size=26,
            color=ORANGE,
        ).next_to(highlight_point, UP, buff=0.5)

        density_meter = VGroup(
            Rectangle(width=0.5, height=3.2, stroke_color=GRAY_B, fill_color=BLUE_D, fill_opacity=0.35),
            Rectangle(width=0.5, height=2.1, stroke_color=GRAY_B, fill_color=GREEN_D, fill_opacity=0.55),
            Rectangle(width=0.5, height=0.9, stroke_color=GRAY_B, fill_color=YELLOW_E, fill_opacity=0.65),
        ).arrange(RIGHT, buff=0.15)
        density_meter.next_to(axes, RIGHT, buff=1.1)

        density_labels = VGroup(
            Text("Total parameters", font_size=22, color=BLUE_C),
            Text("Active parameters", font_size=22, color=GREEN_C),
            Text("Tokens per expert", font_size=22, color=YELLOW_C),
        ).arrange(DOWN, buff=0.25).next_to(density_meter, RIGHT, buff=0.3)

        brace = Brace(density_meter, RIGHT, color=WHITE)
        brace_label = (
            brace.get_text("Balancing the three scales matters")
            .set_color(PURPLE_B)
            .scale(0.6)
        )

        self.play(Create(axes), FadeIn(labels))
        self.play(FadeIn(curve_glow), Create(graph))
        self.play(GrowFromCenter(highlight_point), FadeIn(highlight_label, shift=UP * 0.2))
        self.wait(0.6)
        self.play(
            FadeIn(density_meter, scale=0.8),
            LaggedStart(*[FadeIn(lbl, shift=RIGHT * 0.2) for lbl in density_labels], lag_ratio=0.15),
        )
        self.play(GrowFromCenter(brace), FadeIn(brace_label, shift=RIGHT * 0.2))
        self.wait(1.2)

        return VGroup(
            axes,
            labels,
            graph,
            curve_glow,
            highlight_point,
            highlight_label,
            density_meter,
            density_labels,
            brace,
            brace_label,
        )

    def stepfun_landscapes(self):
        panel_titles = [
            ("Low sparsity", "Na/N = 0.27"),
            ("Medium sparsity", "Na/N = 0.58"),
            ("Still medium, deeper model", "D = 8B, Na/N ≈ 0.58"),
        ]
        panels = VGroup()

        for idx, (title, note) in enumerate(panel_titles):
            frame = Rectangle(
                width=3.6,
                height=2.8,
                stroke_color=BLUE_B,
                stroke_width=3,
                fill_color=BLUE_E,
                fill_opacity=0.2,
            )
            frame.shift(RIGHT * (idx - 1) * 4.3 + UP * 1.2)

            axes = NumberPlane(
                x_range=[0, 1, 0.2],
                y_range=[0, 1, 0.2],
                background_line_style={
                    "stroke_color": GRAY_D,
                    "stroke_opacity": 0.3,
                },
            )
            axes.scale(0.9).move_to(frame.get_center())

            contour_colors = [BLUE_D, TEAL_D, GREEN_B, YELLOW_B]
            contours = VGroup()
            for scale_factor, color in zip([1.0, 0.75, 0.55, 0.35], contour_colors):
                ellipse = Ellipse(width=3.0 * scale_factor, height=2.2 * scale_factor)
                ellipse.move_to(frame.get_center())
                ellipse.set_stroke(color=color, width=3)
                contours.add(ellipse)

            optimum = Star(color=ORANGE, fill_opacity=1, density=2).scale(0.18)
            optimum.move_to(frame.get_center() + RIGHT * 0.6 + UP * 0.3)

            title_text = Text(title, font_size=24, color=WHITE).next_to(frame, UP, buff=0.2)
            note_text = Text(note, font_size=20, color=GRAY_C).next_to(frame, DOWN, buff=0.2)

            panel = VGroup(frame, axes, contours, optimum, title_text, note_text)
            panels.add(panel)

        caption = Text(
            "StepFun scaling landscapes: stable minima across sparsity ratios",
            font_size=28,
            t2c={"StepFun": BLUE_C, "sparsity": GREEN_C},
        ).shift(DOWN * 2.6)

        self.play(LaggedStart(*[FadeIn(panel, shift=UP * 0.4) for panel in panels], lag_ratio=0.2))
        self.play(Write(caption))
        self.wait(1)

        return VGroup(panels, caption)

    def ant_group_heatmap(self):
        grid = VGroup()
        colors = [
            [BLUE_E, BLUE_D, TEAL_D],
            [BLUE_D, GREEN_D, YELLOW_D],
            [GREEN_D, YELLOW_D, GOLD_E],
        ]
        for i in range(3):
            row = VGroup()
            for j in range(3):
                square = Square(side_length=1.0)
                square.set_fill(color=colors[i][j], opacity=0.85)
                square.set_stroke(color=GRAY_E, width=1.5)
                row.add(square)
            row.arrange(RIGHT, buff=0)
            grid.add(row)
        grid.arrange(DOWN, buff=0)
        grid.shift(LEFT * 4.2 + DOWN * 1.5)

        axes_labels = VGroup(
            Text("Activation ratio λ", font_size=24, color=WHITE).next_to(grid, DOWN, buff=0.4),
            Text("Learning rate", font_size=24, color=WHITE).rotate(PI / 2).next_to(grid, LEFT, buff=0.4),
        )

        near_optimal_label = Text(
            "Near-optimal band (≤ 0.25% loss from best)",
            font_size=26,
            color=YELLOW_C,
        ).next_to(grid, RIGHT, buff=1)
        highlight = SurroundingRectangle(grid[1][1], buff=0.1, color=YELLOW_E)

        title = Text(
            "Ant Group observation: active parameters align across sparsity window",
            font_size=28,
            t2c={"active": GREEN_C, "sparsity": BLUE_C},
        ).to_edge(DOWN)

        self.play(FadeIn(grid))
        self.play(Write(axes_labels))
        self.play(Create(highlight), FadeIn(near_optimal_label, shift=RIGHT * 0.2))
        self.play(Write(title))
        self.wait(1)

        return VGroup(grid, axes_labels, near_optimal_label, highlight, title)

    def present_loss_equation(self):
        equation_terms = VGroup(
            MathTex(r"\log L(F, \hat{B})", color=WHITE),
            MathTex(r"\triangleq", color=WHITE),
            MathTex(r"a \log F", color=BLUE_C),
            MathTex(r"+ b \log \hat{B}", color=GREEN_C),
            MathTex(r"+ c \log F \log \hat{B}", color=PURPLE_B),
            MathTex(r"+ d", color=GRAY_C),
        ).arrange(RIGHT, buff=0.3)
        equation_terms.to_edge(UP)

        equation = VGroup(*equation_terms)

        braces = VGroup(
            Brace(equation_terms[2], UP, color=BLUE_C),
            Brace(equation_terms[3], UP, color=GREEN_C),
            Brace(equation_terms[4], UP, color=PURPLE_B),
        )
        brace_labels = VGroup(
            Text("Forward FLOPs", font_size=26, color=BLUE_C).next_to(braces[0], UP, buff=0.1),
            Text("MoE capacity", font_size=26, color=GREEN_C).next_to(braces[1], UP, buff=0.1),
            Text("Coupling of both", font_size=26, color=PURPLE_B).next_to(braces[2], UP, buff=0.1),
        )

        commentary = Paragraph(
            "Clark et al. fit MoE loss via forward-pass FLOPs (F) and routing capacity (B̂).",
            "The cross-term condenses how scaling sparsity reshapes optimization geometry.",
            alignment="left",
            font_size=26,
        ).next_to(equation, DOWN, buff=0.6).set_width(10)

        self.play(LaggedStart(*[Write(term) for term in equation_terms], lag_ratio=0.15))
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(GrowFromCenter(brace), FadeIn(label, shift=UP * 0.2))
                    for brace, label in zip(braces, brace_labels)
                ],
                lag_ratio=0.2,
            )
        )
        self.play(FadeIn(commentary, shift=UP * 0.3))
        self.wait(1.1)

        return VGroup(equation, braces, brace_labels, commentary)

    def animate_loss_cross_sections(self):
        axes_left = Axes(
            x_range=[1, 16, 3],
            y_range=[-1, 3, 1],
            x_length=5,
            y_length=3,
            axis_config={"color": GRAY_B},
        ).shift(LEFT * 3.5 + DOWN * 0.5)
        axes_left_labels = axes_left.get_axis_labels(
            Tex("Forward FLOPs $F$", color=WHITE),
            Tex(r"$\log L$", color=WHITE),
        )

        def loss_slice_f(x, b_hat=4.0):
            return 0.6 * np.log(x) + 0.2 * np.log(b_hat) + 0.08 * np.log(x) * np.log(b_hat) - 0.4

        graph_left = axes_left.plot(lambda x: loss_slice_f(x), x_range=[1.2, 15.5], color=BLUE_D)
        graph_left.set_stroke(width=4)

        axes_right = Axes(
            x_range=[1, 10, 1],
            y_range=[-1, 3, 1],
            x_length=5,
            y_length=3,
            axis_config={"color": GRAY_B},
        ).shift(RIGHT * 3.5 + DOWN * 0.5)
        axes_right_labels = axes_right.get_axis_labels(
            Tex("Capacity $\\hat{B}$", color=WHITE),
            Tex(r"$\log L$", color=WHITE),
        )

        def loss_slice_b(b_hat, f_val=6.0):
            return 0.6 * np.log(f_val) + 0.2 * np.log(b_hat) + 0.08 * np.log(f_val) * np.log(b_hat) - 0.4

        graph_right = axes_right.plot(lambda x: loss_slice_b(x), x_range=[1.2, 9.5], color=GREEN_D)
        graph_right.set_stroke(width=4)

        left_dot = Dot(color=YELLOW).move_to(axes_left.c2p(2, loss_slice_f(2)))
        right_dot = Dot(color=YELLOW).move_to(axes_right.c2p(2, loss_slice_b(2)))

        slope_text = Text(
            "Scaling F alone saturates -> diminishing returns",
            font_size=24,
            color=BLUE_C,
        ).next_to(axes_left, DOWN, buff=0.6)
        capacity_text = Text(
            "Boosting capacity widens minima until routing saturates",
            font_size=24,
            color=GREEN_C,
        ).next_to(axes_right, DOWN, buff=0.6)

        cross_term_arrow = CurvedArrow(
            start_point=axes_left.get_corner(UP + RIGHT),
            end_point=axes_right.get_corner(UP + LEFT),
            color=PURPLE_B,
            angle=PI / 4,
        )
        cross_term_label = Text(
            "Coupling term ensures both scales stay synchronized",
            font_size=24,
            color=PURPLE_B,
        ).next_to(cross_term_arrow, UP, buff=0.2)

        self.play(Create(axes_left), FadeIn(axes_left_labels))
        self.play(Create(axes_right), FadeIn(axes_right_labels))
        self.play(Create(graph_left), Create(graph_right))

        self.play(GrowFromCenter(left_dot))
        self.play(MoveAlongPath(left_dot, graph_left), run_time=2.5, rate_func=there_and_back)

        self.play(GrowFromCenter(right_dot))
        self.play(MoveAlongPath(right_dot, graph_right), run_time=2.5, rate_func=there_and_back)

        self.play(Write(slope_text), Write(capacity_text))
        self.play(Create(cross_term_arrow), FadeIn(cross_term_label, shift=UP * 0.2))
        self.wait(1.2)

        return VGroup(
            axes_left,
            axes_left_labels,
            graph_left,
            axes_right,
            axes_right_labels,
            graph_right,
            left_dot,
            right_dot,
            slope_text,
            capacity_text,
            cross_term_arrow,
            cross_term_label,
        )

    def closing_synthesis(self):
        summary = VGroup(
            Text(
                "Tokens per parameter is a duet:",
                font_size=32,
                weight=BOLD,
                color=WHITE,
            ),
            Text(
                "Total capacity (B) shapes the theatre, active usage sculpts the performance.",
                font_size=28,
                t2c={"Total capacity": BLUE_C, "active usage": GREEN_C},
            ),
            Text(
                "Scaling laws agree when we respect both the budget (F) and the routing bandwidth (\\hat{B}).",
                font_size=28,
                t2c={"both": GOLD},
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        summary.to_edge(DOWN).shift(UP * 0.5)

        halo = Circle(radius=3.2, color=GOLD_E, stroke_width=3)
        halo.set_fill(color=GOLD_E, opacity=0.15)
        halo.set_z_index(-2)

        crest = VGroup(
            RegularPolygon(n=6, color=BLUE_C, stroke_width=2).scale(0.6),
            RegularPolygon(n=5, color=GREEN_C, stroke_width=2).scale(0.45),
        ).arrange(RIGHT, buff=0.3)
        crest.move_to(ORIGIN + UP * 1.2)

        self.play(FadeIn(halo, scale=1.2))
        self.play(FadeIn(crest, shift=UP * 0.2))
        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3) for line in summary], lag_ratio=0.2))
        self.wait(2)
