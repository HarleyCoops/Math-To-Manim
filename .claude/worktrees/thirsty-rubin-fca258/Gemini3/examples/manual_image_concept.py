from manim import *
import sys
import os

# Add the src directory to path so we can import the tool
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import generate_concept_image

class ConceptWithImage(ThreeDScene):
    def construct(self):
        # 1. "Pre-production": Generate the assets
        # In the full pipeline, the VisualDesigner agent would do this.
        print("Generating assets...")
        chaos_image_path = generate_concept_image(
            prompt="A chaotic abstract representation of high entropy", 
            filename="entropy_chaos"
        )
        
        order_image_path = generate_concept_image(
            prompt="A perfectly ordered crystal lattice structure", 
            filename="entropy_order"
        )
        
        # 2. Define the Scene using these assets
        
        # Introduction
        title = Text("Entropy: Chaos vs Order").scale(0.8).to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Show Chaos
        chaos_img = ImageMobject(chaos_image_path).scale(2)
        chaos_label = Text("High Entropy").next_to(chaos_img, DOWN)
        
        self.play(FadeIn(chaos_img))
        self.play(Write(chaos_label))
        self.wait(2)
        
        # Transition to Order
        order_img = ImageMobject(order_image_path).scale(2)
        order_label = Text("Low Entropy").next_to(order_img, DOWN)
        
        self.play(
            FadeOut(chaos_img),
            FadeOut(chaos_label),
            FadeIn(order_img),
            FadeIn(order_label)
        )
        
        # 3D rotation to show it's a "flat" image in 3D space
        self.move_camera(phi=60 * DEGREES, theta=45 * DEGREES, run_time=2)
        self.wait()
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=2)
        
        self.wait()

if __name__ == "__main__":
    # Render command
    os.system("manim -pql Gemini3/examples/manual_image_concept.py ConceptWithImage")
