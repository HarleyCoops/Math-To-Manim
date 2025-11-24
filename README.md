# Math-To-Manim

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red)](https://ffmpeg.org/)
[![Manim Version](https://img.shields.io/badge/manim-v0.19.0-orange)](https://www.manim.community/)
[![Claude Sonnet 4.5](https://img.shields.io/badge/Claude-Sonnet%204.5-blueviolet)](https://www.anthropic.com)


[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=date&legend=top-left)](https://www.star-history.com/#HarleyCoops/Math-To-Manim&type=date&legend=top-left)

---

<div align="center">

# The Hopf Fibration

![Hopf Fibration](public/TeachingHopf.gif)

*A visualization of the S3 to S2 mapping, showing how 4D hypersphere fibers map to linked circles in 3D space. Generated purely from a natural language prompt using the new Gemini 3 Agent Pipeline.*

</div>

---

## NEW: Google Gemini 3 Agent Pipeline (November 24, 2025)

**Full Google ADK Agent pipeline now available!** See `Gemini3/` folder for complete implementation.

We've refactored the entire system to use the **Google Agent Development Kit (ADK)** and **Gemini 3** models:
- **Six-Agent Swarm** - Concept Analyzer, Prerequisite Explorer, Math Enricher, Visual Designer, Narrative Composer, Code Generator
- **Google ADK Integration** - Native agent orchestration
- **Gemini 3 Reasoning** - State-of-the-art logic for complex topology and physics
- **Full Pipeline Refactor** - Clean, modular agent architecture

**Quick Start:**
```bash
# Set API key
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Run full pipeline
python Gemini3/run_pipeline.py "Explain the Hopf Fibration"
```

**Full docs**: [Gemini3/docs/GOOGLE_ADK_AGENTS.md](Gemini3/docs/GOOGLE_ADK_AGENTS.md)

> **Note:** The original **Claude Sonnet 4.5**, **Kimi K2**, and **DeepSeek** pipelines all still work! Use the one that fits your API access and needs.

---

## NEW: Kimi K2 Implementation (November 6, 2025)

**Full Kimi K2 pipeline now available!** See `KimiK2Thinking/` folder for complete implementation.

We've built an alternative pipeline using **Kimi K2 thinking model** from Moonshot AI with:
- **OpenAI-compatible API** - Easier integration
- **Tool-calling interface** - Structured data extraction via function calling  
- **Complete enrichment chain** - Math, visual, and narrative agents
- **LaTeX-focused** - Focuses on exact math rendering, lets Manim handle visuals

**Quick Start:**
```bash
# Set API key
echo "MOONSHOT_API_KEY=your_key_here" >> .env

# Run full pipeline
python KimiK2Thinking/examples/run_enrichment_pipeline.py tree.json
```

**Full docs**: [KimiK2Thinking/README.md](KimiK2Thinking/README.md)

---

## See It In Action

<div align="center">

**Brownian Motion: From Pollen to Portfolio**

![Brownian Motion](public/BrownianFinance.gif)

*A journey from Robert Brown's microscope to Einstein's heat equation, arriving at the Black-Scholes model for financial options pricing. Visualizes the connection between random walks, diffusion, and stochastic calculus.*

---

**ProLIP: Probabilistic Vision-Language Model**

![ProLIP Animation](media/videos/prolip/480p15/ProLIPScene_preview.gif)

*Automatic visualization of contrastive learning, uncertainty quantification, and probabilistic embeddings — generated from a single natural language prompt.*

---

**GRPO: Group Relative Policy Optimization**

![GRPO Animation](media/videos/GRPO2/480p15/GRPOArtisticExplanationOnly_ManimCE_v0.19.0.gif)

*Complete visualization of Group Relative Policy Optimization for reinforcement learning — showing policy updates, reward shaping, and gradient flow through neural networks. Generated from a single prompt with zero manual editing.*

---

**Recursive Rhombicosidodecahedron**

![Recursive Rhombicosidodecahedron](public/Rhombicosidodecahedron.gif)

*A fractal Archimedean solid where every vertex spawns another complete rhombicosidodecahedron, showcasing precise 3D transformations and recursive geometry driven from a single prompt.*

</div>

---

## What This Does

You give me: **"explain quantum field theory"**

I give you back: **A complete Manim animation** showing Minkowski spacetime, QED Lagrangians, Feynman diagrams, renormalization flow - with 2000+ tokens of LaTeX-rich instructions that actually render correctly.

**The secret?** I don't use training data. I use a **Reverse Knowledge Tree** that asks "What must I understand BEFORE X?" recursively until hitting foundation concepts, then builds animations from the ground up.

---

## The Innovation: Reverse Knowledge Tree

Most systems try to learn patterns from examples. I do the opposite.

### The Problem I Solved

Traditional approach:
```
Simple prompt -> Pattern matching -> Hope for the best
```

Problems:
- Requires massive training datasets
- Brittle when concepts are new
- Can't handle edge cases
- Limited to what it's seen before

### My Approach: Recursive Prerequisite Discovery

```
"Explain cosmology"
    v
What must I understand BEFORE cosmology?
    -> General Relativity
    -> Hubble's Law
    -> Redshift
    -> CMB radiation
    v
What must I understand BEFORE General Relativity?
    -> Special Relativity
    -> Differential Geometry
    -> Gravitational Fields
    v
What must I understand BEFORE Special Relativity?
    -> Galilean Relativity
    -> Speed of light
    -> Lorentz Transformations
    v
[Continue until hitting high school physics...]
    v
Build animation from foundation -> target
```

**Result**: Every animation builds conceptual understanding layer by layer, naturally creating the verbose prompts that actually work.

### Future: Semantic Knowledge Graphs

**Coming Soon**: Integration with [Nomic Atlas](https://atlas.nomic.ai/) to create a semantic knowledge graph:
- **10x faster** prerequisite discovery (cached graph instead of recursive Claude calls)
- **Interactive visualization** of entire learning paths (algebra -> quantum field theory)
- **Community knowledge** - everyone contributes to shared concept database
- **Automatic discovery** of prerequisite relationships via embeddings

See [docs/NOMIC_ATLAS_INTEGRATION.md](docs/NOMIC_ATLAS_INTEGRATION.md) for the complete vision.

Read the full technical explanation: [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md)

---

## How It Works: The Agent Pipeline

I've built a 6-agent system powered by Claude Sonnet 4.5 (with a 7th VideoReview agent underway):

### 1. ConceptAnalyzer
- Parses your casual prompt
- Identifies core concept, domain, difficulty level
- Determines visualization approach

### 2. PrerequisiteExplorer (The Key Innovation)
- Recursively asks "What before X?"
- Builds complete knowledge tree
- Identifies foundation concepts
- Creates conceptual dependency graph

### 3. MathematicalEnricher
- Adds LaTeX equations to each tree node
- Ensures mathematical rigor
- Links formulas to visualizations

### 4. VisualDesigner
- Specifies camera movements, colors, animations
- Maps concepts to visual metaphors
- Designs scene transitions

### 5. NarrativeComposer
- Walks the tree from foundation -> target
- Generates 2000+ token verbose prompt
- Weaves narrative arc through concepts

### 6. CodeGenerator
- Translates verbose prompt -> Manim code
- Handles LaTeX rendering correctly
- Produces working Python scenes

### 7. VideoReview *(Planned)*
- Automates post-render QA for the generated MP4
- Uses the video review toolkit to extract frames and build a web player
- Prepares review artifacts (metadata, frame set, HTML player) for fast iteration

**Technology**: Claude Agent SDK with automatic context management, built-in tools, and MCP integration.

See full architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/HarleyCoops/Math-To-Manim
cd Math-To-Manim

# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Install FFmpeg
# Windows: choco install ffmpeg
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Try the Agent Pipeline

```bash
# Launch Gradio interface
python src/app_claude.py
```

Then enter a simple prompt like:
- "explain quantum mechanics"
- "visualize optimal transport theory"
- "show me the Pythagorean theorem"

Watch the agents build the knowledge tree and generate the verbose prompt automatically.

### Run Example Animations

I've organized 55+ working examples by topic:

```bash
# Physics - Quantum mechanics
manim -pql examples/physics/quantum/QED.py QEDJourney

# Mathematics - Geometry
manim -pql examples/mathematics/geometry/pythagorean.py PythagoreanScene

# Computer Science - Neural networks
manim -pql examples/computer_science/machine_learning/AlexNet.py AlexNetScene

# Cosmology
manim -pql examples/cosmology/Claude37Cosmic.py CosmicScene
```

**Flags**:
- `-p` = Preview when done
- `-q` = Quality (`l` low, `m` medium, `h` high, `k` 4K)

Browse all examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## Repository Structure

```
Math-To-Manim/
├── src/                        # Core agent system
│   ├── agents/
│   │   ├── prerequisite_explorer_claude.py   # Reverse knowledge tree agent
│   │   └── prerequisite_explorer.py          # Legacy implementation
│   ├── app_claude.py                         # Gradio UI (Claude SDK)
│   └── app.py                                # Legacy UI
│
├── examples/                   # 55+ working animations
│   ├── physics/
│   │   ├── quantum/           # 13 QED/QFT animations
│   │   ├── gravity/           # Gravitational waves
│   │   ├── nuclear/           # Atomic structure
│   │   └── particle_physics/  # Electroweak symmetry
│   ├── mathematics/
│   │   ├── geometry/          # Proofs, 3D shapes
│   │   ├── analysis/          # Optimal transport, diffusion
│   │   ├── fractals/          # Fractal patterns
│   │   ├── statistics/        # Information geometry
│   │   └── trigonometry/      # Trig identities
│   ├── computer_science/
│   │   ├── machine_learning/  # Neural nets, attention
│   │   ├── algorithms/        # Gale-Shapley, sorting
│   │   └── spatial_reasoning/ # 3D tests
│   ├── cosmology/             # Cosmic evolution
│   ├── finance/               # Option pricing
│   └── misc/                  # Experimental
│
├── docs/                       # Documentation
│   ├── EXAMPLES.md            # Complete catalog
│   ├── ARCHITECTURE.md        # System design
│   ├── MIGRATION_TO_CLAUDE.md # Claude SDK migration
│   └── TESTING_ARCHITECTURE.md
│
└── tests/                      # Testing infrastructure
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## The Secret: LaTeX-Rich Prompting

Most people prompt in English. That's why it fails.

### Wrong Way (English)
```
"Create an animation showing quantum field theory"
```
Result: Generic, incorrect, or broken code.

### Right Way (LaTeX + Detailed Cinematography)
```
"Begin by slowly fading in a panoramic star field backdrop. As the camera
orients itself, introduce a title reading 'Quantum Field Theory: A Journey
into the Electromagnetic Interaction' in bold glowing text. The title shrinks
and moves to the upper-left corner, making room for a rotating wireframe
representation of 4D Minkowski spacetime. Display the relativistic metric:

$$ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2$$

with each component highlighted in a different hue to emphasize the negative
time component. Zoom into the origin to introduce undulating plane waves in
red (electric field $\vec{E}$) and blue (magnetic field $\vec{B}$),
oscillating perpendicularly. Display Maxwell's equations morphing from
classical vector calculus notation to relativistic four-vector form:

$$\partial_\mu F^{\mu \nu} = \mu_0 J^\nu$$

Animate each transformation by dissolving and reassembling symbols. Then shift
focus to the QED Lagrangian density:

$$\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}$$

Project this onto a semi-transparent plane with each symbol color-coded:
Dirac spinor $\psi$ in orange, covariant derivative $D_\mu$ in green,
gamma matrices $\gamma^\mu$ in bright teal, field strength tensor
$F_{\mu\nu}$ in gold. Let terms pulse to indicate dynamic fields..."

[...continues for 2000+ tokens]
```

Result: Perfect animations with correct LaTeX, camera movements, colors, and timing.

**My agents generate these verbose prompts automatically** by walking the knowledge tree.

---

## Why This Works: The Technical Insight

### 1. Foundation -> Target Building
By starting with high school concepts and building up, the animations naturally explain prerequisites before advanced topics. This creates coherent narrative flow.

### 2. LaTeX Forces Precision
When you write formulas in LaTeX, you're forced to be mathematically precise. This eliminates the ambiguity that breaks code generation.

### 3. Cinematography Matters
Specifying exact camera movements, colors, timings, and transitions gives the LLM unambiguous instructions. "Show quantum fields" is vague. "Display red undulating waves labeled $\vec{E}$ oscillating perpendicular to blue waves labeled $\vec{B}$" is precise.

### 4. No Training Data Needed
Claude Sonnet 4.5's reasoning capabilities handle the recursive prerequisite discovery. I don't need training datasets - just well-structured prompts.

### 5. Self-Correcting
If the LLM generates broken code, I can pass it back with the error and ask for "verbose explanations." This often fixes LaTeX rendering issues automatically.

---

## Recent Updates

### November 6, 2025: Kimi K2 Thinking Model Integration

**New**: Full Kimi K2 implementation now available in `KimiK2Thinking/` folder!

We've built a complete alternative pipeline using **Kimi K2 thinking model** from Moonshot AI. This implementation:

- **Uses OpenAI-compatible API** - Easier integration than Claude SDK
- **Tool-calling interface** - Structured data extraction via function calling
- **Complete enrichment chain** - Mathematical, visual, and narrative agents
- **Focuses on LaTeX equations** - Let Manim handle visual elements automatically

**Key Features:**
- `KimiPrerequisiteExplorer` - Builds knowledge trees recursively
- `KimiEnrichmentPipeline` - Three-stage enrichment (math → visuals → narrative)
- Tool adapter system - Converts tools to verbose instructions when needed
- CLI tools for running the full pipeline

**How It Works:**
1. **Prerequisite Exploration**: Recursively discovers what concepts must be understood before the target concept
2. **Mathematical Enrichment**: Adds LaTeX equations, definitions, and examples to each node using tool calls
3. **Visual Design**: Describes visual content (not Manim classes) - focuses on what should appear, not how to implement it
4. **Narrative Composition**: Stitches everything into a 2000+ word verbose prompt with exact LaTeX rendering

**Getting Started:**
```bash
# Set up Kimi API key
echo "MOONSHOT_API_KEY=your_key_here" >> .env

# Run prerequisite exploration
python KimiK2Thinking/examples/test_kimi_integration.py

# Run full enrichment pipeline on existing tree
python KimiK2Thinking/examples/run_enrichment_pipeline.py path/to/tree.json
```

**Documentation**: See [KimiK2Thinking/README.md](KimiK2Thinking/README.md) for complete setup, usage, and architecture details.

**Why Kimi K2?**
- OpenAI-compatible API makes integration straightforward
- Tool-calling interface provides structured data extraction
- Thinking mode shows reasoning steps
- Cost-effective alternative to Claude for many use cases

---

## What I'm Working On

### Current Status (November 2025)
- Refactored to Claude Sonnet 4.5 + Claude Agent SDK
- 55+ working example animations
- Reverse knowledge tree core algorithm implemented
- Repository reorganized for first-time users
- Testing architecture designed

### Next Steps

**Short Term (1-2 months)**:
1. **Complete Agent Pipeline**: Finalize the core 6 agents and bring the VideoReview step online
2. **Testing Suite**: Comprehensive unit/integration/e2e tests
3. **Knowledge Tree Visualization**: Web UI showing the prerequisite graph

**Medium Term (3-6 months)**:
4. **Nomic Atlas Integration**: Semantic knowledge graph for instant prerequisite discovery [*] NEW
   - Cache all prerequisite relationships in a shared knowledge graph
   - 10x faster prerequisite discovery with semantic search
   - Interactive visualization of learning paths
   - Community-contributed concept database
   - See [docs/NOMIC_ATLAS_INTEGRATION.md](docs/NOMIC_ATLAS_INTEGRATION.md) for full vision

**Long Term (6-12 months)**:
5. **Community Platform**: Public knowledge graph, animation gallery, learning path sharing
6. **Fine-Tuning Experiments**: RL on successful verbose prompts

---

## Examples by Difficulty

### Beginner (Great for learning Manim)
- [Pythagorean Theorem](examples/mathematics/geometry/pythagorean.py) - Visual proof
- [Bouncing Balls](examples/mathematics/geometry/bouncing_balls.py) - Physics simulation
- [Trig Identities](examples/mathematics/trigonometry/TrigInference.py) - Basic trig

### Intermediate (Requires domain knowledge)
- [Fractal Patterns](examples/mathematics/fractals/fractal_scene.py) - Self-similarity
- [Gale-Shapley Algorithm](examples/computer_science/algorithms/gale_shaply.py) - Stable matching
- [AlexNet Architecture](examples/computer_science/machine_learning/AlexNet.py) - CNN visualization

### Advanced (Complex mathematics)
- [Quantum Electrodynamics](examples/physics/quantum/QED.py) - Complete QED journey
- [Optimal Transport Theory](examples/mathematics/analysis/diffusion_optimal_transport.py) - Wasserstein distance
- [Information Geometry](examples/mathematics/statistics/information_geometry.py) - Statistical manifolds
- [Electroweak Symmetry](examples/physics/particle_physics/ElectroweakSymmetryScene.py) - Higgs mechanism

See all examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## Key Features

### Cross-Model Support
I've used multiple AI models to generate examples:
- **Claude Sonnet 4.5**: Primary agent system (Claude SDK)
- **Kimi K2**: Alternative implementation with OpenAI-compatible API (see `KimiK2Thinking/`)
- **DeepSeek R1**: Many quantum physics examples
- **Gemini 2.5 Pro**: Alternative QED visualizations
- **Grok 3**: Quantum mechanics approaches
- **Qwen Max**: Mathematical analysis
- **Mistral Large**: Gravitational waves

Each model brings unique perspectives, catching edge cases others miss.

### Dual-Stream Output
I can generate both:
1. **Manim Python code** - The animation itself
2. **LaTeX study notes** - Complete mathematical explanation

Just pass any working scene back to the LLM and ask for "verbose explanations fully rendered as LaTeX study notes" - you'll get a complete PDF-ready document.

### Adaptive Complexity
My system handles:
- Basic geometric proofs (high school level)
- Advanced physics (graduate level)
- Cutting-edge ML concepts (research level)
- Financial mathematics (professional level)

The knowledge tree approach automatically adjusts depth based on the target concept.

---

## Documentation

- **[Reverse Knowledge Tree](REVERSE_KNOWLEDGE_TREE.md)** - Core innovation explained
- **[Architecture](docs/ARCHITECTURE.md)** - Agent system design
- **[Examples Catalog](docs/EXAMPLES.md)** - All 55+ animations by topic
- **[Migration Guide](docs/MIGRATION_TO_CLAUDE.md)** - DeepSeek -> Claude transition
- **[Testing Strategy](docs/TESTING_ARCHITECTURE.md)** - Comprehensive testing approach
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - User-friendly tutorial
- **[Reorganization Plan](REORGANIZATION_PLAN.md)** - New structure details
- **[Contributing](CONTRIBUTING.md)** - How to add examples

---

## Common Pitfalls (And How I Solve Them)

### Problem 1: LaTeX Rendering Errors
**Most one-shot animation attempts fail because of LaTeX syntax errors.**

My solution: The verbose prompts explicitly show every LaTeX formula that will be rendered on screen, formatted correctly. The agents verify mathematical notation during enrichment.

### Problem 2: Vague Cinematography
**"Show a quantum field" is too vague - what colors? What motion? From which angle?**

My solution: The VisualDesigner agent specifies exact camera movements, color schemes, timing, and transitions. No ambiguity.

### Problem 3: Missing Prerequisites
**Jumping straight to QED without explaining special relativity first.**

My solution: The PrerequisiteExplorer agent automatically discovers what concepts must be explained first, ensuring logical narrative flow.

### Problem 4: Inconsistent Notation
**Using $E$ for energy in one equation and electric field in another.**

My solution: The MathematicalEnricher agent maintains consistent notation across the entire knowledge tree.

---

## Technical Requirements

- **Python**: 3.10+
- **Claude API Key**: From Anthropic (for agent system)
- **FFmpeg**: For video rendering
- **Manim Community**: v0.19.0
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional but speeds up rendering

See full requirements: [requirements.txt](requirements.txt)

---

## Performance Notes

### Agent Pipeline
- Prerequisite tree generation: ~30-60 seconds for complex topics
- Verbose prompt composition: ~20-40 seconds
- Code generation: ~15-30 seconds
- **Total**: ~1-2 minutes for complete pipeline

### Rendering
- Low quality (`-ql`): 10-30 seconds per scene
- High quality (`-qh`): 1-5 minutes per scene
- 4K quality (`-qk`): 5-20 minutes per scene

Times vary based on animation complexity.

---

## Why Claude Agent SDK?

I switched from DeepSeek to Claude Sonnet 4.5 + Claude Agent SDK in October 2025 because:

1. **Superior Reasoning**: Claude Sonnet 4.5 handles recursive logic better
2. **Automatic Context Management**: Never runs out of context
3. **Built-in Tools**: File ops, code execution, web search out-of-the-box
4. **MCP Integration**: Easy to connect external services
5. **Production Ready**: Powers Claude Code, battle-tested at scale
6. **Native Agent Framework**: Built by Anthropic specifically for autonomous agents

See migration details: [docs/MIGRATION_TO_CLAUDE.md](docs/MIGRATION_TO_CLAUDE.md)

---

## Contributing

I welcome contributions! Here's how you can help:

1. **Add Examples**: Create animations for new topics
2. **Improve Agents**: Enhance the prerequisite discovery algorithm
3. **Fix Bugs**: Report and fix issues
4. **Documentation**: Improve guides and explanations
5. **Testing**: Add test coverage

See guidelines: [CONTRIBUTING.md](CONTRIBUTING.md)

### Adding Your Own Examples

```bash
# 1. Create your animation in the appropriate category
examples/physics/quantum/my_new_animation.py

# 2. Follow the naming convention
# Use descriptive names: schrodinger_equation.py, not scene1.py

# 3. Add a docstring explaining the concept
"""
Visualization of the Schrödinger equation in quantum mechanics.
Shows wave function evolution, probability density, and energy eigenstates.
"""

# 4. Test it renders correctly
manim -pql examples/physics/quantum/my_new_animation.py MyScene

# 5. Submit a pull request
```

---

## FAQ

**Q: Do I need GPU for rendering?**
A: No, Manim runs on CPU. GPU just speeds things up.

**Q: Can I use DeepSeek instead of Claude?**
A: Yes, the old implementation is in `src/agents/prerequisite_explorer.py`

**Q: How do I fix LaTeX rendering errors?**
A: Pass the error back to the LLM with the broken code and ask for corrections.

**Q: What if my animation doesn't work?**
A: Check the [examples/](examples/) directory for working references in your topic area.

**Q: Can I use this for commercial projects?**
A: Yes, MIT license. Attribution appreciated.

**Q: How accurate are the animations?**
A: Very accurate - I use LaTeX for all mathematical notation and validate formulas during enrichment.

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- **Manim Community** - Incredible animation framework
- **Anthropic** - Claude Sonnet 4.5 and Agent SDK
- **DeepSeek** - Original inspiration and many examples
- **Community Contributors** - The 1000+ stars and growing
- **You** - For checking out this project

---

## Connect

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Contributions welcome
- **Discussions**: Share your animations and ideas

**Star this repo if you find it useful!** It helps others discover the project.

---

**Built with recursive reasoning, not training data. Powered by Claude Sonnet 4.5.**

