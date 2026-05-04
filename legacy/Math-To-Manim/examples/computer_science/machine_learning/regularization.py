# regularization_viz.py
# Requires Manim Community v0.19.0
# Run using: manim -pql regularization_viz.py SceneName

from manim import (
    Scene, Tex, MathTex, Axes, Dot, Ellipse, Circle, Polygon, VGroup,
    Create, Write, FadeIn, Indicate, FadeOut, ShowPassingFlash, Transform, MoveAlongPath,
    ValueTracker, DecimalNumber, Line,
    StealthTip, linear
)
import numpy as np

# --- Define Constants Directly ---
# Directions
UP = np.array([0., 1., 0.])
DOWN = np.array([0., -1., 0.])
RIGHT = np.array([1., 0., 0.])
LEFT = np.array([-1., 0., 0.])
UR = np.array([1., 1., 0.])
UL = np.array([-1., 1., 0.])
DR = np.array([1., -1., 0.])
DL = np.array([-1., -1., 0.])
ORIGIN = np.array([0., 0., 0.])

# Math
PI = np.pi

# Colors (Hex Codes)
BLACK = "#000000"
WHITE = "#FFFFFF"
GRAY = "#888888"
CYAN = "#00FFFF"
ORANGE = "#FFA500"
PURPLE = "#800080"
YELLOW = "#FFFF00"
BLUE_D = "#236B8E"
BLUE_C = "#58C4DD"
BLUE_A = "#84C6E6"
GREEN_B = "#6BC26A"
YELLOW_C = "#F7D379"
RED_A = "#FF6B6B"
RED_C = "#D72626"

# --- Configuration ---
AXES_CONFIG = {
    "x_range": [-4, 4, 1],
    "y_range": [-4, 4, 1],
    "x_length": 7,
    "y_length": 7,
    "axis_config": {"include_numbers": True, "tip_shape": StealthTip},
    "x_axis_config": {"label_direction": DOWN},
    "y_axis_config": {"label_direction": LEFT},
}
LOSS_MIN_COLOR = BLACK
LOSS_CONTOUR_COLORS = [BLUE_D, BLUE_C, BLUE_A, GREEN_B, YELLOW_C, RED_A, RED_C] # Approx gradient
UNREG_DOT_COLOR = BLACK
L1_HARD_COLOR = CYAN
L2_HARD_COLOR = CYAN
L1_PENALTY_COLOR = ORANGE
L2_PENALTY_COLOR = ORANGE
L1_SOL_COLOR = PURPLE # Using PURPLE for solutions as requested
L2_SOL_COLOR = PURPLE

# --- Helper Functions ---
def get_ellipse_contours(center, width, height, angle, num_levels=5, scale_factor=1.5):
    """Creates a VGroup of ellipses representing contours."""
    contours = VGroup()
    for i in range(1, num_levels + 1):
        ellipse = Ellipse(
            width=width * (scale_factor ** (i - 1)),
            height=height * (scale_factor ** (i - 1)),
            color=LOSS_CONTOUR_COLORS[i % len(LOSS_CONTOUR_COLORS)], # Cycle through colors
            stroke_width=2.5
        ).move_to(center).rotate(angle)
        contours.add(ellipse)
    return contours

def get_l2_penalty_contours(radius, num_levels=4, scale_factor=1.3):
    """Creates a VGroup of circles for L2 penalty."""
    contours = VGroup()
    for i in range(1, num_levels + 1):
        circle = Circle(
            radius=radius * (scale_factor ** (i - 1)),
            color=L2_PENALTY_COLOR,
            stroke_width=2.0,
            stroke_opacity=0.7
        ).move_to(ORIGIN)
        contours.add(circle)
    return contours

def get_l1_penalty_contours(size, num_levels=4, scale_factor=1.3):
    """Creates a VGroup of diamonds for L1 penalty."""
    contours = VGroup()
    for i in range(1, num_levels + 1):
        s = size * (scale_factor ** (i-1))
        diamond = Polygon(
            [s, 0, 0], [0, s, 0], [-s, 0, 0], [0, -s, 0],
            color=L1_PENALTY_COLOR,
            stroke_width=2.0,
            stroke_opacity=0.7
        ).move_to(ORIGIN)
        contours.add(diamond)
    return contours

# --- Scenes ---

