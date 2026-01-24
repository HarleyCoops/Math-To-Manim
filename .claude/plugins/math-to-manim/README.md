# Math-To-Manim Skill for Claude Code

Transform any concept into professional Manim animations using a six-agent reverse knowledge tree pipeline.

## Overview

This Claude Code skill provides a complete workflow for generating mathematical animations without requiring any training data. It uses pure LLM reasoning through a six-agent pipeline:

1. **ConceptAnalyzer** - Parse user intent
2. **PrerequisiteExplorer** - Build knowledge tree recursively
3. **MathematicalEnricher** - Add LaTeX equations
4. **VisualDesigner** - Design animation specifications
5. **NarrativeComposer** - Generate verbose prompt
6. **CodeGenerator** - Produce working Manim code

## Installation

### Option 1: Install from GitHub

```bash
# Using skills.sh (coming soon)
npx skills add HarleyCoops/Math-To-Manim/skill
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/HarleyCoops/Math-To-Manim.git

# Run Claude Code with the plugin
claude --plugin-dir ./Math-To-Manim/skill
```

## Usage

Once installed, the skill automatically activates when you ask Claude to:

- "Create a math animation about [topic]"
- "Animate [mathematical concept]"
- "Generate Manim code for [topic]"
- "Visualize [concept] with animation"
- "Explain [topic] visually"

### Example

```
User: Create an animation explaining the Pythagorean theorem

Claude: [Uses Math-To-Manim skill to:]
1. Analyze the concept
2. Build prerequisite tree (angles → triangles → squares → theorem)
3. Enrich with LaTeX equations
4. Design visual specifications
5. Generate 2000+ token verbose prompt
6. Produce working Manim Python code
```

## Core Innovation: Reverse Knowledge Tree

Instead of training on example animations, this system recursively asks:

**"What must I understand BEFORE this concept?"**

This builds pedagogically sound animations that flow naturally from foundation concepts to advanced topics.

## Directory Structure

```
skill/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   └── math-to-manim/
│       ├── SKILL.md         # Main skill definition
│       ├── references/      # Detailed documentation
│       │   ├── reverse-knowledge-tree.md
│       │   ├── agent-system-prompts.md
│       │   ├── verbose-prompt-format.md
│       │   └── manim-code-patterns.md
│       └── examples/        # Working examples
│           └── pythagorean-theorem/
└── README.md
```

## Requirements

- Claude Code CLI
- Python 3.8+
- Manim Community Edition (for rendering)

```bash
pip install manim
```

## License

MIT License - See the main repository for details.

## Contributing

Contributions welcome! Please see the main [Math-To-Manim repository](https://github.com/HarleyCoops/Math-To-Manim) for contribution guidelines.
