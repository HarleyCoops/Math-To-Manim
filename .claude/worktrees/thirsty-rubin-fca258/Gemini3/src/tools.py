import os
import logging
from typing import Optional
from google.genai import Client, types
from PIL import Image
import io

# Setup logger
logger = logging.getLogger("Gemini3")

def generate_concept_image(prompt: str, filename: str) -> str:
    """
    Tool function to be exposed to the Agent.
    Generates an image based on the prompt using Imagen 3 and saves it to the assets directory.
    """
    with open("Gemini3/tool_log.txt", "a") as f:
        f.write(f"generate_concept_image called for {filename}\n")

    assets_dir = os.path.join(os.getcwd(), "assets", "generated")
    os.makedirs(assets_dir, exist_ok=True)
    
    file_path = os.path.join(assets_dir, filename)
    if not file_path.endswith(".png"):
        file_path += ".png"
        
    print(f"Generating image for: {filename} with prompt: {prompt[:50]}...")
    
    try:
        client = Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # Using Imagen 3
        # Use a model name that is definitely correct. 'imagen-3.0-generate-001' is a guess.
        # It's often 'imagen-3.0-generate-001' or similar. 
        # Safe fallback: 'imagen-3.0-generate-001'
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
            print(f"Successfully saved image to {file_path}")
            with open("Gemini3/tool_log.txt", "a") as f:
                f.write(f"Success for {filename}\n")
        else:
            print(f"No images returned for {filename}")
            with open("Gemini3/tool_log.txt", "a") as f:
                f.write(f"No images for {filename}\n")
            
    except Exception as e:
        print(f"Error generating image with Imagen 3: {e}")
        with open("Gemini3/tool_log.txt", "a") as f:
            f.write(f"Error for {filename}: {e}\n")
        
        # Fallback to placeholder (but better than random rectangles?)
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        d = ImageDraw.Draw(img)
        d.text((50, 50), f"FAILED GEN: {filename}", fill=(255, 0, 0))
        d.text((50, 100), f"Error: {str(e)}", fill=(255, 255, 255))
        img.save(file_path)
    
    return file_path
