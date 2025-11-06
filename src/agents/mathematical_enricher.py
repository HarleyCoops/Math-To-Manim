"""
Mathematical Enricher Agent - Adds mathematical rigor to knowledge tree nodes
For each concept in the tree, adds:
- Key equations in LaTeX
- Variable definitions
- Physical/mathematical interpretations
- Worked examples

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
# Import the optional Claude Agent SDK bridge if available. Tests do not need it,
# so we degrade gracefully when the dependency is missing.
try:
    from src.agents.claude_agent_runtime import run_query_via_sdk
except ImportError:
    try:
        from claude_agent_runtime import run_query_via_sdk
    except ImportError:
        run_query_via_sdk = None  # type: ignore[assignment]

# KnowledgeNode is required for the enricher to operate, so fail fast with a clear
# error if we cannot import it.
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
            "Unable to import KnowledgeNode for MathematicalEnricher. "
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
class MathematicalContent:
    """Mathematical content for a concept"""
    concept: str
    equations: List[str] = field(default_factory=list)
    definitions: Dict[str, str] = field(default_factory=dict)
    interpretation: str = ""
    examples: List[str] = field(default_factory=list)
    typical_values: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'concept': self.concept,
            'equations': self.equations,
            'definitions': self.definitions,
            'interpretation': self.interpretation,
            'examples': self.examples,
            'typical_values': self.typical_values
        }


class MathematicalEnricher:
    """
    Agent that enriches knowledge tree nodes with mathematical content.

    For each concept, generates:
    - LaTeX equations appropriate to the depth level
    - Clear variable definitions
    - Physical/mathematical interpretation
    - Worked examples with typical values

    Powered by Claude Sonnet 4.5 for mathematical reasoning.
    """

    def __init__(self, model: str = CLAUDE_MODEL):
        self.model = model

    async def enrich_node_async(self, node: KnowledgeNode) -> KnowledgeNode:
        """
        Enrich a single node with mathematical content.

        Args:
            node: The knowledge node to enrich

        Returns:
            The same node with equations, definitions, and examples added
        """
        print(f"{'  ' * node.depth}Enriching: {node.concept} (depth {node.depth})")

        # If it's a foundation concept, keep math simple
        # If it's advanced, add more rigor
        complexity = "high school level" if node.is_foundation else "undergraduate/graduate level"

        math_content = await self._generate_math_content_async(node.concept, complexity, node.depth)

        # Update the node with mathematical content
        node.equations = math_content.equations
        node.definitions = math_content.definitions

        # Store additional metadata in visual_spec if not already set
        if node.visual_spec is None:
            node.visual_spec = {}
        node.visual_spec['interpretation'] = math_content.interpretation
        node.visual_spec['examples'] = math_content.examples
        node.visual_spec['typical_values'] = math_content.typical_values

        # Recursively enrich prerequisites
        enriched_prereqs = []
        for prereq in node.prerequisites:
            enriched_prereq = await self.enrich_node_async(prereq)
            enriched_prereqs.append(enriched_prereq)
        node.prerequisites = enriched_prereqs

        return node

    async def _generate_math_content_async(
        self,
        concept: str,
        complexity: str,
        depth: int
    ) -> MathematicalContent:
        """Generate mathematical content for a concept using Claude"""

        system_prompt = """You are an expert mathematician and physicist who excels at
presenting mathematical concepts with perfect LaTeX notation.

Your task is to provide the key mathematical formulations for a concept,
formatted for use in Manim animations.

Important LaTeX guidelines:
- Use raw string format: r"$\\frac{a}{b}$"
- Double backslashes for LaTeX commands
- Use proper LaTeX math mode delimiters
- Ensure all equations are syntactically correct
- Use MathTex-compatible notation

