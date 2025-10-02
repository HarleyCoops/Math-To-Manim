# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Math-To-Manim transforms simple prompts like "explain cosmology" into professional Manim Community Edition animations using a multi-agent system based on **reverse knowledge tree decomposition**. The core innovation: recursively asking "What must I understand BEFORE X?" to build pedagogically sound animations from foundation concepts up to advanced topics.

**Powered by**: Claude Sonnet 4.5 + Claude Agent SDK (October 2025 release)

**Current Status**: Fully refactored to use Claude Agent SDK. Working prototype with reverse knowledge tree implementation ready for testing.

## Core Architecture: Reverse Knowledge Tree

**Key Principle**: NO training data required. The system uses Claude Sonnet 4.5's superior reasoning to recursively decompose concepts.

**Pipeline Flow**:
```
"Explain cosmology"
  → ConceptAnalyzer (parse intent via Claude)
  → PrerequisiteExplorer (build tree recursively) ⭐ KEY INNOVATION
  → MathematicalEnricher (add equations to nodes)
  → VisualDesigner (specify animations)
  → NarrativeComposer (tree → 2000+ token verbose prompt)
  → CodeGenerator (verbose prompt → Manim code via Claude Sonnet 4.5)
  → Render animation
```

The **PrerequisiteExplorer** is the critical component that recursively asks "To understand X, what must I know first?" until reaching foundation concepts (high school level), then builds up from there.

**Claude Agent SDK Integration**: Provides automatic context management, built-in tools, and subagent support for parallel processing.

## Essential Documentation

Before making changes, read these in order:
1. [MIGRATION_TO_CLAUDE.md](MIGRATION_TO_CLAUDE.md) - **START HERE** - Migration from DeepSeek to Claude SDK
2. [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md) - Complete technical specification of the core algorithm
3. [ROADMAP.md](ROADMAP.md) - 12-month development plan and agent architecture
4. [prerequisite_explorer_claude.py](prerequisite_explorer_claude.py) - Working demo implementation (Claude SDK version)

**Note**: Old files (`prerequisite_explorer.py`, `app.py`) use deprecated DeepSeek API and are kept for reference only.

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

