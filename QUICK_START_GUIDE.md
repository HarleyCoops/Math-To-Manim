# Quick Start Guide - Math-To-Manim

Welcome to Math-To-Manim! This guide will help you get started quickly with the newly reorganized repository.

## For First-Time Users

### 1. Browse Examples by Topic

The repository is now organized by topic. Navigate to the category that interests you:

**Physics Animations**
- [Quantum Mechanics](examples/physics/quantum/) - QED, QFT, quantum field theory
- [Gravity](examples/physics/gravity/) - Gravitational waves, general relativity
- [Nuclear Physics](examples/physics/nuclear/) - Atomic structure, radioactive decay
- [Particle Physics](examples/physics/particle_physics/) - Electroweak symmetry, interactions

**Mathematics Animations**
- [Geometry](examples/mathematics/geometry/) - Pythagorean theorem, polyhedra
- [Analysis](examples/mathematics/analysis/) - Optimal transport, diffusion
- [Fractals](examples/mathematics/fractals/) - Fractal patterns
- [Statistics](examples/mathematics/statistics/) - Information geometry, Brownian motion
- [Trigonometry](examples/mathematics/trigonometry/) - Trig identities

**Computer Science Animations**
- [Machine Learning](examples/computer_science/machine_learning/) - Neural networks, attention
- [Algorithms](examples/computer_science/algorithms/) - Gale-Shapley, sorting
- [Spatial Reasoning](examples/computer_science/spatial_reasoning/) - 3D tests

**Other Topics**
- [Cosmology](examples/cosmology/) - Cosmic evolution, probability
- [Finance](examples/finance/) - Option pricing
- [Miscellaneous](examples/misc/) - Experimental animations

### 2. Install Dependencies

```bash
# Clone repository
git clone https://github.com/HarleyCoops/Math-To-Manim
cd Math-To-Manim

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg
# Windows: choco install ffmpeg
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### 3. Run Your First Animation

Pick any example and render it:

```bash
# Beginner: Pythagorean theorem
manim -pql examples/mathematics/geometry/pythagorean.py PythagoreanScene

# Intermediate: Fractal patterns
manim -pql examples/mathematics/fractals/fractal_scene.py FractalScene

# Advanced: Quantum Electrodynamics
manim -pql examples/physics/quantum/QED.py QEDJourney
```

The `-pql` flags mean:
- `-p` = Preview when done
- `-q` = Quality
- `l` = Low quality (fast rendering for testing)

For high-quality renders, use `-qh` instead of `-ql`.

### 4. Explore the Complete Catalog

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for a complete catalog of all 55+ examples with descriptions and usage instructions.

## For Contributors

### Where to Put New Examples

Add new animations to the appropriate category:

```bash
# Physics example
examples/physics/quantum/my_new_qft_animation.py

# Math example
examples/mathematics/geometry/my_geometry_proof.py

# CS example
examples/computer_science/algorithms/my_sorting_algorithm.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guidelines.

### Understanding the Core Code

The application code lives in [src/](src/):

```bash
src/
├── agents/
│   ├── prerequisite_explorer.py        # Legacy implementation
│   └── prerequisite_explorer_claude.py # Claude Sonnet 4.5 implementation
├── app.py                              # Legacy Gradio interface
└── app_claude.py                       # Claude-based interface
```

### Key Architecture Documents

1. [REVERSE_KNOWLEDGE_TREE.md](docs/REVERSE_KNOWLEDGE_TREE.md) - Core innovation
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
3. [MIGRATION_TO_CLAUDE.md](docs/MIGRATION_TO_CLAUDE.md) - Claude SDK migration
4. [TESTING_ARCHITECTURE.md](docs/TESTING_ARCHITECTURE.md) - Testing strategy

## For Educators

### Finding Examples by Difficulty

