# Math-To-Manim

[INSERT PROJECT LOGO/BANNER HERE]

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red)]()
[![Manim Version](https://img.shields.io/badge/manim-v0.19.0-orange)]()

> Transform mathematical concepts into beautiful animations using AI-powered generation

[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date)](https://star-history.com/#HarleyCoops/Math-To-Manim&Date)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Latest Updates

## SmolAgents Prompt Expander

We now integrate Hugging Face's [SmolAgents](https://github.com/huggingface/smolagents) to automatically expand short user prompts into the detailed LaTeX‑based prompts required for one‑shot animations.

**Installation**
```bash
pip install git+https://github.com/huggingface/smolagents.git@main
```

**Usage**
```bash
python Scripts/smolagent_expander.py "Draw me the universe as explained through cosmology" \
    > expanded_prompt.tex
```

The generated `expanded_prompt.tex` can then be passed to your Math‑To‑Manim pipeline or DeepSeek client to produce fully featured animations.

### Customizing the Expansion Template

By default, the expander uses a built-in system prompt to instruct the agent. You can inspect or override it using the `--system-prompt` flag.

```text
You are an expert prompt engineer specializing in converting short, high-level user descriptions into extremely detailed, step-by-step animation directives for Manim.
Each instruction must use LaTeX for any mathematical expressions.
Your expanded prompt should guide the animation engine through scene setup, camera movements, text renderings, equation animations, and transitions.
Be explicit about durations, visual styles, colors, and scene composition.
Structure your output with clear sections and bullet points.
Do not include any code; only provide the LaTeX-based storyboard for the animation.
```

```bash
python Scripts/smolagent_expander.py "Draw me the universe as explained through cosmology" \
    --system-prompt "$(cat my_system_prompt.txt)" \
    > expanded_prompt.tex
```

## Important Note

This repository contains the **output files** of a mathematical animation generation process, not the complete pipeline. Users can run these files to render the animations on their machines, but the model and methodology used to generate these animation scripts are not included. 

In other words, this repo provides the Manim code that produces the visualizations, but not the AI system that creates this code from mathematical concepts. The complete pipeline from mathematical concept to animation code remains proprietary.

## Overview

This project uses DeepSeek AI (and some Google Gemini (and now #Grok3) to generate mathematical animations using Manim with better prompts. It includes various examples of complex mathematical concepts visualized through animation. The intent here is to attempt to automatically chart concepts that far exceed most humans' capacity to visualize complex connections across math and physics in a one-shot animation.

[INSERT DEMO GIF HERE - Perhaps the QED or Quantum Field Theory animation]

## Features

### Technical Highlights
- **LaTeX Matters**: Base prompt engineering technique yielding much better results for displaying formulas on screen
- **Dual-Stream Output**: Simultaneous animation code + study notes generation
- **Cross-Model Synergy**: Leveraging multiple AI models (DeepSeek, Gemini, Grok3)
- **Automated Documentation**: Generates comprehensive LaTeX documentation

### Real-World Applications
- **Academic Research**: Visualizing complex mathematical proofs
- **Education**: Creating engaging STEM materials
- **Scientific Communication**: Bridging abstract math and visual understanding
- **Research Validation**: Visual verification of mathematical concepts

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/HarleyCoops/Math-To-Manim
   cd Math-To-Manim
   ```

2. **Environment Setup**
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

Your prompts need extreme detail to work effectively. Here's a basic example:

```latex
[EXISTING QUANTUM FIELD THEORY PROMPT HERE]
```

## Examples

### Featured Animations

[INSERT GRID OF ANIMATION PREVIEWS/GIFS]

1. **Quantum Field Theory Journey**
   - [INSERT QED ANIMATION GIF]
   - Source: `grok_quantum2.py`
   - [View Documentation](docs/QwenQED.pdf)

2. **Benamou-Brenier-Wasserstein**
   - [INSERT BBW ANIMATION GIF]
   - Source: `CosmicProbabilityScene.py`
   - [View Documentation](docs/BBW.pdf)

[ADD MORE EXAMPLES WITH PREVIEWS]

## Rendering Options

### Quality Settings
- `-ql` : 480p (development)
- `-qm` : 720p (medium quality)
- `-qh` : 1080p (high quality)
- `-qk` : 4K (ultra high quality)

### Development Tips
```bash
# Quick development preview
python -m manim -pql YourScene.py YourSceneName

# High-quality final render
python -m manim -qh YourScene.py YourSceneName
```

## Documentation

[INSERT DOCUMENTATION DIAGRAM/FLOWCHART]

- [Full Documentation](docs/README.md)
- [API Reference](docs/API.md)
- [Examples Guide](docs/Examples.md)
- [Troubleshooting](docs/Troubleshooting.md)

## Contributing

[INSERT CONTRIBUTION WORKFLOW DIAGRAM]

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the [INSERT LICENSE TYPE] - see the [LICENSE](LICENSE) file for details.

## Spatial Reasoning Test

[EXISTING SPATIAL REASONING TEST CONTENT WITH IMAGES]

## Citation

```bibtex
[EXISTING CITATION]
```

## Acknowledgments

[INSERT ACKNOWLEDGMENTS SECTION]

---

[INSERT FOOTER WITH SOCIAL LINKS/CONTACT INFO] 