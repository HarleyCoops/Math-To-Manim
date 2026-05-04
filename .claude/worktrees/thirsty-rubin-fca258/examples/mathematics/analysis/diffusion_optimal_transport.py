from text_to_manim import MLAnimationGenerator, create_animation
from manim import *
import numpy as np

# The text description for our scene
SCENE_DESCRIPTION = """
1. Diffusion's Nebula:
   Two galaxies α₀ and α₁ shimmer in the void, their stars (particles) glowing blue and gold.
   A bridge of light αₜ forms between them, its hue shifting from azure to amber as time t flows.
   Each photon traces the convex combination (1-t)P₀ + tP₁, merging the galaxies into a luminous gradient.

2. River of Least Resistance:
   A river of silver currents νₜ winds through spacetime, its flow minimizing kinetic energy ‖νₜ‖².
   The riverbanks are defined by the continuity equation—particles cascade without loss, obeying the cosmic law div(αₜνₜ) + ∂ₜαₜ = 0.

3. Wasserstein's Forge:
   A blacksmith T₁ hammers starlight into new constellations. Each strike reshapes α₀ into α₁, measuring effort by ‖x - T₁(x)‖².
   The geodesic αₜ emerges as molten gold, cooling into the optimal path (1-t)Id + tT₁.

4. Benamou-Brenier's Symphony:
   A grand orchestra conducts the transport: violins hum the velocity field, cellos resonate the continuity equation, and timpani thunder the Wasserstein metric.
   The crescendo peaks as α₀ and α₁ unite, their harmony echoing the theorem's proof.

Manim Scene Instructions:
- Render α₀ and α₁ as particle clouds with color gradients
- Animate αₜ as a morphing bridge with interpolated hues
- Visualize νₜ as vector fields with streamline traces
- Illustrate T₁ as a warping grid or heatmap
- Use fluid dynamics simulations for the continuity equation

In the calculus of shapes, Wasserstein is the sculptor, and Benamou-Brenier the chisel—carving geodesics from the marble of probability.
"""

class DiffusionAndOptimalTransport(ThreeDScene):
    def construct(self):
        # Set up the scene
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.1)

        # Title
        title = Text("Diffusion Models and Optimal Transport", font_size=40)
        subtitle = Text("Benamou-Brenier Theorem and Wasserstein Distance", font_size=30)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Step 1: Diffusion's Nebula
        self.diffusions_nebula()

        # Step 2: River of Least Resistance
        self.river_of_least_resistance()

        # Step 3: Wasserstein's Forge
        self.wassersteins_forge()

        # Step 4: Benamou-Brenier's Symphony
        self.benamou_breniers_symphony()

    def diffusions_nebula(self):
        # Create two particle clouds (α₀ and α₁)
        alpha_0 = VGroup(*[Dot(color=BLUE) for _ in range(50)]).arrange_in_grid(rows=5, cols=10)
        alpha_1 = VGroup(*[Dot(color=GOLD) for _ in range(50)]).arrange_in_grid(rows=5, cols=10)
        alpha_0.move_to(LEFT * 3)
        alpha_1.move_to(RIGHT * 3)
        self.play(FadeIn(alpha_0), FadeIn(alpha_1))
        self.wait(1)

        # Animate the bridge αₜ
        alpha_t = VGroup()
        for t in np.linspace(0, 1, 50):
            point = Dot(color=interpolate_color(BLUE, GOLD, t)).move_to(
                interpolate(LEFT * 3, RIGHT * 3, t)
            )
            alpha_t.add(point)
        self.play(Create(alpha_t), run_time=3)
        self.wait(2)

    def river_of_least_resistance(self):
        # Create a vector field (νₜ)
        plane = NumberPlane()
        vector_field = VectorField(
            lambda x: np.array([-x[1], x[0], 0]), plane
        ).set_color(SILVER)
        self.play(Create(plane), Create(vector_field))
        self.wait(2)

        # Animate particles flowing along the field
        particles = VGroup(*[Dot(color=WHITE) for _ in range(50)])
        for particle in particles:
            particle.move_to(np.random.uniform(-5, 5, 3))
        self.play(FadeIn(particles))
        self.play(
            LaggedStart(
                *[
                    MoveAlongPath(particle, vector_field.get_stream_line(particle.get_center()))
                    for particle in particles
                ],
                run_time=5,
                lag_ratio=0.1,
            )
        )
        self.wait(2)

    def wassersteins_forge(self):
        # Create a warping grid (since we can't load SVG files directly)
        grid = NumberPlane()
        self.play(Create(grid))
        self.wait(1)

        # Animate the grid warping (T₁)
        warped_grid = grid.copy().apply_function(
            lambda x: x + np.array([0.5 * x[1], 0.5 * x[0], 0])
        )
        self.play(Transform(grid, warped_grid), run_time=3)
        self.wait(2)

    def benamou_breniers_symphony(self):
        # Create symbolic representations instead of SVG files
        violin = Circle(color=RED).scale(0.5).move_to(LEFT * 3)
        cello = Square(color=BLUE).scale(0.5).move_to(RIGHT * 3)
        timpani = Triangle(color=GREEN).scale(0.5).move_to(UP * 2)
        self.play(FadeIn(violin), FadeIn(cello), FadeIn(timpani))
        self.wait(1)

        # Animate the crescendo (uniting α₀ and α₁)
        alpha_0 = VGroup(*[Dot(color=BLUE) for _ in range(50)]).arrange_in_grid(rows=5, cols=10)
        alpha_1 = VGroup(*[Dot(color=GOLD) for _ in range(50)]).arrange_in_grid(rows=5, cols=10)
        alpha_0.move_to(LEFT * 3)
        alpha_1.move_to(RIGHT * 3)
        self.play(FadeIn(alpha_0), FadeIn(alpha_1))
        self.play(
            alpha_0.animate.move_to(ORIGIN),
            alpha_1.animate.move_to(ORIGIN),
            run_time=3,
        )
        self.wait(2)

        # Final text
        final_text = Text(
            "In the calculus of shapes, Wasserstein is the sculptor,\n"
            "and Benamou-Brenier the chisel—carving geodesics\n"
            "from the marble of probability.",
            font_size=30,
        )
        self.play(Write(final_text))
        self.wait(3)

def main():
    # Configure Manim
    config.media_dir = "./media"  # Output directory
    config.output_file = "benamou_brenier"
    config.quality = "medium_quality"
    config.preview = True
    
    # Method 1: Using MLAnimationGenerator (more sophisticated)
    print("Generating and rendering sophisticated scene...")
    generator = MLAnimationGenerator()
    sophisticated_scene = generator.generate_scene(SCENE_DESCRIPTION)
    scene = sophisticated_scene()
    scene.render()
    
    # Method 2: Using simple create_animation function
    print("Generating and rendering simple scene...")
    simple_scene = create_animation(SCENE_DESCRIPTION)
    scene = simple_scene()
    scene.render()
    
    print(f"Animations have been rendered to: {config.media_dir}")

if __name__ == "__main__":
    main()
