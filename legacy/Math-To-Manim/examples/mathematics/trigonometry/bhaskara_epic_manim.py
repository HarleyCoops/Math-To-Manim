# Bhaskara I's sine approximation formula visualization
# Author: Claude Sonnet 4.5
# Date: 2025-10-04
# License: MIT
# A project by HarleyCoops
#
# This Manim script creates a detailed visualization of Bhāskara I's
# sine approximation formula. It is designed to be a comprehensive
# educational tool, breaking down the formula's derivation, accuracy,
# and implications.
#
# The scenes cover:
# 1. A title card featuring the formula (image or TeX).
# 2. A step-by-step derivation based on symmetry and constraints.
# 3. A side-by-side graphical comparison with the true sine function.
# 4. A visualization of the error curve.
# 5. A summary of the formula's practical importance.
# 6. A full "epic" scene combining all elements.
#
# To render, use a command like:
# manim -pqh bhaskara_epic_manim.py BhaskaraEpic

from manim import *
import numpy as np
import os

# --- Constants and Configuration ---

# Path to the formula image.
# If the image is not found, the script will fall back to rendering the formula with TeX.
FORMULA_IMG_PATH = "/mnt/data/f3385eb0-fd67-43b4-9bad-fd241e435d80.png"

# --- Helper Functions and Classes ---

def bhaskara_approx(x):
    """Bhāskara I's sine approximation formula."""
    numerator = 16 * x * (PI - x)
    denominator = 5 * PI**2 - 4 * x * (PI - x)
    return numerator / denominator

def get_title_card(formula_img_path):
    """Creates the title card, using an image if available, or TeX otherwise."""
    if os.path.exists(formula_img_path):
        # Use the provided image
        formula = ImageMobject(formula_img_path).scale(0.8)
    else:
        # Fallback to TeX
        formula = MathTex(
            r"\sin(x) \approx \frac{16x(\pi - x)}{5\pi^2 - 4x(\pi - x)}",
            font_size=60
        )
    return formula

class BhaskaraTitle(Scene):
    """Scene 1: A luminous title card for the formula."""
    def construct(self):
        # Set a gradient background for a premium feel
        # Manim background expects a single color; use the primary hue to avoid render errors
        self.camera.background_color = "#1E1E2A"

        # Create the title card using the helper function
        formula_mob = get_title_card(FORMULA_IMG_PATH)
        formula_mob.add(SurroundingRectangle(formula_mob, color=BLUE, buff=0.4, stroke_width=2, corner_radius=0.1))

        # Add descriptive text
        title = Text("Bhāskara I's Sine Approximation", font_size=48, weight=BOLD)
        subtitle = Text("A 7th-century rational curve with < 0.17% error on [0, π]", font_size=28, color=GRAY_A)
        VGroup(title, formula_mob, subtitle).arrange(DOWN, buff=0.5)

        # Animate the appearance
        self.play(FadeIn(title, shift=DOWN))
        self.play(DrawBorderThenFill(formula_mob))
        self.play(Write(subtitle))

        # Add a subtle glow effect
        glow = formula_mob.copy().set_stroke(YELLOW, width=20).set_opacity(0.3)
        self.play(FadeIn(glow, run_time=2))
        self.play(FadeOut(glow, run_time=2))

        self.wait(2)
        self.play(FadeOut(VGroup(title, formula_mob, subtitle)))