class Scene1(Scene):
    """Scene 1: Setup and Non-Regularized Loss"""
    def construct(self):
        # Title
        title = Tex("Regularization Visualization", font_size=48).to_edge(UP)
        scene_title = Tex("Scene 1: The Loss Landscape", font_size=36).next_to(title, DOWN)
        self.play(Write(title), Write(scene_title))
        self.wait(1)

        # Axes
        axes = Axes(
            **AXES_CONFIG
        ).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label=MathTex("w_1"), y_label=MathTex("w_2"))
        self.play(Create(axes), Write(axes_labels))
        self.wait(0.5)

        # Loss function minimum
        loss_min_coords = axes.c2p(2.5, 1.5) # Coordinates in plot space
        loss_min_dot = Dot(point=loss_min_coords, color=UNREG_DOT_COLOR, radius=0.1)
        loss_min_label = MathTex(r"w_{OLS}", font_size=30).next_to(loss_min_dot, UR, buff=0.1)

        # Loss contours (Ellipses)
        loss_contours = get_ellipse_contours(
            center=loss_min_coords,
            width=0.5,  # Base width
            height=1.0, # Base height
            angle=PI / 6, # Rotation angle
            num_levels=5,
            scale_factor=1.6
        )

        self.play(FadeIn(loss_contours, shift=UP*0.5), run_time=1.5)
        self.play(Create(loss_min_dot), Write(loss_min_label))
        self.wait(1)

        # Explanation Text
        explanation = Tex(
            r"This represents the loss function $L(w)$.",
            r"Lower loss (more blue) is better.",
            r"The black dot ($w_{OLS}$) is the minimum loss",
            r"point without regularization (Ordinary Least Squares).",
            font_size=32
        ).to_corner(DR).shift(LEFT*0.5)
        explanation.set_color_by_tex("loss function", YELLOW)

        self.play(Write(explanation[0]))
        self.wait(1)
        self.play(Write(explanation[1]))
        # Indicate blue region briefly
        self.play(Indicate(loss_contours[0], color=BLUE_D, scale_factor=1.1), run_time=1)
        self.wait(0.5)
        self.play(Write(explanation[2]))
        self.play(Write(explanation[3]))
        self.play(Indicate(loss_min_dot, color=WHITE, scale_factor=1.5), run_time=1)
        self.wait(3)

        # Fade out explanation for next scene if running sequentially
        # self.play(FadeOut(explanation), FadeOut(title), FadeOut(scene_title))
        # self.wait()

