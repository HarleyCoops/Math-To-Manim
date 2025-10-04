# Reverse Knowledge Tree Architecture
## Recursive Concept Decomposition for Math-To-Manim

**Powered by**: Claude Sonnet 4.5 + Claude Agent SDK

**Core Insight**: Don't train on examples. Instead, build a knowledge tree by asking "What do I need to understand BEFORE this?" recursively until reaching foundational concepts, then animate from foundation -> target.

**Technology**: Uses Claude Sonnet 4.5's superior reasoning capabilities via the Claude Agent SDK - no training data required!

---

## The Problem with Training Data Approach

**Wrong**: "Learn patterns from simple -> verbose prompt pairs"
- Requires massive training datasets
- Limited to what we've seen before
- Doesn't generalize to new topics
- Brittle when concepts evolve

**Right**: "Recursively decompose any concept into prerequisites"
- Works on ANY mathematical/scientific topic
- Discovers connections dynamically
- Self-enriching through exploration
- Builds complete conceptual understanding

---

## The Reverse Knowledge Tree Algorithm

### Step 1: Question Analysis
```
User: "Explain cosmology to me"

Concept Agent asks:
1. What is the core concept? -> "cosmology"
2. What domain? -> "physics/astronomy"
3. What level? -> "beginner" (inferred from casual language)
```

### Step 2: Prerequisite Discovery (Recursive)
```
Question: "To understand cosmology, what must I know first?"

Answer (from Research Agent):
- General Relativity (high-level)
- Hubble's Law
- Redshift
- Cosmic Microwave Background
- Dark Matter & Dark Energy

For EACH prerequisite, ask again:
"To understand General Relativity, what must I know first?"
  -> Special Relativity
  -> Differential Geometry (simplified)
  -> Gravitational Fields

"To understand Special Relativity, what must I know first?"
  -> Galilean Relativity
  -> Speed of light constancy
  -> Lorentz Transformations

... continue until hitting FOUNDATION concepts that need no prerequisites
```

### Step 3: Foundation Identification
```
Stopping criteria:
- Concept is "common knowledge" (high school level)
- No further meaningful decomposition
- Recursion depth limit reached (configurable: 3-5 levels)

Foundation for cosmology example:
Level 0 (Foundation):
  - Basic geometry (distances, angles)
  - Velocity concept
  - Light as waves
  - Time measurement

Level 1 (Building blocks):
  - Galilean relativity
  - Doppler effect
  - Gravity basics

Level 2 (Intermediate):
  - Special relativity
  - Curved spacetime intuition
  - Redshift

Level 3 (Advanced):
  - General relativity concepts
  - Universe expansion
  - CMB

Level 4 (Target):
  - Cosmology (Big Bang, inflation, dark energy)
```

### Step 4: Knowledge Tree Construction
```
cosmology
├── general_relativity
│   ├── special_relativity
│   │   ├── galilean_relativity [FOUNDATION]
│   │   ├── speed_of_light [FOUNDATION]
│   │   └── lorentz_transforms
│   ├── curved_spacetime
│   │   ├── gravity [FOUNDATION]
│   │   └── geometry [FOUNDATION]
│   └── field_equations
├── hubbles_law
│   ├── redshift
│   │   ├── doppler_effect [FOUNDATION]
│   │   └── wavelength [FOUNDATION]
│   └── expansion
├── cmb
│   ├── blackbody_radiation [FOUNDATION]
│   └── early_universe
└── dark_matter
    └── galaxy_rotation [FOUNDATION]
```

### Step 5: Enrichment Walk (Foundation -> Target)
```
Now traverse the tree FROM the leaves UP:

1. Start at foundation concepts
   For each concept at current level:
   - Generate mathematical formulas
   - Create visual metaphors
   - Write narrative explanation
   - Design animation sequence

2. Move up one level
   Build on what was explained below:
   - Connect to prerequisites
   - Add complexity incrementally
   - Maintain visual continuity

3. Repeat until reaching target concept

Result: Complete narrative arc from basics -> cosmology
```

---

## Agent Pipeline (No Training Required!)