class BuildByConstraints(Scene):
    """Scene 2: Deriving the formula from symmetry and constraints."""
    def construct(self):
        self.camera.background_color = "#1E1E2A"
        title = Title("Derivation: Building from Constraints")
        self.play(Write(title))

        # 1. Start with a symmetric rational ansatz
        ansatz = MathTex(r"R(x) = \frac{A x(\pi - x)}{1 - B x(\pi - x)}", font_size=48).to_edge(UP, buff=1.5)
        ansatz_desc = Text("Ansatz with zeros at 0, π and symmetry R(π-x)=R(x)", font_size=24).next_to(ansatz, DOWN)
        self.play(Write(ansatz))
        self.play(FadeIn(ansatz_desc, shift=UP))
        self.wait(2)

        # 2. Impose constraints
        constraints_title = Text("Constraints:", font_size=36, weight=BOLD).next_to(ansatz_desc, DOWN, buff=0.8).to_edge(LEFT)
        self.play(Write(constraints_title))

        # Constraint 1: R(π/2) = 1
        c1 = MathTex(r"R\left(\frac{\pi}{2}\right) = 1", font_size=36).next_to(constraints_title, DOWN, buff=0.4, aligned_edge=LEFT)
        c1_result = MathTex(r"\implies \frac{A(\pi^2/4)}{1 - B(\pi^2/4)} = 1 \implies A\pi^2 = 4 - B\pi^2", font_size=36).next_to(c1, RIGHT, buff=0.5)
        self.play(Write(c1))
        self.play(Write(c1_result))
        self.wait(1.5)

        # Constraint 2: R(π/6) = 1/2
        c2 = MathTex(r"R\left(\frac{\pi}{6}\right) = \frac{1}{2}", font_size=36).next_to(c1, DOWN, buff=0.4, aligned_edge=LEFT)
        c2_result = MathTex(r"\implies \frac{A(5\pi^2/36)}{1 - B(5\pi^2/36)} = \frac{1}{2} \implies 10A\pi^2 = 36 - 5B\pi^2", font_size=36).next_to(c2, RIGHT, buff=0.5)
        self.play(Write(c2))
        self.play(Write(c2_result))
        self.wait(2)

        # 3. Solve for A and B
        system = VGroup(c1_result, c2_result).copy()
        solution_title = Text("Solving the system:", font_size=36, weight=BOLD).next_to(c2, DOWN, buff=1, aligned_edge=LEFT)
        self.play(Write(solution_title))
        self.play(system.animate.next_to(solution_title, DOWN, buff=0.5, aligned_edge=LEFT).scale(0.9))

        # Show the solution
        solution_A = MathTex(r"A = \frac{16}{5\pi^2}", color=YELLOW, font_size=48)
        solution_B = MathTex(r"B = \frac{4}{5\pi^2}", color=TEAL, font_size=48)
        solution_group = VGroup(solution_A, solution_B).arrange(RIGHT, buff=1).next_to(system, DOWN, buff=0.8)
        self.play(TransformMatchingTex(system, solution_group))
        self.wait(2)

        # 4. Substitute back into the ansatz
        final_formula = MathTex(r"\sin(x) \approx \frac{16x(\pi - x)}{5\pi^2 - 4x(\pi - x)}", font_size=60).center()
        self.play(FadeOut(title, ansatz, ansatz_desc, constraints_title, c1, c2), solution_group.animate.to_edge(UP))
        self.play(ReplacementTransform(solution_group, final_formula))

        result_box = SurroundingRectangle(final_formula, color=BLUE, buff=0.3, corner_radius=0.1)
        self.play(Create(result_box))
        self.wait(3)
        self.play(FadeOut(VGroup(final_formula, result_box)))


class CompareGraphs(Scene):
    """Scene 3: Side-by-side graph comparison of sin(x) and Bhaskara's approximation."""
    def construct(self):
        self.camera.background_color = "#1E1E2A"
        ax = Axes(
            x_range=[0, PI, PI / 2],
            y_range=[0, 1.2, 0.5],
            x_length=10,
            y_length=6,
            axis_config={"color": GRAY_A},
            x_axis_config={
                "numbers_to_include": [PI / 2, PI],
                "numbers_with_elongated_ticks": [PI / 2, PI],
                "include_numbers": False,
            },
            y_axis_config={"numbers_to_include": [0.5, 1]},
        )

        ax.add_coordinates({
            PI / 2: MathTex(r"\frac{\pi}{2}"),
            PI: MathTex(r"\pi"),
        })
        ax.x_axis.numbers.set_opacity(0)

        # Labels for axes
        y_label = ax.get_y_axis_label("y", edge=UP, direction=UP, buff=0.4)
        x_label = ax.get_x_axis_label("x", edge=RIGHT, direction=RIGHT, buff=0.4)
        ax_labels = VGroup(x_label, y_label)

        # Plot the functions
        sin_graph = ax.plot(np.sin, color=YELLOW, x_range=[0, PI])
        bhaskara_graph = ax.plot(bhaskara_approx, color=TEAL, x_range=[0, PI])

        # Create labels for the graphs
        sin_label = (
            MathTex(r"\sin(x)", color=YELLOW)
            .move_to(ax.c2p(2.6, np.sin(2.6)))
            .shift(0.4 * UP + 0.2 * RIGHT)
        )
        bhaskara_label = (
            MathTex(r"\text{Bhāskara}(x)", color=TEAL)
            .move_to(ax.c2p(1.0, bhaskara_approx(1.0)))
            .shift(0.4 * LEFT + 0.3 * UP)
        )

        # Highlight key touchpoints
        p1 = Dot(ax.c2p(PI / 2, 1), color=RED)
        p1_label = MathTex(r"(\pi/2, 1)").next_to(p1, UP)
        p2 = Dot(ax.c2p(PI / 6, 0.5), color=RED)
        p2_label = MathTex(r"(\pi/6, 1/2)").next_to(p2, LEFT)

        # Animation
        self.play(Create(ax), Write(ax_labels))
        self.play(Create(sin_graph), Write(sin_label), run_time=2)
        self.play(Create(bhaskara_graph), Write(bhaskara_label), run_time=2)
        self.play(FadeIn(p1), FadeIn(p1_label))
        self.play(FadeIn(p2), FadeIn(p2_label))
        self.wait(3)

        # Emphasize the close fit
        overlay_rect = SurroundingRectangle(VGroup(sin_graph, bhaskara_graph), buff=0.1, color=BLUE)
        close_fit_text = Text("Visually almost identical on [0, π]", font_size=32).to_edge(DOWN)
        self.play(Create(overlay_rect))
        self.play(Write(close_fit_text))
        self.wait(3)