class Scene2(Scene):
    """Scene 2: Conceptual Hard Constraints"""
    def construct(self):
        # Title
        title = Tex("Scene 2: Conceptual 'Hard' Constraints", font_size=40).to_edge(UP)
        self.play(Write(title))

        # Axes and Loss (recreated quickly)
        axes = Axes(**AXES_CONFIG).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label=MathTex("w_1"), y_label=MathTex("w_2"))
        loss_min_coords = axes.c2p(2.5, 1.5)
        loss_min_dot = Dot(point=loss_min_coords, color=UNREG_DOT_COLOR, radius=0.1)
        loss_min_label = MathTex(r"w_{OLS}", font_size=30).next_to(loss_min_dot, UR, buff=0.1)
        loss_contours = get_ellipse_contours(loss_min_coords, 0.5, 1.0, PI / 6, 5, 1.6)
        self.add(axes, axes_labels, loss_contours, loss_min_dot, loss_min_label)
        self.wait(0.5)

        # --- L2 Ridge ---
        l2_radius = 2.0 # Radius of constraint in plot units
        l2_constraint = Circle(
            radius=l2_radius,
            color=L2_HARD_COLOR,
            stroke_width=3
        ).move_to(axes.c2p(0,0))
        l2_label = MathTex(r"||w||_2^2 \le t", font_size=36, color=L2_HARD_COLOR)\
            .next_to(l2_constraint, UP, buff=0.2).shift(RIGHT*l2_radius*0.8)

        explanation_l2 = Tex(r"L2 (Ridge): Constrain $w$ inside a circle.",
                              r"Find lowest loss point touching the boundary.", font_size=32)\
                              .to_corner(DR).shift(LEFT*0.5)

        self.play(Write(explanation_l2[0]))
        self.play(Create(l2_constraint), Write(l2_label))
        self.wait(1)

        # Approximate L2 solution point (tangent)
        # Visual approximation: point on circle closest to loss_min_dot
        vec_to_min = loss_min_coords - axes.c2p(0,0)
        l2_sol_point_coords = axes.c2p(0,0) + vec_to_min * (l2_radius / np.linalg.norm(vec_to_min))
        l2_sol_dot = Dot(point=l2_sol_point_coords, color=L2_SOL_COLOR, radius=0.1)
        l2_sol_label = MathTex(r"w_{L2}", font_size=30, color=L2_SOL_COLOR)\
            .next_to(l2_sol_dot, DL, buff=0.1)

        # Show contour touching
        touching_contour_l2 = Ellipse(
             width=loss_contours[2].width, # Use an existing contour size for visual consistency
             height=loss_contours[2].height,
             color=loss_contours[2].get_color(),
             stroke_width=3
         ).move_to(loss_min_coords).rotate(PI / 6)
        # We need to shift this contour so it becomes tangent
        # This is complex, so we approximate by placing the dot and implying tangency
        self.play(Write(explanation_l2[1]))
        self.play(loss_contours.animate.set_opacity(0.3), run_time=0.5) # Dim background contours
        self.play(ShowPassingFlash(l2_constraint.copy().set_color(WHITE), time_width=0.5),
                  Create(l2_sol_dot), Write(l2_sol_label), run_time=1.5)
        self.play(Indicate(l2_sol_dot, color=WHITE, scale_factor=1.5))
        self.wait(2)

        # Clear L2 elements
        l2_group = VGroup(l2_constraint, l2_label, l2_sol_dot, l2_sol_label, explanation_l2)
        self.play(FadeOut(l2_group), loss_contours.animate.set_opacity(1.0))
        self.wait(0.5)

        # --- L1 Lasso ---
        l1_size = 1.8 # Defines the vertices (+- size, 0), (0, +- size)
        l1_constraint = Polygon(
            axes.c2p(l1_size, 0), axes.c2p(0, l1_size), axes.c2p(-l1_size, 0), axes.c2p(0, -l1_size),
            color=L1_HARD_COLOR, stroke_width=3
        )
        l1_label = MathTex(r"||w||_1 \le t", font_size=36, color=L1_HARD_COLOR)\
            .next_to(l1_constraint, UP, buff=0.2).shift(RIGHT*l1_size*0.8)

        explanation_l1 = Tex(r"L1 (Lasso): Constrain $w$ inside a diamond.",
                              r"Corners are often the optimal points.", font_size=32)\
                              .to_corner(DR).shift(LEFT*0.5)

        self.play(Write(explanation_l1[0]))
        self.play(Create(l1_constraint), Write(l1_label))
        self.wait(1)

        # Approximate L1 solution point (often a corner)
        # Find corner closest to the loss minimum
        corners = [axes.c2p(l1_size, 0), axes.c2p(0, l1_size), axes.c2p(-l1_size, 0), axes.c2p(0, -l1_size)]
        distances = [np.linalg.norm(loss_min_coords - c) for c in corners]
        l1_sol_point_coords = corners[np.argmin(distances)] # Closest corner
        # Adjust slightly if the minimum is exactly between corners for better visualization
        if np.isclose(l1_sol_point_coords[0], 0): # On y-axis
             l1_sol_point_coords = axes.c2p(0, l1_size) # Force to upper corner if min is upper right

        l1_sol_dot = Dot(point=l1_sol_point_coords, color=L1_SOL_COLOR, radius=0.1)
        l1_sol_label = MathTex(r"w_{L1}", font_size=30, color=L1_SOL_COLOR)\
            .next_to(l1_sol_dot, DR, buff=0.1)

        self.play(Write(explanation_l1[1]))
        self.play(loss_contours.animate.set_opacity(0.3), run_time=0.5)
        self.play(ShowPassingFlash(l1_constraint.copy().set_color(WHITE), time_width=0.5),
                  Create(l1_sol_dot), Write(l1_sol_label), run_time=1.5)
        self.play(Indicate(l1_sol_dot, color=WHITE, scale_factor=1.5))
        self.wait(2)

        # Transition Text
        l1_group = VGroup(l1_constraint, l1_label, l1_sol_dot, l1_sol_label, explanation_l1)
        self.play(FadeOut(l1_group), loss_contours.animate.set_opacity(1.0))
        self.wait(0.5)

        transition_text = Tex("This is conceptual.", "Implementation uses 'soft' penalties.", font_size=36).center()
        transition_text[0].shift(UP*0.5)
        transition_text[1].shift(DOWN*0.5)

        self.play(Write(transition_text))
        self.wait(3)

        # Fade out for next scene
        # self.play(FadeOut(transition_text), FadeOut(title))
        # self.wait()

