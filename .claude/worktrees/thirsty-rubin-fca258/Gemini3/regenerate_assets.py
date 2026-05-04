import os
import io
from google.genai import Client, types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

def generate_concept_image(prompt: str, filename: str) -> str:
    print(f"Generating {filename}...")
    assets_dir = os.path.join(os.getcwd(), "assets", "generated")
    os.makedirs(assets_dir, exist_ok=True)
    
    file_path = os.path.join(assets_dir, filename)
    if not file_path.endswith(".png"):
        file_path += ".png"
        
    try:
        client = Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9" 
            )
        )
        
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            image.save(file_path)
            print(f"Saved to {file_path}")
        else:
            print(f"No images returned for {filename}")
            
    except Exception as e:
        print(f"Error generating {filename}: {e}")
        # Create a dummy failure image so we know
        img = Image.new('RGB', (1920, 1080), color=(50, 0, 0))
        img.save(file_path)

    return file_path

def regenerate():
    print("Regenerating assets with Imagen 3...")
    
    assets = [
        {
            "filename": "math_texture_overlay.png",
            "prompt": "Vintage parchment paper texture overlaid with faint, handwritten mathematical equations and geometric diagrams. Da Vinci style sketches. Sepia tones, subtle, low contrast, high resolution, 8k, detailed texture."
        },
        {
            "filename": "quantum_foam_bg.png",
            "prompt": "Abstract representation of quantum foam, sub-atomic chaos, dark nebula colors, blurry, depth of field, noise, ethereal blue and purple clouds. Cinematic lighting, photorealistic, 8k."
        },
        {
            "filename": "starfield_lensing_bg.png",
            "prompt": "Hyper-realistic close-up of a black hole event horizon, gravitational lensing distortion, accretion disk edge, glowing gold and orange plasma against deep space. Cinematic lighting, Interstellar movie style, 8k."
        },
        {
            "filename": "entropy_chaos.png",
            "prompt": "Artistic interpretation of entropy and heat death of the universe. Cold, dark, distinct particles fading into void. Melancholic atmosphere, minimal lighting, deep blacks and faint greys. 8k resolution."
        }
    ]
    
    for asset in assets:
        generate_concept_image(asset['prompt'], asset['filename'])

if __name__ == "__main__":
    regenerate()




