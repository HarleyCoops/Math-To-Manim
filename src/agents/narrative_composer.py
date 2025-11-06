"""
Narrative Composer Agent - Composes the narrative prompt from knowledge tree
Walks the tree from foundation -> target, creating a coherent story that:
- Builds from simple to complex
- Connects concepts logically
- Generates 2000+ token verbose prompts
- Includes all mathematical and visual specifications

Uses Claude Sonnet 4.5 via the Anthropic Claude Agent SDK.
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from anthropic import Anthropic, NotFoundError
from dotenv import load_dotenv

# Import from same package
try:
    from src.agents.claude_agent_runtime import run_query_via_sdk
except ImportError:
    try:
        from claude_agent_runtime import run_query_via_sdk
    except ImportError:
        run_query_via_sdk = None  # type: ignore[assignment]

CLAUDE_MODEL = "claude-sonnet-4-5"
try:
    from src.agents.prerequisite_explorer_claude import KnowledgeNode, CLAUDE_MODEL as _CLAUDE_MODEL
    CLAUDE_MODEL = _CLAUDE_MODEL
except ImportError:
    try:
        from prerequisite_explorer_claude import KnowledgeNode, CLAUDE_MODEL as _CLAUDE_MODEL
        CLAUDE_MODEL = _CLAUDE_MODEL
    except ImportError as exc:
        raise ImportError(
            "Unable to import KnowledgeNode for NarrativeComposer. "
            "Ensure the src package is on PYTHONPATH."
        ) from exc

load_dotenv()

CLI_CLIENT: Optional[Anthropic] = None


def _ensure_client() -> Anthropic:
    global CLI_CLIENT
    if CLI_CLIENT is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set.")
        CLI_CLIENT = Anthropic(api_key=api_key)
    return CLI_CLIENT


@dataclass
class Narrative:
    """Complete narrative for a Manim animation"""
    target_concept: str
    verbose_prompt: str
    concept_order: List[str] = field(default_factory=list)
    total_duration: int = 0
    scene_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'target_concept': self.target_concept,
            'verbose_prompt': self.verbose_prompt,
            'concept_order': self.concept_order,
            'total_duration': self.total_duration,
            'scene_count': self.scene_count
        }


class NarrativeComposer:
    """
    Agent that composes a narrative prompt from a knowledge tree.

    Walks the tree from foundation concepts to the target concept,
    generating a 2000+ token verbose prompt that includes:
    - Clear progression from simple to complex
    - All mathematical equations in LaTeX
    - Detailed visual specifications
    - Smooth transitions between concepts
    - Specific Manim instructions

    This generates the "verbose LaTeX-rich prompts" that produce
    high-quality Manim code.

    Powered by Claude Sonnet 4.5 for narrative coherence.
    """

    def __init__(self, model: str = CLAUDE_MODEL):
        self.model = model

    def compose(self, tree: KnowledgeNode) -> Narrative:
        """
        Compose a narrative from a knowledge tree.

        Args:
            tree: Root of the knowledge tree (target concept)

        Returns:
            Narrative with verbose prompt suitable for Manim code generation
        """
        return asyncio.run(self.compose_async(tree))

    async def compose_async(self, tree: KnowledgeNode) -> Narrative:
        """Async version of compose"""
        print(f"\nComposing narrative for: {tree.concept}")
        print("=" * 70)

        # Step 1: Topologically sort the tree (foundation -> target)
        ordered_nodes = self._topological_sort(tree)
        concept_order = [node.concept for node in ordered_nodes]

        print(f"\nConcept progression ({len(ordered_nodes)} concepts):")
        for i, concept in enumerate(concept_order, 1):
            print(f"  {i}. {concept}")

        # Step 2: Generate narrative segments for each concept
        print("\nGenerating narrative segments...")
        segments = []
        total_duration = 0

        for i, node in enumerate(ordered_nodes):
            # Get context: what came before
            previous_concepts = [n.concept for n in ordered_nodes[:i]]

            # Generate segment
            segment = await self._generate_segment_async(
                node=node,
                segment_number=i + 1,
                total_segments=len(ordered_nodes),
                previous_concepts=previous_concepts,
                is_final=(i == 0)  # Root is last in topo sort, first in depth
            )

            segments.append(segment)

            # Accumulate duration
            if node.visual_spec and 'duration' in node.visual_spec:
                total_duration += node.visual_spec['duration']

        # Step 3: Stitch segments into final verbose prompt
        verbose_prompt = self._assemble_prompt(
            target_concept=tree.concept,
            segments=segments,
            concept_order=concept_order,
            total_duration=total_duration
        )

        return Narrative(
            target_concept=tree.concept,
            verbose_prompt=verbose_prompt,
            concept_order=concept_order,
            total_duration=total_duration,
            scene_count=len(ordered_nodes)
        )

    def _topological_sort(self, root: KnowledgeNode) -> List[KnowledgeNode]:
        """
        Sort nodes from foundation (leaves) to target (root).

        Uses depth-first search to ensure prerequisites come before
        concepts that depend on them.
        """
        visited = set()
        result = []

        def dfs(node: KnowledgeNode):
            if node.concept in visited:
                return
            visited.add(node.concept)

            # Visit prerequisites first (foundation concepts)
            for prereq in node.prerequisites:
                dfs(prereq)

            # Then add this node
            result.append(node)

        dfs(root)
        return result

    async def _generate_segment_async(
        self,
        node: KnowledgeNode,
        segment_number: int,
        total_segments: int,
        previous_concepts: List[str],
        is_final: bool
    ) -> str:
        """Generate a narrative segment for a single concept"""

        print(f"  Segment {segment_number}/{total_segments}: {node.concept}")

        # Extract info from node
        equations = node.equations if node.equations else []
        definitions = node.definitions if node.definitions else {}
        visual_spec = node.visual_spec if node.visual_spec else {}

        system_prompt = """You are an expert educational animator who writes detailed,
