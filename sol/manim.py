"""Deterministically compile Sol's typed scene plan into conservative Manim."""

from __future__ import annotations

import re

from sol.models import CalculationResult

_DANGEROUS_LATEX = re.compile(
    r"\\(?:input|include|write|openout|read|usepackage|documentclass|immediate|csname)\b",
    re.IGNORECASE,
)
_PALETTE = {"coral": "#d97757", "blue": "#6a9bcc", "gold": "#e5b566", "green": "#788c5d"}


def sanitize_latex(value: str) -> str:
    cleaned = value.strip()[:500]
    if _DANGEROUS_LATEX.search(cleaned):
        raise ValueError("unsafe LaTeX command in scene plan")
    return cleaned.replace("'''", "")


def compile_manim(result: CalculationResult) -> str:
    beat_rows = []
    for beat in result.scene[:8]:
        beat_rows.append(repr((beat.caption, sanitize_latex(beat.expression_latex or r"\text{Continue}"), _PALETTE[beat.accent])))
    beats = ",\n            ".join(beat_rows)
    title = result.problem.strip()[:110]
    answer = sanitize_latex(result.answer_latex)
    return f'''from manim import *


class SolCalculationScene(Scene):
    """Generated from a typed GPT-5.6 Sol calculation contract."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        title = Text({title!r}, font_size=34, color="#faf9f5").to_edge(UP)
        rule = Line(LEFT * 6, RIGHT * 6, color="#2b2b29", stroke_width=1).next_to(title, DOWN)
        self.play(FadeIn(title), Create(rule))

        beats = [
            {beats}
        ]
        current = None
        for caption_text, latex, color in beats:
            caption = Text(caption_text, font_size=24, color="#c8c6bf").to_edge(DOWN)
            formula = MathTex(latex, font_size=58, color=color)
            group = VGroup(formula, caption)
            if current is None:
                self.play(FadeIn(group, shift=UP * 0.2))
            else:
                self.play(ReplacementTransform(current, group))
            current = group
            self.wait(0.7)

        answer = MathTex({answer!r}, font_size=68, color="#e5b566")
        if current is not None:
            self.play(ReplacementTransform(current, answer))
        else:
            self.play(FadeIn(answer))
        self.play(Indicate(answer, color="#faf9f5"))
        self.wait(1.2)
'''
