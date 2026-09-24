from manim import *


class StructureFirstJourney(Scene):
    def construct(self):
        title = Text("Structure tells us what to combine first")
        equation = MathTex(r"\operatorname{GCF}(12,18)=6")
        self.play(Write(title))
        self.play(title.animate.to_edge(UP), Write(equation))
        self.wait()