class Scene3(Scene):
    """Scene 3: Implementation with Soft Constraints"""
    def construct(self):
        # Title
        title = Tex("Scene 3: Implementation 'Soft' Constraints (Penalties)", font_size=40).to_edge(UP)
        self.play(Write(title))

        # Axes and Loss (recreated)
        axes = Axes(**AXES_CONFIG).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label=MathTex("w_1"), y_label=MathTex("w_2"))
        loss_min_coords = axes.c2p(2.5, 1.5)
        loss_min_dot = Dot(point=loss_min_coords, color=UNREG_DOT_COLOR, radius=0.1)
        loss_min_label = MathTex(r"w_{OLS}", font_size=30).next_to(loss_min_dot, UR, buff=0.1)
        loss_contours = get_ellipse_contours(loss_min_coords, 0.5, 1.0, PI / 6, 5, 1.6)
        origin_dot = Dot(axes.c2p(0,0), radius=0.05, color=GRAY)
        self.add(axes, axes_labels, loss_contours, loss_min_dot, loss_min_label, origin_dot)
        self.wait(0.5)

        # Lambda value (fixed for this scene)
        lambda_val = 0.8
        lambda_tex = MathTex(r"\lambda =", f"{lambda_val:.1f}", font_size=36).to_corner(UL)
        self.play(Write(lambda_tex))

        # --- L2 Ridge Implementation ---
        l2_penalty_contours = get_l2_penalty_contours(radius=0.5, num_levels=5, scale_factor=1.5)
        l2_penalty_label = MathTex(r"\lambda ||w||_2^2", color=L2_PENALTY_COLOR, font_size=36)\
            .next_to(l2_penalty_contours[-1], DOWN, buff=0.2)

        explanation_l2 = Tex(r"Add L2 penalty: $\lambda ||w||_2^2$",
                              r"Combined Loss = $L(w) + \lambda ||w||_2^2$",
                              r"Minimum shifts towards origin.", font_size=32)\
                              .to_corner(DR).shift(LEFT*0.5)

        self.play(Write(explanation_l2[0]))
        self.play(FadeIn(l2_penalty_contours), Write(l2_penalty_label), run_time=1.5)
        self.wait(1)

        # Calculate approximate L2 soft solution
        # For quadratic loss, it moves along the line connecting origin and w_OLS
        # The amount depends on lambda and the Hessian (shape of contours)
        # Approximation: move partway towards the origin. Stronger pull for higher lambda.
        shift_factor_l2 = 1.0 / (1.0 + lambda_val * 0.5) # Heuristic shift factor
        l2_sol_soft_coords = axes.c2p(0,0) + (loss_min_coords - axes.c2p(0,0)) * shift_factor_l2
        l2_sol_soft_dot = Dot(point=l2_sol_soft_coords, color=L2_SOL_COLOR, radius=0.1)
        l2_sol_soft_label = MathTex(r"w_{L2}", font_size=30, color=L2_SOL_COLOR)\
            .next_to(l2_sol_soft_dot, DL, buff=0.1)

        # Show shift
        loss_contours_copy = loss_contours.copy().set_opacity(0.3)
        loss_min_dot_copy = loss_min_dot.copy()
        self.add(loss_contours_copy) # Keep original contours faded in background

        self.play(Write(explanation_l2[1]))
        self.play(
            Transform(loss_contours, loss_contours.copy().move_to(l2_sol_soft_coords)), # Animate contours shifting center
            Transform(loss_min_dot, l2_sol_soft_dot), # Animate dot moving
            FadeOut(loss_min_label), # Fade old label
            Write(l2_sol_soft_label), # Write new label
            run_time=2.0
        )
        self.play(Write(explanation_l2[2]))
        self.play(Indicate(l2_sol_soft_dot, color=WHITE, scale_factor=1.5))
        self.wait(2)

        # Clean up L2 elements, restore original loss
        l2_impl_group = VGroup(l2_penalty_contours, l2_penalty_label, explanation_l2)
        self.play(FadeOut(l2_impl_group))
        # Restore original loss for L1 explanation
        self.play(
            Transform(loss_contours, loss_contours_copy),
            Transform(loss_min_dot, loss_min_dot_copy),
            FadeOut(l2_sol_soft_label),
            FadeIn(loss_min_label),
            run_time=1.0
        )
        self.remove(loss_contours_copy, loss_min_dot_copy) # Clean up copies
        self.wait(1)

        # --- L1 Lasso Implementation ---
        l1_penalty_contours = get_l1_penalty_contours(size=0.4, num_levels=5, scale_factor=1.5)
        l1_penalty_label = MathTex(r"\lambda ||w||_1", color=L1_PENALTY_COLOR, font_size=36)\
            .next_to(l1_penalty_contours[-1], DOWN, buff=0.2).shift(RIGHT*0.5)

        explanation_l1 = Tex(r"Add L1 penalty: $\lambda ||w||_1$",
                              r"Combined Loss = $L(w) + \lambda ||w||_1$",
                              r"Minimum shifts, often towards axes.", font_size=32)\
                              .to_corner(DR).shift(LEFT*0.5)

        self.play(Write(explanation_l1[0]))
        self.play(FadeIn(l1_penalty_contours), Write(l1_penalty_label), run_time=1.5)
        self.wait(1)

        # Calculate approximate L1 soft solution
        # This path is more complex (piecewise). Approximating a point partway,
        # possibly closer to an axis than L2. For this loss_min, it likely won't be exactly on axis yet.
        shift_factor_l1_x = 1.0 / (1.0 + lambda_val * 0.8) # Heuristic, stronger pull maybe
        shift_factor_l1_y = 1.0 / (1.0 + lambda_val * 0.4) # Different pull per axis possible
        l1_sol_soft_coords = axes.c2p(
            axes.p2c(loss_min_coords)[0] * shift_factor_l1_x,
            axes.p2c(loss_min_coords)[1] * shift_factor_l1_y
        )

        l1_sol_soft_dot = Dot(point=l1_sol_soft_coords, color=L1_SOL_COLOR, radius=0.1)
        l1_sol_soft_label = MathTex(r"w_{L1}", font_size=30, color=L1_SOL_COLOR)\
            .next_to(l1_sol_soft_dot, DR, buff=0.1)

        # Show shift
        loss_contours_copy = loss_contours.copy().set_opacity(0.3)
        loss_min_dot_copy = loss_min_dot.copy()
        self.add(loss_contours_copy)

        self.play(Write(explanation_l1[1]))
        self.play(
            Transform(loss_contours, loss_contours.copy().move_to(l1_sol_soft_coords)),
            Transform(loss_min_dot, l1_sol_soft_dot),
            FadeOut(loss_min_label),
            Write(l1_sol_soft_label),
            run_time=2.0
        )
        self.play(Write(explanation_l1[2]))
        self.play(Indicate(l1_sol_soft_dot, color=WHITE, scale_factor=1.5))
        self.wait(3)

        # Fade out for next scene
        # l1_impl_group = VGroup(l1_penalty_contours, l1_penalty_label, explanation_l1, lambda_tex)
        # self.play(FadeOut(l1_impl_group), FadeOut(loss_contours), FadeOut(loss_min_dot),
        #           FadeOut(l1_sol_soft_label), FadeOut(origin_dot), FadeOut(axes), FadeOut(axes_labels),
        #           FadeOut(title))
        # self.wait()


