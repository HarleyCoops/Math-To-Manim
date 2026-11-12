"""Manim scenes for the 2D parts of a film: cards, and overlays for 3D shots.

- ``build_card``: an animated card. A headline, the shot's equations, a few
  lines of text. Its length is exactly the shot's ``duration_s``.
- ``build_overlay``: one transparent still that lies over a 3D shot: the
  caption at the foot and the first equation at the head, each on a dark band.

Both read a compiled shot (see ``studio.spec.compile``).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from manim import (
    BOLD,
    DOWN,
    UP,
    FadeIn,
    Line,
    MathTex,
    Paragraph,
    Rectangle,
    Scene,
    Text,
    VGroup,
    Write,
    config,
)

MAX_WIDTH = 12.0


def _fit(mobject, width: float = MAX_WIDTH):
    if mobject.width > width:
        mobject.scale_to_fit_width(width)
    return mobject


def build_card(compiled_path: str | Path) -> type[Scene]:
    compiled = json.loads(Path(compiled_path).read_text(encoding="utf-8"))

    class StudioCard(Scene):
        def construct(self) -> None:
            self.camera.background_color = compiled["background"]
            headline = _fit(Text(compiled["headline"], font_size=44, weight=BOLD,
                                 color=compiled["ink"]))
            rule = Line([-0.6, 0, 0], [0.6, 0, 0], color=compiled["accent"], stroke_width=4)
            equations = [_fit(MathTex(latex, font_size=54, color=compiled["accent"]), 11.0)
                         for latex in compiled["equations"]]
            parts = [headline, rule, *equations]
            body = None
            if compiled.get("body"):
                lines = textwrap.wrap(compiled["body"], width=62) or [""]
                body = _fit(Paragraph(*lines, font_size=27, color=compiled["muted"],
                                      alignment="center", line_spacing=0.9))
                parts.append(body)
            group = VGroup(*parts).arrange(DOWN, buff=0.55)
            if group.height > 6.6:
                group.scale_to_fit_height(6.6)
            group.move_to([0, 0, 0])

            steps = [(FadeIn(headline, shift=0.2 * UP), 0.7), (FadeIn(rule), 0.3)]
            steps += [(Write(eq), 1.1) for eq in equations]
            if body is not None:
                steps.append((FadeIn(body), 0.6))
            duration = compiled["duration_s"]
            planned = sum(seconds for _, seconds in steps)
            # Animations use at most 70% of the card; the rest is time to read.
            factor = min(1.0, 0.7 * duration / planned)
            used = 0.0
            for animation, seconds in steps:
                self.play(animation, run_time=seconds * factor)
                used += seconds * factor
            self.wait(max(duration - used, 1.0 / compiled["fps"]))

    return StudioCard


def build_overlay(compiled_path: str | Path) -> type[Scene]:
    compiled = json.loads(Path(compiled_path).read_text(encoding="utf-8"))

    class StudioOverlay(Scene):
        def construct(self) -> None:
            half_h, half_w = config.frame_height / 2, config.frame_width / 2

            def band(mobject, y: float) -> None:
                mobject.move_to([0, y, 0])
                strip = Rectangle(width=2 * half_w, height=mobject.height + 0.45,
                                  stroke_width=0, fill_color=compiled["background"],
                                  fill_opacity=0.62).move_to([0, y, 0])
                self.add(strip, mobject)

            if compiled.get("caption"):
                caption = _fit(Text(compiled["caption"], font_size=30, color=compiled["ink"]))
                band(caption, -half_h + 0.75)
            if compiled["equations"]:
                equation = _fit(MathTex(compiled["equations"][0], font_size=44,
                                        color=compiled["ink"]), 11.0)
                band(equation, half_h - 0.85)
            self.wait(1.0 / compiled["fps"])

    return StudioOverlay
