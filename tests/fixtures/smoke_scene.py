from manim import *


class SmokeScene(Scene):
    """Tiny canned scene for the init-to-render smoke test. No LaTeX."""

    def construct(self):
        square = Square(color=BLUE)
        self.play(Write(square))
        self.wait(0.3)
        self.play(FadeOut(square))