class Scene4(Scene):
    """Scene 4: Why L1 Creates Sparsity"""
    def construct(self):
         # Title
        title = Tex("Scene 4: Why L1 (Lasso) Creates Sparsity", font_size=40).to_edge(UP)
        self.play(Write(title))

        # Axes setup
        axes = Axes(**AXES_CONFIG).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label=MathTex("w_1"), y_label=MathTex("w_2"))
        origin_dot = Dot(axes.c2p(0,0), radius=0.05, color=GRAY)
        self.add(axes, axes_labels, origin_dot)

        # Loss minimum close to an axis
        loss_min_w1_sparse = 0.5
        loss_min_w2_sparse = 2.5
        loss_min_coords = axes.c2p(loss_min_w1_sparse, loss_min_w2_sparse)
        loss_min_dot = Dot(point=loss_min_coords, color=UNREG_DOT_COLOR, radius=0.1)
        loss_min_label = MathTex(r"w_{OLS}", font_size=30).next_to(loss_min_dot, UP, buff=0.1)

        # Elongated contours
        loss_contours = get_ellipse_contours(
            center=loss_min_coords,
            width=2.0, # Wider along w1
            height=0.6, # Narrower along w2
            angle=0, # No rotation
            num_levels=5,
            scale_factor=1.6
        )

        setup_text = Tex(r"Consider loss minimum near $w_2$ axis ($w_1 \approx 0$).", font_size=32).to_corner(UR)
        self.play(Write(setup_text))
        self.play(Create(loss_contours), Create(loss_min_dot), Write(loss_min_label))
        self.wait(1)
        self.play(FadeOut(setup_text))


        # Lambda value (fixed)
        lambda_val_sparse = 1.5
        lambda_tex = MathTex(r"\lambda =", f"{lambda_val_sparse:.1f}", font_size=36).to_corner(UL)
        self.play(Write(lambda_tex))

        # --- L1 Case ---
        explanation_l1 = Tex(r"L1 Penalty ($\lambda ||w||_1$):",
                             r"Sharp 'diamond' pulls strongly along axes.",
                             r"Optimal point often 'snaps' to an axis ($w_1=0$).", font_size=32)\
                             .to_corner(DR).shift(LEFT*0.5)

        l1_penalty_contours = get_l1_penalty_contours(size=0.4, num_levels=4, scale_factor=1.4)

        # Approximate L1 solution ON the axis
        # Estimate where it hits axis based on projection / gradient concept
        # Simplified: Find y-intercept of line from origin through a point slightly shifted from minimum
        approx_l1_y = loss_min_w2_sparse / (1 + lambda_val_sparse * 0.5) # Heuristic y-value on axis
        l1_sol_sparse_coords = axes.c2p(0, approx_l1_y)
        l1_sol_sparse_dot = Dot(point=l1_sol_sparse_coords, color=L1_SOL_COLOR, radius=0.1)
        l1_sol_sparse_label = MathTex(r"w_{L1}", font_size=30, color=L1_SOL_COLOR)\
            .next_to(l1_sol_sparse_dot, RIGHT, buff=0.15)

        self.play(Write(explanation_l1[0]))
        self.play(FadeIn(l1_penalty_contours.set_opacity(0.5)), run_time=1)
        self.play(Write(explanation_l1[1]))
        self.play(ShowPassingFlash(l1_penalty_contours[1].copy().set_color(WHITE), time_width=0.5))
        self.wait(0.5)

        # Animate the shift to axis
        shift_path_l1 = Line(loss_min_dot.get_center(), l1_sol_sparse_dot.get_center(), stroke_opacity=0)
        self.play(
            MoveAlongPath(loss_min_dot, shift_path_l1),
            FadeOut(loss_min_label),
            Write(l1_sol_sparse_label),
            run_time=2.0
        )
        self.play(Write(explanation_l1[2]))
        self.play(Indicate(l1_sol_sparse_dot, color=WHITE, scale_factor=1.5))
        self.wait(2)

        # Reset dot for L2 explanation
        self.play(
            FadeOut(l1_penalty_contours),
            FadeOut(explanation_l1),
            loss_min_dot.animate.move_to(loss_min_coords),
            FadeOut(l1_sol_sparse_label),
            FadeIn(loss_min_label)
         )
        self.wait(0.5)


        # --- L2 Case ---
        explanation_l2 = Tex(r"L2 Penalty ($\lambda ||w||_2^2$):",
                             r"Smooth 'circular' pull.",
                             r"Minimum moves closer, but rarely hits axis exactly.", font_size=32)\
                             .to_corner(DR).shift(LEFT*0.5)

        l2_penalty_contours = get_l2_penalty_contours(radius=0.5, num_levels=4, scale_factor=1.4)

        # Approximate L2 solution (closer to origin, but not on axis)
        shift_factor_l2_sparse = 1.0 / (1.0 + lambda_val_sparse * 0.3) # Heuristic shift
        l2_sol_sparse_coords = axes.c2p(0,0) + (loss_min_coords - axes.c2p(0,0)) * shift_factor_l2_sparse
        l2_sol_sparse_dot = Dot(point=l2_sol_sparse_coords, color=L2_SOL_COLOR, radius=0.1)
        l2_sol_sparse_label = MathTex(r"w_{L2}", font_size=30, color=L2_SOL_COLOR)\
            .next_to(l2_sol_sparse_dot, UP, buff=0.15)


        self.play(Write(explanation_l2[0]))
        self.play(FadeIn(l2_penalty_contours.set_opacity(0.5)), run_time=1)
        self.play(Write(explanation_l2[1]))
        self.play(ShowPassingFlash(l2_penalty_contours[1].copy().set_color(WHITE), time_width=0.5))
        self.wait(0.5)

        # Animate the shift for L2
        shift_path_l2 = Line(loss_min_dot.get_center(), l2_sol_sparse_dot.get_center(), stroke_opacity=0)
        self.play(
            MoveAlongPath(loss_min_dot, shift_path_l2),
            FadeOut(loss_min_label),
            Write(l2_sol_sparse_label),
            run_time=2.0
        )
        self.play(Write(explanation_l2[2]))
        self.play(Indicate(l2_sol_sparse_dot, color=WHITE, scale_factor=1.5))
        self.wait(3)

        # Fade out for next scene
        # final_group = VGroup(loss_contours, loss_min_dot, origin_dot, axes, axes_labels,
        #                     l2_penalty_contours, explanation_l2, l2_sol_sparse_label, lambda_tex, title)
        # self.play(FadeOut(final_group))
        # self.wait()