### Agent 1: Concept Analyzer
**Question**: "What is this really asking?"

```python
def analyze_concept(user_input: str) -> ConceptAnalysis:
    """
    Parse the user's question to identify:
    - Core concept(s)
    - Domain (physics, math, CS, etc.)
    - Complexity level desired
    - Visual possibilities
    """
    prompt = f"""
    User asked: "{user_input}"

    1. What is the MAIN concept they want to understand?
    2. What scientific/mathematical domain?
    3. What complexity level seems appropriate? (beginner/intermediate/advanced)
    4. Is this visualizable? How?
    5. What's the "aha!" moment we're building toward?
    """

    return {
        'core_concept': 'cosmology',
        'domain': 'physics/astronomy',
        'level': 'beginner',
        'visual_potential': 'excellent (expanding universe, timelines, 3D spacetime)',
        'goal': 'understand how universe evolved from Big Bang to now'
    }
```

### Agent 2: Prerequisite Explorer (Recursive)
**Question**: "What must I understand BEFORE this?"

```python
def explore_prerequisites(concept: str, depth: int = 0, max_depth: int = 4) -> KnowledgeNode:
    """
    Recursively discover prerequisites until hitting foundation.
    This is the KEY agent that builds the tree.
    """

    # Base case: check if this is foundational
    if is_foundation_concept(concept) or depth >= max_depth:
        return KnowledgeNode(
            concept=concept,
            prerequisites=[],
            depth=depth,
            is_foundation=True
        )

    # Recursive case: find prerequisites
    prompt = f"""
    To understand {concept}, what 3-5 prerequisite concepts must someone know first?

    Rules:
    - Only list ESSENTIAL prerequisites
    - Order from most to least important
    - Assume high school education as baseline
    - Focus on concepts that enable understanding, not just context

    Return as JSON list.
    """

    prereqs = llm_call(prompt)  # Returns ['special_relativity', 'curved_spacetime', ...]

    # Recurse on each prerequisite
    children = [
        explore_prerequisites(prereq, depth + 1, max_depth)
        for prereq in prereqs
    ]

    return KnowledgeNode(
        concept=concept,
        prerequisites=children,
        depth=depth,
        is_foundation=False
    )

def is_foundation_concept(concept: str) -> bool:
    """Determine if concept is foundational (no further decomposition needed)"""

    prompt = f"""
    Is "{concept}" a foundational concept that a typical high school graduate
    would understand without further explanation?

    Examples of foundational: velocity, distance, time, force, waves, numbers
    Examples of non-foundational: Lorentz transforms, gauge theory, tensors

    Answer: yes/no
    """

    return llm_call(prompt).lower().startswith('yes')
```

### Agent 3: Mathematical Enricher
**Question**: "What are the precise mathematical formulations?"

```python
def enrich_with_math(node: KnowledgeNode) -> EnrichedNode:
    """
    For each node in the tree, add mathematical rigor:
    - Key equations
    - Derivations (simplified if needed)
    - Units and magnitudes
    - Worked examples
    """

    prompt = f"""
    Concept: {node.concept}
    Level: {node.depth} (0=foundation, higher=more advanced)

    Provide:
    1. Key equation(s) in LaTeX
    2. Variable definitions
    3. Physical interpretation
    4. Typical values/magnitudes
    5. Simple worked example

    Format for Manim rendering.
    """

    math_content = llm_call(prompt)

    return EnrichedNode(
        **node.__dict__,
        equations=math_content['equations'],
        definitions=math_content['definitions'],
        examples=math_content['examples']
    )
```

### Agent 4: Visual Designer
**Question**: "How do we SHOW this concept?"

