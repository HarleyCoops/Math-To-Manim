#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Add current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from Gemini3.src.pipeline import Gemini3Pipeline, logger
from google.genai.types import Part

def main():
    pipeline = Gemini3Pipeline()

    # Read the text prompt
    text_path = Path("Gemini3/curriculum_prompt.txt")
    if not text_path.exists():
        logger.console.print(f"[bold red]Error: {text_path} not found.[/bold red]")
        return
    
    with open(text_path, "r", encoding="utf-8") as f:
        text_prompt = f.read()

    # Define image paths
    # Define image paths
    image_paths = []

    parts = [text_prompt]
    
    # Image loading block removed as requested

    try:
        logger.console.print("[bold blue]Running pipeline with input...[/bold blue]")
        result = pipeline.run(parts)

        # Extract code block
        import re
        
        clean_result = str(result)
        
        # Fallback to standard regex
        code_matches = list(re.finditer(r"```python\s*(.*?)```", clean_result, re.DOTALL | re.IGNORECASE))
        output_file = "Gemini3/output_scene.py"

        if code_matches:
            # Take the last code block found
            final_code = code_matches[-1].group(1).strip()
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_code)
            logger.console.print(f"\n[bold green]SUCCESS! Animation code saved to {output_file}[/bold green]")
            logger.console.print(f"Run it with: [cyan]manim -pql {output_file} <SceneName>[/cyan]")
        else:
            logger.console.print("\n[bold red]WARNING: No valid Python code block found in the output.[/bold red]")
            logger.console.print("Raw output saved to Gemini3/raw_output.txt")
            with open("Gemini3/raw_output.txt", "w", encoding="utf-8") as f:
                f.write(clean_result)

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
