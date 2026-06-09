"""Single-formula Manim scene used by the Atlas video compositor.

Renders the LaTeX in ``M2M_FORMULA_TEX`` as a white MathTex with a dark
background stroke, on a transparent canvas. Invoked via the manim CLI with
``-s -t`` (save last frame, transparent) by atlas_video.render_formula_png.
"""

from __future__ import annotations

import os

from manim import BLACK, WHITE, MathTex, Scene


class FormulaScene(Scene):
    def construct(self) -> None:
        tex = os.environ.get("M2M_FORMULA_TEX", "x")
        formula = MathTex(tex, color=WHITE)
        formula.set_stroke(BLACK, width=4, background=True)
        formula.scale(2.2)
        self.add(formula)
