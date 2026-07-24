from manim import *


class Erdos1038PotentialLandscape(ThreeDScene):
    def construct(self):
        title = Text("A polynomial becomes terrain")
        zero_plane = Square(side_length=5, color=GOLD).set_opacity(0.2)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        self.play(Write(title), Create(zero_plane))
        self.move_camera(phi=55 * DEGREES, theta=-20 * DEGREES)
        self.wait()
