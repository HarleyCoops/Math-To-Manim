from manim import *

class LShape3D(ThreeDScene):
    def construct(self):
        # Configure camera orientation
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES, zoom=0.8)

        # Create the three blocks with colors and labels
        bottom_block = Prism(dimensions=[3, 2, 1], fill_color=BLUE, fill_opacity=0.6, stroke_width=2)
        middle_block = Prism(dimensions=[2, 2, 1], fill_color=GREEN, fill_opacity=0.6, stroke_width=2)
        top_block = Prism(dimensions=[2, 1, 1], fill_color=RED, fill_opacity=0.6, stroke_width=2)

        # Position the blocks according to their coordinates
        bottom_block.move_to([1.5, 0.5, 1])    # Centered at (1.5, 0.5, 1) in 3D space
        middle_block.move_to([1, 1.5, 1])      # Centered at (1, 1.5, 1)
        top_block.move_to([1, 2.5, 0.5])       # Centered at (1, 2.5, 0.5)

        # Add labels
        bottom_label = Text("Bottom Block").scale(0.4).next_to(bottom_block, OUT, buff=0.2).set_color(WHITE)
        middle_label = Text("Middle Block").scale(0.4).next_to(middle_block, LEFT, buff=0.2).set_color(WHITE)
        top_label = Text("Top Block").scale(0.4).next_to(top_block, UP, buff=0.2).set_color(WHITE)

        # Animate the blocks and labels
        self.play(
            Create(bottom_block),
            Write(bottom_label),
            run_time=2
        )
        self.play(
            Create(middle_block),
            Write(middle_label),
            run_time=2
        )
        self.play(
            Create(top_block),
            Write(top_label),
            run_time=2
        )
        self.wait(1)

        # Rotate the entire structure to show 3D
        self.move_camera(phi=75*DEGREES, theta=30*DEGREES, run_time=3)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(3)
