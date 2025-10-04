# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Math-To-Manim transforms simple prompts like "explain cosmology" into professional Manim Community Edition animations using a multi-agent system based on **reverse knowledge tree decomposition**. The core innovation: recursively asking "What must I understand BEFORE X?" to build pedagogically sound animations from foundation concepts up to advanced topics.

**Powered by**: Claude Sonnet 4.5 + Anthropic SDK
**Current Status**: Working prototype with reverse knowledge tree (prerequisite_explorer_claude.py). Building toward full 6-agent system.

## Core Architecture: Reverse Knowledge Tree

**Key Principle**: NO training data required. The system uses Claude Sonnet 4.5's superior reasoning to recursively decompose concepts.

**Pipeline Flow**:
```
"Explain cosmology"
  -> ConceptAnalyzer (parse intent via Claude)
  -> PrerequisiteExplorer (build tree recursively) [*] KEY INNOVATION
  -> MathematicalEnricher (add equations to nodes)
  -> VisualDesigner (specify animations)
  -> NarrativeComposer (tree -> 2000+ token verbose prompt)
  -> CodeGenerator (verbose prompt -> Manim code via Claude Sonnet 4.5)
  -> Render animation
```

The **PrerequisiteExplorer** is the critical component that recursively asks "To understand X, what must I know first?" until reaching foundation concepts (high school level), then builds up from there.

## Essential Documentation

Read these for architecture context:
1. [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md) - Core algorithm specification
2. [ROADMAP.md](ROADMAP.md) - Development plan and agent architecture
3. [prerequisite_explorer_claude.py](prerequisite_explorer_claude.py) - Working implementation
4. [README.md](README.md) - Complete project overview with examples

## Environment Setup

### Required Environment Variables
Create a `.env` file with:
```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
```

Get your Claude API key from: https://console.anthropic.com/

**Note**: Copy `.env.example` to `.env` and add your key.

### System Dependencies
**FFmpeg** is required for Manim video rendering:
- Windows: Download from https://www.gyan.dev/ffmpeg/builds/ or `choco install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

**LaTeX Distribution** (for study notes):
- Windows: MiKTeX (https://miktex.org/download)
- Linux: `sudo apt-get install texlive-full`
- macOS: MacTeX

### Python Setup
```bash
pip install -r requirements.txt
```

Requires Python 3.10+, Manim 0.19.0+, Anthropic SDK.

## Running the System

### Test the Prerequisite Explorer (Core Innovation)
```bash
python prerequisite_explorer_claude.py
```
This demos building knowledge trees for cosmology, QFT, and Fourier analysis using Claude Sonnet 4.5.

### Launch Web Interface
```bash
python app_claude.py
```
Opens Gradio interface at http://localhost:7860 for interactive code generation and prompt expansion.

### Render Existing Manim Examples
```bash
# Development preview (low quality, fast)
python -m manim -pql <file>.py <SceneName>

# Final render (high quality)
python -m manim -qh <file>.py <SceneName>

# Quality flags:
# -ql: 480p (development)
# -qm: 720p (medium)
# -qh: 1080p (high quality)
# -qk: 4K (ultra high)

# Additional flags:
# -p: Preview when done
# -f: Show output file in file browser
```

Output location: `media/videos/<SceneName>/<quality>/<SceneName>.mp4`

## Code Architecture

### Current Structure
```
Math-To-Manim/
├── prerequisite_explorer_claude.py   # Core innovation - recursive tree builder
├── app_claude.py                     # Gradio web interface (Claude Sonnet 4.5)
├── examples/                          # 55+ working animations organized by domain
│   ├── physics/                      # quantum/, gravity/, particle_physics/, nuclear/
│   ├── mathematics/                  # geometry/, analysis/, statistics/, fractals/
│   ├── computer_science/             # machine_learning/, algorithms/, spatial_reasoning/
│   ├── cosmology/
│   └── finance/
└── docs/                              # Architecture and specifications
```

### Key Components

**prerequisite_explorer_claude.py** - The foundation of the new system:
- `PrerequisiteExplorer`: Recursively builds knowledge trees via Claude Sonnet 4.5 reasoning
- `ConceptAnalyzer`: Parses user input to identify core concepts using Claude
- `KnowledgeNode`: Data structure representing concept + prerequisites
- Caches prerequisite queries to avoid redundant API calls
- Uses Anthropic SDK for native Claude integration

**app_claude.py** - Web interface:
- Claude Sonnet 4.5 (`claude-sonnet-4.5-20251022`) for code generation
- Chat mode for concept discussion and code help
- Prompt expander for creating detailed prompts
- LaTeX formatting for Gradio display

**Examples directory** - 55+ working animations:
- Each file contains Manim Scene classes with complete animations
- Generated from verbose prompts with extensive LaTeX
- Organized by domain (physics, mathematics, CS, cosmology, finance)

## Agent System Design

### Current Status

[DONE] **Implemented**:
1. **ConceptAnalyzer** - Parses user input -> core concept, domain, level
2. **PrerequisiteExplorer** - Recursively builds knowledge tree (CORE INNOVATION)
3. **CodeGenerator** - Verbose prompt -> Manim code (in app_claude.py)

[WIP] **Planned**:
4. **MathematicalEnricher** - Add equations/derivations to tree nodes
5. **VisualDesigner** - Specify colors, camera movements, animations
6. **NarrativeComposer** - Tree -> 2000+ token verbose prompt

### Data Structures

```python
@dataclass
class KnowledgeNode:
    concept: str              # e.g., "cosmology"
    depth: int               # 0 = target, higher = more foundational
    is_foundation: bool      # True if high school level
    prerequisites: List[KnowledgeNode]  # Recursive structure

    # Added by enrichment agents:
    equations: Optional[List[str]]
    definitions: Optional[Dict[str, str]]
    visual_spec: Optional[VisualSpec]
    narrative: Optional[str]
```

## Working with Claude API

### Anthropic SDK Basics
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4.5-20251022",
    max_tokens=4000,
    temperature=0.7,
    system="System prompt here",
    messages=[{"role": "user", "content": prompt}]
)

