# Math-To-Manim

<div align="center">

<!-- Core Requirements -->
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Manim Version](https://img.shields.io/badge/manim-v0.19.0-orange)](https://www.manim.community/)
[![GitHub Stars](https://img.shields.io/github/stars/HarleyCoops/Math-To-Manim?style=social)](https://github.com/HarleyCoops/Math-To-Manim)

<!-- AI Models / LLMs -->
[![Claude Sonnet 4.5](https://img.shields.io/badge/Claude-Sonnet%204.5-blueviolet)](https://www.anthropic.com)
[![Gemini 3](https://img.shields.io/badge/Gemini-3-4285F4?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Kimi K2](https://img.shields.io/badge/Kimi-K2-00D4AA)](https://kimi.moonshot.cn/)
[![DeepSeek R1](https://img.shields.io/badge/DeepSeek-R1-536DFE)](https://www.deepseek.com/)
[![Grok 3](https://img.shields.io/badge/Grok-3-000000)](https://x.ai/)

</div>

[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left)](https://www.star-history.com/#HarleyCoops/Math-To-Manim&type=date&legend=top-left)

---

<div align="center">

![Math-To-Manim Gemini Edition](public/GeminiM2M.jpeg)

**Transform natural language into beautiful mathematical animations using AI-powered agent pipelines.**

</div>

---

## The Core Innovation: Reverse Knowledge Tree

Most AI animation systems try to learn patterns from examples. **Math-To-Manim does the opposite.**

Instead of pattern matching, we use **Recursive Prerequisite Discovery**:

```
"Explain cosmology"
    |
    v
What must I understand BEFORE cosmology?
    -> General Relativity, Hubble's Law, Redshift, CMB radiation
    |
    v
What must I understand BEFORE General Relativity?
    -> Special Relativity, Differential Geometry, Gravitational Fields
    |
    v
What must I understand BEFORE Special Relativity?
    -> Galilean Relativity, Speed of light, Lorentz Transformations
    |
    v
[Continue until hitting foundational concepts...]
    |
    v
Build animation from foundation -> target concept
```

**Result**: Every animation builds understanding layer by layer, generating verbose LaTeX-rich prompts that produce working code.

---

## Three AI Pipelines, One Goal

Math-To-Manim offers **three distinct AI pipelines**. Choose based on your API access and preferences:

### Pipeline Comparison

| Feature | Gemini 3 (Google ADK) | Claude Sonnet 4.5 | Kimi K2 |
|:--------|:---------------------|:------------------|:--------|
| **Framework** | Google Agent Development Kit | Anthropic Agent SDK | OpenAI-compatible API |
| **Architecture** | Six-Agent Swarm | Six-Agent Pipeline | Three-Stage Enrichment |
| **Strengths** | Complex topology, physics reasoning | Reliable code generation, recursion | Chain-of-thought, structured tools |
| **Best For** | Advanced 3D math, Kerr metrics | General purpose, production use | LaTeX-heavy explanations |
| **Setup Complexity** | Moderate | Simple | Simple |

---

## Pipeline 1: Google Gemini 3 (ADK)

**Location**: `Gemini3/`

The Gemini pipeline uses the **Google Agent Development Kit** with a six-agent swarm architecture. Each agent is a specialist with a specific role in the animation generation process.

### How It Works

```mermaid
graph TD
    UserPrompt[User Prompt] --> CA
    
    CA["<b>1. ConceptAnalyzer</b><br/>Deconstructs prompt into:<br/>- Core concept<br/>- Target audience<br/>- Difficulty level<br/>- Mathematical domain"]
    
    CA --> PE
    PE["<b>2. PrerequisiteExplorer</b><br/>Builds knowledge DAG:<br/>'What must be understood BEFORE X?'<br/>Recursively discovers dependencies"]
    
    PE --> ME
    ME["<b>3. MathematicalEnricher</b><br/>Adds to each node:<br/>- LaTeX definitions<br/>- Key equations<br/>- Theorems/physical laws"]
    
    ME --> VD
    VD["<b>4. VisualDesigner</b><br/>Designs using Manim primitives:<br/>- Visual metaphors (sphere = particle)<br/>- Camera movements<br/>- Color palette (hex codes)<br/>- Transitions"]
    
    VD --> NC
    NC["<b>5. NarrativeComposer</b><br/>Weaves 2000+ token verbose prompt:<br/>- Exact LaTeX strings<br/>- Animation timing<br/>- Scene-by-scene description"]
    
    NC --> CG
    CG["<b>6. CodeGenerator</b><br/>Produces executable Manim code:<br/>- ThreeDScene with camera movements<br/>- Correct LaTeX rendering<br/>- No external assets required"]

    style CA fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:black,align:left
    style PE fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:black,align:left
    style ME fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:black,align:left
    style VD fill:#f3e5f5,stroke:#880e4f,stroke-width:2px,color:black,align:left
    style NC fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:black,align:left
    style CG fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:black,align:left
```

### Quick Start

```bash
# Set API key
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Run the pipeline
python Gemini3/run_pipeline.py "Explain the Hopf Fibration"
```

### Key Files

- `Gemini3/run_pipeline.py` - Entry point
- `Gemini3/src/agents.py` - Agent definitions with system prompts
- `Gemini3/src/pipeline.py` - Orchestration logic
- `Gemini3/docs/GOOGLE_ADK_AGENTS.md` - Full documentation

---

## Pipeline 2: Claude Sonnet 4.5 (Anthropic SDK)

**Location**: `src/`

The Claude pipeline uses the **Anthropic Agent SDK** with automatic context management and built-in tools.

### How It Works

```mermaid
graph TD
    UserPrompt[User Prompt] --> CA
    
    CA["<b>1. ConceptAnalyzer</b><br/>Parses prompt, identifies:<br/>- Core concept<br/>- Domain (physics, math, CS)<br/>- Visualization approach"]
    
    CA --> PE
    PE["<b>2. PrerequisiteExplorer</b><br/>THE KEY INNOVATION:<br/>Recursively asks 'What before X?'<br/>Builds complete knowledge tree<br/>Identifies foundation concepts"]
    
    PE --> ME
    ME["<b>3. MathematicalEnricher</b><br/>Ensures mathematical rigor:<br/>- LaTeX for every equation<br/>- Consistent notation<br/>- Links formulas to visuals"]
    
    ME --> VD
    VD["<b>4. VisualDesigner</b><br/>Specifies exact cinematography:<br/>- Camera angles and movements<br/>- Color schemes with meaning<br/>- Timing and transitions"]
    
    VD --> NC
    NC["<b>5. NarrativeComposer</b><br/>Walks tree from foundation->target:<br/>- 2000+ token verbose prompt<br/>- Narrative arc through concepts"]
    
    NC --> CG
    CG["<b>6. CodeGenerator</b><br/>Translates to Manim:<br/>- Working Python scenes<br/>- Handles LaTeX rendering<br/>- 3D camera movements"]

    style CA fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:black,align:left
    style PE fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:black,align:left
    style ME fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:black,align:left
    style VD fill:#f3e5f5,stroke:#880e4f,stroke-width:2px,color:black,align:left
    style NC fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:black,align:left
    style CG fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:black,align:left
```


### Key Files

- `src/app_claude.py` - Gradio UI entry point
- `src/agents/prerequisite_explorer_claude.py` - Claude SDK agent
- `docs/ARCHITECTURE.md` - System design details

---

## Pipeline 3: Kimi K2 Thinking Model

**Location**: `KimiK2Thinking/`

The Kimi pipeline uses Moonshot AI's **K2 thinking model** with an OpenAI-compatible API and tool-calling interface.

### How It Works

```mermaid
graph TD
    UserPrompt[User Prompt] --> KPE
    
    KPE["<b>1. KimiPrerequisiteExplorer</b><br/>Builds knowledge tree:<br/>- Tool-calling for structured output<br/>- Thinking mode shows reasoning<br/>- Recursive dependency discovery"]
    
    KPE --> ME
    ME["<b>2. MathematicalEnrichment</b><br/>Three-stage enrichment:<br/>- Math Enricher: LaTeX equations, definitions<br/>- Visual Designer: Descriptions (not Manim classes)<br/>- Narrative Composer: Connects everything"]
    
    ME --> CG
    CG["<b>3. CodeGeneration</b><br/>Final Manim code:<br/>- Focuses on LaTeX rendering<br/>- Lets Manim handle visuals<br/>- Tool adapter for verbose instructions"]

    style KPE fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:black,align:left
    style ME fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:black,align:left
    style CG fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:black,align:left
```

### Quick Start

```bash
# Set API key
echo "MOONSHOT_API_KEY=your_key_here" >> .env

# Run prerequisite exploration
python KimiK2Thinking/examples/test_kimi_integration.py

# Run full enrichment pipeline
python KimiK2Thinking/examples/run_enrichment_pipeline.py path/to/tree.json
```

### Key Files

- `KimiK2Thinking/kimi_client.py` - API client
- `KimiK2Thinking/agents/enrichment_chain.py` - Three-stage pipeline
- `KimiK2Thinking/README.md` - Complete documentation

---

## See It In Action

<div align="center">

**Brownian Motion: From Pollen to Portfolio**

![Brownian Motion](public/BrownianFinance.gif)

*A journey from Robert Brown's microscope to Einstein's heat equation, arriving at the Black-Scholes model for financial options pricing.*

---

**Recursive Rhombicosidodecahedron**

![Recursive Rhombicosidodecahedron](public/Rhombicosidodecahedron.gif)

*A fractal Archimedean solid where every vertex spawns another complete rhombicosidodecahedron.*

---

**The Hopf Fibration**

![Teaching Hopf](public/TeachingHopf.gif)

*Stereographic projection of S3 fibers creating nested tori - pure topology rendered in 3D.*

</div>

---

## Installation

```bash
# Clone repository
git clone https://github.com/HarleyCoops/Math-To-Manim
cd Math-To-Manim

# Install dependencies
pip install -r requirements.txt

# Set up your preferred API key
echo "ANTHROPIC_API_KEY=your_key" >> .env    # For Claude
echo "GOOGLE_API_KEY=your_key" >> .env       # For Gemini
echo "MOONSHOT_API_KEY=your_key" >> .env     # For Kimi

# Install FFmpeg (required for video rendering)
# Windows: choco install ffmpeg
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

---

## Run Example Animations

We have **55+ working examples** organized by topic:

```bash
# Physics - Black Hole Symphony
manim -pql examples/physics/black_hole_symphony.py BlackHoleSymphony

# Mathematics - Hopf Fibration
manim -pql examples/misc/epic_hopf.py HopfFibrationEpic

# Finance - Option Pricing
manim -pql examples/finance/optionskew.py OptionSkewScene

# Computer Science - Neural Networks
manim -pql examples/computer_science/machine_learning/AlexNet.py AlexNetScene
```

**Flags**: `-p` preview, `-q` quality (`l` low, `m` medium, `h` high, `k` 4K)

Browse all examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## Repository Structure

```
Math-To-Manim/
|
+-- src/                    # Claude Sonnet 4.5 pipeline
|   +-- agents/             # Agent implementations
|   +-- app_claude.py       # Gradio UI
|
+-- Gemini3/                # Google Gemini 3 pipeline
|   +-- src/                # Agent definitions
|   +-- docs/               # Gemini-specific docs
|   +-- run_pipeline.py     # Entry point
|
+-- KimiK2Thinking/         # Kimi K2 pipeline
|   +-- agents/             # Enrichment chain
|   +-- examples/           # Usage examples
|
+-- examples/               # 55+ working animations
|   +-- physics/            # Quantum, gravity, particles
|   +-- mathematics/        # Geometry, topology, analysis
|   +-- computer_science/   # ML, algorithms
|   +-- cosmology/          # Cosmic evolution
|   +-- finance/            # Option pricing
|
+-- docs/                   # Documentation
+-- tests/                  # Test suite
+-- tools/                  # Utility scripts
```

---

## Why LaTeX-Rich Prompting Works

### The Problem with Vague Prompts

```
"Create an animation showing quantum field theory"
```
**Result**: Generic, incorrect, or broken code.

### The Solution: Verbose LaTeX Prompts

```
"Begin with Minkowski spacetime showing the metric:

$$ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2$$

Each component highlighted in different hues. Introduce the QED Lagrangian:

$$\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}$$

with Dirac spinor $\psi$ in orange, covariant derivative $D_\mu$ in green..."
```
**Result**: Perfect animations with correct LaTeX, camera movements, and timing.

**Our agents generate these verbose prompts automatically** by walking the knowledge tree.

---

## Common Pitfalls (And How We Solve Them)

| Problem | Traditional Approach | Our Solution |
|:--------|:--------------------|:-------------|
| **LaTeX Errors** | Hope for the best | Verbose prompts show exact formulas |
| **Vague Cinematography** | "Show quantum field" | Specify colors, angles, timing |
| **Missing Prerequisites** | Jump to advanced topics | Recursive dependency discovery |
| **Inconsistent Notation** | Mixed symbols | Mathematical enricher maintains consistency |

---

## Technical Requirements

- **Python**: 3.10+
- **API Key**: Anthropic, Google, or Moonshot
- **FFmpeg**: For video rendering
- **Manim Community**: v0.19.0
- **RAM**: 8GB minimum, 16GB recommended

---

## Contributing

We welcome contributions:

1. **Add Examples**: Create animations for new topics
2. **Improve Agents**: Enhance prerequisite discovery
3. **Fix Bugs**: Report and fix issues
4. **Documentation**: Improve guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Documentation

- [Reverse Knowledge Tree](docs/REVERSE_KNOWLEDGE_TREE.md) - Core innovation
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Examples Catalog](docs/EXAMPLES.md) - All 55+ animations
- [Gemini Pipeline](Gemini3/docs/GOOGLE_ADK_AGENTS.md) - Google ADK details
- [Kimi Pipeline](KimiK2Thinking/README.md) - Moonshot AI integration
- [Quick Start Guide](docs/QUICK_START_GUIDE.md) - Get started fast

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- **Manim Community** - Incredible animation framework
- **Anthropic** - Claude Sonnet 4.5 and Agent SDK
- **Google** - Gemini 3 and Agent Development Kit
- **Moonshot AI** - Kimi K2 thinking model
- **1400+ Stargazers** - Thank you for the support!

---

<div align="center">

**Built with recursive reasoning, not training data.**

**Star this repo if you find it useful!**

</div>
