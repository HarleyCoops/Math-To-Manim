from manim import *

class SteppedShape(ThreeDScene):
    def construct(self):
        # Set up 3D axes
        axes = ThreeDAxes(
            x_range=[0, 4, 1],
            y_range=[0, 3, 1],
            z_range=[0, 4, 1],
            x_length=4,
            y_length=3,
            z_length=4
        )
        self.add(axes)

        # Adjust camera for a clear 3D view
        self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES, distance=8)

        # --- Bottom block: 3×2×1 ---
        # A unit Cube is centered at (0,0,0) with side length 1
        # Scaling it by [3,2,1] changes its dimensions
        # Then shifting by (1.5,1,0.5) moves its corners to x∈[0,3], y∈[0,2], z∈[0,1]
        bottom = Cube().scale([3, 2, 1])
        bottom.shift([1.5, 1, 0.5])

        # --- Middle block: 2×2×1, stacked above the bottom block ---
        # After scaling to 2×2×1, shift so corners go from x=0..2, y=0..2, z=1..2
        middle = Cube().scale([2, 2, 1])
        middle.shift([1, 1, 1.5])

        # --- Top block: 2×1×1, stacked yet higher ---
        # After scaling to 2×1×1, shift so corners go from x=0..2, y=0..1, z=2..3
        top = Cube().scale([2, 1, 1])
        top.shift([1, 0.5, 2.5])

        # Group all blocks, apply some style
        shape = VGroup(bottom, middle, top)
        shape.set_fill(BLUE, opacity=0.5)
        shape.set_stroke(BLUE_E, width=1)

        # Animate creation
        self.play(Create(shape))
        self.wait()
