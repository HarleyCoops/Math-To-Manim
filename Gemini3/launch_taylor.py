import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add workspace root to sys.path
# We are in Gemini3/launch_taylor.py, so root is ..
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from Gemini3.src.pipeline import Gemini3Pipeline, logger
from PIL import Image

def main():
    load_dotenv()
    
    prompt_path = os.path.join(root_dir, "Gemini3", "taylor_prompt.txt")
    image_path = "C:/Users/chris/.gemini/antigravity/brain/ec1ac387-4434-418c-b576-a59ee4ba66f9/uploaded_image_1765652053419.png"
    output_file = os.path.join(root_dir, "Gemini3", "taylor_scene.py")
    
    logger.console.print(f"[bold]Reading prompt from {prompt_path}[/bold]")
    with open(prompt_path, "r", encoding="utf-8") as f:
        text_prompt = f.read()
        
    parts = [text_prompt]
    
    if os.path.exists(image_path):
        logger.console.print(f"[bold blue]Loading image from {image_path}...[/bold blue]")
        try:
            img = Image.open(image_path)
            parts.append(img)
            logger.console.print("[green]Image loaded successfully via PIL.[/green]")
        except Exception as e:
            logger.console.print(f"[bold red]Failed to load image via PIL: {e}[/bold red]")
    else:
        logger.console.print(f"[bold red]Image not found at {image_path}[/bold red]")

    pipeline = Gemini3Pipeline()
    try:
        logger.console.print("[bold blue]Launching Taylor Series Topology Pipeline...[/bold blue]")
        result = pipeline.run(parts)
        
        # Extract code
        import re
        clean_result = str(result)
        # Look for code blocks
        code_matches = list(re.finditer(r"```python\s*(.*?)```", clean_result, re.DOTALL | re.IGNORECASE))
        
        if code_matches:
            final_code = code_matches[-1].group(1).strip()
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_code)
            logger.console.print(f"\n[bold green]SUCCESS! Animation code saved to {output_file}[/bold green]")
            logger.console.print(f"Run it with: [cyan]manim -pql {output_file} TaylorSeries3D[/cyan] (or check class name)")
        else:
            logger.console.print("\n[bold red]WARNING: No valid Python code block found in the output.[/bold red]")
            raw_out = os.path.join(root_dir, "Gemini3", "raw_taylor_output.txt")
            with open(raw_out, "w", encoding="utf-8") as f:
                f.write(clean_result)
            logger.console.print(f"Raw output saved to {raw_out}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