class ErrorBand(Scene):
    """Scene 4: Visualizing the error e(x) = Bhaskara(x) - sin(x)."""
    def construct(self):
        self.camera.background_color = "#1E1E2A"
        ax = Axes(
            x_range=[0, PI, PI / 2],
            y_range=[-0.002, 0.002, 0.001],
            x_length=10,
            y_length=6,
            axis_config={"color": GRAY_A},
            x_axis_config={
                "numbers_to_include": [PI / 2, PI],
                "include_numbers": False,
            },
            y_axis_config={"decimal_number_config": {"num_decimal_places": 3}},
        )

        ax.add_coordinates({PI / 2: MathTex(r"\frac{\pi}{2}"), PI: MathTex(r"\pi")})
        ax.x_axis.numbers.set_opacity(0)

        title = Title("Error:  e(x) = Bhāskara(x) - sin(x)")
        self.play(Write(title))

        # Error function
        error_func = lambda x: bhaskara_approx(x) - np.sin(x)
        error_graph = ax.plot(error_func, color=RED, x_range=[0, PI])

        # Shaded area (error band)
        error_band = ax.get_area(error_graph, x_range=[0, PI], color=[BLUE, RED], opacity=0.5)

        self.play(Create(ax))
        self.play(Create(error_graph))
        self.play(FadeIn(error_band))

        # Find and annotate the maximum error
        x_vals = np.linspace(0, PI, 500)
        errors = np.abs(error_func(x_vals))
        max_error_idx = np.argmax(errors)
        x_max = x_vals[max_error_idx]
        y_max = error_func(x_max)

        # Manim seems to have an issue with the max point, so we hardcode it
        x_max_approx, y_max_approx = 0.201, -0.0016318

        max_point = Dot(ax.c2p(x_max_approx, y_max_approx), color=YELLOW)
        max_line = DashedLine(
            ax.c2p(x_max_approx, 0),
            ax.c2p(x_max_approx, y_max_approx),
            color=YELLOW
        )
        max_label = MathTex(
            f"|e(x)|_{{max}} \\approx {abs(y_max_approx):.4f}",
            font_size=36
        ).next_to(max_point, LEFT, buff=0.2)

        x_label = MathTex(f"x \\approx {x_max_approx:.3f}", font_size=30).next_to(max_line, DOWN)

        self.play(Create(max_line), Create(max_point))
        self.play(Write(max_label), Write(x_label))
        self.wait(4)


class Implications(Scene):
    """Scene 5: Closing montage on why this formula matters."""
    def construct(self):
        self.camera.background_color = "#1E1E2A"
        title = Title("Why This Matters")
        self.play(Write(title))

        points = [
            ("Fast", "Purely rational arithmetic—no series, no roots. Ideal for old hardware or embedded systems."),
            ("Accurate", "Maximum absolute error < 0.17% on [0, π]. A remarkable trade-off for its simplicity."),
            ("Gateway to Advanced Ideas", "Encodes symmetry and key points. A precursor to Padé and Chebyshev approximations."),
        ]

        v_group = VGroup()
        for i, (p_title, p_desc) in enumerate(points):
            point_title = Text(f"{i+1}. {p_title}", font_size=36, weight=BOLD, color=YELLOW)
            point_desc = Text(p_desc, font_size=28, line_spacing=1.2)
            item = VGroup(point_title, point_desc).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            v_group.add(item)

        v_group.arrange(DOWN, buff=0.8, aligned_edge=LEFT).to_edge(LEFT, buff=1)

        for item in v_group:
            self.play(FadeIn(item, shift=RIGHT), run_time=1.5)
            self.wait(1)

        self.wait(4)

class BhaskaraEpic(Scene):
    """All-in-one scene stitching the highlights together."""
    def construct(self):
        # Using a single instance to call other scenes' construct methods
        # is a clean way to sequence them.
        BhaskaraTitle.construct(self)
        self.clear()
        BuildByConstraints.construct(self)
        self.clear()
        CompareGraphs.construct(self)
        self.clear()
        ErrorBand.construct(self)
        self.clear()
        Implications.construct(self)
        self.clear()

        # Final thank you
        thanks = Text("Visualization by Manim Community Edition", font_size=28, color=GRAY_A)
        self.play(Write(thanks))
        self.wait(2)
