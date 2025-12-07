from manim import *
import numpy as np
from PIL import Image

def create_sample_image(filename="sample_image.png"):
    # Create a simple gradient image
    width, height = 400, 400
    array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            array[y, x] = [x % 255, y % 255, (x+y) % 255]
            
    img = Image.fromarray(array)
    img.save(filename)
    print(f"Created {filename}")

class ImageTestScene(Scene):
    def construct(self):
        # Ensure image exists
        create_sample_image("sample_image.png")
        
        # Create ImageMobject
        image = ImageMobject("sample_image.png")
        image.scale(0.5)
        
        # Title
        title = Text("Manim Image Test").to_edge(UP)
        
        self.play(Write(title))
        self.play(FadeIn(image))
        self.play(image.animate.rotate(PI/4))
        self.play(image.animate.scale(1.5))
        self.play(FadeOut(image))
        self.wait()

if __name__ == "__main__":
    # This allows running the script directly to render if manim is set up
    import os
    os.system("manim -pql Gemini3/examples/manim_image_test.py ImageTestScene")