**LaTeX Distribution** (for study notes generation):
- Windows: MiKTeX (https://miktex.org/download)
- Linux: `sudo apt-get install texlive-full`
- macOS: MacTeX

### Python Setup
```bash
pip install -r requirements.txt
```

Requires Python 3.10+, Manim 0.19.0+, and Claude Agent SDK.

**IMPORTANT**: Also requires Node.js for Claude Agent SDK:
```bash
npm install -g @anthropic-ai/claude-code
```

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
Opens Gradio interface at http://localhost:7860 with:
- Standard Mode: Chat with Claude Sonnet 4.5 for Manim code generation
- Prompt Expander: Transform simple ideas into detailed prompts
- Knowledge Tree: (Coming soon) Visual tree builder

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

### Current Structure (Being Reorganized)
```
Math-To-Manim/
├── app.py                    # Gradio web interface (DeepSeek R1 chat)
├── prerequisite_explorer.py  # Core innovation - recursive tree builder
├── smolagent_prototype.py    # Placeholder (will be replaced by reverse tree)
├── Scripts/                  # 40+ example Manim animations
│   ├── QED.py               # Quantum field theory
│   ├── Gemini2.5ProQED.py   # Alternative QED implementation
│   ├── fractal_scene.py     # Fractal visualizations
│   └── [many more examples]
└── docs/
    ├── ARCHITECTURE.md
    ├── EXAMPLES.md
    └── SMOLAGENTS_IMPLEMENTATION.md  # Outdated - use REVERSE_KNOWLEDGE_TREE.md
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for planned professional reorganization.

### Key Components

**prerequisite_explorer_claude.py** - The foundation of the new system:
- `PrerequisiteExplorer`: Recursively builds knowledge trees via Claude Sonnet 4.5 reasoning
- `ConceptAnalyzer`: Parses user input to identify core concepts using Claude
- `KnowledgeNode`: Data structure representing concept + prerequisites
- Caches prerequisite queries to avoid redundant API calls
- Uses Anthropic SDK for native Claude integration

**app_claude.py** - Current web interface:
- Uses Claude Sonnet 4.5 (`claude-sonnet-4.5-20251022`) for reasoning + code generation
- Formats LaTeX for Gradio display
- Provides prompt expansion and chat modes
- Ready for reverse tree integration

**Manim Code Examples** (in Scripts/, root, and subdirectories):
- Each `.py` file contains one or more Manim `Scene` classes
- Generated from 2000+ token verbose prompts
- Examples span physics, math, CS (QFT, relativity, topology, algorithms)

## Agent System Design

### The Six Agents (in development order)

1. **ConceptAnalyzer** (prerequisite_explorer.py)
   - Status: Implemented
   - Purpose: Parse user input → extract core concept, domain, level

2. **PrerequisiteExplorer** (prerequisite_explorer.py)
   - Status: Implemented
   - Purpose: Recursively build knowledge tree by asking "what must I know BEFORE this?"
   - Critical: This is the CORE INNOVATION - everything builds on this

3. **MathematicalEnricher** (planned)
   - Purpose: Add equations, derivations, examples to each tree node
   - Input: KnowledgeNode tree
   - Output: EnrichedNode tree with LaTeX equations

4. **VisualDesigner** (planned)
   - Purpose: Specify visual elements, colors, animations for each concept
   - Creates VisualSpec for each node

5. **NarrativeComposer** (planned)
   - Purpose: Walk tree from foundation → target, stitch into 2000+ token verbose prompt
   - Critical: Must maintain pedagogical flow and visual continuity

6. **CodeGenerator** (partially working)
   - Status: Existing DeepSeek R1 integration works well
   - Purpose: Verbose prompt → Manim Python code
   - Note: This already works! Focus on improving upstream agents.

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

### Claude Sonnet 4.5 Integration
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4.5-20251022",  # Latest Sonnet 4.5
    max_tokens=4000,  # Must be specified
    temperature=0.7,
    system="You are an expert educator...",  # System prompt separate
    messages=[{"role": "user", "content": prompt}]
)

# Get response
answer = response.content[0].text
```

### Key Differences from OpenAI API
- **System prompts**: Dedicated `system` parameter (not in messages)
- **Max tokens**: Must be specified explicitly
- **Response format**: `.content[0].text` (not `.choices[0].message.content`)
- **Streaming**: Use `stream=True` and iterate over events

### Claude Agent SDK Features
- **Automatic context compaction**: Never run out of context
- **Built-in tools**: File ops, code execution, web search
- **MCP integration**: Connect external services
- **Subagents**: Parallel processing support
- **Permissions**: Fine-grained tool access control

### Model Strategy (All Claude)
- **All Agents**: Claude Sonnet 4.5 (unified model)
  - Superior reasoning for concept analysis
  - Excellent at LaTeX and code generation
  - Coherent long-form narrative composition
  - Single API, consistent behavior

## Prompt Engineering for Manim

### The Secret: Prompt in LaTeX, Not English

Successful Manim code generation requires 2000+ token verbose prompts with:
1. **Extreme detail**: Specify every visual element, color, timing
2. **LaTeX-heavy**: All equations in proper LaTeX format
3. **Sequential instructions**: "Begin by...", "Next...", "Then...", "Finally..."
4. **Visual continuity**: Connect each scene to previous
5. **Color coding**: Specify colors for every mathematical object

### Example Verbose Prompt Structure
```
Begin by fading in a [description of background/setting].

Show a title "[Title]" at the center, rendered in [font/style].
The title moves to [position] as [next element] appears.

Display the equation:
$$[LaTeX equation]$$

Use color coding:
- Variable X in [COLOR]
- Term Y in [COLOR]
- Background in [COLOR]

Animate [specific transformation] over [duration] seconds.

[... continues for 2000+ tokens ...]

End with [conclusion/summary].
```

See README.md lines 111-133 for a real example (QED animation prompt).

## Common Development Tasks

### Testing Prerequisite Explorer on New Topics
```python
# Edit the examples list in prerequisite_explorer.py:
examples = [
    "Your new topic here",
    # ... existing examples
]

python prerequisite_explorer.py
```

Output: JSON files with knowledge trees saved to `knowledge_tree_<concept>.json`

### Adding New Manim Examples
1. Create `<topic>.py` in Scripts/ or root
2. Define Scene class inheriting from `manim.Scene`
3. Implement `construct(self)` method with animation logic
4. Test: `python -m manim -pql <topic>.py <SceneName>`
5. If successful, document in docs/EXAMPLES.md

### Implementing New Agents
1. Read REVERSE_KNOWLEDGE_TREE.md for agent specification
2. Add class to appropriate file (or create new file)
3. Follow pattern from PrerequisiteExplorer:
   - Clear docstrings
   - Type hints
   - LLM prompt templates as f-strings
   - Caching where appropriate
4. Test with multiple diverse topics
5. Update ROADMAP.md checklist

## Important Constraints

### LaTeX in Manim
- Most common error: LaTeX interpreted as code instead of rendered formula
- Always use raw strings: `r"$\frac{a}{b}$"` not `"$\frac{a}{b}$"`
- Use `MathTex()` for equations, `Text()` for regular text
- Test LaTeX compilation separately before embedding

### Knowledge Tree Depth
- Default max_depth: 4 (configurable)
- Too shallow: Missing foundational concepts
- Too deep: Overly granular, slow, expensive
- Foundation detection: High school level baseline

### API Costs
- DeepSeek R1 is affordable but not free
- Cache prerequisite queries (already implemented)
- Limit max_depth to avoid exponential explosion
- Batch LLM calls where possible

## Testing Strategy

Currently: Manual testing via demos
Planned (see ROADMAP.md Phase 1):
- Unit tests for each agent
- Integration tests for tree building
- End-to-end tests (simple prompt → animation)
- Success rate metrics (% of working animations)

## Git Workflow

- Main branch: `main`
- Recent commits focus on architecture documentation
- No pre-commit hooks or linting configured yet (planned)
- Commit style: Descriptive messages ("feat: add X", "docs: update Y")

## Key Files to NOT Modify (Unless Necessary)

- Examples in Scripts/ - these are proven working animations
- docs/*.pdf - Generated LaTeX study notes
- .env - User-specific API keys (gitignored)
- media/ - Generated videos (gitignored, large files)

## Critical Design Principles

1. **No Training Data**: System uses LLM reasoning, not pattern matching
2. **Foundation First**: Always build from high school level concepts up
3. **Pedagogical Correctness**: Logical progression matters more than brevity
4. **Transparency**: Users should see the knowledge tree
5. **Caching**: Avoid redundant LLM calls (expensive & slow)
6. **Manim Focus**: Output must be valid Manim Community Edition code

## Future Architecture (See PROJECT_STRUCTURE.md)

Planned reorganization:
```
src/
├── math_to_manim/
│   ├── agents/           # All agent implementations
│   ├── orchestrator/     # LangGraph workflow
│   ├── models/          # LLM integrations
│   ├── validators/      # LaTeX, Manim, math validation
│   └── prompts/         # Prompt templates
examples/                # Organized by domain (physics/, math/, cs/)
training/                # (Future) Fine-tuning data
tests/                   # (Future) Comprehensive test suite
```

Do NOT reorganize files yet - wait for explicit approval in ROADMAP Phase 1.

## Resources

- Manim Community Docs: https://docs.manim.community/
- DeepSeek API Docs: https://platform.deepseek.com/api-docs
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Project Roadmap: [ROADMAP.md](ROADMAP.md) (12-month plan)

## Quick Reference: Model Names

Current (as of Oct 2025):
- "deepseek-reasoner" (reasoning model with chain-of-thought)
- "deepseek-r1" (latest stable)
- "deepseek-chat" (for production without reasoning traces)

Legacy (being phased out):
- "deepseek-ai/DeepSeek-R1-Zero" (HuggingFace format, old)

## Development Status

**Working**:
- ✅ Verbose prompt → Manim code (DeepSeek R1)
- ✅ Dual-stream output (animations + LaTeX study notes)
- ✅ 40+ example animations across domains
- ✅ PrerequisiteExplorer + ConceptAnalyzer (recursive tree building)

**In Progress**:
- 🚧 Mathematical Enricher (add equations to tree nodes)
- 🚧 Visual Designer (animation specs per concept)
- 🚧 Narrative Composer (tree → verbose prompt)

**Planned**:
- 📋 Full orchestrator with LangGraph
- 📋 Web UI showing knowledge tree visualization
- 📋 Testing suite and CI/CD
- 📋 Project structure reorganization

## Questions or Issues?

1. Check [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md) for algorithm details
2. Check [ROADMAP.md](ROADMAP.md) for planned features
3. Check [SUMMARY.md](SUMMARY.md) for recent changes overview
4. Open GitHub issue with tag based on component (agent, manim, docs, etc.)

---

**Last Updated**: 2025-10-02
**Project Maintainer**: @HarleyCoops
**License**: MIT (pending)
