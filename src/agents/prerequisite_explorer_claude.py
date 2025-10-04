"""
Prerequisite Explorer - The Core Innovation (Claude Agent SDK Version)
Recursively decomposes concepts by asking "What must I understand BEFORE this?"

Uses Claude Sonnet 4.5 via the Anthropic Claude Agent SDK.
No training data required - uses Claude's reasoning to build knowledge trees.
"""

import os
import json
import asyncio
from dataclasses import dataclass
from functools import partial
from typing import Dict, List, Optional

from anthropic import Anthropic
from anthropic import NotFoundError
from dotenv import load_dotenv

# Import from same package using absolute imports
try:
    from src.agents.claude_agent_runtime import run_query_via_sdk
except ImportError:
    # Fallback for direct execution
    try:
        from claude_agent_runtime import run_query_via_sdk
    except ImportError:
        run_query_via_sdk = None  # type: ignore[assignment]

try:
    from src.agents.nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
except ImportError:  # pragma: no cover - optional dependency
    try:
        from nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
    except ImportError:
        AtlasClient = None  # type: ignore[assignment]
        AtlasConcept = None  # type: ignore[assignment]
        NomicNotInstalledError = RuntimeError  # type: ignore[assignment]

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


CLAUDE_MODEL = "claude-sonnet-4-5"  # Claude Sonnet 4.5


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
        self.atlas_client: Optional[AtlasClient] = None

    def enable_atlas_integration(self, dataset_name: str) -> None:
        """Enable Nomic Atlas integration for caching and search."""

        if AtlasClient is None:
            print("Nomic Atlas client not available. Skipping integration.")
            return

        try:
            client = AtlasClient(dataset_name)  # type: ignore[call-arg]
            client.ensure_dataset()
        except NomicNotInstalledError:
            print("Nomic Atlas client not available. Skipping integration.")
            return

        self.atlas_client = client

    async def explore_async(self, concept: str, depth: int = 0) -> KnowledgeNode:
        print(f"{'  ' * depth}Exploring: {concept} (depth {depth})")

        if depth >= self.max_depth or await self.is_foundation_async(concept):
            print(f"{'  ' * depth}  -> Foundation concept")
            return KnowledgeNode(concept=concept, depth=depth, is_foundation=True, prerequisites=[])

        prerequisites = await self.lookup_prerequisites_async(concept)
        nodes = []
        for prereq in prerequisites:
            nodes.append(await self.explore_async(prereq, depth + 1))

        return KnowledgeNode(concept=concept, depth=depth, is_foundation=False, prerequisites=nodes)

    async def is_foundation_async(self, concept: str) -> bool:
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

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            answer = response.content[0].text
        except NotFoundError:
            answer = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0,
                max_tokens=10,
            )

        return answer.strip().lower().startswith('yes')

    async def lookup_prerequisites_async(self, concept: str) -> List[str]:
        if concept in self.cache:
            print(f"  -> Using in-memory cache for {concept}")
            return self.cache[concept]

        if self.atlas_client is not None:
            loop = asyncio.get_running_loop()
            atlas_results = await loop.run_in_executor(
                None, partial(self._atlas_fetch_prerequisites, concept)
            )
            if atlas_results:
                print(f"  -> Loaded {len(atlas_results)} prerequisites from Atlas")
                self.cache[concept] = atlas_results
                return atlas_results

        prerequisites = await self.discover_prerequisites_async(concept)
        self.cache[concept] = prerequisites

        if self.atlas_client is not None and AtlasConcept is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, partial(self._atlas_store_prerequisites, concept, prerequisites)
            )

        return prerequisites

    async def discover_prerequisites_async(self, concept: str) -> List[str]:
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

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500,
            )

        try:
            prerequisites = json.loads(content)
        except json.JSONDecodeError:
            if "```" in content:
                section = content.split("```")[1]
                if section.startswith("json"):
                    section = section[4:]
                prerequisites = json.loads(section.strip())
            else:
                import re

                match = re.search(r"\[.*?\]", content, re.DOTALL)
                if match:
                    prerequisites = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse prerequisites from: {content}")

        return prerequisites[:5]

    # ------------------------------------------------------------------
    # Backwards-compatible sync wrappers
    # ------------------------------------------------------------------
    def explore(self, concept: str, depth: int = 0) -> KnowledgeNode:
        return asyncio.run(self.explore_async(concept, depth))

    def is_foundation(self, concept: str) -> bool:
        return asyncio.run(self.is_foundation_async(concept))

    def lookup_prerequisites(self, concept: str) -> List[str]:
        return asyncio.run(self.lookup_prerequisites_async(concept))

    def discover_prerequisites(self, concept: str) -> List[str]:
        return asyncio.run(self.discover_prerequisites_async(concept))

    # ------------------------------------------------------------------
    # Atlas helpers
    # ------------------------------------------------------------------
    def _atlas_fetch_prerequisites(self, concept: str) -> List[str]:
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
        if self.atlas_client is None or AtlasConcept is None:
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

        client = _ensure_client()
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
            print(f"\n[FAIL] Error: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*70)
        input("\nPress Enter to continue to next example...")


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
