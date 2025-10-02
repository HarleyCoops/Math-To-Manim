#!/usr/bin/env python
import sys
import os

# Define the presentation order
presentation_scenes = [
    "CosmicIntroduction",
    "MinkowskiSpace",
    "FieldVisual",
    "MaxwellEquations",
    "LagrangianDensity",
    "FeynmanDiagram",
    "CouplingConstant",
    "Renormalization",
    "FinalScene"
]

if __name__ == "__main__":
    # Set default quality if not specified in command line
    quality = "l"  # low quality for fast rendering
    if len(sys.argv) > 1:
        quality = sys.argv[1]
    
    # Create presentation directory if it doesn't exist
    os.makedirs("presentation", exist_ok=True)
    
    # Render all scenes in sequence
    for i, scene_name in enumerate(presentation_scenes):
        print(f"Rendering scene {i+1}/{len(presentation_scenes)}: {scene_name}")
        os.system(f"python -m manim Hunyuan-T1QED.py {scene_name} -pq{quality}")
        
    print("All scenes rendered successfully!")
    print("Videos are available in the media/videos directory.") 