class Scene5(Scene):
    """Scene 5: The Effect of Lambda"""
    def construct(self):
        # Title
        title = Tex("Scene 5: The Effect of Regularization Strength $\lambda$", font_size=40).to_edge(UP)
        self.play(Write(title))

        # Axes setup (same sparse setup as Scene 4)
        axes = Axes(**AXES_CONFIG).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label=MathTex("w_1"), y_label=MathTex("w_2"))
        origin_dot = Dot(axes.c2p(0,0), radius=0.05, color=GRAY)
        self.add(axes, axes_labels, origin_dot)

        loss_min_w1_sparse = 0.5
        loss_min_w2_sparse = 2.5
        loss_min_coords_np = np.array([loss_min_w1_sparse, loss_min_w2_sparse]) # Numpy for calcs
        loss_min_coords_manim = axes.c2p(*loss_min_coords_np)

        loss_min_dot = Dot(point=loss_min_coords_manim, color=UNREG_DOT_COLOR, radius=0.1)
        loss_min_label = MathTex(r"w_{OLS}", font_size=30).next_to(loss_min_dot, UP, buff=0.1)

        # Keep loss contours static this time
        loss_contours = get_ellipse_contours(
            center=loss_min_coords_manim, width=2.0, height=0.6, angle=0, num_levels=4, scale_factor=1.8
        ).set_opacity(0.4)

        self.play(Create(loss_contours), Create(loss_min_dot), Write(loss_min_label))
        self.wait(1)

        # Lambda ValueTracker and Display
        lambda_tracker = ValueTracker(0.01) # Start with very small lambda
        lambda_display_val = DecimalNumber(
            lambda_tracker.get_value(),
            num_decimal_places=2,
            show_ellipsis=False
        )
        lambda_display_tex = MathTex(r"\lambda = ", font_size=36)
        lambda_display = VGroup(lambda_display_tex, lambda_display_val).arrange(RIGHT).to_corner(UL)
        lambda_display_val.add_updater(lambda d: d.set_value(lambda_tracker.get_value()))
        self.play(Write(lambda_display))

        # --- Create L1 and L2 solution dots ---
        l1_sol_dot = Dot(color=L1_SOL_COLOR, radius=0.1)
        l1_sol_label = MathTex(r"w_{L1}", color=L1_SOL_COLOR, font_size=30).next_to(l1_sol_dot, RIGHT, buff=0.1)

        l2_sol_dot = Dot(color=L2_SOL_COLOR, radius=0.1)
        l2_sol_label = MathTex(r"w_{L2}", color=L2_SOL_COLOR, font_size=30).next_to(l2_sol_dot, UP, buff=0.1)

        # --- Add Updaters to move dots based on lambda ---
        # L2 Path (Approximation: shrinks linearly towards origin)
        def l2_updater_func(mob):
            l = lambda_tracker.get_value()
            # More sophisticated model could involve Hessian, but simple shrinkage is illustrative
            shrink_factor = 1.0 / (1.0 + l * 0.5) # Heuristic factor
            new_pos_np = loss_min_coords_np * shrink_factor
            mob.move_to(axes.c2p(*new_pos_np))

        # L1 Path (Approximation: moves towards axis, snaps, then moves along axis)
        def l1_updater_func(mob):
            l = lambda_tracker.get_value()
            # Simplified ISTA-like path: shrink each component towards 0
            # Threshold is roughly proportional to lambda
            thresh_w1 = l * 0.4 # Heuristic thresholds
            thresh_w2 = l * 0.2

            # Shrink w1
            w1_shrunk = np.sign(loss_min_coords_np[0]) * max(0, abs(loss_min_coords_np[0]) - thresh_w1)
            # Shrink w2
            w2_shrunk = np.sign(loss_min_coords_np[1]) * max(0, abs(loss_min_coords_np[1]) - thresh_w2)

            mob.move_to(axes.c2p(w1_shrunk, w2_shrunk))

        l2_sol_dot.add_updater(l2_updater_func)
        l1_sol_dot.add_updater(l1_updater_func)

        # Add labels that follow the dots
        l1_sol_label.add_updater(lambda m: m.next_to(l1_sol_dot, RIGHT, buff=0.1))
        l2_sol_label.add_updater(lambda m: m.next_to(l2_sol_dot, UP, buff=0.1))

        self.play(Create(l1_sol_dot), Create(l2_sol_dot),
                  Write(l1_sol_label), Write(l2_sol_label))
        self.wait(1)

        # Explanation Text
        explanation = Tex(r"Increasing $\lambda$ increases the penalty strength.",
                           r"Both $w_{L1}$ and $w_{L2}$ shrink towards origin.",
                           r"$w_{L1}$ (purple) hits the axis ($w_1=0$) first.", font_size=32)\
                           .to_corner(DR).shift(LEFT*0.5)

        self.play(Write(explanation[0]))
        self.wait(1)
        self.play(Write(explanation[1]))

        # Animate Lambda increasing
        self.play(lambda_tracker.animate.set_value(3.0), run_time=6.0, rate_func=linear)
        self.play(Write(explanation[2]))
        self.play(Indicate(l1_sol_dot, color=WHITE, scale_factor=1.5))
        self.wait(1)

        # Animate Lambda increasing further
        self.play(lambda_tracker.animate.set_value(8.0), run_time=4.0, rate_func=linear)
        self.wait(3)

        # Clean up everything
        # self.play(*[FadeOut(mob) for mob in self.mobjects])
        # self.wait()

