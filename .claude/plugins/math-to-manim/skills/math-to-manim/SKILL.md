---
name: Math-To-Manim
description: This skill should be used when the user asks to "create a math animation", "animate a mathematical concept", "generate Manim code", "visualize [topic] with animation", "explain [concept] visually", "create an educational video", "build a Manim scene", or mentions "reverse knowledge tree", "prerequisite discovery", or "verbose prompt generation". Provides a complete six-agent workflow for transforming any concept into professional Manim animations through recursive prerequisite discovery.
version: 1.0.0
---

# Math-To-Manim: Reverse Knowledge Tree Animation Pipeline

Transform any concept into professional mathematical animations using a six-agent workflow that requires NO training data - only pure LLM reasoning.

## Core Innovation: Reverse Knowledge Tree

Instead of training on example animations, this system recursively asks: **"What must I understand BEFORE this concept?"** This builds pedagogically sound animations that flow naturally from foundation concepts to advanced topics.

## When to Use This Skill

Invoke this workflow when:
- Creating mathematical or scientific animations
- Building educational visualizations with Manim
- Generating code from conceptual explanations
- Needing pedagogically structured content progression

## The Six-Agent Pipeline

### Agent 1: ConceptAnalyzer
Parse user intent to extract:
- **Core concept** (specific topic name)
- **Domain** (physics, math, CS, etc.)
- **Level** (beginner/intermediate/advanced)
- **Goal** (learning objective)

### Agent 2: PrerequisiteExplorer (Key Innovation)
Recursively build knowledge tree:
1. Ask: "What are the prerequisites for [concept]?"
2. For each prerequisite, recursively ask the same question
3. Stop when hitting foundation concepts (high school level)
4. Build DAG structure with depth tracking

**Foundation detection criteria**: Would a high school graduate understand this without further explanation?

### Agent 3: MathematicalEnricher
For each node in the tree, add:
- LaTeX equations (2-5 key formulas)
- Variable definitions and interpretations
- Worked examples with typical values
- Complexity-appropriate rigor

### Agent 4: VisualDesigner
For each node, design:
- Visual elements (graphs, 3D objects, diagrams)
- Color scheme (maintain consistency)
- Animation sequences (FadeIn, Transform, etc.)
- Camera movements and transitions
- Duration and pacing

### Agent 5: NarrativeComposer
Walk tree from foundation to target:
1. Topologically sort nodes
2. Generate 200-300 word segment per concept
3. Include exact LaTeX, colors, animations
4. Stitch into 2000+ token verbose prompt

### Agent 6: CodeGenerator
Generate working Manim code:
- Use Manim Community Edition
- Handle LaTeX with raw strings: `r"$\frac{a}{b}$"`
- Implement all visual specifications
- Produce runnable Python file

## Workflow Execution

To execute this workflow for a user request:

### Step 1: Analyze the Concept
```python
# Extract intent
analysis = {
    "core_concept": "quantum tunneling",
    "domain": "physics/quantum mechanics",
    "level": "intermediate",
    "goal": "Understand barrier penetration"
}
```

### Step 2: Build Knowledge Tree
Recursively discover prerequisites with max depth of 3-4 levels:
```
Target: quantum tunneling
├─ wave-particle duality
│   ├─ de Broglie wavelength [FOUNDATION]
│   └─ Heisenberg uncertainty
├─ Schrödinger equation
│   ├─ wave function
│   └─ probability density
└─ potential barriers [FOUNDATION]
```

### Step 3: Enrich with Mathematics
Add to each node:
- Primary equations in LaTeX
- Variable definitions
- Physical interpretations

### Step 4: Design Visuals
Specify for each concept:
- Elements: `['wave_function', 'potential_barrier']`
- Colors: `{'wave': 'BLUE', 'barrier': 'RED'}`
- Animations: `['FadeIn', 'Create', 'Transform']`
- Duration: 15-30 seconds per concept

### Step 5: Compose Narrative
Generate verbose prompt with:
- Scene-by-scene instructions
- Exact LaTeX formulas
- Specific animation timings
- Color and position details

### Step 6: Generate Code
Produce complete Python file:
```python
from manim import *

class ConceptAnimation(ThreeDScene):
    def construct(self):
        # Implementation following verbose prompt
        ...
```

## Critical Implementation Details

### LaTeX Handling
Always use raw strings for LaTeX:
```python
equation = MathTex(r"E = mc^2")
```

### Color Consistency
Define color palette at scene start and reuse throughout.

### Transition Pattern
Connect concepts with smooth animations:
- Previous concept fades
- New concept builds from prior elements
- Use `Transform` or `ReplacementTransform`

### Verbose Prompt Format
Structure prompts with:
1. Overview section with concept count and duration
2. Scene-by-scene instructions
3. Exact specifications (no ambiguity)

See `references/verbose-prompt-format.md` for complete template.

## Output Files

The pipeline generates:
- `{concept}_prompt.txt` - Verbose prompt
- `{concept}_tree.json` - Knowledge tree structure
- `{concept}_animation.py` - Manim Python code
- `{concept}_result.json` - Complete metadata

## Additional Resources

### Reference Files
- **`references/reverse-knowledge-tree.md`** - Detailed algorithm explanation
- **`references/agent-system-prompts.md`** - All six agent prompts
- **`references/verbose-prompt-format.md`** - Complete prompt template
- **`references/manim-code-patterns.md`** - Code generation patterns

### Example Files
- **`examples/pythagorean-theorem/`** - Complete workflow example

## Quick Start

For immediate use, follow this simplified pattern:

1. **Parse**: Extract the core concept from user input
2. **Discover**: Build prerequisite tree (depth 3-4)
3. **Enrich**: Add math and visual specs to each node
4. **Compose**: Generate verbose prompt (2000+ tokens)
5. **Generate**: Produce working Manim code

The key insight: verbose, specific prompts with exact LaTeX and visual specifications produce dramatically better code than vague descriptions.