```python
def design_visuals(enriched_node: EnrichedNode) -> VisualSpec:
    """
    For each concept, design the visual representation:
    - What objects to show (graphs, shapes, animations)
    - Color schemes
    - Camera movements
    - Transitions from previous concepts
    """

    prompt = f"""
    Concept: {enriched_node.concept}
    Equations: {enriched_node.equations}
    Prerequisites shown: {[p.concept for p in enriched_node.prerequisites]}

    Design a Manim animation segment:
    1. What visual elements? (3D shapes, graphs, text, etc.)
    2. Color scheme (that builds on previous segments)
    3. Key animation moments (what changes, when)
    4. How to connect to what came before visually
    5. Estimated duration (3-30 seconds)

    Remember: This is part of a larger animation building from simple -> complex.
    """

    return VisualSpec(
        concept=enriched_node.concept,
        elements=llm_call(prompt)['elements'],
        colors=llm_call(prompt)['colors'],
        animations=llm_call(prompt)['animations'],
        duration=llm_call(prompt)['duration']
    )
```

### Agent 5: Narrative Composer
**Question**: "What's the story connecting these concepts?"

```python
def compose_narrative(knowledge_tree: KnowledgeNode) -> Narrative:
    """
    Walk the tree from foundation -> target, creating a coherent story.
    This generates the VERBOSE PROMPT.
    """

    # Topological sort: foundation concepts first
    ordered_concepts = topological_sort(knowledge_tree)

    narrative_parts = []

    for i, concept in enumerate(ordered_concepts):
        prompt = f"""
        We're explaining {knowledge_tree.concept} step by step.

        Current step ({i+1}/{len(ordered_concepts)}): {concept.concept}

        Previous concepts covered: {[c.concept for c in ordered_concepts[:i]]}
        This concept's prerequisites: {[p.concept for p in concept.prerequisites]}

        Write a 200-word narrative segment that:
        1. Connects to what we just learned
        2. Introduces {concept.concept} naturally
        3. Explains the key equation: {concept.equations[0]}
        4. Sets up for the next concept
        5. Specifies visual elements: {concept.visual_spec}

        Write in second person, enthusiastic teaching tone.
        Include detailed Manim instructions (colors, timing, LaTeX formatting).
        """

        segment = llm_call(prompt)
        narrative_parts.append(segment)

    # Stitch together into final verbose prompt
    verbose_prompt = "\n\n".join([
        "# Manim Animation: " + knowledge_tree.concept,
        "## Scene Overview",
        f"This animation builds {knowledge_tree.concept} from first principles.",
        f"Total concepts: {len(ordered_concepts)}",
        f"Progression: {' -> '.join([c.concept for c in ordered_concepts])}",
        "",
        "## Animation Sequence",
        *narrative_parts
    ])

    return Narrative(
        prompt=verbose_prompt,
        concept_order=ordered_concepts,
        total_duration=sum(c.visual_spec.duration for c in ordered_concepts)
    )
```

### Agent 6: Code Generator
**Question**: "How do we implement this in Manim?"

```python
def generate_manim_code(narrative: Narrative) -> str:
    """
    Convert the verbose prompt into actual Manim code.
    This is your EXISTING strength - keep using it!
    """

    # Use Claude Sonnet 4.5 for superior code generation
    # Feed the verbose prompt to Claude

    code = claude_generate(
        prompt=narrative.prompt,
        model="claude-sonnet-4.5-20251022",
        system="You are an expert Manim animator. Generate Python code using Manim Community Edition."
    )

    return code
```

---

## Example Walkthrough

### Input
```
"Explain cosmology to me"
```

### Agent Pipeline Execution

#### 1. Concept Analyzer
```json
{
  "core_concept": "cosmology",
  "domain": "physics/astronomy",
  "level": "beginner",
  "visual_potential": "excellent",
  "goal": "Big Bang -> present day universe"
}
```

#### 2. Prerequisite Explorer (Recursive)
```
Depth 0: "To understand cosmology, what must I know?"
  -> General Relativity, Hubble's Law, Redshift, CMB

Depth 1: "To understand General Relativity, what must I know?"
  -> Special Relativity, Curved Spacetime, Gravity

Depth 2: "To understand Special Relativity, what must I know?"
  -> Galilean Relativity, Speed of Light, Reference Frames

Depth 3: Foundation reached
  -> All concepts here are understandable to high school graduate
  -> STOP recursion
```

