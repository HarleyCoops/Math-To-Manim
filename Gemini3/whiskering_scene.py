from manim import *
import numpy as np

# Global Configuration for Off-White Theme
config.background_color = "#F5F5F7"  # Off-white / light grey
# config.tex_template = TexTemplate() # Use default template

# Colors
COLOR_0_CELL = "#333333"  # Dark Grey for objects
COLOR_1_CELL = "#555555"  # Grey for 1-morphisms
COLOR_2_CELL_A = "#1E90FF"  # Blue
COLOR_2_CELL_B = "#FF8C00"  # Orange
TEXT_COLOR = "#000000"

class WhiskeringExchangeScene(ThreeDScene):
    def construct(self):
        # 1. Setup Camera and Lighting (Simulated)
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        
        # Title
        title = Tex("The Whiskering Exchange Law", color=TEXT_COLOR).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # 2. Define geometry for the diagram
        # We will build the diagram:
        # Top-Left: (f . alpha) . (beta . g')  -- Wait, notation varies.
        # Let's use the layout from the image transcription.
        # Top-Left, Top-Right, Bottom-Left, Bottom-Right nodes of the commutation square.
        
        # Coordinates in 3D
        tl = np.array([-3, 2, 0])
        tr = np.array([3, 2, 0])
        bl = np.array([-3, -2, 0])
        br = np.array([3, -2, 0])
        
        # Nodes (representing the composite 2-cells spaces)
        # Using MathTex for node labels roughly based on the diagram
        
        # Top Left: Horizontal composition then Vertical
        # Bottom Right: Vertical composition then Horizontal
        # (The law says they are isomorphic/equal)
        
        # Let's represent the specific diagram from the user's image (Bottom part)
        # Top Left: \Pi \Pi X_{ij}
        # Top Right: \Pi V_i
        # Bottom Left: \Pi Y_j
        # Bottom Right: U(...)
        
        node_tl = MathTex(r"\prod_j \prod_i X_{ij}(f_{ij-1}, f_{ij})", color=TEXT_COLOR).move_to(tl).scale(0.7)
        node_tr = MathTex(r"\prod_i V_i(f_{i0}, f_{im})", color=TEXT_COLOR).move_to(tr).scale(0.7)
        node_bl = MathTex(r"\prod_j Y_j(\eta_{j-1}, \eta_j)", color=TEXT_COLOR).move_to(bl).scale(0.7)
        node_br = MathTex(r"U(l\eta'_0, r\eta_m)", color=TEXT_COLOR).move_to(br).scale(0.7)
        
        # Orient text to camera
        for node in [node_tl, node_tr, node_bl, node_br]:
            self.add_fixed_orientation_mobjects(node)
            # Or just Rotate to face camera if using proper 3D
            node.rotate(90*DEGREES, RIGHT) # Start flat? No.
            # Let's keep them as 2D objects in 3D space, but we might need to rotate them to be readable
            # For now, let's keep them in the XY plane and we look from an angle.
            pass

        # Arrows
        arrow_top = Arrow(tl, tr, color=COLOR_2_CELL_A)
        arrow_left = Arrow(tl, bl, color=COLOR_2_CELL_B)
        arrow_right = Arrow(tr, br, color=COLOR_2_CELL_B)
        arrow_bottom = Arrow(bl, br, color=COLOR_2_CELL_A)
        
        label_top = MathTex(r"\prod_i \psi_i", color=COLOR_2_CELL_A).next_to(arrow_top, UP, buff=0.1).scale(0.6)
        label_left = MathTex(r"\prod_j \alpha_j", color=COLOR_2_CELL_B).next_to(arrow_left, LEFT, buff=0.1).scale(0.6)
        label_right = MathTex(r"\alpha'", color=COLOR_2_CELL_B).next_to(arrow_right, RIGHT, buff=0.1).scale(0.6)
        label_bottom = MathTex(r"\psi'", color=COLOR_2_CELL_A).next_to(arrow_bottom, DOWN, buff=0.1).scale(0.6)
        
        group_diagram = VGroup(
            node_tl, node_tr, node_bl, node_br,
            arrow_top, arrow_left, arrow_right, arrow_bottom,
            label_top, label_left, label_right, label_bottom
        )
        
        # 3. Animate Construction
        self.play(FadeIn(node_tl), FadeIn(node_tr), FadeIn(node_bl), FadeIn(node_br))
        self.wait(0.5)
        
        self.play(GrowArrow(arrow_top), Write(label_top))
        self.play(GrowArrow(arrow_left), Write(label_left))
        
        # Path 1: Top then Right (Wait, the diagram is commutative)
        # Highlight Path 1 (Horizontal whiskering first)
        path1 = VGroup(arrow_top, label_top, arrow_right, label_right)
        self.play(
            arrow_top.animate.set_color(COLOR_2_CELL_A),
            arrow_right.animate.set_color(COLOR_2_CELL_A),
            GrowArrow(arrow_right), Write(label_right)
        )
        
        # Path 2: Left then Bottom (Vertical whiskering first)
        path2 = VGroup(arrow_left, label_left, arrow_bottom, label_bottom)
        self.play(
            arrow_left.animate.set_color(COLOR_2_CELL_B),
            arrow_bottom.animate.set_color(COLOR_2_CELL_B),
            GrowArrow(arrow_bottom), Write(label_bottom)
        )
        
        # 4. Whiskering Visualization (Conceptual)
        # Move camera to show 3D depth
        self.move_camera(phi=75 * DEGREES, theta=-10 * DEGREES, run_time=3)
        
        # Show specific simplified equation for 2-category exchange
        # (f . alpha) . (beta . g') = (beta . g) . (f' . alpha)
        # We create this equation floating in 3D
        
        eq_text = MathTex(
            r"(\alpha \ast g) \cdot (f' \ast \beta) = (f \ast \beta) \cdot (\alpha \ast g')",
            color=TEXT_COLOR
        ).scale(1.2)
        eq_text.move_to(np.array([0, 0, 2])) # Float above
        
        # Highlight components
        # alpha is Blue, beta is Orange
        eq_text[0][1].set_color(COLOR_2_CELL_A) # alpha
        eq_text[0][9:10].set_color(COLOR_2_CELL_B) # beta
        eq_text[0][13].set_color(COLOR_2_CELL_A) # f
        eq_text[0][15].set_color(COLOR_2_CELL_B) # beta
        eq_text[0][20].set_color(COLOR_2_CELL_A) # alpha
         
        self.play(Write(eq_text))
        
        # 5. Visual Metaphor: Sliding tiles
        # Create two squares representing 2-cells
        
        square_alpha = Square(side_length=1.5, fill_color=COLOR_2_CELL_A, fill_opacity=0.5, stroke_color=COLOR_2_CELL_A)
        square_beta = Square(side_length=1.5, fill_color=COLOR_2_CELL_B, fill_opacity=0.5, stroke_color=COLOR_2_CELL_B)
        
        # Position them
        square_alpha.move_to(np.array([-1, 1, 1]))
        square_beta.move_to(np.array([1, -1, 1]))
        
        self.play(FadeIn(square_alpha), FadeIn(square_beta))
        
        # Animate exchange: Slide them past each other
        # This visualizes that the order of "height" doesn't matter if they are spatially separated horizontally
        
        self.play(
            square_alpha.animate.move_to(np.array([1, 1, 1])),
            square_beta.animate.move_to(np.array([-1, -1, 1])),
            run_time=2
        )
        
        self.play(
            square_alpha.animate.move_to(np.array([1, -1, 1])),
            square_beta.animate.move_to(np.array([-1, 1, 1])),
            run_time=2
        )
        
        # 6. Conclusion
        self.move_camera(phi=0, theta=-90*DEGREES, run_time=2)
        final_text = Tex("The Diagram Commutes", color=TEXT_COLOR).next_to(eq_text, DOWN)
        self.play(Write(final_text))
        self.wait(2)
        
        self.play(FadeOut(group_diagram), FadeOut(eq_text), FadeOut(square_alpha), FadeOut(square_beta), FadeOut(final_text))
