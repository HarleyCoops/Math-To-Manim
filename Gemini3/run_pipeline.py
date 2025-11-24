#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from Gemini3.src.pipeline import Gemini3Pipeline, logger

def main():
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        logger.console.print("[bold yellow]No prompt provided. Using default.[/bold yellow]")
        user_prompt = "Explain the concept of Gradient Descent in Machine Learning"

    pipeline = Gemini3Pipeline()

    try:
        result = pipeline.run(user_prompt)

        # Extract code block
        import re
        code_match = re.search(r"```python(.*?)```", result, re.DOTALL)
        output_file = "Gemini3/output_scene.py"

        if code_match:
            final_code = code_match.group(1).strip()
            with open(output_file, "w") as f:
                f.write(final_code)
            logger.console.print(f"\n[bold green]SUCCESS! Animation code saved to {output_file}[/bold green]")
            logger.console.print(f"Run it with: [cyan]manim -pql {output_file} <SceneName>[/cyan]")
        else:
            logger.console.print("\n[bold red]WARNING: No valid Python code block found in the output.[/bold red]")
            logger.console.print("Raw output saved to Gemini3/raw_output.txt")
            with open("Gemini3/raw_output.txt", "w") as f:
                f.write(result)

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
