# Spatial Reasoning Test Output

This directory contains test scripts and source files for spatial reasoning demonstrations.

## Generated Output Files

Previously, this directory contained large generated GIF files (> 20MB each) that have been removed to reduce repository size:
- `DeepSeek_LShape3D_ManimCE_v0.19.0.gif`
- `OpenAIPro_SteppedShape_ManimCE_v0.19.0.gif`

## How to Generate Output

To regenerate these animations, run the corresponding Python scripts:

```bash
manim -pql DeepSeek_LShape3D.py
manim -pql OpenAIPro_LShape3D.py
```

The generated files will be created locally but won't be tracked by git, keeping the repository size manageable.
