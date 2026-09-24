from manim import *

INK = "#0c0c0b"
IVORY = "#faf9f5"
CORAL = "#d97757"
SKY = "#6a9bcc"
OLIVE = "#788c5d"


class GeodesicFilm(ThreeDScene):
    """Pinned cinematic-3D contract for the Mythos house style.

    Mythos stages a top-down ThreeDScene (phi=0, theta=-90) on the
    house background and tilts only for set pieces.
    """

    def construct(self):
        self.camera.background_color = INK
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0)
        title = Text("A geodesic is the straightest path", font_size=64, color=IVORY)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title))
        self.wait(0.8)
        self.play(FadeOut(title))
        equation = MathTex(r"\nabla_{\dot\gamma}\dot\gamma", r"=", r"0", color=CORAL)
        caption = Text("The acceleration along the path vanishes", font_size=30, color=SKY)
        caption.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(caption)
        self.play(FadeIn(equation), FadeIn(caption))
        self.move_camera(frame_center=equation.get_center(), zoom=2.2, run_time=1.2)
        self.wait(0.6)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.0)
        leftover = Text("structure", font_size=28, color=OLIVE)
        leftover.next_to(equation, DOWN)
        self.play(FadeIn(leftover))
        self.play(FadeOut(equation), FadeOut(caption), FadeOut(leftover))