LaTeX-rich prompts for Manim Community Edition animations.

Your narrative segments should:
1. Connect naturally to what was just explained
2. Introduce the new concept smoothly
3. Include ALL equations in proper LaTeX format (use double backslashes)
4. Specify exact visual elements, colors, positions
5. Describe animations and transitions precisely
6. Use enthusiastic, second-person teaching tone
7. Be 200-300 words of detailed Manim instructions

Critical: ALL LaTeX must use Manim-compatible syntax with double backslashes.

Format each segment as a complete scene description for Manim."""

        # Build context string
        previous_str = ', '.join(previous_concepts) if previous_concepts else 'None (this is the first concept)'

        user_prompt = f'''Write a 200-300 word narrative segment for a Manim animation.

Segment {segment_number} of {total_segments}
Concept: {node.concept}
Previous concepts covered: {previous_str}
{"This is the FINAL segment - the target concept we're building toward!" if is_final else ""}

Mathematical content:
Equations: {json.dumps(equations) if equations else "Define appropriate equations"}
Definitions: {json.dumps(definitions) if definitions else "Define key variables"}

Visual specification:
Elements: {json.dumps(visual_spec.get('elements', []))}
Colors: {json.dumps(visual_spec.get('colors', {}))}
Animations: {json.dumps(visual_spec.get('animations', []))}
Layout: {visual_spec.get('layout', 'Design appropriate layout')}
Duration: {visual_spec.get('duration', 15)} seconds

Write a detailed Manim animation segment that:
1. Starts by connecting to the previous concept (if any)
2. Introduces {node.concept} naturally
3. Displays the key equations with exact LaTeX notation
4. Specifies colors, positions, and timing
5. Describes each animation step clearly
6. Sets up for the next concept (if not final)

Use phrases like:
- "Begin by fading in..."
- "Next, display the equation..."
- "Transform the previous visualization into..."
- "Highlight in [COLOR] to emphasize..."
- "Camera zooms to show..."

Format: A single paragraph of 200-300 words with detailed Manim instructions.
Include all LaTeX equations with double backslashes.'''

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.7,  # Higher for creative narrative
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            segment = response.content[0].text
        except NotFoundError:
            segment = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1500,
            )

        return segment.strip()

    def _assemble_prompt(
        self,
        target_concept: str,
        segments: List[str],
        concept_order: List[str],
        total_duration: int
    ) -> str:
        """Assemble individual segments into the final verbose prompt"""

        header = f"""# Manim Animation: {target_concept}

## Overview
This animation builds {target_concept} from first principles through a carefully
constructed knowledge tree. Each concept is explained with mathematical rigor
and visual clarity, building from foundational ideas to advanced understanding.

