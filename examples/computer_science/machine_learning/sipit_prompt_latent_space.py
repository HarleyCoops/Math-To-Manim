"""
Visualization of Prompt Space to Latent Space mapping with LLM and SiPIT inversion.

This animation explains the concept of how Large Language Models (LLMs) create an 
injective mapping from prompts to latent representations, and how SiPIT (a proposed 
inversion method) can invert this mapping.

Key Concepts:
- Prompt Space: The domain of input prompts (complex, curved manifold)
- Latent Space: Numerical embeddings/representations (structured, multi-dimensional)
- Injective Mapping: Distinct prompts map to distinct latent representations
- SiPIT: Method to invert the LLM mapping
"""

from manim import *
import numpy as np


# Color scheme matching the diagram description
BEIGE = "#D2B48C"
BEIGE_LIGHT = "#F5DEB3"
BLACK = "#000000"
WHITE = "#FFFFFF"
GRAY = "#888888"
LIGHT_GRAY = "#D3D3D3"
BLUE = "#4A90E2"
DARK_BLUE = "#236B8E"
RED = "#E74C3C"
GREEN = "#2ECC71"
PURPLE = "#9B59B6"
ORANGE = "#E67E22"
YELLOW = "#F1C40F"


class PromptLatentSpaceMapping(Scene):
    """Main scene explaining Prompt Space to Latent Space mapping with SiPIT inversion."""
    
    def construct(self):
        # Scene 1: Introduction and Title
        self.introduce_concept()
        
        # Scene 2: The Prompt Space
        prompt_space = self.create_prompt_space()
        
        # Scene 3: The Latent Space
        latent_space = self.create_latent_space()
        
        # Scene 4: Two distinct prompts
        x, x_prime, delta = self.introduce_prompts(prompt_space)
        
        # Scene 5: The LLM Mapping (Forward Pass)
        z, z_prime, epsilon, llm_arrows = self.show_llm_mapping(
            prompt_space, latent_space, x, x_prime, delta
        )
        
        # Scene 6: The Injective Property
        self.explain_injective_property(delta, epsilon)
        
        # Scene 7: The SiPIT Inversion (Backward Pass)
        self.show_sipit_inversion(latent_space, prompt_space, z, x)
        
        # Scene 8: Concluding Caption
        self.show_conclusion()
    
    def introduce_concept(self):
        """Introduce the overall concept with title."""
        title = Tex(
            "Prompt Space to Latent Space Mapping",
            font_size=48,
            color=BLUE
        )
        subtitle = Tex(
            "Understanding LLM Embeddings and SiPIT Inversion",
            font_size=36,
            color=GRAY
        ).next_to(title, DOWN, buff=0.5)
        
        title_box = SurroundingRectangle(
            VGroup(title, subtitle),
            color=BLUE,
            buff=0.3,
            corner_radius=0.2
        )
        
        self.play(
            DrawBorderThenFill(title_box),
            Write(title),
            Write(subtitle),
            run_time=2
        )
        self.wait(1)
        
        self.play(
            title.animate.scale(0.7).to_corner(UL),
            subtitle.animate.scale(0.7).to_corner(UL).shift(DOWN * 0.4),
            title_box.animate.scale(0.7).to_corner(UL).shift(DOWN * 0.2)
        )
        self.wait(0.5)
    
    def create_prompt_space(self):
        """Create the Prompt Space visualization."""
        # Create a 3D-like curved surface using a parametric surface
        # We'll simulate this with a curved grid pattern
        
        # Create surface-like appearance with fill (background)
        surface = Polygon(
            LEFT * 6.5 + DOWN * 3,
            LEFT * 1.5 + DOWN * 3,
            LEFT * 1.5 + UP * 3,
            LEFT * 6.5 + UP * 3,
            color=BEIGE_LIGHT,
            fill_opacity=0.3,
            stroke_width=0
        )
        
        # Create grid lines for the prompt space
        grid_lines = VGroup()
        
        # Horizontal grid lines (curved)
        for i in range(-3, 4):
            y_pos = i * 0.8 - 3.5
            # Create curved line using ParametricFunction
            curve = ParametricFunction(
                lambda t, y=y_pos: np.array([
                    t * 2.5 - 3.5,
                    y + 0.3 * np.sin(t * 2),
                    0
                ]),
                t_range=[0, 3],
                color=BEIGE,
                stroke_width=1.5
            ).shift(LEFT * 4)
            grid_lines.add(curve)
        
        # Vertical grid lines (curved)
        for i in range(-3, 4):
            x_pos = i * 0.8 - 3.5
            curve = ParametricFunction(
                lambda t, x=x_pos: np.array([
                    x + 0.2 * np.cos(t * 1.5),
                    t * 2.5 - 3.5,
                    0
                ]),
                t_range=[0, 3],
                color=BEIGE,
                stroke_width=1.5
            ).shift(LEFT * 4)
            grid_lines.add(curve)
        
        # Label for Prompt Space
        prompt_space_label = Text(
            "PROMPT SPACE",
            font_size=36,
            color=DARK_BLUE,
            weight=BOLD
        ).next_to(surface, UP, buff=0.3)
        
        # Add scattered dots representing prompts
        # Use fixed seed for reproducibility
        np.random.seed(42)
        prompt_dots = VGroup()
        surface_center = surface.get_center()
        for _ in range(15):
            dot = Dot(
                point=surface_center + np.array([
                    np.random.uniform(-2, 2),
                    np.random.uniform(-2, 2),
                    0
                ]),
                color=BLACK,
                radius=0.08
            )
            prompt_dots.add(dot)
        np.random.seed(None)  # Reset seed
        
        # Animate the creation
        self.play(
            FadeIn(surface, shift=UP * 0.5),
            run_time=1.5
        )
        self.play(
            LaggedStart(
                *[Create(line) for line in grid_lines],
                lag_ratio=0.05
            ),
            run_time=2
        )
        self.play(
            Write(prompt_space_label),
            LaggedStart(
                *[FadeIn(dot, scale=0.5) for dot in prompt_dots],
                lag_ratio=0.1
            ),
            run_time=1.5
        )
        self.wait(1)
        
        return VGroup(surface, grid_lines, prompt_space_label, prompt_dots)
    
    def create_latent_space(self):
        """Create the Latent Space visualization."""
        # Create a 2D Cartesian coordinate system
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            x_length=4,
            y_length=3,
            axis_config={
                "include_numbers": True,
                "stroke_color": LIGHT_GRAY,
                "stroke_width": 2
            },
            x_axis_config={"label_direction": DOWN},
            y_axis_config={"label_direction": LEFT}
        ).shift(RIGHT * 3.5)
        
        # Add axis labels
        x_label = MathTex("w_1", font_size=32).next_to(
            axes.x_axis.get_end(), DOWN, buff=0.2
        )
        y_label = MathTex("w_2", font_size=32).next_to(
            axes.y_axis.get_end(), LEFT, buff=0.2
        )
        
        # Add dimension notation
        dim_label = MathTex(r"\mathbb{R}^d", font_size=28, color=GRAY).next_to(
            axes, UP, buff=0.1
        ).shift(RIGHT * 1.5)
        
        # Create grid pattern
        grid = NumberPlane(
            x_range=[-3, 3, 0.5],
            y_range=[-2, 2, 0.5],
            x_length=4,
            y_length=3,
            background_line_style={
                "stroke_color": LIGHT_GRAY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        ).shift(RIGHT * 3.5)
        
        # Label for Latent Space
        latent_space_label = Text(
            "LATENT SPACE",
            font_size=36,
            color=DARK_BLUE,
            weight=BOLD
        ).next_to(axes, UP, buff=0.5)
        
        # Right angle symbol at origin (implicit in the axes)
        origin_dot = Dot(
            axes.c2p(0, 0),
            radius=0.05,
            color=GRAY
        )
        
        # Animate the creation
        self.play(
            Create(grid),
            Create(axes),
            run_time=1.5
        )
        self.play(
            Write(x_label),
            Write(y_label),
            Write(dim_label),
            Create(origin_dot),
            run_time=1
        )
        self.play(
            Write(latent_space_label),
            run_time=1
        )
        self.wait(1)
        
        return VGroup(axes, grid, x_label, y_label, dim_label, latent_space_label, origin_dot)
    
    def introduce_prompts(self, prompt_space):
        """Introduce two distinct prompts x and x' with distance δ."""
        surface = prompt_space[0]
        
        # Position two distinct prompts
        x_pos = surface.get_center() + np.array([-1.2, 0.8, 0])
        x_prime_pos = surface.get_center() + np.array([0.3, -0.5, 0])
        
        # Create dots for x and x'
        x_dot = Dot(point=x_pos, color=BLACK, radius=0.12)
        x_prime_dot = Dot(point=x_prime_pos, color=BLACK, radius=0.12)
        
        # Labels
        x_label = MathTex(r"\mathbf{x}", font_size=32, color=BLACK).next_to(
            x_dot, UR, buff=0.15
        )
        x_prime_label = MathTex(r"\mathbf{x}'", font_size=32, color=BLACK).next_to(
            x_prime_dot, DL, buff=0.15
        )
        
        # Distance line δ
        delta_line = DashedLine(
            x_pos,
            x_prime_pos,
            color=RED,
            stroke_width=2.5
        )
        delta_label = MathTex(r"\delta", font_size=28, color=RED).next_to(
            delta_line.get_center(), UP, buff=0.1
        )
        
        # Highlight the dots
        self.play(
            Indicate(x_dot, color=BLUE, scale_factor=1.5),
            Write(x_label),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            Indicate(x_prime_dot, color=BLUE, scale_factor=1.5),
            Write(x_prime_label),
            run_time=1
        )
        self.wait(0.5)
        
        # Show distance
        self.play(
            Create(delta_line),
            Write(delta_label),
            run_time=1.5
        )
        
        # Explanation text
        explanation = Tex(
            "Two distinct prompts, 'x' and 'x'', separated by distance $\\delta > 0$.",
            font_size=28,
            color=WHITE
        ).to_corner(DL).shift(UP * 0.5 + RIGHT * 0.5)
        explanation_box = SurroundingRectangle(
            explanation,
            color=BLUE,
            buff=0.15,
            corner_radius=0.1
        )
        
        self.play(
            Write(explanation),
            Create(explanation_box),
            run_time=2
        )
        self.wait(2)
        
        self.play(
            FadeOut(explanation),
            FadeOut(explanation_box)
        )
        
        return x_dot, x_prime_dot, VGroup(delta_line, delta_label)
    
    def show_llm_mapping(self, prompt_space, latent_space, x_dot, x_prime_dot, delta):
        """Show the LLM mapping from Prompt Space to Latent Space."""
        axes = latent_space[0]
        
        # Calculate corresponding positions in latent space
        # Map x to z
        z_pos = axes.c2p(-1.5, 1.2)
        z_dot = Dot(point=z_pos, color=BLACK, radius=0.12)
        z_label = MathTex(r"\mathbf{z}", font_size=32, color=BLACK).next_to(
            z_dot, UR, buff=0.15
        )
        
        # Map x' to z'
        z_prime_pos = axes.c2p(1.2, -0.8)
        z_prime_dot = Dot(point=z_prime_pos, color=BLACK, radius=0.12)
        z_prime_label = MathTex(r"\mathbf{z}'", font_size=32, color=BLACK).next_to(
            z_prime_dot, DL, buff=0.15
        )
        
        # Distance line ε
        epsilon_line = DashedLine(
            z_pos,
            z_prime_pos,
            color=RED,
            stroke_width=2.5
        )
        epsilon_label = MathTex(r"\varepsilon", font_size=28, color=RED).next_to(
            epsilon_line.get_center(), DOWN, buff=0.1
        )
        
        # Create curved arrows showing the mapping
        arrow_x_to_z = CurvedArrow(
            x_dot.get_center(),
            z_dot.get_center(),
            color=BLUE,
            stroke_width=4,
            tip_length=0.3
        )
        arrow_x_prime_to_z_prime = CurvedArrow(
            x_prime_dot.get_center(),
            z_prime_dot.get_center(),
            color=BLUE,
            stroke_width=4,
            tip_length=0.3
        )
        
        # LLM label
        llm_label = Text(
            "LLM",
            font_size=32,
            color=BLUE,
            weight=BOLD
        ).move_to(
            (prompt_space[0].get_center() + axes.get_center()) / 2
        ).shift(UP * 1.5)
        
        llm_arrow = MathTex(r"\rightarrow", font_size=36, color=BLUE).next_to(
            llm_label, RIGHT, buff=0.2
        )
        
        # Animate the mapping
        self.play(
            Write(llm_label),
            Write(llm_arrow),
            run_time=1
        )
        self.wait(0.5)
        
        # Show x -> z mapping
        self.play(
            Create(arrow_x_to_z),
            run_time=1.5
        )
        self.play(
            FadeIn(z_dot, scale=0.5),
            Write(z_label),
            run_time=1
        )
        self.wait(0.5)
        
        # Show x' -> z' mapping
        self.play(
            Create(arrow_x_prime_to_z_prime),
            run_time=1.5
        )
        self.play(
            FadeIn(z_prime_dot, scale=0.5),
            Write(z_prime_label),
            run_time=1
        )
        self.wait(0.5)
        
        # Show distance ε
        self.play(
            Create(epsilon_line),
            Write(epsilon_label),
            run_time=1.5
        )
        
        # Explanation
        explanation = Tex(
            "The LLM maps prompt 'x' to latent representation 'z',",
            "and prompt 'x'' to latent representation 'z''.",
            font_size=26,
            color=WHITE
        ).to_corner(DL).shift(UP * 0.8 + RIGHT * 0.5)
        explanation_box = SurroundingRectangle(
            explanation,
            color=BLUE,
            buff=0.15,
            corner_radius=0.1
        )
        
        self.play(
            Write(explanation[0]),
            Create(explanation_box),
            run_time=1.5
        )
        self.play(
            Write(explanation[1]),
            run_time=1.5
        )
        self.wait(2)
        
        self.play(
            FadeOut(explanation),
            FadeOut(explanation_box)
        )
        
        return (
            z_dot,
            z_prime_dot,
            VGroup(epsilon_line, epsilon_label),
            VGroup(arrow_x_to_z, arrow_x_prime_to_z_prime, llm_label, llm_arrow)
        )
    
    def explain_injective_property(self, delta, epsilon):
        """Explain the injective property: δ > 0 ⇒ ε > 0."""
        # Create the mathematical statement
        injective_eq = MathTex(
            r"\delta > 0 \Rightarrow \varepsilon > 0",
            font_size=48,
            color=GREEN
        ).move_to(ORIGIN).shift(DOWN * 2.5)
        
        injective_box = SurroundingRectangle(
            injective_eq,
            color=GREEN,
            buff=0.3,
            corner_radius=0.2,
            stroke_width=3
        )
        
        # Explanation text
        explanation = VGroup(
            Text(
                "Injective Property:",
                font_size=32,
                color=GREEN,
                weight=BOLD
            ),
            Tex(
                "If two prompts are distinct ($\\delta > 0$),",
                font_size=28
            ),
            Tex(
                "then their latent representations are also distinct ($\\varepsilon > 0$).",
                font_size=28
            ),
            Tex(
                "No two different prompts map to the same latent representation.",
                font_size=26,
                color=YELLOW
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(
            injective_eq, UP, buff=0.8
        )
        
        # Animate
        self.play(
            Write(explanation[0]),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            Write(explanation[1]),
            Write(explanation[2]),
            run_time=2
        )
        self.wait(1)
        
        self.play(
            Create(injective_box),
            Write(injective_eq),
            run_time=2
        )
        self.wait(1)
        
        self.play(
            Write(explanation[3]),
            run_time=2
        )
        self.wait(2)
        
        # Highlight the distances
        self.play(
            Indicate(delta, color=GREEN, scale_factor=1.2),
            Indicate(epsilon, color=GREEN, scale_factor=1.2),
            run_time=2
        )
        self.wait(2)
        
        # Store for later cleanup
        self.injective_components = VGroup(
            explanation, injective_eq, injective_box
        )
    
    def show_sipit_inversion(self, latent_space, prompt_space, z_dot, x_dot):
        """Show the SiPIT inversion mapping from Latent Space back to Prompt Space."""
        axes = latent_space[0]
        
        # Create curved arrow showing inversion
        arrow_z_to_x = CurvedArrow(
            z_dot.get_center(),
            x_dot.get_center(),
            color=PURPLE,
            stroke_width=4,
            tip_length=0.3
        )
        
        # SiPIT label
        sipit_label = Text(
            "SiPIT",
            font_size=32,
            color=PURPLE,
            weight=BOLD
        ).move_to(
            (prompt_space[0].get_center() + axes.get_center()) / 2
        ).shift(DOWN * 1.5)
        
        sipit_arrow = MathTex(r"\leftarrow", font_size=36, color=PURPLE).next_to(
            sipit_label, LEFT, buff=0.2
        )
        
        # Explanation
        explanation = VGroup(
            Text(
                "The Challenge: Can we reverse this process?",
                font_size=28,
                color=PURPLE,
                weight=BOLD
            ),
            Tex(
                "SiPIT aims to invert the LLM's mapping,",
                font_size=26
            ),
            Tex(
                "taking a latent representation and reconstructing the original prompt.",
                font_size=26
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(DR).shift(LEFT * 0.5 + UP * 0.5)
        
        explanation_box = SurroundingRectangle(
            explanation,
            color=PURPLE,
            buff=0.15,
            corner_radius=0.1
        )
        
        # Animate
        self.play(
            Write(explanation[0]),
            Create(explanation_box),
            run_time=1.5
        )
        self.wait(1)
        
        self.play(
            Write(sipit_label),
            Write(sipit_arrow),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            Create(arrow_z_to_x),
            run_time=2
        )
        self.wait(1)
        
        self.play(
            Write(explanation[1]),
            Write(explanation[2]),
            run_time=2
        )
        
        # Highlight the path
        self.play(
            ShowPassingFlash(
                arrow_z_to_x.copy().set_color(WHITE),
                time_width=0.8
            ),
            Indicate(z_dot, color=PURPLE, scale_factor=1.5),
            Indicate(x_dot, color=PURPLE, scale_factor=1.5),
            run_time=2
        )
        self.wait(2)
        
        # Store for later
        self.sipit_components = VGroup(
            arrow_z_to_x, sipit_label, sipit_arrow, explanation, explanation_box
        )
    
    def show_conclusion(self):
        """Show the concluding caption."""
        # Fade out injective property explanation
        if hasattr(self, 'injective_components'):
            self.play(
                FadeOut(self.injective_components),
                run_time=1
            )
        
        # Create caption
        caption = Tex(
            "Figure 1: The map from prompts to latent space is injective. SiPIT inverts it.",
            font_size=32,
            color=WHITE
        ).to_edge(DOWN).shift(UP * 0.3)
        
        caption_box = SurroundingRectangle(
            caption,
            color=BLUE,
            buff=0.2,
            corner_radius=0.1
        )
        
        # Summary points
        summary = VGroup(
            Text(
                "Summary:",
                font_size=32,
                color=BLUE,
                weight=BOLD
            ),
            Tex(
                r"1. LLM creates an injective map: distinct prompts → distinct embeddings",
                font_size=24
            ),
            Tex(
                r"2. Injective property ensures: $\delta > 0 \Rightarrow \varepsilon > 0$",
                font_size=24
            ),
            Tex(
                r"3. SiPIT provides the mechanism to invert this mapping",
                font_size=24
            ),
            Tex(
                r"4. This allows reconstruction of prompts from their latent forms",
                font_size=24
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(
            caption, UP, buff=0.8
        )
        
        # Animate
        self.play(
            Write(summary[0]),
            run_time=1
        )
        self.wait(0.5)
        
        for i in range(1, len(summary)):
            self.play(
                Write(summary[i]),
                run_time=1.5
            )
            self.wait(0.5)
        
        self.play(
            Create(caption_box),
            Write(caption),
            run_time=2
        )
        self.wait(3)
        
        # Final emphasis
        self.play(
            Flash(caption_box, color=BLUE, line_length=0.5),
            Flash(summary[0], color=BLUE, line_length=0.3),
            run_time=2
        )
        self.wait(2)


class PromptLatentSpaceDetailed(Scene):
    """
    A more detailed version with additional scenes breaking down each concept.
    Can be used for educational purposes with step-by-step explanations.
    """
    
    def construct(self):
        # This would contain even more detailed scenes
        # For now, we'll use the main scene above
        pass
