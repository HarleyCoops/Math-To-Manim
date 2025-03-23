from manim import *
from manim.opengl import *
import random

class StarField(VGroup):
    def __init__(self, n_stars=100, **kwargs):
        super().__init__(**kwargs)
        for _ in range(n_stars):
            star = Dot(
                point=[random.uniform(-8, 8), random.uniform(-5, 5), 0],
                radius=random.uniform(0.01, 0.03),
                color=WHITE,
                stroke_width=0
            )
            self.add(star)

class CosmicIntroduction(Scene):
    def construct(self):
        # Star field backdrop
        starfield = StarField().scale(4)
        self.play(FadeIn(starfield), run_time=3)
        
        # Coordinate axes
        axes = ThreeDAxes()
        self.play(Create(axes), run_time=2)
        
        # Title animation
        title = Text(
            "Quantum Field Theory: A Journey into the Electromagnetic Interaction",
            font_size=48,
            color=WHITE,
            sheen_direction=RIGHT
        ).scale(0.5).move_to(ORIGIN)
        
        self.play(Write(title), run_time=3)
        self.play(title.animate.scale(0.3).to_corner(UL), run_time=2)
        self.wait(1)

class MinkowskiSpace(Scene):
    def construct(self):
        # 3D Minkowski wireframe
        axes = ThreeDAxes()
        self.play(Create(axes), run_time=3)
        
        # Minkowski surface approximation with a grid
        grid_size = 20
        grid_points = []
        for i in range(-grid_size, grid_size+1, 2):
            for j in range(-grid_size, grid_size+1, 2):
                x, y = i/10, j/10
                z = np.sqrt(x**2 + y**2)
                grid_points.append([x, y, z])
        
        dots = VGroup(*[Dot3D(point=p, color=BLUE, radius=0.05) for p in grid_points])
        self.play(Create(dots), run_time=3)
        
        # Rotating light cone
        light_cone = Cone(height=2, base_radius=1, color=YELLOW)
        self.play(Create(light_cone), run_time=3)
        
        # Metric equation
        metric = MathTex(
            "ds^2 = ",
            "-c^2 dt^2", "+", "dx^2", "+", "dy^2", "+", "dz^2",
            color=[RED, BLUE, GREEN, YELLOW, PURPLE, PINK]
        ).scale(0.5).next_to(ORIGIN, UP)
        
        self.play(Write(metric), run_time=3)
        self.wait(2)

class FieldVisual(Scene):
    def construct(self):
        # Plane waves
        E_wave = ParametricFunction(
            lambda t: [t, 0, np.sin(t)],
            t_range=[-PI, PI],
            color=RED
        )
        B_wave = ParametricFunction(
            lambda t: [t, np.sin(t), 0],
            t_range=[-PI, PI],
            color=BLUE
        )
        
        self.play(Create(E_wave), Create(B_wave), run_time=3)
        
        # Labels and arrows
        E_label = MathTex(r"\vec{E}", color=RED).next_to(E_wave.get_end(), RIGHT)
        B_label = MathTex(r"\vec{B}", color=BLUE).next_to(B_wave.get_end(), UP)
        self.play(Write(E_label), Write(B_label))
        
        # Propagation arrow
        prop_arrow = Arrow(start=E_wave.get_start(), end=E_wave.get_end(), color=YELLOW)
        self.play(Create(prop_arrow), run_time=2)

class MaxwellEquations(Scene):
    def construct(self):
        # Equation transformation
        classical_eq = MathTex(
            r"\nabla \cdot \mathbf{E} =", 
            r"\rho", 
            r"\quad \nabla \times \mathbf{B} =", 
            r"\mathbf{J} + \frac{\partial \mathbf{E}}{\partial t}"
        ).scale(0.5)
        
        tensor_eq = MathTex(
            r"\partial_\mu F^{\mu\nu} =", 
            r"\mu_0 J^\nu"
        ).scale(0.5).next_to(classical_eq, DOWN)
        
        self.play(Write(classical_eq), run_time=3)
        self.play(Transform(classical_eq, tensor_eq), run_time=3)

class LagrangianDensity(Scene):
    def construct(self):
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} =", 
            r"\bar{\psi}", 
            r"(i \gamma^\mu D_\mu - m)\psi", 
            r"- \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
            color=[ORANGE, GREEN, TEAL, GOLD]
        ).scale(0.5)
        
        self.play(Write(lagrangian), run_time=3)
        
        # Pulse animation
        self.play(
            lagrangian[0].animate.scale(1.2),
            lagrangian[1].animate.scale(1.2),
            lagrangian[2].animate.scale(1.2),
            lagrangian[3].animate.scale(1.2),
            run_time=2
        )

class FeynmanDiagram(Scene):
    def construct(self):
        # Electron and photon paths
        electron1 = CubicBezier(
            start_anchor=LEFT*3,
            start_handle=DOWN*1 + LEFT*2,
            end_handle=UP*1 + RIGHT*2,
            end_anchor=RIGHT*3,
            color=BLUE
        )
        electron2 = CubicBezier(
            start_anchor=RIGHT*3,
            start_handle=DOWN*1 + RIGHT*2,
            end_handle=UP*1 + LEFT*2,
            end_anchor=LEFT*3,
            color=BLUE
        )
        photon = CubicBezier(
            start_anchor=LEFT*2,
            start_handle=LEFT*1,
            end_handle=RIGHT*1,
            end_anchor=RIGHT*2,
            color=YELLOW
        )
        
        labels = VGroup(
            MathTex(r"e^-", color=BLUE).next_to(electron1.get_start(), LEFT),
            MathTex(r"e^-", color=BLUE).next_to(electron2.get_end(), RIGHT),
            MathTex(r"\gamma", color=YELLOW).next_to(photon.get_center(), UP)
        )
        
        self.play(Create(electron1), Create(electron2), Create(photon), Write(labels))

class CouplingConstant(Scene):
    def construct(self):
        # Numeric to symbolic transition
        alpha_num = DecimalNumber(1/137, num_decimal_places=3, color=YELLOW).shift(UP)
        alpha_sym = MathTex(r"\alpha =", r"\frac{e^2}{4 \pi \epsilon_0 \hbar c}", color=YELLOW).shift(DOWN)
        
        self.play(Write(alpha_num), run_time=2)
        self.play(Transform(alpha_num, alpha_sym), run_time=3)

class Renormalization(Scene):
    def construct(self):
        # Graph axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 1.5, 0.5],
            axis_config={"color": BLUE},
        )
        
        curve = axes.plot(lambda x: 1/(1 + np.exp(-x)), color=RED)
        
        self.play(Create(axes), Create(curve), run_time=3)

class FinalScene(Scene):
    def construct(self):
        # Composite scene
        elements = VGroup(
            StarField().scale(4),
            ThreeDAxes(),
            MathTex("QED: Unifying Light and Matter Through Gauge Theory").scale(0.6).to_edge(UP),
            Text("Finis", color=GOLD).scale(2).to_edge(DOWN)
        )
        
        self.play(*[FadeIn(el) for el in elements], run_time=5)
        self.play(FadeOut(elements), run_time=5)