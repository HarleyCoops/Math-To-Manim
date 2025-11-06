"""Kimi K2 Prerequisite Explorer - Refactored for Kimi K2 thinking model.

This version uses:
- Kimi K2 API (OpenAI-compatible) instead of Claude
- Tool adapter to convert tool calls to verbose instructions when needed
- Same interface as EnhancedPrerequisiteExplorer for compatibility
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Import Kimi K2 components
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import modules directly (Python can handle hyphens in folder names via sys.path)
from kimi_client import KimiClient, get_kimi_client
from tool_adapter import ToolAdapter
from config import TOOLS_ENABLED, FALLBACK_TO_VERBOSE

# Try to import tools from original implementation
try:
    from src.agents.claude_sdk_tools import ALL_TOOLS
except ImportError:
    try:
        from claude_sdk_tools import ALL_TOOLS
    except ImportError:
        print("Warning: Could not import custom tools")
        ALL_TOOLS = []


@dataclass
class KnowledgeNode:
    """Represents a concept in the knowledge tree"""
    concept: str
    depth: int
    is_foundation: bool
    prerequisites: List['KnowledgeNode']

    # Metadata from enrichment
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


class KimiPrerequisiteExplorer:
    """
    Prerequisite explorer using Kimi K2 thinking model.

    Key features:
    - Uses Kimi K2 API (OpenAI-compatible)
    - Converts tool calls to verbose instructions when tools unavailable
    - Same interface as EnhancedPrerequisiteExplorer for compatibility
    """

    def __init__(self, max_depth: int = 4, use_tools: bool = True):
        """
        Initialize Kimi prerequisite explorer.

        Args:
            max_depth: Maximum depth for prerequisite exploration
            use_tools: Whether to attempt using tools (may fallback to verbose)
        """
        self.max_depth = max_depth
        self.use_tools = use_tools and TOOLS_ENABLED
        self.cache: Dict[str, List[str]] = {}
        self.client = get_kimi_client()
        self.tool_adapter = ToolAdapter()

        # Prepare tools for Kimi (convert to OpenAI format)
        self.tools = self._prepare_tools() if self.use_tools else None

    def _prepare_tools(self) -> Optional[List[Dict[str, Any]]]:
        """Prepare tools in OpenAI function calling format."""
        if not ALL_TOOLS:
            return None

        # Convert tools to OpenAI format
        openai_tools = []
        for tool in ALL_TOOLS:
            # Tools from claude_sdk_tools use @tool decorator
            # We need to extract the schema
            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": getattr(tool, 'input_schema', {})
                    }
                }
                openai_tools.append(openai_tool)

        return openai_tools if openai_tools else None

    async def explore_async(
        self,
        concept: str,
        depth: int = 0,
        verbose: bool = True
    ) -> KnowledgeNode:
        """
        Explore prerequisites using Kimi K2.

        Args:
            concept: The concept to explore
            depth: Current depth in the tree
            verbose: Whether to print progress

        Returns:
            KnowledgeNode representing the concept and its prerequisites
        """
        if verbose:
            print(f"{'  ' * depth}Exploring: {concept} (depth {depth})")

        # Check if we've hit max depth or found a foundation
        if depth >= self.max_depth:
            if verbose:
                print(f"{'  ' * depth}  -> Max depth reached")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[]
            )

        # Check if it's a foundation concept
        is_foundation = await self._is_foundation_async(concept)
        if is_foundation:
            if verbose:
                print(f"{'  ' * depth}  -> Foundation concept")
            return KnowledgeNode(
                concept=concept,
                depth=depth,
                is_foundation=True,
                prerequisites=[]
            )

        # Get prerequisites (using tools if available, or verbose instructions)
        prerequisites = await self._get_prerequisites_async(concept, verbose)

        # Recursively explore prerequisites
        prereq_nodes = []
        for prereq in prerequisites:
            node = await self.explore_async(prereq, depth + 1, verbose)
            prereq_nodes.append(node)

        return KnowledgeNode(
            concept=concept,
            depth=depth,
            is_foundation=False,
            prerequisites=prereq_nodes
        )

    async def _is_foundation_async(self, concept: str) -> bool:
        """Check if a concept is foundational using Kimi K2."""
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
- Hilbert spaces

Answer with ONLY "yes" or "no"."""

        user_prompt = f'Is "{concept}" a foundational concept?'

        # Make API call
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=50,  # Short response expected
            temperature=0.3,  # Lower temperature for yes/no questions
        )

        response_text = self.client.get_text_content(response)
        return response_text.strip().lower().startswith('yes')

    async def _get_prerequisites_async(
        self,
        concept: str,
        verbose: bool = True
    ) -> List[str]:
        """Get prerequisites for a concept, using cache or Kimi K2."""

        # Check in-memory cache first
        if concept in self.cache:
            if verbose:
                print(f"  -> Using in-memory cache for {concept}")
            return self.cache[concept]

        # Prepare system prompt
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

        # Handle tools vs verbose instructions
        if self.use_tools and self.tools:
            # Try with tools first
            try:
                response = self.client.chat_completion(
                    messages=[{"role": "user", "content": user_prompt}],
                    system=system_prompt,
                    tools=self.tools,
                    tool_choice="auto",
                    max_tokens=1000,
                )

                # Check if tool was called
                if self.client.has_tool_calls(response):
                    # Handle tool calls (for now, extract from response)
                    # In a full implementation, we'd execute the tools
                    tool_calls = self.client.get_tool_calls(response)
                    if verbose:
                        print(f"  -> Tool calls detected: {len(tool_calls)}")
                    # For now, fall through to get text response
                    # In production, execute tools and continue conversation

                # Get text response
                response_text = self.client.get_text_content(response)
            except Exception as e:
                if verbose:
                    print(f"  -> Tool call failed, using verbose instructions: {e}")
                # Fallback to verbose instructions
                response_text = await self._get_prerequisites_verbose(
                    concept, system_prompt, user_prompt
                )
        else:
            # Use verbose instructions directly
            response_text = await self._get_prerequisites_verbose(
                concept, system_prompt, user_prompt
            )

        # Parse JSON response
        prerequisites = self._parse_prerequisites(response_text)

        # Cache the result
        self.cache[concept] = prerequisites

        return prerequisites

    async def _get_prerequisites_verbose(
        self,
        concept: str,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """Get prerequisites using verbose instructions (no tools)."""
        # Enhance prompt with tool instructions if tools exist
        enhanced_prompt = user_prompt

        if self.tools and FALLBACK_TO_VERBOSE:
            # Add tool instructions to prompt
            tool_instructions = self.tool_adapter.tools_to_instructions(self.tools)
            enhanced_prompt = self.tool_adapter.create_verbose_prompt(
                user_prompt,
                tools=self.tools,
                tool_call_context=f"Looking up prerequisites for '{concept}'. "
                                 f"If you have cached information, use it. "
                                 f"Otherwise, provide the prerequisites directly."
            )

        # Make API call
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": enhanced_prompt}],
            system=system_prompt,
            max_tokens=1000,
        )

        return self.client.get_text_content(response)

    def _parse_prerequisites(self, response_text: str) -> List[str]:
        """Parse prerequisites from Kimi's response."""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            if "```" in response_text:
                sections = response_text.split("```")
                for section in sections[1::2]:  # Every other section (code blocks)
                    if section.startswith("json"):
                        section = section[4:]
                    try:
                        return json.loads(section.strip())
                    except:
                        continue
            else:
                # Extract JSON array using regex
                match = re.search(r"\[.*?\]", response_text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except:
                        pass

            # Last resort: try to extract quoted strings
            matches = re.findall(r'"([^"]+)"', response_text)
            if matches:
                return matches[:5]  # Limit to 5

            raise ValueError(f"Could not parse prerequisites from: {response_text}")

    # Synchronous wrapper for backwards compatibility
    def explore(self, concept: str, depth: int = 0, verbose: bool = True) -> KnowledgeNode:
        """Synchronous wrapper around explore_async."""
        return asyncio.run(self.explore_async(concept, depth, verbose))


async def demo():
    """Demo the Kimi K2 prerequisite explorer."""
    print("""
======================================================================
   Kimi K2 Prerequisite Explorer
======================================================================

Features:
  * Uses Kimi K2 thinking model from Moonshot AI
  * OpenAI-compatible API format
  * Converts tool calls to verbose instructions when needed
  * Same interface as Claude version for compatibility

Powered by: Kimi K2 (Moonshot AI)
======================================================================
    """)

    explorer = KimiPrerequisiteExplorer(max_depth=3, use_tools=True)

    concept = "quantum field theory"
    print(f"\n{'='*70}")
    print(f"Building knowledge tree for: {concept}")
    print('='*70)

    try:
        tree = await explorer.explore_async(concept, verbose=True)

        print("\n" + '='*70)
        print("Knowledge Tree:")
        print('='*70)
        tree.print_tree()

        # Save to JSON
        output_file = f"knowledge_tree_{concept.replace(' ', '_')}_kimi.json"
        with open(output_file, 'w') as f:
            json.dump(tree.to_dict(), f, indent=2)
        print(f"\nSaved tree to: {output_file}")

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("MOONSHOT_API_KEY"):
        print("[FAIL] Error: MOONSHOT_API_KEY environment variable not set.")
        print("\nPlease set your Moonshot API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: MOONSHOT_API_KEY=your_key_here")
        print("\nGet your API key from: https://platform.moonshot.ai/")
        exit(1)

    asyncio.run(demo())