answer = response.content[0].text
```

**Key Points**:
- System prompt is a separate parameter (not in messages)
- Max tokens must be specified
- Response format: `.content[0].text`
- Model name: `claude-sonnet-4.5-20251022` (current)

## Prompt Engineering for Manim

### Critical Success Factor: Verbose LaTeX-Rich Prompts

Successful Manim code generation requires detailed 2000+ token prompts with:
1. **Extreme specificity**: Every visual element, color, position, timing
2. **Proper LaTeX**: All equations in correct LaTeX format with raw strings
3. **Sequential structure**: "Begin by...", "Next...", "Then...", "Finally..."
4. **Visual continuity**: Connect scenes logically
5. **Consistent notation**: Color-code mathematical objects throughout

Example structure: See README.md for complete QED animation example showing proper verbose prompt format.

## Common Development Tasks

### Testing Prerequisite Explorer
```bash
python prerequisite_explorer_claude.py
```
Edit the `examples` list to test new topics. Outputs JSON knowledge trees.

### Adding New Manim Examples
```bash
# Create file in appropriate examples/ subdirectory
examples/physics/quantum/my_animation.py

# Test render
manim -pql examples/physics/quantum/my_animation.py SceneName
```

### Implementing New Agents
1. Read [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md) for specification
2. Follow PrerequisiteExplorer pattern: docstrings, type hints, caching
3. Test on diverse topics (physics, math, CS)
4. Update ROADMAP.md

## Important Constraints

### LaTeX in Manim
**Most common error**: LaTeX syntax issues
- Always use raw strings: `r"$\frac{a}{b}$"`
- Use `MathTex()` for equations, `Text()` for regular text
- Escape backslashes properly

### Knowledge Tree Depth
- Default max_depth: 4 (configurable in PrerequisiteExplorer)
- Balance: Too shallow misses foundations, too deep is slow/expensive
- Foundation detection: High school level baseline

### API Usage
- Cache prerequisite queries (implemented in prerequisite_explorer_claude.py)
- Limit recursion depth to avoid exponential API calls
- Monitor costs with complex topics

## Design Principles

1. **No Training Data** - Uses LLM reasoning, not pattern matching
2. **Foundation First** - Build from high school concepts upward
3. **Pedagogical Correctness** - Logical progression over brevity
4. **Caching** - Avoid redundant API calls
5. **Manim Focus** - Output must be valid Manim Community Edition code

## Development Status

**Working**:
- [DONE] PrerequisiteExplorer + ConceptAnalyzer (recursive tree building)
- [DONE] Verbose prompt -> Manim code (Claude Sonnet 4.5)
- [DONE] 55+ example animations across domains
- [DONE] Web interface (app_claude.py)

**In Progress**:
- [WIP] MathematicalEnricher (equations for tree nodes)
- [WIP] VisualDesigner (animation specifications)
- [WIP] NarrativeComposer (tree -> verbose prompt)

**Planned**:
- [TODO] Full agent orchestration
- [TODO] Knowledge tree web visualization
- [TODO] Comprehensive testing suite

See [ROADMAP.md](ROADMAP.md) for complete 12-month development plan.

---

**Last Updated**: 2025-10-04
**Project**: Math-To-Manim
**License**: MIT
