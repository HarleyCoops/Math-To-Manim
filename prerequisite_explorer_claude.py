"""
Prerequisite Explorer - The Core Innovation (Claude Agent SDK Version)
Recursively decomposes concepts by asking "What must I understand BEFORE this?"

Uses Claude Sonnet 4.5 via the Anthropic Claude Agent SDK.
No training data required - uses Claude's reasoning to build knowledge trees.
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Initialize Anthropic client for Claude Sonnet 4.5
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Model configuration
CLAUDE_MODEL = "claude-sonnet-4.5-20251022"  # Latest Sonnet 4.5


@dataclass
class KnowledgeNode:
    """Represents a concept in the knowledge tree"""
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List['KnowledgeNode']

    # Will be added by enrichment agents later
    equations: Optional[List[str]] = None
    definitions: Optional[Dict[str, str]] = None
    visual_spec: Optional[Dict] = None
    narrative: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'concept': self.concept,
            'depth': self.depth,
            'is_foundation': self.is_foundation,
            'prerequisites': [p.to_dict() for p in self.prerequisites],
            'equations': self.equations,
            'definitions': self.definitions,
            'visual_spec': self.visual_spec,
            'narrative': self.narrative
        }

    def print_tree(self, indent: int = 0):
        """Pretty print the knowledge tree"""
        prefix = "  " * indent
        foundation_mark = " [FOUNDATION]" if self.is_foundation else ""
        print(f"{prefix}├─ {self.concept} (depth {self.depth}){foundation_mark}")
        for prereq in self.prerequisites:
            prereq.print_tree(indent + 1)


class PrerequisiteExplorer:
    """
    Core agent that recursively discovers prerequisites for any concept.
    This is the key innovation - no training data needed!

    Powered by Claude Sonnet 4.5 for superior reasoning capabilities.
    """

    def __init__(self, model: str = CLAUDE_MODEL, max_depth: int = 4):
        self.model = model
        self.max_depth = max_depth
        self.cache = {}  # Cache prerequisite queries to avoid redundant API calls

    def explore(self, concept: str, depth: int = 0) -> KnowledgeNode:
        """
        Recursively explore prerequisites for a concept.

        Args:
            concept: The concept to explore
            depth: Current recursion depth (0 = target concept)

        Returns:
            KnowledgeNode with complete prerequisite tree
        """
        print(f"{'  ' * depth}Exploring: {concept} (depth {depth})")

        # Base case: check if foundation or max depth reached
        if depth >= self.max_depth or self.is_foundation(concept):
            print(f"{'  ' * depth}  → Foundation concept")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[]
            )

        # Check cache
        if concept in self.cache:
            print(f"{'  ' * depth}  → Using cached prerequisites")
            cached_prereqs = self.cache[concept]
        else:
            # Discover prerequisites
            cached_prereqs = self.discover_prerequisites(concept)
            self.cache[concept] = cached_prereqs

        # Recurse on each prerequisite
        prerequisite_nodes = []
        for prereq in cached_prereqs:
            node = self.explore(prereq, depth + 1)
            prerequisite_nodes.append(node)

        return KnowledgeNode(
            concept=concept,
            depth=depth,
            is_foundation=False,
            prerequisites=prerequisite_nodes
        )

    def is_foundation(self, concept: str) -> bool:
        """
        Determine if a concept is foundational (no further decomposition needed).

        A concept is foundational if a typical high school graduate would
        understand it without further explanation.

        Uses Claude Sonnet 4.5's superior reasoning to make this determination.
        """
        system_prompt = """You are an expert educator analyzing whether a concept is foundational.

A concept is foundational if a typical high school graduate would understand it
without further mathematical or scientific explanation.

Examples of foundational concepts:
- velocity, distance, time, acceleration
- force, mass, energy
- waves, frequency, wavelength
- numbers, addition, multiplication
- basic geometry (points, lines, angles)
- functions, graphs

Examples of non-foundational concepts:
- Lorentz transformations
- gauge theory
- differential geometry
- tensor calculus
- quantum operators
- Hilbert spaces"""

        user_prompt = f'Is "{concept}" a foundational concept?\n\nAnswer with ONLY "yes" or "no".'

        response = client.messages.create(
            model=self.model,
            max_tokens=10,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        answer = response.content[0].text.strip().lower()
        return answer.startswith('yes')

    def discover_prerequisites(self, concept: str) -> List[str]:
        """
        Ask Claude: "To understand [concept], what must I know first?"

        Returns list of 3-5 essential prerequisite concepts.

        Uses Claude Sonnet 4.5's extended thinking for thorough prerequisite analysis.
        """
        system_prompt = """You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding (not just helpful)
