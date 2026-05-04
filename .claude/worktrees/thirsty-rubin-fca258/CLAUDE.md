# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Math-To-Manim transforms simple prompts like "explain cosmology" into professional Manim Community Edition animations using a multi-agent system based on **reverse knowledge tree decomposition**. The core innovation: recursively asking "What must I understand BEFORE X?" to build pedagogically sound animations from foundation concepts up to advanced topics.

**Three AI pipelines**: Claude (Anthropic SDK), Gemini 3 (Google ADK), Kimi K2.5 (Moonshot)

## Repository Structure

```
Math-To-Manim/
├── src/                    # Claude pipeline
│   ├── agents/             # Agent implementations
│   │   ├── prerequisite_explorer.py  # Unified explorer with pluggable clients
│   │   ├── orchestrator.py           # Full pipeline orchestrator
│   │   ├── narrative_composer.py     # Tree -> verbose prompt
│   │   └── threejs_code_generator.py # Three.js output
│   ├── app.py              # DeepSeek Gradio UI
│   └── app_claude.py       # Claude Gradio UI
├── Gemini3/                # Google Gemini 3 pipeline
├── KimiK2.5Swarm/          # Kimi K2.5 Swarm pipeline
├── examples/               # 55+ working animations by domain
├── tools/                  # Utility scripts (mermaid, video review)
├── scripts/                # Dev scripts (env check, pipeline runners)
├── tests/                  # Test suite
└── docs/                   # Architecture docs and research papers
```

## Environment Setup

### Required Environment Variables
Create a `.env` file with your preferred API key:
```bash
ANTHROPIC_API_KEY=your_key    # For Claude pipeline
GOOGLE_API_KEY=your_key       # For Gemini pipeline
MOONSHOT_API_KEY=your_key     # For Kimi pipeline
```

### System Dependencies
- **Python 3.10+**
- **FFmpeg**: `apt install ffmpeg` / `brew install ffmpeg`
- **LaTeX**: `apt install texlive-full` / MacTeX / MiKTeX

### Python Setup
```bash
pip install -e ".[dev]"  # or: pip install -r requirements.txt
```

## Running the System

### Launch Web Interface
```bash
python src/app_claude.py
```
Opens Gradio at http://localhost:7860 for interactive code generation.

### Render Manim Examples
```bash
manim -pql examples/physics/black_hole_symphony.py BlackHoleSymphony  # Low quality preview
manim -qh examples/mathematics/topology/hopf.py HopfScene            # High quality render
```

### Run Tests
```bash
pytest                    # Unit tests (no API key needed)
pytest -m integration     # Integration tests (needs API key)
```

## Core Architecture: Reverse Knowledge Tree

```
"Explain cosmology"
  -> ConceptAnalyzer (parse intent)
  -> PrerequisiteExplorer (recursive tree) [KEY INNOVATION]
  -> MathematicalEnricher (add equations)
  -> VisualDesigner (specify animations)
  -> NarrativeComposer (tree -> 2000+ token verbose prompt)
  -> CodeGenerator (verbose prompt -> Manim code)
```

The **PrerequisiteExplorer** recursively asks "To understand X, what must I know first?" until reaching foundation concepts (high school level).

## Key Data Structure

```python
@dataclass
class KnowledgeNode:
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List[KnowledgeNode]
    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[Dict] = None
    narrative: Optional[str] = None
```

## Important Constraints

### LaTeX in Manim
- Always use raw strings: `r"$\frac{a}{b}$"`
- Use `MathTex()` for equations, `Text()` for regular text

### Knowledge Tree Depth
- Default `max_depth=4` (configurable)
- Cache prerequisite queries to avoid redundant API calls
- Foundation detection: high school level baseline

## Essential Documentation

1. [docs/REVERSE_KNOWLEDGE_TREE.md](docs/REVERSE_KNOWLEDGE_TREE.md) - Core algorithm
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
3. [docs/EXAMPLES.md](docs/EXAMPLES.md) - All 55+ animations
4. [docs/ROADMAP.md](docs/ROADMAP.md) - Development plan