class Scene6(Scene):
    """Scene 6: Summary"""
    def construct(self):
        title = Tex("Scene 6: Summary", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        summary_points = VGroup(
            Tex(r"1. Conceptual view uses hard constraints (fixed boundaries).", font_size=34),
            Tex(r" - L2 (Ridge): Circle boundary $||w||_2^2 \le t$", font_size=30, color=L2_HARD_COLOR),
            Tex(r" - L1 (Lasso): Diamond boundary $||w||_1 \le t$", font_size=30, color=L1_HARD_COLOR),
            Tex(r"2. Implementation uses soft penalty terms added to loss.", font_size=34),
            Tex(r" - L2 (Ridge): Adds $\lambda ||w||_2^2$, smooth pull to origin.", font_size=30, color=L2_PENALTY_COLOR),
            Tex(r" - L1 (Lasso): Adds $\lambda ||w||_1$, sharp pull, encourages zeros.", font_size=30, color=L1_PENALTY_COLOR),
            Tex(r"3. L1's diamond shape/penalty is why it promotes sparse solutions (zero coefficients).", font_size=34),
            Tex(r"4. Increasing $\lambda$ increases shrinkage towards the origin.", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).center().shift(DOWN*0.5)

        # Animate points appearing
        for i, point in enumerate(summary_points):
            self.play(Write(point), run_time=1.5 if i % 3 == 0 else 1.0) # Slightly longer for main points
            self.wait(0.75)

        self.wait(5)
        # End scene
        # self.play(*[FadeOut(mob) for mob in self.mobjects])
        # self.wait()
