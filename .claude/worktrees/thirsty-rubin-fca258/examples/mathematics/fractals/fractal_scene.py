from manim import *
import numpy as np

config.renderer = "opengl"
config.frame_size = (1200, 800)

class FractalQuantumTransition(ThreeDScene):
    def construct(self):
        # Generate Mandelbrot fractal programmatically
        mandelbrot = self.create_mandelbrot()
        equation1 = MathTex(r"z_{n+1} = z_n^2 + c", font_size=36).to_edge(UL)
        
        # Add initial objects
        self.add_fixed_in_frame_mobjects(equation1)
        self.play(FadeIn(mandelbrot), Write(equation1), run_time=2)
        
        # Animate fractal zoom
        self.camera.frame.save_state()
        self.play(
            self.camera.frame.animate.set_width(2).move_to(mandelbrot.get_center()),
            rate_func=rate_functions.ease_in_out_cubic,
            run_time=3
        )
        
        # Transform to quantum orbital
        orbital = self.create_orbital()
        self.play(Transform(mandelbrot, orbital), run_time=3)
        
        # Create collapse particles
        particles = self.create_collapse_particles(50)
        self.play(Create(particles), run_time=2)
        self.wait(2)

    def create_mandelbrot(self, iterations=50, width=4):
        # Generate Mandelbrot set using numpy
        x = np.linspace(-2, 1, 400)
        y = np.linspace(-1.5, 1.5, 400)
        c = x[:, None] + 1j*y[None, :]
        
        z = np.zeros_like(c)
        fractal = np.zeros(c.shape)
        
        for n in range(iterations):
            mask = np.abs(z) < 4
            z[mask] = z[mask]**2 + c[mask]
            fractal[mask] = n
        
        # Normalize the values to [0, 1]
        fractal_normalized = fractal / iterations
        
        # Create color array
        colored_fractal = np.zeros((fractal.shape[0], fractal.shape[1], 3))
        
        # Create a smooth color gradient
        for i in range(fractal.shape[0]):
            for j in range(fractal.shape[1]):
                val = fractal_normalized[i, j]
                if val == 1:  # Points in the set
                    colored_fractal[i, j] = [0, 0, 0]  # Black
                else:
                    # Smooth color transition
                    if val < 0.33:
                        colored_fractal[i, j] = [0, 0, val * 3]  # Blue gradient
                    elif val < 0.66:
                        colored_fractal[i, j] = [0, (val - 0.33) * 3, 1]  # Blue to cyan
                    else:
                        colored_fractal[i, j] = [(val - 0.66) * 3, 1, 1]  # Cyan to white
        
        # Create image and set height after creation
        image = ImageMobject(colored_fractal)
        image.set_height(4)
        return image.scale(width/4)

    def create_orbital(self):
        # Simple 2p_z orbital visualization
        return Surface(
            lambda u, v: np.array([
                np.sin(PI*v) * np.cos(TAU*u),
                np.sin(PI*v) * np.sin(TAU*u),
                np.cos(PI*v) * 0.5
            ]),
            u_range=[0, 1],
            v_range=[0, 1],
            color=BLUE_B,
            opacity=0.5,
            gloss=0.2
        )

    def create_collapse_particles(self, count):
        return DotCloud(
            points=[np.random.uniform(-3,3,3) for _ in range(count)],
            color=YELLOW,
            radius=0.05,
            glow_factor=2.0
        )

# Render with: manim -pql --renderer=opengl fractal_scene.py FractalQuantumTransition