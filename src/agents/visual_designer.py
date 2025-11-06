"""
Visual Designer Agent - Designs visual specifications for knowledge tree nodes
For each concept, designs:
- Visual elements (graphs, shapes, 3D objects)
- Color schemes that build on previous concepts
- Animation sequences and transitions
- Camera movements
- Duration and pacing

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
            "Unable to import KnowledgeNode for VisualDesigner. "
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
class VisualSpec:
    """Visual specification for a concept in a Manim animation"""
    concept: str
    elements: List[str] = field(default_factory=list)  # ['graph', '3d_surface', 'vector_field']
    colors: Dict[str, str] = field(default_factory=dict)  # {'wave': 'BLUE', 'particle': 'RED'}
    animations: List[str] = field(default_factory=list)  # ['FadeIn', 'Transform', 'Rotate']
    transitions: List[str] = field(default_factory=list)  # How to connect to previous scenes
    camera_movement: str = ""
    duration: int = 15  # seconds
    layout: str = ""  # Description of spatial layout

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'concept': self.concept,
            'elements': self.elements,
            'colors': self.colors,
            'animations': self.animations,
            'transitions': self.transitions,
            'camera_movement': self.camera_movement,
            'duration': self.duration,
            'layout': self.layout
        }


class VisualDesigner:
    """
    Agent that designs visual specifications for knowledge tree nodes.

    For each concept, designs:
    - What to show (shapes, graphs, equations, diagrams)
    - Colors that maintain consistency and build on previous scenes
    - Animation sequences (what changes when)
    - Camera movements for 3D scenes
    - Transitions from prerequisite concepts
    - Duration and pacing

    Powered by Claude Sonnet 4.5 for creative visual design.
    """

    def __init__(self, model: str = CLAUDE_MODEL):
        self.model = model
        self.color_palette: Dict[str, str] = {}  # Track colors across concepts
        self.previous_elements: List[str] = []  # Track what was shown before

    async def design_node_async(
        self,
        node: KnowledgeNode,
        parent_spec: Optional[VisualSpec] = None
    ) -> KnowledgeNode:
        """
        Design visual specification for a single node.

        Args:
            node: The knowledge node to design visuals for
            parent_spec: Visual spec of parent concept (for continuity)

        Returns:
            The same node with visual_spec added
        """
        print(f"{'  ' * node.depth}Designing visuals: {node.concept} (depth {node.depth})")

        # Gather context from the node
        equations = node.equations if node.equations else []
        prerequisites = [p.concept for p in node.prerequisites]

        # Design visual spec
        visual_spec = await self._generate_visual_spec_async(
            concept=node.concept,
            equations=equations,
            prerequisites=prerequisites,
            depth=node.depth,
            is_foundation=node.is_foundation,
            parent_spec=parent_spec
        )

        # Update color palette with new colors
        self.color_palette.update(visual_spec.colors)
        self.previous_elements.extend(visual_spec.elements)

        # Store visual spec in node
        if node.visual_spec is None:
            node.visual_spec = {}

        # Merge with existing visual_spec (from MathematicalEnricher)
        node.visual_spec.update(visual_spec.to_dict())

        # Recursively design prerequisites
        designed_prereqs = []
        for prereq in node.prerequisites:
            designed_prereq = await self.design_node_async(prereq, visual_spec)
            designed_prereqs.append(designed_prereq)
        node.prerequisites = designed_prereqs

        return node

    async def _generate_visual_spec_async(
        self,
        concept: str,
        equations: List[str],
        prerequisites: List[str],
        depth: int,
        is_foundation: bool,
        parent_spec: Optional[VisualSpec]
    ) -> VisualSpec:
        """Generate visual specification for a concept using Claude"""

        # Build context about what came before
        previous_context = ""
        if parent_spec:
            previous_context = f"""
Previous concept: {parent_spec.concept}
Previous elements shown: {', '.join(parent_spec.elements)}
Previous colors used: {json.dumps(parent_spec.colors)}
"""

        system_prompt = """You are an expert Manim animator and visual designer who creates
stunning mathematical and scientific visualizations.

Your task is to design the visual specification for a concept that will be
animated using Manim Community Edition.

Design principles:
1. Visual clarity - elements should be easy to understand
2. Color consistency - build on colors used in previous concepts
3. Smooth transitions - connect visually to what came before
4. Mathematical precision - accurately represent the concept
5. Pedagogical value - visualizations should aid understanding

For Manim-specific elements, consider:
- MathTex/Tex for equations
- NumberPlane/Axes for graphs
- 3D objects (Sphere, Surface, etc.) when appropriate
- VGroup for grouping related objects
- Arrows, Vectors, Dots for highlighting
- Color: BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, GOLD, etc.

