import re
import json
import os

def extract_code():
    input_file = "Gemini3/raw_output.txt"
    output_file = "Gemini3/output_scene.py"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"Read {len(content)} chars from {input_file}")

    # Strategy 1: Try to parse as JSON if it looks like it
    # The content might be a JSON string or have a JSON object inside
    try:
        # Sometimes the content is wrapped in ```json ... ``` or just raw JSON
        # Or it might be the 'candidates' list directly
        
        # Find the start of the JSON structure
        json_start = content.find('{"candidates"')
        if json_start != -1:
            json_str = content[json_start:]
            # Try to parse
            data = json.loads(json_str)
            # navigate to text
            text_content = data['candidates'][0]['content']['parts'][0]['text']
            print("Successfully parsed JSON content.")
            content = text_content # Replace content with the actual text
    except Exception as e:
        print(f"JSON parsing failed: {e}")
        # Fallback: try unescaping manually if it looks like a JSON string dump
        if "\\n" in content:
            try:
                # This might be dangerous if it's not a valid python string repr
                # content = content.encode('utf-8').decode('unicode_escape')
                pass 
            except:
                pass

    # Strategy 2: Regex search for python block
    # We look for ```python ... ```
    # If the content was JSON escaped, we might need to handle \\n
    
    # Clean content: replace \\n with \n just in case it's raw escaped string
    content_normalized = content.replace('\\n', '\n').replace('\\"', '"')
    
    patterns = [
        r"```python\s*(.*?)```",
        r"```\s*(.*?)```"
    ]
    
    final_code = None
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, content_normalized, re.DOTALL | re.IGNORECASE))
        if matches:
            # Get the last match as it's usually the final code
            final_code = matches[-1].group(1).strip()
            print("Found code block using regex on normalized content.")
            break
            
    if not final_code:
        # Try on original content (if normalized broke something)
        for pattern in patterns:
            matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
            if matches:
                final_code = matches[-1].group(1).strip()
                print("Found code block using regex on original content.")
                break

    if final_code:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_code)
        print(f"Success! Code written to {output_file}")
    else:
        print("Failed to extract code.")

if __name__ == "__main__":
    extract_code()

