import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Gemini3', 'src'))
from tools import generate_concept_image

print("Testing NanoBanana tool...")
try:
    path = generate_concept_image("Test Prompt", "test_image")
    print(f"Success! Image generated at: {path}")
except Exception as e:
    print(f"Error: {e}")
