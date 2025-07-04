# Math-To-Manim

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Manim Version](https://img.shields.io/badge/manim-v0.19.0-orange)](https://www.manim.community/)

> Transforming mathematical abstractions into visual narratives through AI-powered animation synthesis

[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date)](https://star-history.com/#HarleyCoops/Math-To-Manim&Date)

## A Note on Architecture

This repository houses the **crystallized outputs** of an advanced mathematical animation generation pipeline—not the pipeline itself. Within these directories, you'll find meticulously crafted Manim scripts that transform mathematical concepts into visual experiences. While users can execute these scripts to render animations locally, the underlying AI orchestration that breathes life into these mathematical narratives remains proprietary.

Consider this repository a gallery of mathematical art, where each script represents a successful translation from abstract mathematical thought to concrete visual representation.

**A Testament to AI Capability**: This repository and 99.9% of its code was entirely AI-generated. Christian provided an in-depth outline of the system architecture and desired functionality—nothing more. The implementation, from intricate animation scripts to comprehensive documentation, emerged purely from AI synthesis.

## Recent Developments

**[March 3rd]**: The forthcoming [@smolagents](https://github.com/huggingface/smolagents) integration represents a paradigm shift in accessibility. This trained agent will transform rudimentary prompts into the sophisticated, LaTeX-enriched instructions that our models require—typically spanning 2,000+ tokens. The agent will serve as an intelligent intermediary, allowing users to describe their mathematical visions in natural language while the system handles the complex prompt engineering. Rendering will continue to occur locally, with execution times ranging from minutes to hours depending on scene complexity. The repository already contains numerous exemplars, with the `/Doc` folder showcasing LaTeX outputs rendered as PDFs.

## Project Genesis and Vision

Math-To-Manim emerged from the intersection of advanced language modeling and mathematical visualization. Leveraging DeepSeek AI's capabilities alongside contributions from Google Gemini and Grok3, this project pioneers a new approach to mathematical animation generation through sophisticated prompt engineering.

The core innovation lies not merely in generating animations, but in creating a bridge between human mathematical intuition and machine-generated visual representations that often exceed our cognitive capacity to mentally visualize complex mathematical relationships. The ultimate vision extends toward reinforcement learning-based fine-tuning, achieving perfect one-shot animation generation from textual descriptions alone.

## Technical Innovations & Methodological Breakthroughs

### Core Contributions

- **LaTeX-Centric Prompt Engineering**: A revolutionary approach where mathematical notation becomes the primary communication medium with AI models, yielding dramatically superior formula rendering and mathematical accuracy.

- **Dual-Stream Generation Architecture**: Simultaneous production of animation code and comprehensive study materials without model fine-tuning. By feeding successful scene scripts back to the model with requests for "verbose explanations fully rendered as LaTeX study notes," we achieve automatic generation of educational documentation.

- **Multi-Model Orchestration**: Strategic deployment of multiple AI architectures (DeepSeek, Gemini, Grok3) creates a robust system where each model's strengths complement the others, capturing edge cases and providing diverse perspectives on mathematical visualization.

- **Educational Amplification**: Generated animations transcend mere visualization, serving as pedagogical instruments that decompose complex mathematical concepts into cognitively accessible sequences.

- **Automated Documentation Pipeline**: Beyond animation generation, the system produces comprehensive LaTeX documentation, creating complete educational packages that pair visual and textual learning modalities.

- **Adaptive Complexity Handling**: From elementary geometric proofs to quantum mechanical formulations and optimal transport theory, the system scales gracefully across the mathematical complexity spectrum.

- **Iterative Refinement Framework**: Successful animations feed back into the prompt engineering process, creating a virtuous cycle of continuous improvement.

### Real-World Applications

- **Academic Research**: Visualizing cutting-edge mathematical proofs and theoretical constructs
- **Pedagogical Innovation**: Crafting engaging materials for STEM education at all levels
- **Scientific Communication**: Bridging the chasm between abstract mathematics and intuitive understanding
- **Research Validation**: Providing visual verification and exploration of mathematical conjectures

The underlying model architecture, while not yet a fully fine-tuned variant of [DeepSeek's R1 Zero](https://huggingface.co/deepseek-ai/DeepSeek-R1-Zero), demonstrates remarkable capability through prompt engineering alone. Most generation failures stem from LaTeX interpretation ambiguities—distinguishing between formulas for screen rendering versus code integration.

A particularly fascinating capability is the generation of synchronized "study notes" accompanying each animation. The Benamou animation exemplifies this dual-generation approach, where passing scene code back to the model yields comprehensive mathematical explanations and contextual documentation.

## Quick Start Guide

### 1. Repository Setup
```bash
git clone https://github.com/HarleyCoops/Math-To-Manim
cd Math-To-Manim
```

### 2. Environment Configuration

#### Option 1: Poetry (Recommended)
```bash
# Install Poetry if not present
curl -sSL https://install.python-poetry.org | python3 -

# Configure API credentials
echo "DEEPSEEK_API_KEY=your_key_here" > .env

# Install dependencies and activate environment
poetry install
poetry shell
```

#### Option 2: Traditional pip
```bash
# Configure API credentials
echo "DEEPSEEK_API_KEY=your_key_here" > .env

# Install dependencies
pip install -r requirements.txt
```

### 3. FFmpeg Installation

<details>
<summary>Windows Installation</summary>

- Download from [official builds](https://www.gyan.dev/ffmpeg/builds/)
- Add to system PATH, or use: `choco install ffmpeg`
</details>

<details>
<summary>Linux Installation</summary>

```bash
sudo apt-get install ffmpeg
```
</details>

<details>
<summary>macOS Installation</summary>

```bash
brew install ffmpeg
```
</details>

### 4. Launch the Interface
```bash
python app.py
```

## The Art of Prompt Engineering

Success in mathematical animation generation demands prompts of extraordinary detail and precision. The following example illustrates the baseline complexity required—a testament to the sophisticated communication necessary between human intent and machine interpretation. The secret lies not in conventional prompting, but in speaking the language of LaTeX itself.

```latex
"Begin by slowly fading in a panoramic star field backdrop to set a cosmic stage. As the camera orients itself to reveal a three-dimensional axis frame, introduce a large title reading 'Quantum Field Theory: 
A Journey into the Electromagnetic Interaction,' written in bold, glowing text at the center of the screen. The title shrinks and moves into the upper-left corner, making room for a rotating wireframe representation of 4D Minkowski spacetime—though rendered in 3D for clarity—complete with a light cone that stretches outward. While this wireframe slowly rotates, bring in color-coded equations of the relativistic metric, such as 
ds²=−c²dt²+dx²+dy²+dz², with each component highlighted in a different hue to emphasize the negative time component and positive spatial components.

Next, zoom the camera into the wireframe's origin to introduce the basic concept of a quantum field. Show a ghostly overlay of undulating plane waves in red and blue, symbolizing an electric field and a magnetic field respectively, oscillating perpendicularly in sync. Label these fields as E⃗ and B⃗, placing them on perpendicular axes with small rotating arrows that illustrate their directions over time. Simultaneously, use a dynamic 3D arrow to demonstrate that the wave propagates along the z-axis. 

As the wave advances, display a short excerpt of Maxwell's equations, morphing from their classical form in vector calculus notation to their elegant, relativistic compact form: ∂μFμν=μ₀Jν. Animate each transformation by dissolving and reassembling the symbols, underscoring the transition from standard form to four-vector notation.

Then, shift the focus to the Lagrangian density for quantum electrodynamics (QED):
ℒ_QED = ψ̄(iγμDμ−m)ψ − ¼FμνFμν.

Project this equation onto a semi-transparent plane hovering in front of the wireframe spacetime, with each symbol color-coded: the Dirac spinor ψ in orange, the covariant derivative Dμ in green, the gamma matrices γμ in bright teal, and the field strength tensor Fμν in gold. Let these terms gently pulse to indicate they are dynamic fields in spacetime, not just static quantities. 

While the Lagrangian is on screen, illustrate the gauge invariance by showing a quick animation where ψ acquires a phase factor e^(iα(x)), while the gauge field transforms accordingly. Arrows and short textual callouts appear around the equation to explain how gauge invariance enforces charge conservation.

Next, pan the camera over to a large black background to present a simplified Feynman diagram. Show two electron lines approaching from the left and right, exchanging a wavy photon line in the center. 

The electron lines are labeled e⁻ in bright blue, and the photon line is labeled γ in yellow. Subtitles and small pop-up text boxes narrate how this basic vertex encapsulates the electromagnetic interaction between charged fermions, highlighting that the photon is the force carrier. Then, animate the coupling constant α≈1/137 flashing above the diagram, gradually evolving from a numeric approximation to the symbolic form α=e²/(4πε₀ℏc).

Afterward, transition to a 2D graph that plots the running of the coupling constant α with respect to energy scale, using the renormalization group flow. As the graph materializes, a vertical axis labeled 'Coupling Strength' and a horizontal axis labeled 'Energy Scale' come into view, each sporting major tick marks and numerical values. The curve gently rises, showing α increasing at higher energies. Meanwhile, short textual captions in the corners clarify that this phenomenon arises from virtual particle-antiparticle pairs contributing to vacuum polarization.

In the final sequence, zoom back out to reveal a cohesive collage of all elements: the rotating spacetime grid, the undulating electromagnetic fields, the QED Lagrangian, and the Feynman diagram floating in the foreground. Fade in an overarching summary text reading 'QED: Unifying Light and Matter Through Gauge Theory,' emphasized by a halo effect. The camera then slowly pulls away, letting the cosmic background re-emerge until each component gracefully dissolves, ending on a single star field reminiscent of the opening shot. A concluding subtitle, 'Finis,' appears, marking the animation's closure and prompting reflection on how fundamental quantum field theory is in describing our universe." 
```

## Rendering Pipeline

### Quality Presets
- `-ql` : 480p (rapid prototyping)
- `-qm` : 720p (balanced quality)
- `-qh` : 1080p (production quality)
- `-qk` : 4K (maximum fidelity)

### Rendering Modifiers
- `-p` : Auto-preview upon completion
- `-f` : Reveal in file browser
- `--format gif` : Generate shareable GIF animations

### Output Architecture
```
media/videos/SceneName/[quality]/SceneName.[format]
```

### Development Workflow
```bash
# Rapid iteration during development
python -m manim -pql Scripts/QED.py QEDJourney

# Production-quality final render
python -m manim -qh Scripts/QED.py QEDJourney
```

## Testing Infrastructure

The project incorporates a comprehensive testing framework built on pytest.

### Test Execution

```bash
# Poetry-based execution (recommended)
poetry run test                    # Complete test suite
poetry run pytest -m unit          # Unit tests only
poetry run pytest -m integration   # Integration tests only
poetry run pytest --cov=Scripts    # Coverage analysis

# Standalone validation
python3 tests/test_simple_validation.py  # Basic structural validation
```

### Testing Architecture

- **Unit Tests**: Rapid validation of code structure, imports, and patterns
- **Integration Tests**: Full-stack tests requiring Manim and FFmpeg
- **Coverage Requirements**: Minimum 80% code coverage
- **Reporting**: Terminal output, HTML reports (`htmlcov/`), XML for CI/CD integration

## The Smolagents Revolution

The upcoming smolagents integration promises to democratize mathematical animation creation through several transformative capabilities:

1. **Prompt Translation Engine**: Intelligent transformation of natural language descriptions into the sophisticated, LaTeX-enriched prompts that yield optimal results—automatically expanding simple ideas into the 2,000+ token specifications our models require.

2. **Workflow Orchestration**: Complete pipeline automation from initial concept through detailed prompt generation, Manim code synthesis, and rendering configuration.

3. **Interactive Refinement Loop**: Iterative improvement through natural dialogue, allowing users to sculpt their mathematical visions through conversation.

4. **Knowledge Augmentation**: Automatic enhancement of prompts with relevant mathematical context, visualization best practices, and domain-specific optimizations.

5. **Intelligent Error Recovery**: Automated diagnosis and correction of common generation failures, learning from each interaction to improve future performance.

The smolagent will be released as a standalone repository, designed for seamless integration with this codebase.

## Documentation

- [Examples](docs/EXAMPLES.md) - Curated gallery of mathematical animations
- [Architecture](docs/ARCHITECTURE.md) - Deep dive into system design
- [MCP Troubleshooting](docs/MCP_TROUBLESHOOTING.md) - MCP server resolution guide
- [Contributing](CONTRIBUTING.md) - Contribution guidelines and standards

## Technical Deep Dive: The DeepSeek Advantage

DeepSeek R1-Zero represents the culmination of **multi-year research** into transfer learning, instruction tuning, and long-context neural architectures. Its architecture enables handling of:

- **Complex reading comprehension** (up to 8,192 tokens)  
- **Scenario-based instruction following**  
- **Technical and coding tasks** with exceptional accuracy

Though descended from T5, R1-Zero's modifications to attention mechanisms, context management, and parameter initialization create a fundamentally distinct model.

### Theoretical Foundations

DeepSeek R1-Zero extends the "Attention is All You Need" paradigm through:

1. **Expanded Context Window**  
   - Distributed positional encodings and segment-based attention support sequences up to 8,192 tokens
   - Blockwise local attention in select layers mitigates quadratic memory scaling

2. **Advanced Instruction Tuning**  
   - Exposure to curated prompts (instructions, Q&A, conversations) enhances zero-shot and few-shot performance
   - Reduces hallucination while maintaining creative capability

3. **Semantic Compression**  
   - Encoder compresses textual segments into "semantic slots" for efficient cross-attention
   - Grounded in Manifold Hypothesis: textual input exists on lower-dimensional manifolds amenable to compression

From a cognitive science perspective, R1-Zero balances short-term "working memory" (sequence tokens) with long-term "knowledge representation" (model parameters).

### Architecture Specifications

#### Structural Overview

- **Parameter Count**: ~6.7B  
- **Architecture**: Modified T5 with specialized gating and cross-attention reordering  
- **Context Window**: 8,192 tokens (4× standard T5)  
- **Layer Configuration**: 36 encoder blocks, 36 decoder blocks

#### Detailed Specifications

| Component              | Specification                                    |
|-----------------------|--------------------------------------------------|
| **Architecture Type** | Modified T5 (config: `deepseek_v3`)             |
| **Attention Heads**   | 32 heads (deeper layers)                         |
| **Layer Count**       | 36 encoder + 36 decoder blocks                  |
| **Vocabulary Size**   | 32k tokens (SentencePiece)                      |
| **Positional Encoding**| Absolute + Learned segment-based (8k tokens)   |
| **Training Paradigm** | Instruction-tuned + Domain-specific tasks        |
| **Precision Support** | FP32, FP16, 4-bit, 8-bit quantization           |

## Quantization & Memory Optimization

DeepSeek R1-Zero supports multi-bit quantization for resource optimization:

### 4-Bit Quantization
- **Advantages**: Minimal VRAM usage (~8GB)
- **Trade-offs**: Minor precision loss in generation quality

### 8-Bit Quantization  
- **Advantages**: Reduced memory (~14GB VRAM) with better fidelity
- **Trade-offs**: Slight overhead versus 4-bit

### Full Precision (FP32)
- **Advantages**: Maximum theoretical accuracy
- **Trade-offs**: ~28GB VRAM requirement

Example 4-bit loading with [bitsandbytes](https://github.com/TimDettmers/bitsandbytes):

```python
model_4bit = AutoModelForSeq2SeqLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Zero",
    trust_remote_code=True,
    device_map="auto",
    load_in_4bit=True
)
```

## System Requirements

### Core Dependencies
- **Python** ≥ 3.10  
- **PyTorch** ≥ 2.0  
- **Transformers** ≥ 4.34.0  
- **Accelerate** ≥ 0.24.0  
- **bitsandbytes** ≥ 0.39.0 (for quantization)
- **FFmpeg** (essential for rendering)

### FFmpeg Installation Guide

#### Windows
1. Download from [official builds](https://www.gyan.dev/ffmpeg/builds/)
   - Recommended: "ffmpeg-release-essentials.7z"
2. Extract and add `bin` folder to system PATH
   - Alternative: `choco install ffmpeg`

#### Linux
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built upon the foundations of [Manim Community Edition](https://www.manim.community/) and powered by the collective intelligence of DeepSeek AI, Google Gemini, and Grok3.

## Contributing

We welcome contributions that advance the intersection of AI and mathematical visualization. Please review our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## Support

For issues, feature requests, and discussions, please utilize the [GitHub issue tracker](https://github.com/HarleyCoops/Math-To-Manim/issues).