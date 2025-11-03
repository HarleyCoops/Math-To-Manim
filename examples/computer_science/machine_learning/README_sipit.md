# SiPIT Prompt-Latent Space Mapping Animation

## Overview

This animation explains the concept of how Large Language Models (LLMs) create an injective mapping from prompts to latent representations, and how SiPIT (a proposed inversion method) can invert this mapping.

## Key Concepts Visualized

1. **Prompt Space**: A complex, curved manifold where every point represents a unique input prompt
2. **Latent Space**: A structured, multi-dimensional numerical space (ℝᵈ) where LLMs represent information
3. **LLM Mapping**: The forward transformation from Prompt Space to Latent Space
4. **Injective Property**: The mathematical guarantee that distinct prompts map to distinct latent representations (δ > 0 ⇒ ε > 0)
5. **SiPIT Inversion**: The inverse mapping from Latent Space back to Prompt Space

## Animation Structure

The animation follows this narrative flow:

1. **Introduction**: Title and concept overview
2. **Prompt Space Creation**: Visualizes the curved, beige-colored manifold with scattered prompt points
3. **Latent Space Creation**: Shows the 2D Cartesian coordinate system representing embeddings
4. **Two Distinct Prompts**: Introduces points x and x' with distance δ
5. **LLM Forward Mapping**: Shows how x maps to z and x' maps to z' via curved arrows
6. **Injective Property Explanation**: Demonstrates the mathematical relationship δ > 0 ⇒ ε > 0
7. **SiPIT Inversion**: Shows the reverse mapping from latent space back to prompt space
8. **Conclusion**: Summary caption and key takeaways

## Running the Animation

```bash
# Low quality (fast preview)
manim -pql examples/computer_science/machine_learning/sipit_prompt_latent_space.py PromptLatentSpaceMapping

# Medium quality
manim -pqm examples/computer_science/machine_learning/sipit_prompt_latent_space.py PromptLatentSpaceMapping

# High quality
manim -pqh examples/computer_science/machine_learning/sipit_prompt_latent_space.py PromptLatentSpaceMapping
```

## Visual Design

- **Colors**:
  - Beige/Light Beige: Prompt Space surface
  - Light Gray: Latent Space grid
  - Blue: LLM mapping arrows and labels
  - Purple: SiPIT inversion arrows and labels
  - Red: Distance indicators (δ, ε)
  - Green: Injective property highlighting
  - Black: Point markers

- **Animation Style**:
  - Smooth transitions between scenes
  - Curved arrows showing mappings
  - Progressive revelation of concepts
  - Mathematical notation rendered in LaTeX
  - Verbose explanatory text overlays

## Mathematical Content

The animation emphasizes:
- **Injective Mapping**: δ > 0 ⇒ ε > 0
- **Prompt Space**: Complex manifold structure
- **Latent Space**: ℝᵈ representation
- **Bidirectional Mapping**: Forward (LLM) and backward (SiPIT)

## Educational Use

This animation is suitable for:
- Explaining LLM embedding concepts
- Teaching injective functions in mathematics
- Demonstrating latent space representations
- Introducing prompt inversion methods

## Requirements

- Manim Community Edition v0.19.0
- Python 3.10+
- NumPy

## Notes

- The Prompt Space uses curved parametric functions to simulate a 3D manifold appearance
- The Latent Space is simplified to 2D for clarity, but represents ℝᵈ in general
- All distances and positions are approximate for visualization purposes
