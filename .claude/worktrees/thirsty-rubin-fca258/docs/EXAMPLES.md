# Math-To-Manim Examples Catalog

This document provides a comprehensive catalog of all animation examples in the repository, organized by topic and difficulty level.

**Note**: The repository has been reorganized for better navigation. Examples are now organized in the [examples/](../examples/) directory by topic.

## Quick Navigation

- [Physics](#physics) - Quantum mechanics, gravity, particle physics
- [Mathematics](#mathematics) - Geometry, analysis, statistics
- [Computer Science](#computer-science) - ML, algorithms, spatial reasoning
- [Cosmology](#cosmology) - Cosmic evolution and probability
- [Finance](#finance) - Option pricing
- [Legacy Structure Reference](#legacy-structure-reference)

## Physics

### Quantum Mechanics and QED

**Location**: [examples/physics/quantum/](../examples/physics/quantum/)

Animations visualizing Quantum Electrodynamics (QED), the quantum field theory of the electromagnetic interaction. Topics include:
- Minkowski spacetime
- Electric and magnetic fields
- Maxwell's equations in tensor form
- QED Lagrangian density
- Feynman diagrams
- Fine structure constant
- Renormalization group flow

**Key Examples:**
- `QED.py` - Comprehensive QED journey
- `SpacetimeQEDScene.py` - Relativistic QED visualization
- `quantum_field_theory.py` - QFT fundamentals
- Various model implementations (Gemini, Grok, Qwen, etc.)

**Example Usage:**
```bash
manim -pql examples/physics/quantum/QED.py QEDJourney
```

### Gravity and General Relativity

**Location**: [examples/physics/gravity/](../examples/physics/gravity/)

Animations depicting gravitational waves and general relativity:
- Spacetime distortion
- LIGO detection method
- Binary black hole mergers

**Example Usage:**
```bash
manim -pql examples/physics/gravity/gravitational_wave.py GravitationalWaveScene
```

### Nuclear Physics

**Location**: [examples/physics/nuclear/](../examples/physics/nuclear/)

Visualizations of atomic structure and radioactive decay.

**Example Usage:**
```bash
manim -pql examples/physics/nuclear/radium_atom.py RadiumAtomScene
```

### Particle Physics

**Location**: [examples/physics/particle_physics/](../examples/physics/particle_physics/)

Advanced particle physics concepts including electroweak symmetry breaking.

**Example Usage:**
```bash
manim -pql examples/physics/particle_physics/ElectroweakSymmetryScene.py ElectroweakSymmetryScene
```

## Mathematics

### Geometry

**Location**: [examples/mathematics/geometry/](../examples/mathematics/geometry/)

Geometric visualizations and proofs:
- `pythagorean.py` - Visual proof of Pythagorean theorem
- `bouncing_balls.py` - Physics simulation
- `rhombicosidodecahedron_*.py` - Complex 3D polyhedron animations

**Example Usage:**
```bash
manim -pql examples/mathematics/geometry/pythagorean.py PythagoreanScene
```

### Mathematical Analysis

**Location**: [examples/mathematics/analysis/](../examples/mathematics/analysis/)

Advanced analysis topics:
- Optimal transport theory
- Benamou-Brenier formulation
- Wasserstein distance
- Diffusion processes
- **Lorenz Attractor Symphony** - Chaos theory visualization

**Key Examples:**
- `lorenz_attractor_symphony.py` - **NEW** Epic 3D visualization of deterministic chaos featuring:
  - The iconic "butterfly" strange attractor with 15,000+ trajectory points
  - Velocity-based color mapping (cool cyan to hot red)
  - Multiple trajectories demonstrating sensitivity to initial conditions
  - Lyapunov exponent mathematics
  - Cinematic camera fly-through
  - LaTeX equations for the complete Lorenz system

**Example Usage:**
```bash
# Full animation (recommended)
manim -pqh examples/mathematics/analysis/lorenz_attractor_symphony.py LorenzAttractorSymphony

# Quick preview
manim -pql examples/mathematics/analysis/lorenz_attractor_symphony.py LorenzAttractorSymphony

# Additional scenes
manim -pql examples/mathematics/analysis/lorenz_attractor_symphony.py LorenzBifurcation
manim -pql examples/mathematics/analysis/lorenz_attractor_symphony.py LorenzPhaseSpace
```

### Fractals

**Location**: [examples/mathematics/fractals/](../examples/mathematics/fractals/)

Fractal patterns and self-similarity visualizations.

**Example Usage:**
```bash
manim -pql examples/mathematics/fractals/fractal_scene.py FractalScene
```

### Statistics and Probability

**Location**: [examples/mathematics/statistics/](../examples/mathematics/statistics/)

Statistical concepts and information geometry:
- Brownian motion
- Information geometry
- Statistical manifolds

**Example Usage:**
```bash
manim -pql examples/mathematics/statistics/information_geometry.py InformationGeometryScene
```

### Trigonometry

**Location**: [examples/mathematics/trigonometry/](../examples/mathematics/trigonometry/)

Trigonometric identities and proofs.

**Example Usage:**
```bash
manim -pql examples/mathematics/trigonometry/TrigInference.py
```

## Computer Science

### Machine Learning

**Location**: [examples/computer_science/machine_learning/](../examples/computer_science/machine_learning/)

Neural network architectures and ML concepts:
- `AlexNet.py` - CNN architecture
- `NativeSparseAttention.py` - Transformer attention mechanisms
- `GRPO.py` - Optimization algorithms
- `regularization.py` - Regularization techniques

**Example Usage:**
```bash
manim -pql examples/computer_science/machine_learning/AlexNet.py AlexNetScene
```

### Algorithms

**Location**: [examples/computer_science/algorithms/](../examples/computer_science/algorithms/)

Classic algorithm visualizations:
- `gale_shaply.py` - Stable matching problem

**Example Usage:**
```bash
manim -pql examples/computer_science/algorithms/gale_shaply.py GaleShapleyScene
```

### Spatial Reasoning

**Location**: [examples/computer_science/spatial_reasoning/](../examples/computer_science/spatial_reasoning/)

3D spatial reasoning tests with L-shaped objects.

**Example Usage:**
```bash
manim -pql examples/computer_science/spatial_reasoning/DeepSeek_LShape3D.py LShape3DScene
```

## Cosmology

**Location**: [examples/cosmology/](../examples/cosmology/)

Cosmic evolution and probability visualizations:
- `Claude37Cosmic.py` - Cosmic evolution
- `CosmicProbabilityScene.py` - Probability in cosmic context

**Example Usage:**
```bash
manim -pql examples/cosmology/Claude37Cosmic.py
```

## Finance

**Location**: [examples/finance/](../examples/finance/)

Financial mathematics visualizations:
- `optionskew.py` - Option price skew

**Example Usage:**
```bash
manim -pql examples/finance/optionskew.py OptionSkewScene
```

## Miscellaneous

**Location**: [examples/misc/](../examples/misc/)

Experimental and demo animations:
- `stickman.py` - Basic animation demo
- `GrokLogo.py` - Logo animation
- `generated_scene.py` - Generic test scenes

**Example Usage:**
```bash
manim -pql examples/misc/stickman.py StickmanScene
```

## How to Run Examples

All examples can be run using the standard Manim command:

```bash
manim [flags] <file_path> <SceneName>
```

Common flags:
- `-p` - Preview after rendering
- `-q` - Quality: `l` (low), `m` (medium), `h` (high), `k` (4K)
- `--format` - Output format (mp4, gif, png, etc.)

Examples:
```bash
# Quick preview (low quality)
manim -pql examples/physics/quantum/QED.py QEDScene

# High quality render
manim -qh examples/mathematics/geometry/pythagorean.py PythagoreanScene

# 4K production quality
manim -qk examples/physics/gravity/gravitational_wave.py GravitationalWaveScene
```

## Legacy Structure Reference

For backward compatibility, the old directory structure is preserved. Here's the mapping:

**Old Location** -> **New Location**
- `Scripts/*.py` -> `examples/<category>/<subcategory>/*.py`
- `app.py` -> `src/app.py`
- `app_claude.py` -> `src/app_claude.py`
- `prerequisite_explorer.py` -> `src/agents/prerequisite_explorer.py`

See [REORGANIZATION_PLAN.md](../REORGANIZATION_PLAN.md) for complete mapping.

## Difficulty Levels

Examples are categorized by difficulty:
- **Beginner**: Basic concepts, suitable for learning Manim
- **Intermediate**: More complex visualizations
- **Advanced**: Sophisticated animations of advanced concepts

## Contributing Examples

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on adding new examples.

## Model Attribution

Examples generated by various AI models:
- DeepSeek R1
- Claude Sonnet 4.5
- Gemini 2.5 Pro
- Grok 3
- Qwen Max
- Mistral Large
- OpenAI GPT-4
