from manim import *
from random import uniform
import numpy as np

def SurroundingCircle(mobject, color=BLUE, buffer_factor=1.5):
    width = mobject.get_width()
    height = mobject.get_height()
    radius = max(width, height) / 2 * buffer_factor
    return Circle(radius=radius, color=color).move_to(mobject.get_center())

class QFTRevolution(ThreeDScene):
    def construct(self):
        # Scene 1: Quantum Field Visualization (3D) - 15 seconds
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        field_grid = Surface(
            lambda u, v: np.array([u, v, 0.5*np.sin(3*u)*np.cos(3*v)]),
            u_range=[-3,3], v_range=[-3,3],
            checkerboard_colors=[BLUE_E, GREEN_E],
            resolution=(24,24)
        )

        field_eq = MathTex(
            r"\hat{\phi}(x) = \int \frac{d^3p}{(2\pi)^3}\frac{1}{\sqrt{2\omega_p}}",
            r"\left(a_{\vec{p}}e^{-ip\cdot x} + a_{\vec{p}}^\dagger e^{ip\cdot x}\right)",
            font_size=30
        ).to_corner(UL)

        self.play(Create(field_grid), Write(field_eq[0]))
        self.wait(5)
        self.play(Write(field_eq[1]))
        self.wait(3)
        self.move_camera(phi=60*DEGREES, theta=-30*DEGREES, focal_point=field_eq.get_center(), run_time=2)
        self.play(FadeOut(field_grid, field_eq), run_time=2)

        # Scene 2: Vacuum Fluctuations - 20 seconds
        quantum_foam = VGroup(*[
            Dot(point=[uniform(-5,5), uniform(-3,3),0],
               radius=0.03*uniform(0,1),
               color=interpolate_color(WHITE, BLUE_E, uniform(0,1)))
            for _ in range(200)
        ])
        uncertainty_eq = MathTex(
            r"\Delta E \Delta t \geq \frac{\hbar}{2}",
            font_size=40
        ).to_edge(UP)

        self.play(FadeIn(quantum_foam), Write(uncertainty_eq))
        self.wait(5)

        virtual_pairs = VGroup(
            Arrow(ORIGIN, RIGHT+UP, color=RED),
            Arrow(ORIGIN, LEFT+DOWN, color=BLUE)
        ).arrange(RIGHT, buff=2)
        self.play(Create(virtual_pairs), run_time=3)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3: Feynman Diagrams & Interactions - 25 seconds
        diagram = VGroup(
            Arrow(LEFT*2, ORIGIN, color=BLUE),  # Incoming electron
            ArcBetweenPoints(ORIGIN, RIGHT*2, angle=TAU/4, color=RED),  # Photon
            CurvedArrow(RIGHT*2, ORIGIN, angle=-TAU/4, color=YELLOW), # Another Photon. CurvedArrow gives a nicer visual
            Arrow(ORIGIN, RIGHT*2, color=BLUE)   # Outgoing electron
        )
        diagram.scale(0.8)
        caption = Tex("Electron-Photon Interaction", font_size=30).to_edge(DOWN)
        matrix_element = MathTex(
            r"\mathcal{M} = -ie\gamma^\mu\epsilon_\mu(p)",
            font_size=35
        ).to_edge(UP)

        self.play(LaggedStart(
            Create(diagram[0]), Create(diagram[1]),
            Create(diagram[2]), Create(diagram[3]),
            lag_ratio=0.5))
        self.play(Write(matrix_element), Write(caption))
        self.wait(5)

        # Add loop diagram (representing a higher-order correction)
        loop = ParametricFunction(
            lambda t: np.array([0.5*np.cos(t), 0.5*np.sin(t), 0]),
            t_range=[0, TAU],
            color=GREEN
        ).shift(RIGHT) #Shift to see the result
        self.play(Create(loop), run_time=2)
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

        # Scene 4: Renormalization Process - 25 seconds
        bare_particle = Circle(radius=0.5, color=RED)
        bare_particle.set_color(GREY) # Better bare particle color
        renorm_group = VGroup(
            Circle(radius=0.3, color=RED), # Circle representing "dressed" charge
            SurroundingCircle(bare_particle, color=BLUE, buffer_factor=1.5) #Circle cloud around bare particle
        )
        renorm_eq = MathTex(
            r"\mathcal{L} = \mathcal{L}_{\text{ren}} + \delta\mathcal{L}",
            r"\Gamma^{(n)}(p) = Z^{\frac{n}{2}} \Gamma^{(n)}_0(p)",
            font_size=35
        ).arrange(DOWN).to_edge(UP)

        self.play(Create(bare_particle), Write(renorm_eq[0]))
        self.wait(3)
        self.play(TransformMatchingShapes(bare_particle, renorm_group[0]), Write(renorm_eq[1])) #Transition between bare particle and dressed particle
        self.play(FadeIn(renorm_group[1])) #Show blue circle
        self.wait(5)
        self.play(FadeOut(*self.mobjects))

        # Scene 5: Detector Thought Experiment - 30 seconds
        detector = Rectangle(height=2, width=3, color=GREY_B)
        wave_packet = ParametricFunction(
            lambda t: np.array([t/2, 0.3*np.exp(-t**2)*np.sin(8*t), 0]),  # Gaussian wave packet
            t_range=[-3,3],
            color=BLUE
        ).shift(LEFT*3)
        excitation = Star(n=7, color=YELLOW).scale(0.3).move_to(detector.get_center()) # Star for simple excitation

        self.play(Create(detector), Create(wave_packet))
        self.play(wave_packet.animate.shift(RIGHT*3), run_time=3)
        self.play(FadeIn(excitation), detector.animate.set_fill(YELLOW, opacity=0.3)) #Detector changes
        self.wait(2)

        # Replace image-based chambers with Manim-generated representations
        # Cloud Chamber Representation:  Lines indicating particle tracks
        cloud_chamber = VGroup(*[
            Line(start=detector.get_center() + LEFT * i * 0.2, end=detector.get_center() + RIGHT * (3 - i * 0.2) + UP*uniform(-0.5, 0.5), color=WHITE)
            for i in range(5)
        ]).shift(LEFT*3)

        # Bubble Chamber Representation:  Dots along a path
        bubble_chamber = VGroup(*[
            Dot(point=detector.get_center() + RIGHT * i * 0.2 + UP * np.sin(i*0.5)*0.3, radius=0.05, color=WHITE)
            for i in range(15)
        ]).shift(RIGHT*3)

        self.play(Create(cloud_chamber), Create(bubble_chamber))  # Use Create for the tracks
        self.wait(5)
        self.play(FadeOut(*self.mobjects))

        # Scene 6: Synthesis & Conclusion - 25 seconds
        final_text = VGroup(
            Tex("Particles are measurement-induced"),
            Tex("quantized field excitations"),
            Tex("not fundamental entities"),
            Tex("@profmattstrassler.com/2025/02/10/elementary-particles-do-not-exist")
        ).arrange(DOWN).scale(0.8)

        self.play(Write(final_text[0]))
        self.play(Write(final_text[1]))
        self.play(Write(final_text[2]))
        self.wait(3)
        self.play(FadeIn(final_text[3])) # Reference at the end
        self.wait(5)
        
        #python -m manim -pql strassler.py QFTRevolution