**Resulting Tree**:
```
cosmology [target]
├─ general_relativity
│  ├─ special_relativity
│  │  ├─ galilean_relativity [FOUND]
│  │  ├─ speed_of_light [FOUND]
│  │  └─ reference_frames [FOUND]
│  └─ curved_spacetime
│     ├─ geometry [FOUND]
│     └─ gravity [FOUND]
├─ hubbles_law
│  ├─ redshift
│  │  └─ doppler_effect [FOUND]
│  └─ distance_measurement [FOUND]
└─ cmb
   └─ blackbody_radiation [FOUND]
```

#### 3. Mathematical Enricher
Walks tree, adds equations to each node:

```python
{
  'galilean_relativity': {
    'equation': r"v' = v - u",
    'meaning': "velocity in moving frame",
    'example': "Ball on a train"
  },
  'doppler_effect': {
    'equation': r"f' = f \frac{v}{v \pm v_s}",
    'meaning': "frequency shift from motion",
    'example': "Ambulance siren"
  },
  # ... for every node
}
```

#### 4. Visual Designer
For each concept, specifies how to animate:

```python
{
  'galilean_relativity': {
    'elements': ['train', 'ball', 'reference_frames'],
    'colors': {'train': BLUE, 'ball': RED},
    'animation': 'Show ball thrown on moving train, compare ground/train perspectives',
    'duration': 15
  },
  'redshift': {
    'elements': ['wave', 'stretching_space', 'color_gradient'],
    'colors': 'gradient from BLUE -> RED',
    'animation': 'Wave stretches as space expands, color shifts',
    'duration': 20
  },
  # ... every node gets visual spec
}
```

#### 5. Narrative Composer
Stitches into verbose prompt (2000+ tokens):

```
# Manim Animation: Cosmology

## Scene 1: Galilean Relativity (0:00-0:15)

Begin with a train moving at constant velocity across the screen from left to right,
rendered as a simple blue rectangle with wheels. Show a figure inside the train
throwing a red ball upward. Split the screen into two reference frames...

[continues for 200 words with detailed Manim instructions, LaTeX formatting, colors]

## Scene 2: Speed of Light Constancy (0:15-0:30)

Building on the previous reference frames, now introduce a beam of light from the
train's headlight. Write the equation $c = 299,792,458 \text{ m/s}$ in the corner...

[200 more words]

## Scene 3: Special Relativity (0:30-1:00)

Now that we understand reference frames and light's constant speed, introduce the
Lorentz transformation. Show two synchronized clocks, one on the train moving at
0.9c, one on the ground. Display the time dilation formula...

[200 more words]

... [continues through ALL concepts in tree]

## Scene 12: Cosmology - The Big Bang (4:30-5:00)

Now bringing together everything we've learned - relativity, expansion, redshift -
we arrive at cosmology. Begin with a single point of infinite density. Show the
Friedmann equation: $$\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho$$

Animate the scale factor $a(t)$ growing from 0 to present day...

[200 more words of detailed instructions]
```

**Total**: ~2400 tokens of rich, detailed prompt

#### 6. Code Generator
Feed verbose prompt to DeepSeek R1 -> produces working Manim code (your existing strength!)

---

## Why This Works

### No Training Required
- Agents use Claude Sonnet 4.5's reasoning, not pattern matching
- Works on ANY topic Claude knows about
- Self-improving as Claude models improve
- Claude Agent SDK provides built-in context management and tool integration

### Complete Understanding
- Builds from true foundations
- No conceptual gaps
- Logical progression guaranteed

### Adaptable
- User level detected automatically
- Recursion depth configurable
- Can focus on specific subtrees

### Scalable
- Each agent is stateless and simple
- Parallel execution possible
- Cacheable prerequisite trees

---

## Implementation Strategy

### Phase 1: Build Core Agents (Weeks 1-2)
```python
# Start simple - implement these 3 first:
1. Concept Analyzer (parse user intent)
2. Prerequisite Explorer (recursive tree builder) [*] KEY AGENT
3. Narrative Composer (tree -> verbose prompt)

# Test on 5 diverse topics:
- Pythagorean theorem (simple)
- Fourier analysis (medium)
- Quantum field theory (complex)
- Machine learning (different domain)
- Gödel's incompleteness theorems (logic/math)
```