Return ONLY valid JSON with these exact keys:
- equations: List of LaTeX strings (2-5 key equations)
- definitions: Dict of variable/symbol definitions
- interpretation: Physical or mathematical meaning
- examples: List of worked examples (1-2)
- typical_values: Dict of typical magnitudes/values"""

        user_prompt = f'''Concept: {concept}
Complexity level: {complexity}
Depth in knowledge tree: {depth} (0=advanced, higher=more foundational)

Provide the mathematical content for this concept suitable for a Manim animation.

Return JSON format:
{{
  "equations": ["r\\"$equation1$\\"", "r\\"$equation2$\\""],
  "definitions": {{"symbol": "meaning", ...}},
  "interpretation": "What this equation physically/mathematically means",
  "examples": ["Example 1 calculation", "Example 2 calculation"],
  "typical_values": {{"quantity": "typical value with units", ...}}
}}

Example response for "Newton's Second Law":
{{
  "equations": [
    "r\\"$\\\\vec{{F}} = m\\\\vec{{a}}$\\"",
    "r\\"$F = ma \\\\text{{ (1D form)}}$\\""
  ],
  "definitions": {{
    "F": "Force (Newtons)",
    "m": "Mass (kilograms)",
    "a": "Acceleration (m/s²)"
  }},
  "interpretation": "Force equals mass times acceleration - the acceleration of an object is directly proportional to the net force and inversely proportional to its mass",
  "examples": [
    "A 10 kg object with 20 N force: a = F/m = 20/10 = 2 m/s²",
    "A 2 kg object accelerating at 5 m/s²: F = ma = 2×5 = 10 N"
  ],
  "typical_values": {{
    "Human mass": "50-100 kg",
    "Gravitational acceleration": "9.8 m/s²",
    "Car acceleration": "0-5 m/s²"
  }}
}}'''

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.4,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=2000,
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
                    raise ValueError(f"Could not parse math content from: {content}")

        return MathematicalContent(
            concept=concept,
            equations=data.get('equations', []),
            definitions=data.get('definitions', {}),
            interpretation=data.get('interpretation', ''),
            examples=data.get('examples', []),
            typical_values=data.get('typical_values', {})
        )

    # Backwards-compatible sync wrapper
    def enrich_node(self, node: KnowledgeNode) -> KnowledgeNode:
        """Synchronous wrapper for enrich_node_async"""
        return asyncio.run(self.enrich_node_async(node))

    def enrich_tree(self, root: KnowledgeNode) -> KnowledgeNode:
        """
        Enrich an entire knowledge tree with mathematical content.

        Args:
            root: Root of the knowledge tree

        Returns:
            The enriched tree
        """
        return self.enrich_node(root)


def demo():
    """Demo the mathematical enricher on a sample knowledge tree"""
    from prerequisite_explorer_claude import PrerequisiteExplorer, ConceptAnalyzer

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     MATHEMATICAL ENRICHER - Claude Sonnet 4.5 Version            ║
║                                                                   ║
║  Adds mathematical rigor to knowledge tree nodes:                ║
║  - LaTeX equations                                               ║
║  - Variable definitions                                          ║
║  - Physical interpretations                                      ║
║  - Worked examples                                               ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Build a simple knowledge tree
    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=2)
    enricher = MathematicalEnricher()

    user_input = "Explain special relativity"
    print(f"\nUSER INPUT: {user_input}\n")

    # Step 1: Analyze
    print("[1] Analyzing concept...")
    analysis = analyzer.analyze(user_input)
    print(json.dumps(analysis, indent=2))

    # Step 2: Build tree
    print(f"\n[2] Building knowledge tree for: {analysis['core_concept']}")
    tree = explorer.explore(analysis['core_concept'])
    tree.print_tree()

    # Step 3: Enrich with math
    print("\n[3] Enriching tree with mathematical content...")
    enriched_tree = enricher.enrich_tree(tree)

    # Step 4: Display enriched content
    print("\n[4] Enriched Content:")
    print("=" * 70)

    def print_node_math(node: KnowledgeNode, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}Concept: {node.concept}")
        if node.equations:
            print(f"{prefix}  Equations:")
            for eq in node.equations:
                print(f"{prefix}    - {eq}")
        if node.definitions:
            print(f"{prefix}  Definitions:")
            for symbol, meaning in node.definitions.items():
                print(f"{prefix}    {symbol}: {meaning}")
        print()
        for prereq in node.prerequisites:
            print_node_math(prereq, indent + 1)

    print_node_math(enriched_tree)

    # Step 5: Save
    output_file = "enriched_knowledge_tree.json"
    with open(output_file, 'w') as f:
        json.dump(enriched_tree.to_dict(), f, indent=2)
    print(f"\n[5] Saved enriched tree to: {output_file}")


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