**Total Concepts**: {len(segments)}
**Progression**: {' → '.join(concept_order)}
**Estimated Duration**: {total_duration} seconds ({total_duration // 60}:{total_duration % 60:02d})

## Animation Requirements
- Use Manim Community Edition (manim)
- All LaTeX must be in raw strings: r\"$\\\\frac{{a}}{{b}}$\"
- Use MathTex() for equations, Text() for labels
- Maintain color consistency throughout
- Ensure smooth transitions between scenes
- Include voiceover-friendly pacing (2-3 seconds per concept introduction)

## Scene Sequence

"""

        # Add each segment as a numbered scene
        scene_descriptions = []
        for i, (concept, segment) in enumerate(zip(concept_order, segments), 1):
            # Calculate time range
            start_time = sum(
                concept_order[j] and 15  # default 15 sec if no visual_spec
                for j in range(i - 1)
            )
            duration = 15  # default

            scene_desc = f"""### Scene {i}: {concept}
**Timestamp**: {start_time // 60}:{start_time % 60:02d} - {(start_time + duration) // 60}:{(start_time + duration) % 60:02d}

{segment}

---
"""
            scene_descriptions.append(scene_desc)

        # Assemble full prompt
        full_prompt = header + '\n'.join(scene_descriptions)

        # Add footer
        footer = f"""
## Final Notes

This animation is designed to be pedagogically sound and mathematically rigorous.
The progression from {concept_order[0]} to {target_concept} ensures that viewers
have all necessary prerequisites before encountering advanced concepts.

All visual elements, colors, and transitions have been specified to maintain
consistency and clarity throughout the {total_duration}-second animation.

Generate complete, working Manim Community Edition Python code that implements
this scene sequence with all specified mathematical notation, visual elements,
colors, and animations.
"""

        return full_prompt + footer


def demo():
    """Demo the narrative composer on a complete knowledge tree"""
    from prerequisite_explorer_claude import PrerequisiteExplorer, ConceptAnalyzer
    from mathematical_enricher import MathematicalEnricher
    from visual_designer import VisualDesigner

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     NARRATIVE COMPOSER - Claude Sonnet 4.5 Version               ║
║                                                                   ║
║  Composes verbose LaTeX-rich prompts from knowledge trees:       ║
║  - Topologically sorted (foundation → target)                    ║
║  - 2000+ token detailed descriptions                             ║
║  - Complete Manim specifications                                 ║
║  - Pedagogically sound progression                               ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Build complete pipeline
    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=2)
    enricher = MathematicalEnricher()
    designer = VisualDesigner()
    composer = NarrativeComposer()

    user_input = "Explain the Pythagorean theorem"
    print(f"\nUSER INPUT: {user_input}\n")

    # Step 1: Analyze
    print("[1] Analyzing concept...")
    analysis = analyzer.analyze(user_input)

    # Step 2: Build tree
    print(f"\n[2] Building knowledge tree...")
    tree = explorer.explore(analysis['core_concept'])

    # Step 3: Enrich with math
    print("\n[3] Enriching with mathematics...")
    enriched_tree = enricher.enrich_tree(tree)

    # Step 4: Design visuals
    print("\n[4] Designing visuals...")
    designed_tree = designer.design_tree(enriched_tree)

    # Step 5: Compose narrative
    print("\n[5] Composing narrative...")
    narrative = composer.compose(designed_tree)

    # Step 6: Display results
    print("\n" + "=" * 70)
    print("FINAL VERBOSE PROMPT")
    print("=" * 70)
    print(narrative.verbose_prompt)
    print("\n" + "=" * 70)

    # Step 7: Save
    output_file = "verbose_prompt.txt"
    with open(output_file, 'w') as f:
        f.write(narrative.verbose_prompt)
    print(f"\n[6] Saved verbose prompt to: {output_file}")
    print(f"    Length: {len(narrative.verbose_prompt)} characters")
    print(f"    (~{len(narrative.verbose_prompt.split())} words)")
    print(f"    Scenes: {narrative.scene_count}")
    print(f"    Duration: {narrative.total_duration} seconds")

    # Also save JSON
    json_file = "narrative.json"
    with open(json_file, 'w') as f:
        json.dump(narrative.to_dict(), f, indent=2)
    print(f"    Metadata: {json_file}")


if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nPlease set your Claude API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        print("\nGet your API key from: https://console.anthropic.com/")
        exit(1)

    demo()
