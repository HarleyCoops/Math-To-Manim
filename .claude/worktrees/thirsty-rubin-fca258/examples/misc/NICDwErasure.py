"""Manim scene highlighting a Non-Interactive Correlation Distillation (NICD)
counterexample with erasures at p = 0.4 and n = 5.

This animation embraces the agent-pipeline storytelling structure and only uses
manim-native text, math, and shapes (no external figures). It focuses on the
linear threshold function f(x) = sign(x_1 - 3 x_2 + x_3 - x_4 + 3 x_5) and its
performance advantage over majority functions under the erasure model.
"""

from __future__ import annotations

from typing import Iterable, Tuple

from manim import (
    BLUE_B,
    BLUE_C,
    BLUE_D,
    GOLD_B,
    GREY_B,
    GREY_E,
    LEFT,
    RIGHT,
    UP,
    DOWN,
    FadeIn,
    FadeOut,
    LaggedStart,
    Create,
    Brace,
    BulletedList,
    DashedLine,
    MathTex,
    Paragraph,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    Write,
    BarChart,
)

PANEL_COLOR = "#111826"


class NICDwErasureExplainer(Scene):
    """Verbose, high-production explainer for the NICD with erasures result."""

    def construct(self) -> None:  # noqa: D401
        self.camera.background_color = "#030711"
        self.intro_sequence()
        self.pipeline_sequence()
        self.model_sequence()
        self.data_sequence()
        self.takeaway_sequence()

    # --- Scene segments ---------------------------------------------------
    def intro_sequence(self) -> None:
        title = Text(
            "Non-Interactive Correlation Distillation",
            font_size=48,
            weight="BOLD",
        )
        title.set_color_by_gradient(BLUE_C, BLUE_B, GOLD_B)
        subtitle = Text(
            "When erasures refuse to silence a smarter threshold function",
            font_size=28,
            color=GREY_E,
        )
        subtitle.next_to(title, DOWN, buff=0.4)
        accent = DashedLine(LEFT * 6, RIGHT * 6, dash_length=0.3, color=BLUE_D)
        accent.next_to(subtitle, DOWN, buff=0.3)

        self.play(FadeIn(title, shift=0.3 * DOWN))
        self.play(Write(subtitle))
        self.play(Create(accent))

        statement_panel = build_text_panel(
            "Yang's Erasure Challenge",
            [
                "Random restriction: z_i in {-1, 0, 1} with erasure prob p = 0.4.",
                "Is E[|f(z)|] maximized by majority when n is odd and f unbiased?",
                "Our scene showcases the counterexample that answers no.",
            ],
            width=10.0,
        )
        statement_panel.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(statement_panel, shift=0.4 * UP))
        self.wait(2.5)
        self.play(
            FadeOut(statement_panel, shift=0.5 * DOWN),
            FadeOut(accent),
            FadeOut(subtitle),
            FadeOut(title),
        )
        self.wait(1.0)

    def pipeline_sequence(self) -> None:
        pipeline_steps: Iterable[Tuple[str, str]] = [
            (
                "Signal Capture",
                "Model z in {-1, 0, 1}^5 where erasures strike independently with p = 0.4.",
            ),
            (
                "Hypothesis Engine",
                "Search linear threshold functions beyond the symmetric majorities.",
            ),
            (
                "Quant Analyst",
                "Integrate |f(z)| over erased hypercube slices to estimate Phi_0.4(f).",
            ),
            (
                "Story Weaver",
                "Translate a 0.00120 gap into intuition and broader implications.",
            ),
        ]

        cards = VGroup()
        for label, description in pipeline_steps:
            rect = RoundedRectangle(width=5.8, height=1.6, corner_radius=0.3)
            rect.set_fill(color=PANEL_COLOR, opacity=0.85)
            rect.set_stroke(color=BLUE_D, width=2)

            header = Text(label, font_size=32, weight="BOLD")
            header.set_color_by_gradient(BLUE_C, GOLD_B)
            header.move_to(rect.get_top() + DOWN * 0.35)
            body = Text(description, font_size=22)
            body.set_color(GREY_E)
            body.move_to(rect.get_center() + DOWN * 0.35)

            card = VGroup(rect, header, body)
            cards.add(card)

        cards.arrange(DOWN, buff=0.4)
        cards.to_edge(LEFT).shift(RIGHT * 0.6)

        arrows = VGroup()
        for start, end in zip(cards[:-1], cards[1:]):
            arrow = DashedLine(start.get_bottom(), end.get_top(), dash_length=0.25)
            arrow.set_color(GREY_B)
            arrows.add(arrow)

        self.play(LaggedStart(*[FadeIn(card) for card in cards], lag_ratio=0.2))
        self.play(LaggedStart(*[Create(arrow) for arrow in arrows], lag_ratio=0.2))
        self.wait(2.5)
        self.play(FadeOut(arrows), FadeOut(cards))
        self.wait(1.0)

    def model_sequence(self) -> None:
        headline = Text(
            "The counterexample that refuses to be majority",
            font_size=36,
            color="white",
        )
        headline.to_edge(UP, buff=0.9)

        function_tex = MathTex(
            r"f(x) = \operatorname{sign}(x_1 - 3x_2 + x_3 - x_4 + 3x_5)",
            color=GOLD_B,
        )
        function_tex.scale(1.1)

        details = BulletedList(
            r"Weight vector $w = (1,-3,1,-1,3)$ keeps $f(x) = -f(-x)$ (odd \& unbiased).",
            r"Linear threshold structure tunes sensitivity to erasures asymmetrically.",
            r"Distances to $\text{Maj}_k$ ($k \in \{1,3,5\}$) are 12, 16, 14 within $\{-1,1\}^5$.",
        )
        details.set_color(GREY_E)
        details.scale(0.8)
        details.next_to(function_tex, DOWN, buff=0.6)

        remarks_panel = build_text_panel(
            "Theory sidebars",
            [
                "For p >= 1/2, Yang conjectured dictators maximize Phi_p (proved by O'Donnell & Wright 2012).",
                "Mossel 2010: bounded influences imply Phi_p(f) <= Phi_p(Maj_n).",
                "Our p = 0.4 counterexample evades both arguments via sharp weights.",
            ],
            width=10.2,
        )
        remarks_panel.next_to(details, DOWN, buff=0.7)

        self.play(FadeIn(headline, shift=0.2 * DOWN))
        self.play(Write(function_tex))
        self.play(FadeIn(details, lag_ratio=0.15))
        self.wait(2.0)
        self.play(FadeIn(remarks_panel, shift=0.4 * UP))

        brace = Brace(function_tex, DOWN, color=BLUE_B)
        brace_text = Text(
            "Odd + unbiased -> ideal for erasure resilience",
            font_size=26,
            color=GREY_E,
        )
        brace_text.next_to(brace, DOWN, buff=0.2)
        self.play(Create(brace), FadeIn(brace_text, shift=0.2 * DOWN))
        self.wait(2.5)
        self.play(FadeOut(brace), FadeOut(brace_text), FadeOut(remarks_panel), FadeOut(headline), FadeOut(function_tex), FadeOut(details))
        self.wait(1.0)

    def data_sequence(self) -> None:
        chart = BarChart(
            values=[0.40000, 0.42400, 0.42904, 0.43024],
            bar_names=["Maj1", "Maj3", "Maj5", "f(x)"],
            y_range=[0.39, 0.435, 0.01],
            y_length=4.2,
            x_length=6.4,
            bar_colors=[BLUE_D, BLUE_C, BLUE_B, GOLD_B],
        )
        chart.scale(0.9)
        chart.to_edge(RIGHT).shift(LEFT * 0.6)

        data_caption = Text(
            "Benchmarking Phi_0.4 across majority candidates and f",
            font_size=26,
            color=GREY_E,
        )
        data_caption.next_to(chart, UP)

        highlight_box = SurroundingRectangle(chart.bars[3], color=GOLD_B, buff=0.1)
        delta_tex = MathTex(
            r"\Phi_{0.4}(f) - \max_k \Phi_{0.4}(\text{Maj}_k) = 0.00120",
            color="white",
        )
        delta_tex.scale(0.9)
        delta_tex.next_to(chart, DOWN, buff=0.6)

        note_panel = build_text_panel(
            "Robustness checks",
            [
                "Same LTF beats Maj_3 at p = 0.30 and p = 0.49 (values from constructive proof).",
                "Edge sensitivity comes from -3 and +3 weights responding to erasures differently.",
            ],
            width=10.0,
        )
        note_panel.next_to(delta_tex, DOWN, buff=0.6)

        self.play(FadeIn(data_caption, shift=0.2 * DOWN))
        self.play(Create(chart))
        self.wait(1.5)
        self.play(Create(highlight_box))
        self.play(Write(delta_tex))
        self.wait(2.0)
        self.play(FadeIn(note_panel, shift=0.3 * UP))
        self.wait(2.5)
        self.play(FadeOut(highlight_box), FadeOut(note_panel), FadeOut(data_caption))

        self.bar_chart = chart
        self.delta_tex = delta_tex

    def takeaway_sequence(self) -> None:
        outro_panel = build_text_panel(
            "Why it matters",
            [
                "Erasure noise rewards nuanced weight patterns; majority is not universally optimal.",
                "Agent-style exploration helps surface counterintuitive thresholds quickly.",
                "Tiny Phi-gap hints at deeper structure in biased versus unbiased influence profiles.",
                "Open frontier: automate the discovery of even sharper NICD separations.",
            ],
            width=10.6,
        )
        outro_panel.next_to(self.delta_tex, DOWN, buff=0.8)

        callout = Text(
            "Next investigation: can pipelines expand beyond n = 5 to systematic gaps?",
            font_size=26,
            color=GOLD_B,
        )
        callout.next_to(outro_panel, DOWN, buff=0.5)

        self.play(FadeIn(outro_panel))
        self.wait(2.0)
        self.play(FadeIn(callout))
        self.wait(3.0)
        self.play(
            FadeOut(outro_panel),
            FadeOut(callout),
            FadeOut(self.delta_tex),
            FadeOut(self.bar_chart),
        )
        self.wait(1.0)


def build_text_panel(title: str, body_lines: Iterable[str], width: float = 9.2) -> VGroup:
    """Return a styled panel with a title and body paragraphs."""
    header = Text(title, font_size=30, weight="BOLD")
    header.set_color_by_gradient(BLUE_C, GOLD_B)
    body = Paragraph(*body_lines, alignment="left", font_size=22, line_spacing=0.5)
    body.set_color(GREY_E)

    content = VGroup(header, body).arrange(DOWN, buff=0.25)
    frame_width = max(width, content.width + 1.2)
    frame_height = content.height + 1.0

    frame = RoundedRectangle(width=frame_width, height=frame_height, corner_radius=0.3)
    frame.set_fill(color=PANEL_COLOR, opacity=0.92)
    frame.set_stroke(color=BLUE_D, width=2)

    content.move_to(frame.get_center())

    return VGroup(frame, content)