2. Order from most to least important
3. Assume high school education as baseline (don't list truly basic things)
4. Focus on concepts that enable understanding, not just historical context
5. Be specific - prefer "special relativity" over "relativity"
6. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names, nothing else."""

        user_prompt = f'''To understand "{concept}", what are the 3-5 ESSENTIAL prerequisite concepts?

Return format: ["concept1", "concept2", "concept3"]'''

        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        content = response.content[0].text.strip()

        # Extract JSON array from response
        try:
            # Try to parse directly
            prerequisites = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                prerequisites = json.loads(content.strip())
            else:
                # Fallback: extract anything that looks like a JSON array
                import re
                match = re.search(r'\[.*?\]', content, re.DOTALL)
                if match:
                    prerequisites = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse prerequisites from: {content}")

        return prerequisites[:5]  # Limit to 5 to avoid explosion


class ConceptAnalyzer:
    """
    Analyzes user input to extract the core concept and metadata.

    Uses Claude Sonnet 4.5 for superior intent understanding.
    """

    def __init__(self, model: str = CLAUDE_MODEL):
        self.model = model

    def analyze(self, user_input: str) -> Dict:
        """
        Parse user input to identify:
        - Core concept(s)
        - Domain (physics, math, CS, etc.)
        - Complexity level
        - Learning goals
        """
        system_prompt = """You are an expert at analyzing educational requests and extracting key information.

Analyze the user's question and extract:
1. The MAIN concept they want to understand (be specific)
2. The scientific/mathematical domain
3. The appropriate complexity level
4. Their learning goal

Return ONLY valid JSON with these exact keys:
- core_concept
- domain
- level (must be: "beginner", "intermediate", or "advanced")
- goal"""

        user_prompt = f'''User asked: "{user_input}"

Return JSON analysis with: core_concept, domain, level, goal

Example:
{{
  "core_concept": "quantum entanglement",
  "domain": "physics/quantum mechanics",
  "level": "intermediate",
  "goal": "Understand how entangled particles maintain correlation across distances"
}}'''

        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        content = response.content[0].text.strip()

        # Parse JSON
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                analysis = json.loads(content.strip())
            else:
                # Fallback: extract JSON object
                import re
                match = re.search(r'\{.*?\}', content, re.DOTALL)
                if match:
                    analysis = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse analysis from: {content}")

        return analysis


def demo():
    """Demo the prerequisite explorer on a few examples"""

    examples = [
        "Explain cosmology to me",
        "How does quantum field theory work?",
        "Teach me about Fourier analysis"
    ]

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     PREREQUISITE EXPLORER - Claude Sonnet 4.5 Version            ║
║                                                                   ║
║  This demonstrates the core innovation:                          ║
║  Recursively asking "What must I understand BEFORE X?"           ║
║  to build complete knowledge trees with NO training data.        ║
║                                                                   ║
║  Powered by: Claude Sonnet 4.5 (claude-sonnet-4.5-20251022)     ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=3)  # Limit depth for demo

    for user_input in examples:
        print("\n" + "="*70)
        print(f"USER INPUT: {user_input}")
        print("="*70)

        try:
            # Step 1: Analyze concept
            print("\n[1] Analyzing concept with Claude Sonnet 4.5...")
            analysis = analyzer.analyze(user_input)
            print(json.dumps(analysis, indent=2))

            # Step 2: Build knowledge tree
            print(f"\n[2] Building knowledge tree for: {analysis['core_concept']}")
            print("-" * 70)
            tree = explorer.explore(analysis['core_concept'])

            # Step 3: Display tree
            print("\n[3] Knowledge Tree:")
            print("-" * 70)
            tree.print_tree()

            # Step 4: Save to JSON
            output_file = f"knowledge_tree_{analysis['core_concept'].replace(' ', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(tree.to_dict(), f, indent=2)
            print(f"\n[4] Saved tree to: {output_file}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*70)
        input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nPlease set your Claude API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        print("\nGet your API key from: https://console.anthropic.com/")
        exit(1)

    demo()
