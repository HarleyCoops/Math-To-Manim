import sys
import os

print("Starting test...")
try:
    from Gemini3.src.tools import generate_concept_image
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()




