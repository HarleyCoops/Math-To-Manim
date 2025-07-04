# Math-To-Manim

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Manim Version](https://img.shields.io/badge/manim-v0.19.0-orange)](https://www.manim.community/)

> Transform mathematical concepts into beautiful animations using AI-powered generation

[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date)](https://star-history.com/#HarleyCoops/Math-To-Manim&Date)

## Important Note

This repository contains the **output files** of a mathematical animation generation process, not the complete pipeline. Users can run these files to render the animations on their machines, but the model and methodology used to generate these animation scripts are not included. 

In other words, this repo provides the Manim code that produces the visualizations, but not the AI system that creates this code from mathematical concepts. The complete pipeline from mathematical concept to animation code remains proprietary.

## Latest Updates

**[March 3rd]**: I will soon publish an [@smolagents](https://github.com/huggingface/smolagents) that is trained on taking basic prompts and turning them into the prompts the LLM needs. You need about a 2000 token prompt to get fully working manim code out. The agent will make that for you. Rendering will still happen on your machine. The output is the python, depending on the scene, render time could be 5 minutes to 4 hours. There are a wide number of examples already in the repo. The /Doc folder is the Latex output from the model rendered into a PDF. An agent seems like what would help most people so I'll publish that soon.

## Project Overview 

This project uses DeepSeek AI (and some Google Gemini and now #Grok3) to generate mathematical animations using Manim with better prompts. It includes various examples of complex mathematical concepts visualized through animation. The intent here is to attempt to automatically chart concepts that far exceed most humans' capacity to visualize complex connections across math and physics in a one-shot animation. The future intent is to use RL to fine tune a model on all the working verbose prompts to arrive at 100% one-shot animations from only text descriptions.

## Key Features & Innovations

### Technical Highlights
- **LaTeX Matters**: Base prompt engineering technique yielding much better results for displaying formulas on screen.
- **Dual-Stream Output**: Simultaneous animation code + study notes generation. No model fine tuning necessary. Just pass any working python scene script back as a prompt and ask for "verbose explanations fully rendered as latext study notes.." and you will get working latex that renders into a PDF set at Overleaf.
- **Cross-Model Synergy**: Leveraging multiple AI models (DeepSeek, Gemini, Grok3) allows for unique perspectives on mathematical visualization, often catching edge cases a single model might miss.
- **Educational Impact**: The generated animations serve as powerful teaching tools, breaking down complex mathematical concepts into visually digestible sequences.
- **Automated Documentation**: The system not only generates animations but also produces comprehensive LaTeX documentation, creating a complete learning package.
- **Adaptive Complexity**: Can handle everything from basic geometric proofs to advanced topics like quantum mechanics and optimal transport theory.
- **Interactive Development**: The project includes a feedback loop where successful animations can be used to improve prompt engineering for future generations.

### Real-World Applications
- **Academic Research**: Visualizing complex mathematical proofs and theories
- **Education**: Creating engaging materials for STEM courses
- **Scientific Communication**: Bridging the gap between abstract mathematics and visual understanding
- **Research Validation**: Providing visual verification of mathematical concepts and relationships

The model is *not yet* a fully fine-tuned version of [DeepSeek's R1 Zero](https://huggingface.co/deepseek-ai/DeepSeek-R1-Zero), but I am working on that (Still working on this, better prompting still works best). Most errors you will encounter when attempting animations on your own in one shot will be related to how LaTeX is being interpreted as a formula to be rendered on the screen or as part of the code itself. 

An interesting new thing to ask for is the capacity to generate simultaneous "study notes" that accompany each animation with a complete explanation of the math and context of the animation. The Benamou animation and notes were the first attempt at this. This also just works straight from the prompt if you pass the scene code directly back to the model.

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/HarleyCoops/Math-To-Manim
   cd Math-To-Manim
   ```

2. **Environment Setup**

   ### Option 1: Using Poetry (Recommended)
   ```bash
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Create and configure .env file with your API key
   echo "DEEPSEEK_API_KEY=your_key_here" > .env
   
   # Install all dependencies
   poetry install
   
   # Activate virtual environment
   poetry shell
   ```
   
   ### Option 2: Using pip
   ```bash
   # Create and configure .env file with your API key
   echo "DEEPSEEK_API_KEY=your_key_here" > .env
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   <details>
   <summary>Windows</summary>
   
   - Download from https://www.gyan.dev/ffmpeg/builds/
   - Add to PATH or use: `choco install ffmpeg`
   </details>

   <details>
   <summary>Linux</summary>
   
   ```bash
   sudo apt-get install ffmpeg
   ```
   </details>

   <details>
   <summary>macOS</summary>
   
   ```bash
   brew install ffmpeg
   ```
   </details>

4. **Launch Interface**
   ```bash
   python app.py
   ```

## Prompt Requirements

Your prompts need extreme detail in order for this to work. For example, this below is a BASIC prompt. You MUST have this level of detail. Most people can't write half of this so the project uses training to try and improve what someone might write as a basic prompt into a what the LLMs are actually looking for. Anyone can do this on your own, I promise this is all prompting but the secret NOT prompting in english - you have to prompt in Latex. Happy hunting!

```latex
"Begin by slowly fading in a panoramic star field backdrop to set a cosmic stage. As the camera orients itself to reveal a three-dimensional axis frame, introduce a large title reading 'Quantum Field Theory: 
A Journey into the Electromagnetic Interaction,' written in bold, glowing text at the center of the screen. The title shrinks and moves into the upper-left corner, making room for a rotating wireframe representation of 4D Minkowski spacetime—though rendered in 3D for clarity—complete with a light cone that stretches outward. While this wireframe slowly rotates, bring in color-coded equations of the relativistic metric, such as 
ds2=−c2dt2+dx2+dy2+dz2ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2, with each component highlighted in a different hue to emphasize the negative time component and positive spatial components.

Next, zoom the camera into the wireframe's origin to introduce the basic concept of a quantum field. Show a ghostly overlay of undulating plane waves in red and blue, symbolizing an electric field and a magnetic field respectively, oscillating perpendicularly in sync. Label these fields as E⃗\\vec{E} and B⃗\\vec{B}, placing them on perpendicular axes with small rotating arrows that illustrate their directions over time. Simultaneously, use a dynamic 3D arrow to demonstrate that the wave propagates along the z-axis. 

As the wave advances, display a short excerpt of Maxwell's equations, morphing from their classical form in vector calculus notation to their elegant, relativistic compact form: ∂μFμν=μ0Jν\\partial_\\mu F^{\\mu \\nu} = \\mu_0 J^\\nu. Animate each transformation by dissolving and reassembling the symbols, underscoring the transition from standard form to four-vector notation.

Then, shift the focus to the Lagrangian density for quantum electrodynamics (QED):
LQED=ψ̄(iγμDμ−m)ψ−14FμνFμν.\\mathcal{L}_{\\text{QED}} = \\bar{\\psi}(i \\gamma^\\mu D_\\mu - m)\\psi - \\tfrac{1}{4}F_{\\mu\\nu}F^{\\mu\\nu}.

Project this equation onto a semi-transparent plane hovering in front of the wireframe spacetime, with each symbol color-coded: the Dirac spinor ψ\\psi in orange, the covariant derivative Dμ D_\\mu in green, the gamma matrices γμ\\gamma^\\mu in bright teal, and the field strength tensor Fμν F_{\\mu\\nu} in gold. Let these terms gently pulse to indicate they are dynamic fields in spacetime, not just static quantities. 

While the Lagrangian is on screen, illustrate the gauge invariance by showing a quick animation where ψ\\psi acquires a phase factor eiα(x)e^{i \\alpha(x)}, while the gauge field transforms accordingly. Arrows and short textual callouts appear around the equation to explain how gauge invariance enforces charge conservation.
Next, pan the camera over to a large black background to present a simplified Feynman diagram. Show two electron lines approaching from the left and right, exchanging a wavy photon line in the center. 

The electron lines are labeled e−e^- in bright blue, and the photon line is labeled γ\\gamma in yellow. Subtitles and small pop-up text boxes narrate how this basic vertex encapsulates the electromagnetic interaction between charged fermions, highlighting that the photon is the force carrier. Then, animate the coupling constant α≈1137\\alpha \\approx \\frac{1}{137} flashing above the diagram, gradually evolving from a numeric approximation to the symbolic form α=e24πε0ℏc\\alpha = \\frac{e^2}{4 \\pi \\epsilon_0 \\hbar c}.

Afterward, transition to a 2D graph that plots the running of the coupling constant α\\alpha with respect to energy scale, using the renormalization group flow. As the graph materializes, a vertical axis labeled 'Coupling Strength' and a horizontal axis labeled 'Energy Scale' come into view, each sporting major tick marks and numerical values. The curve gentl...(truncated from 20157 characters)...nwhile, short textual captions in the corners clarify that this phenomenon arises from virtual particle-antiparticle pairs contributing to vacuum polarization.

In the final sequence, zoom back out to reveal a cohesive collage of all elements: the rotating spacetime grid, the undulating electromagnetic fields, the QED Lagrangian, and the Feynman diagram floating in the foreground. Fade in an overarching summary text reading 'QED: Unifying Light and Matter Through Gauge Theory,' emphasized by a halo effect. The camera then slowly pulls away, letting the cosmic background re-emerge until each component gracefully dissolves, ending on a single star field reminiscent of the opening shot. A concluding subtitle, 'Finis,' appears, marking the animation's closure and prompting reflection on how fundamental quantum field theory is in describing our universe." 
```

## Rendering Options

### Quality Settings
- `-ql` : 480p (development)
- `-qm` : 720p (medium quality)
- `-qh` : 1080p (high quality)
- `-qk` : 4K (ultra high quality)

### Additional Rendering Options
- `-p` Preview the animation when done
- `-f` Show the output file in file browser

### Output Location
The rendered animation will be saved in:
```
media/videos/SceneName/[quality]/SceneName.[format]
```

### Development Tips
1. Use `-pql` during development for quick previews
2. Use `-qh` for final renders
3. Add `-f` to easily locate output files
4. Use `--format gif` for easily shareable animations

For example:
```bash
# During development (preview QEDJourney scene from QED.py in low quality)
python -m manim -pql QED.py QEDJourney

# Final render (render QEDJourney scene from QED.py in high quality)
python -m manim -qh QED.py QEDJourney
```

## Testing

The project now includes a comprehensive testing infrastructure using pytest.

### Running Tests

```bash
# With Poetry (recommended)
poetry run test              # Run all tests
poetry run pytest -m unit    # Run unit tests only
poetry run pytest -m integration  # Run integration tests only
poetry run pytest --cov=Scripts   # Run with coverage report

# Without full environment
python3 tests/test_simple_validation.py  # Basic validation tests
```

### Test Coverage

- **Unit Tests**: Fast tests for code structure, imports, and patterns
- **Integration Tests**: Tests that require Manim and FFmpeg for actual rendering
- **Coverage Requirement**: 80% minimum
- **Reports**: Terminal output, HTML (`htmlcov/`), and XML for CI/CD

## Upcoming Smolagents Integration

The upcoming smolagents integration will revolutionize how you interact with Math-To-Manim:

1. **Prompt Translation**: The smolagent will transform simple, natural language descriptions into the detailed, LaTeX-rich prompts required by the LLM to generate high-quality Manim code.

2. **Workflow Automation**: The agent will handle the entire pipeline from basic prompt → detailed prompt → Manim code generation → rendering configuration.

3. **Interactive Refinement**: You'll be able to iteratively refine your animations through natural conversation with the agent.

4. **Knowledge Augmentation**: The agent will automatically enhance your prompts with relevant mathematical context and visualization best practices.

5. **Error Handling**: When the generated code has issues, the agent will automatically diagnose and fix common problems.

The smolagent will be published as a separate repository that you can easily integrate with this codebase. Stay tuned for the release announcement!

## Documentation

- [Examples](docs/EXAMPLES.md) - Showcase of various mathematical animations
- [Architecture](docs/ARCHITECTURE.md) - Technical details of the system
- [MCP Troubleshooting](docs/MCP_TROUBLESHOOTING.md) - Guide for resolving MCP server issues
- [Contributing](CONTRIBUTING.md) - Guidelines for contributing to the project

## Technical Details: Why DeepSeek Might Be So Good At This

DeepSeek R1-Zero represents the culmination of **multi-year research** at DeepSeek AI into **transfer learning**, **instruction tuning**, and **long-context neural architectures**. Its central objective is to provide a single, all-purpose encoder-decoder model that can handle:

- **Complex reading comprehension** (up to 8,192 tokens)  
- **Scenario-based instruction following** (e.g., "Given a set of constraints, produce a short plan.")  
- **Technical and coding tasks** (including code generation, transformation, and debugging assistance)  

Though R1-Zero is a "descendant" of T5, the modifications to attention, context management, and parameter initialization distinguish it significantly from vanilla T5 implementations.

### Philosophical & Theoretical Foundations

While standard Transformer models rely on the "Attention is All You Need" paradigm (Vaswani et al., 2017), **DeepSeek R1-Zero** extends this by:

1. **Expanded Context Window**  
   - By employing distributed positional encodings and segment-based attention, R1-Zero tolerates sequences up to 8,192 tokens.  
   - The extended context window leverages **blockwise local attention** (in certain layers) to mitigate quadratic scaling in memory usage.

2. **Instruction Tuning**  
   - Similar to frameworks like FLAN-T5 or InstructGPT, R1-Zero was exposed to curated prompts (instructions, Q&A, conversation) to improve zero-shot and few-shot performance.  
   - This approach helps the model produce more stable, context-aware answers and reduces "hallucination" events.

3. **Semantic Compression**  
   - The encoder can compress textual segments into "semantic slots," enabling more efficient cross-attention in the decoder stage.  
   - This is theoretically grounded in **Manifold Hypothesis** arguments, where the textual input can be seen as lying on a lower-dimensional manifold, thus amenable to a compressed representation.

From a **cognitive science** perspective, R1-Zero aspires to mimic a layered approach to knowledge assimilation, balancing short-term "working memory" (sequence tokens) with long-term "knowledge representation" (model parameters).

### Model Architecture

#### Summary of Structural Modifications

- **Parameter Count**: ~6.7B  
- **Encoder-Decoder**: Maintains T5's text-to-text approach but with specialized gating and partial reordering in cross-attention blocks.  
- **Context Window**: 8,192 tokens (a 4× expansion over many standard T5 models).  
- **Layer Stacking**: The modifications allow some dynamic scheduling of attention heads, facilitating better throughput in multi-GPU environments.

#### Detailed Specifications

| Aspect                      | Specification                                     |
|----------------------------|---------------------------------------------------|
| **Architecture Type**      | Modified T5 (custom config named `deepseek_v3`)  |
| **Heads per Attention**    | 32 heads (in deeper layers)                      |
| **Layer Count**            | 36 encoder blocks, 36 decoder blocks             |
| **Vocabulary Size**        | 32k tokens (SentencePiece-based)                 |
| **Positional Encoding**    | Absolute + Learned segment-based for 8k tokens   |
| **Training Paradigm**      | Instruction-tuned + Additional domain tasks      |
| **Precision**              | FP32, FP16, 4-bit, 8-bit quantization (via BnB)  |

## Quantization & Memory Footprint

DeepSeek R1-Zero supports **multi-bit quantization** to optimize memory usage:

1. **4-Bit Quantization**  
   - **Pros**: Minimizes VRAM usage (~8GB).  
   - **Cons**: Potentially minor losses in numeric accuracy or generative quality.

2. **8-Bit Quantization**  
   - **Pros**: Still significantly reduces memory (~14GB VRAM).  
   - **Cons**: Slight overhead vs. 4-bit but often better fidelity.

3. **Full Precision (FP32)**  
   - **Pros**: The highest theoretical accuracy.  
   - **Cons**: ~28GB VRAM usage, not feasible on smaller GPUs.

Sample quantized load (4-bit) with [bitsandbytes](https://github.com/TimDettmers/bitsandbytes):

```python
model_4bit = AutoModelForSeq2SeqLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Zero",
    trust_remote_code=True,
    device_map="auto",
    load_in_4bit=True
)
```

## Installation & Requirements

### Requirements

- **Python** >= 3.8  
- **PyTorch** >= 2.0  
- **Transformers** >= 4.34.0  
- **Accelerate** >= 0.24.0  
- **bitsandbytes** >= 0.39.0 (if using 4-bit/8-bit)
- **FFmpeg** (required for video rendering)

### Installing FFmpeg

FFmpeg is required for Manim to render animations. Here's how to install it:

#### Windows:
1. Download from https://www.gyan.dev/ffmpeg/builds/ 
   - Recommended: "ffmpeg-release-essentials.7z"
2. Extract the archive
3. Add the `bin` folder to your system PATH
   - Or install via package manager: `choco install ffmpeg`

#### Linux:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

### Installing via `pip`

```bash
pip install --upgrade torch transformers accelerate bitsandbytes
```

If your environment's default PyTorch is older than 2.0, consider updating or installing from PyPI/conda channels that provide a recent version.

## License & Usage Restrictions

[Insert license information here]

## Acknowledgments

[Insert acknowledgments here]

# Math-To-Manim Documentation

Welcome to the Math-To-Manim documentation! This directory contains comprehensive documentation for the Math-To-Manim project.

## Table of Contents

- [Architecture](ARCHITECTURE.md) - Technical details of the system architecture
- [Examples](EXAMPLES.md) - Showcase of various mathematical animations
- [MCP Troubleshooting](MCP_TROUBLESHOOTING.md) - Guide for resolving MCP server issues
- [Smolagents Implementation](SMOLAGENTS_IMPLEMENTATION.md) - Details on the smolagents integration

## Getting Started

If you're new to Math-To-Manim, we recommend starting with the main [README.md](../README.md) file in the root directory, which provides an overview of the project and installation instructions.

## Contributing to Documentation

We welcome contributions to the documentation! If you find any errors or have suggestions for improvements, please feel free to submit a pull request or open an issue.

When contributing to documentation, please follow these guidelines:

1. Use clear, concise language
2. Include examples where appropriate
3. Use proper Markdown formatting
4. Keep documentation up-to-date with code changes

## Building Documentation

The documentation is written in Markdown and can be viewed directly on GitHub or in any Markdown viewer.

If you want to generate a more polished documentation site, you can use tools like MkDocs or Sphinx with the markdown extension. Instructions for setting up these tools will be added in the future.

