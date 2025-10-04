"""
Prerequisite Explorer - The Core Innovation
Recursively decomposes concepts by asking "What must I understand BEFORE this?"

No training data required - uses LLM reasoning to build knowledge trees.
"""

import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from openai import OpenAI
try:
try:
    from .nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
except ImportError:  # pragma: no cover - optional dependency
    AtlasClient = None  # type: ignore[assignment]
    AtlasConcept = None  # type: ignore[assignment]
    NomicNotInstalledError = RuntimeError  # type: ignore[assignment]
except Exception:  # pragma: no cover - optional dependency
    AtlasClient = AtlasConcept = NomicNotInstalledError = None  # type: ignore

load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


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
    """

    def __init__(self, model: str = "deepseek-reasoner", max_depth: int = 4):
        self.model = model
        self.max_depth = max_depth
        self.cache = {}  # Cache prerequisite queries to avoid redundant LLM calls
        self.atlas_client: Optional[AtlasClient] = None

    def enable_atlas_integration(self, dataset_name: str) -> None:
        """Enable Nomic Atlas integration for caching and search."""

        if AtlasClient is None:
            print("Nomic Atlas client not available. Skipping integration.")
            return

        try:
            client = AtlasClient(dataset_name)  # type: ignore[call-arg]
            client.ensure_dataset()
        except NomicNotInstalledError:  # type: ignore[misc]
            print("Nomic Atlas client not available. Skipping integration.")
            return

        self.atlas_client = client

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
            print(f"{'  ' * depth}  -> Foundation concept")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[]
            )

        # Check cache
        cached_prereqs = self.lookup_prerequisites(concept)

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
        """
        prompt = f"""Is "{concept}" a foundational concept that a typical high school graduate
would understand without further mathematical/scientific explanation?

Examples of foundational concepts:
- velocity, distance, time, acceleration
- force, mass, energy
- waves, frequency, wavelength
- numbers, addition, multiplication
- basic geometry (points, lines, angles)

Examples of non-foundational concepts:
- Lorentz transformations
- gauge theory
- differential geometry
- tensor calculus
- quantum operators

Answer with ONLY "yes" or "no"."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith('yes')

    def lookup_prerequisites(self, concept: str) -> List[str]:
        """Lookup prerequisites via cache, Atlas, or LLM fallback."""

        # Local cache
        if concept in self.cache:
            print(f"  -> Using in-memory cache for {concept}")
            return self.cache[concept]

        # Atlas cache
        if self.atlas_client is not None:
            atlas_results = self._atlas_fetch_prerequisites(concept)
            if atlas_results:
                print(f"  -> Loaded {len(atlas_results)} prerequisites from Atlas")
                self.cache[concept] = atlas_results
                return atlas_results

        # LLM fallback
        prerequisites = self.discover_prerequisites(concept)
        self.cache[concept] = prerequisites

        # Push to Atlas for future reuse
        if self.atlas_client is not None and AtlasConcept is not None:
            self._atlas_store_prerequisites(concept, prerequisites)

        return prerequisites

    def discover_prerequisites(self, concept: str) -> List[str]:
        """
        Ask LLM: "To understand [concept], what must I know first?"

        Returns list of 3-5 essential prerequisite concepts.
        """
        prompt = f"""To understand "{concept}", what are the 3-5 ESSENTIAL prerequisite concepts
that someone must understand first?

Rules:
1. Only list concepts that are NECESSARY for understanding {concept}
2. Order from most to least important
3. Assume high school education as baseline (don't list truly basic things)
4. Focus on concepts that enable understanding, not just historical context
5. Be specific - prefer "special relativity" over "relativity"

Return ONLY a JSON array of concept names, nothing else.
Example format: ["concept1", "concept2", "concept3"]"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()

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
                raise ValueError(f"Could not parse prerequisites from: {content}")

        return prerequisites[:5]  # Limit to 5 to avoid explosion

    # ------------------------------------------------------------------
    # Atlas helpers
    # ------------------------------------------------------------------
    def _atlas_fetch_prerequisites(self, concept: str) -> List[str]:
        """Retrieve cached prerequisites for a concept from Atlas metadata."""

        if self.atlas_client is None:
            return []

        try:
            results = self.atlas_client.search_similar(
                concept,
                k=5,
                fields=["concept", "prerequisites"],
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Atlas fetch failed: {exc}")
            return []

        for result in results:
            metadata = result.get("data") or result
            if metadata.get("concept") == concept:
                prereqs = metadata.get("prerequisites")
                if isinstance(prereqs, list):
                    return prereqs
        return []

    def _atlas_store_prerequisites(self, concept: str, prerequisites: List[str]) -> None:
        """Persist discovered prerequisites back to Atlas for future reuse."""

        if self.atlas_client is None:
            return

        try:
            self.atlas_client.upsert_concepts(
                [
                    AtlasConcept(
                        concept=concept,
                        metadata={"prerequisites": prerequisites},
                    )
                ]
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Atlas store failed: {exc}")


class ConceptAnalyzer:
    """Analyzes user input to extract the core concept and metadata"""

    def __init__(self, model: str = "deepseek-reasoner"):
        self.model = model

    def analyze(self, user_input: str) -> Dict:
        """
        Parse user input to identify:
        - Core concept(s)
        - Domain (physics, math, CS, etc.)
        - Complexity level
        - Learning goals
        """
        prompt = f"""User asked: "{user_input}"

Analyze this request and return a JSON object with:
1. "core_concept": The MAIN concept they want to understand (be specific)
2. "domain": Scientific/mathematical domain (e.g., "physics/quantum mechanics", "mathematics/calculus")
3. "level": Appropriate complexity level ("beginner", "intermediate", "advanced")
4. "goal": What understanding are they seeking? (1 sentence)

Example response:
{{
  "core_concept": "quantum entanglement",
  "domain": "physics/quantum mechanics",
  "level": "intermediate",
  "goal": "Understand how entangled particles maintain correlation across distances"
}}

Return ONLY valid JSON, nothing else."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()

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
                raise ValueError(f"Could not parse analysis from: {content}")

        return analysis


def demo():
    """Demo the prerequisite explorer on a few examples"""

    examples = [
        "Explain cosmology to me",
        "How does quantum field theory work?",
        "Teach me about Fourier analysis"
    ]

    analyzer = ConceptAnalyzer()
    explorer = PrerequisiteExplorer(max_depth=3)  # Limit depth for demo

    for user_input in examples:
        print("\n" + "="*70)
        print(f"USER INPUT: {user_input}")
        print("="*70)

        # Step 1: Analyze concept
        print("\n[1] Analyzing concept...")
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

        print("\n" + "="*70)
        input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║           PREREQUISITE EXPLORER - Demo                           ║
║                                                                   ║
║  This demonstrates the core innovation:                          ║
║  Recursively asking "What must I understand BEFORE X?"           ║
║  to build complete knowledge trees with NO training data.        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    demo()
