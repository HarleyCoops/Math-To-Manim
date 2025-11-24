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
        import json
        
        clean_result = result
        
        # Check if result seems to be a string representation of a JSON object containing 'candidates'
        # This matches the log output structure seen in the user files
        if '"candidates":' in result or '"parts":' in result:
            # Try to extract the "text" field from the parts manually using regex 
            # since parsing the potentially truncated log file as JSON might fail
            # Look for "text": "```python ... ```" pattern accounting for escaped newlines
            
            # This regex looks for "text":" (content) "
            # We want to capture content that starts with ```python
            # The content might be heavily escaped like \"```python\\n...\"
            
            # First, try to normalize the string by interpreting escapes
            try:
                # The logs show the content is inside a JSON structure.
                # Let's try to find the specific text field that contains the python code.
                # It typically looks like: "text": "```python\n..."
                
                # Regex to find the text value associated with the code block
                # We look for "text": " ... ```python ... ``` ... "
                # We allow for escaped quotes inside the value
                
                # A simpler approach: find ```python and the closing ``` in the raw string,
                # then unescape the content.
                
                # Find start index of ```python
                start_marker = "```python"
                start_idx = result.find(start_marker)
                
                if start_idx != -1:
                    # Found the start. Now find the end ```
                    # We start searching from start_idx + len(start_marker)
                    end_idx = result.find("```", start_idx + len(start_marker))
                    
                    if end_idx != -1:
                        # Extract the raw substring
                        raw_code = result[start_idx + len(start_marker):end_idx]
                        
                        # Now we need to unescape it. It likely has \\n for \n, \" for ", etc.
                        # We can use unicode_escape, but we need to be careful about how many levels of escaping there are.
                        # The logs show e.g. "\\nclass" which is single escape level.
                        
                        try:
                            # Convert to bytes then decode with unicode_escape
                            final_code = raw_code.encode('utf-8').decode('unicode_escape')
                            
                            # Write to file
                            output_file = "Gemini3/output_scene.py"
                            with open(output_file, "w") as f:
                                f.write(final_code)
                            logger.console.print(f"\n[bold green]SUCCESS! Animation code saved to {output_file}[/bold green]")
                            logger.console.print(f"Run it with: [cyan]manim -pql {output_file} <SceneName>[/cyan]")
                            return
                        except Exception as e:
                            logger.console.print(f"[bold red]Error unescaping code block: {e}[/bold red]")
            except Exception as e:
                logger.console.print(f"[bold red]Error parsing JSON-like output: {e}[/bold red]")

        # Fallback to standard regex if the above manual extraction didn't return
        code_matches = list(re.finditer(r"```python\s*(.*?)```", result, re.DOTALL | re.IGNORECASE))
        output_file = "Gemini3/output_scene.py"

        if code_matches:
            # Take the last code block found
            final_code = code_matches[-1].group(1).strip()
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