### Phase 2: Add Enrichment (Weeks 3-4)
```python
4. Mathematical Enricher (equations, derivations)
5. Visual Designer (animation specifications)
```

### Phase 3: Polish & Integrate (Weeks 5-6)
```python
6. Code Generator (verbose prompt -> Manim code)
   - Use your existing DeepSeek pipeline
   - Add validation/retry logic
7. Quality checks
8. Web UI showing the knowledge tree visualization
```

---

## Data Structures

### KnowledgeNode
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class KnowledgeNode:
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List['KnowledgeNode']

    # Added by enrichment agents
    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[VisualSpec] = None
    narrative: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'concept': self.concept,
            'depth': self.depth,
            'is_foundation': self.is_foundation,
            'prerequisites': [p.to_dict() for p in self.prerequisites],
            'equations': self.equations,
            'visual_spec': self.visual_spec.__dict__ if self.visual_spec else None
        }
```

### VisualSpec
```python
@dataclass
class VisualSpec:
    elements: List[str]  # ['graph', '3d_surface', 'equation']
    colors: Dict[str, str]  # {'wave': 'BLUE', 'particle': 'RED'}
    animations: List[str]  # ['fade_in', 'transform', 'rotate']
    duration: int  # seconds
    camera_movement: Optional[str] = None
```

---

## Agent Orchestration (Simplified)

```python
class ReverseKnowledgeTreeOrchestrator:
    def __init__(self):
        self.concept_analyzer = ConceptAnalyzer()
        self.prereq_explorer = PrerequisiteExplorer()
        self.math_enricher = MathematicalEnricher()
        self.visual_designer = VisualDesigner()
        self.narrative_composer = NarrativeComposer()
        self.code_generator = CodeGenerator()

    def process(self, user_input: str) -> AnimationResult:
        # Step 1: Analyze
        analysis = self.concept_analyzer.analyze(user_input)

        # Step 2: Build knowledge tree (recursive!)
        tree = self.prereq_explorer.explore(
            concept=analysis.core_concept,
            max_depth=4  # configurable
        )

        # Step 3: Enrich tree with math
        enriched_tree = self.math_enricher.enrich_tree(tree)

        # Step 4: Design visuals for each node
        visual_tree = self.visual_designer.design_tree(enriched_tree)

        # Step 5: Compose narrative (foundation -> target)
        narrative = self.narrative_composer.compose(visual_tree)

        # Step 6: Generate Manim code
        code = self.code_generator.generate(narrative.prompt)

        # Step 7: Render (your existing pipeline)
        video = render_manim(code)

        return AnimationResult(
            video=video,
            code=code,
            knowledge_tree=tree.to_dict(),
            verbose_prompt=narrative.prompt
        )
```

---

## Key Differences from Original Plan

| Original (Training-Based) | New (Recursive Decomposition) |
|---------------------------|-------------------------------|
| Learn from examples | Reason from first principles |
| Requires datasets | Zero training data |
| Limited to seen patterns | Works on any topic |
| Static knowledge | Dynamic exploration |
| Pattern matching | Logical decomposition |
| Prompt Agent is ML model | Prompt Agent is tree walker |

---

## Next Steps

1. **Implement Prerequisite Explorer** (this is the core innovation)
   - Start with simple topics
   - Test recursion depth limits
   - Validate foundation detection

2. **Test on diverse topics**
   - Math: Calculus, topology, number theory
   - Physics: QM, relativity, thermodynamics
   - CS: Algorithms, complexity theory
   - Cross-domain: Game theory, information theory

3. **Build tree visualization**
   - Show users the knowledge tree
   - Let them prune/expand branches
   - Interactive exploration

4. **Optimize**
   - Cache prerequisite trees
   - Parallel agent execution
   - Progressive enhancement

---

**This approach leverages LLM reasoning abilities, not memorization. It's fundamentally more robust and scalable than training-based methods.**

**Last Updated**: 2025-10-02
**Author**: Based on conversation with @HarleyCoops