Return ONLY valid JSON with these exact keys:
- elements: List of visual objects to create
- colors: Dict mapping objects to Manim color names
- animations: List of Manim animation types (FadeIn, Transform, Create, Write, etc.)
- transitions: List of transition descriptions from previous concept
- camera_movement: Camera movement description (for 3D scenes)
- duration: Estimated duration in seconds (5-30)
- layout: Description of spatial arrangement"""

        user_prompt = f'''Concept: {concept}
Equations to visualize: {json.dumps(equations) if equations else "None yet"}
Prerequisite concepts: {', '.join(prerequisites) if prerequisites else 'None'}
Depth: {depth} (0=target concept, higher=more foundational)
Is foundation: {is_foundation}
{previous_context}

Design a Manim animation segment for this concept.

Return JSON format:
{{
  "elements": ["list", "of", "manim", "objects"],
  "colors": {{"object_name": "MANIM_COLOR"}},
  "animations": ["FadeIn", "Transform", "Write"],
  "transitions": ["description of how to transition from previous concept"],
  "camera_movement": "camera movement description or empty string",
  "duration": 15,
  "layout": "description of spatial layout"
}}

Example for "Special Relativity":
{{
  "elements": [
    "Two reference frames (train and platform)",
    "Light beam with constant speed c",
    "Lorentz transformation equations",
    "Time dilation visualization",
    "Length contraction diagram"
  ],
  "colors": {{
    "train_frame": "BLUE",
    "platform_frame": "GREEN",
    "light_beam": "YELLOW",
    "time_labels": "WHITE",
    "equations": "TEAL"
  }},
  "animations": [
    "FadeIn reference frames",
    "Create light beam propagating",
    "Write Lorentz equations",
    "Transform clocks to show time dilation",
    "Indicate length contraction with arrows"
  ],
  "transitions": [
    "Build on Galilean reference frames from previous scene",
    "Show that unlike Galilean case, light speed stays constant",
    "Fade in new equations while keeping frame visualization"
  ],
  "camera_movement": "",
  "duration": 25,
  "layout": "Split screen: left shows train frame (blue), right shows platform frame (green). Equations appear at bottom. Light beam travels through both frames."
}}'''

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=2500,
                temperature=0.6,  # Higher temperature for creative visual design
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=2500,
            )

        # Parse JSON response
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            if "```" in content:
                section = content.split("```")[1]
                if section.startswith("json"):
                    section = section[4:]
                data = json.loads(section.strip())
            else:
                # Fallback: extract JSON object
                import re
                match = re.search(r'\{.*?\}', content, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse visual spec from: {content}")

        return VisualSpec(
            concept=concept,
            elements=data.get('elements', []),
            colors=data.get('colors', {}),
            animations=data.get('animations', []),
            transitions=data.get('transitions', []),
            camera_movement=data.get('camera_movement', ''),
            duration=data.get('duration', 15),
            layout=data.get('layout', '')
        )

    # Backwards-compatible sync wrapper
    def design_node(self, node: KnowledgeNode, parent_spec: Optional[VisualSpec] = None) -> KnowledgeNode:
        """Synchronous wrapper for design_node_async"""
        return asyncio.run(self.design_node_async(node, parent_spec))

    def design_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        """
        Design visual specifications for an entire knowledge tree.

        Args:
            root: Root of the knowledge tree

        Returns:
            The tree with visual specifications added to all nodes
        """
        return self.design_node(root)


def demo():
    """Demo the visual designer on a sample knowledge tree"""
    from prerequisite_explorer_claude import PrerequisiteExplorer, ConceptAnalyzer
    from mathematical_enricher import MathematicalEnricher

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     VISUAL DESIGNER - Claude Sonnet 4.5 Version                  ║
║                                                                   ║
║  Designs visual specifications for knowledge tree nodes:         ║
║  - Manim visual elements                                         ║
║  - Color schemes                                                 ║
║  - Animation sequences                                           ║
║  - Camera movements                                              ║
║  - Transitions                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Build and enrich a knowledge tree
    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=2)
    enricher = MathematicalEnricher()
    designer = VisualDesigner()

    user_input = "Explain quantum tunneling"
    print(f"\nUSER INPUT: {user_input}\n")

    # Step 1: Analyze
    print("[1] Analyzing concept...")
    analysis = analyzer.analyze(user_input)
    print(json.dumps(analysis, indent=2))

    # Step 2: Build tree
    print(f"\n[2] Building knowledge tree for: {analysis['core_concept']}")
    tree = explorer.explore(analysis['core_concept'])

    # Step 3: Enrich with math
    print("\n[3] Enriching with mathematical content...")
    enriched_tree = enricher.enrich_tree(tree)

    # Step 4: Design visuals
    print("\n[4] Designing visual specifications...")
    designed_tree = designer.design_tree(enriched_tree)

    # Step 5: Display visual specs
    print("\n[5] Visual Specifications:")
    print("=" * 70)

    def print_node_visuals(node: KnowledgeNode, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}Concept: {node.concept}")
        if node.visual_spec:
            vs = node.visual_spec
            print(f"{prefix}  Elements: {', '.join(vs.get('elements', []))}")
            print(f"{prefix}  Colors: {json.dumps(vs.get('colors', {}))}")
            print(f"{prefix}  Duration: {vs.get('duration', 0)} seconds")
            print(f"{prefix}  Layout: {vs.get('layout', 'N/A')[:60]}...")
        print()
        for prereq in node.prerequisites:
            print_node_visuals(prereq, indent + 1)

    print_node_visuals(designed_tree)

    # Step 6: Save
    output_file = "designed_knowledge_tree.json"
    with open(output_file, 'w') as f:
        json.dump(designed_tree.to_dict(), f, indent=2)
    print(f"\n[6] Saved designed tree to: {output_file}")


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