**Beginner** (Good for learning Manim basics):
- [pythagorean.py](examples/mathematics/geometry/pythagorean.py)
- [bouncing_balls.py](examples/mathematics/geometry/bouncing_balls.py)
- [stickman.py](examples/misc/stickman.py)
- [TrigInference.py](examples/mathematics/trigonometry/TrigInference.py)

**Intermediate** (Requires domain knowledge):
- [fractal_scene.py](examples/mathematics/fractals/fractal_scene.py)
- [gale_shaply.py](examples/computer_science/algorithms/gale_shaply.py)
- [AlexNet.py](examples/computer_science/machine_learning/AlexNet.py)
- [optionskew.py](examples/finance/optionskew.py)

**Advanced** (Complex mathematical concepts):
- [QED.py](examples/physics/quantum/QED.py)
- [diffusion_optimal_transport.py](examples/mathematics/analysis/diffusion_optimal_transport.py)
- [information_geometry.py](examples/mathematics/statistics/information_geometry.py)
- [ElectroweakSymmetryScene.py](examples/physics/particle_physics/ElectroweakSymmetryScene.py)

### Creating Course Materials

1. Browse examples by topic
2. Render high-quality versions: `manim -qh <file> <scene>`
3. Find rendered videos in `media/videos/<scene>/1080p60/`
4. Use in presentations or online courses

## For Researchers

### Visualizing Your Research

1. Study the [prompt examples](README.md#prompt-requirements) to understand the detail needed
2. Use the Claude-based interface for prompt expansion:
   ```bash
   python src/app_claude.py
   ```
3. The system uses reverse knowledge tree approach - it asks "What must I understand BEFORE X?"
4. See [REVERSE_KNOWLEDGE_TREE.md](docs/REVERSE_KNOWLEDGE_TREE.md) for methodology

### API Usage

Set up your API key:
```bash
# For Claude Sonnet 4.5 (recommended)
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# For legacy DeepSeek
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

## Common Tasks

### Render All Examples in a Category

```bash
# All quantum physics animations
for file in examples/physics/quantum/*.py; do
  manim -ql "$file"
done

# All geometry animations
for file in examples/mathematics/geometry/*.py; do
  manim -ql "$file"
done
```

### Convert to GIF

```bash
manim -pql --format gif examples/mathematics/geometry/pythagorean.py PythagoreanScene
```

### High Quality Production Render

```bash
manim -qk examples/physics/quantum/QED.py QEDJourney
```

This will take much longer but produces 4K quality output.

## Getting Help

- **Examples**: See [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Technical Issues**: Check [docs/MCP_TROUBLESHOOTING.md](docs/MCP_TROUBLESHOOTING.md)
- **Architecture Questions**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Contributing**: Review [CONTRIBUTING.md](CONTRIBUTING.md)
- **File Organization**: See [REORGANIZATION_PLAN.md](REORGANIZATION_PLAN.md)

## What's Next?

1. **Browse Examples**: Explore the [examples/](examples/) directory
2. **Read Core Docs**: Understand the [reverse knowledge tree](docs/REVERSE_KNOWLEDGE_TREE.md) approach
3. **Try the Interface**: Run `python src/app_claude.py` to use the Gradio UI
4. **Contribute**: Add your own examples following the guidelines

## Quick Reference

| Task | Command |
|------|---------|
| Low quality preview | `manim -pql <file> <scene>` |
| High quality render | `manim -qh <file> <scene>` |
| 4K render | `manim -qk <file> <scene>` |
| GIF output | `manim -pql --format gif <file> <scene>` |
| List scenes in file | `manim <file>` |
| Launch Gradio UI | `python src/app_claude.py` |

## Repository Stats

- 55+ animation examples
- 19 example categories
- 6 major topic areas
- 1000+ GitHub stars
- Powered by Claude Sonnet 4.5

---

**Welcome to the Math-To-Manim community!**

For questions or contributions, see [CONTRIBUTING.md](CONTRIBUTING.md) or open an issue on GitHub.
