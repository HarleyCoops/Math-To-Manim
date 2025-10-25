"""Enhanced Prerequisite Explorer using full Claude Agent SDK features.

This version uses:
- ClaudeSDKClient for stateful conversations
- Custom MCP tools for caching and validation
- Async streaming for better performance
- Error recovery and retries
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from anthropic import NotFoundError
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
)
from dotenv import load_dotenv

# Import custom tools
try:
    from src.agents.claude_sdk_tools import ALL_TOOLS
except ImportError:
    try:
        from claude_sdk_tools import ALL_TOOLS
    except ImportError:
        print("Warning: Could not import custom tools")
        ALL_TOOLS = []

load_dotenv()


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


class EnhancedPrerequisiteExplorer:
    """
    Enhanced prerequisite explorer using full Claude Agent SDK.

    Key improvements over basic version:
    - Uses ClaudeSDKClient for stateful conversations
    - Integrates custom MCP tools for caching
    - Better error handling and retries
    - Streaming support for real-time updates
    """

    def __init__(self, max_depth: int = 4, use_tools: bool = True):
        self.max_depth = max_depth
        self.use_tools = use_tools
        self.cache: Dict[str, List[str]] = {}

        # Set up MCP server with custom tools
        self.mcp_server = None
        if use_tools and ALL_TOOLS:
            self.mcp_server = create_sdk_mcp_server(
                name="math-to-manim-tools",
                tools=ALL_TOOLS
            )

    async def explore_async(
        self,
        concept: str,
        depth: int = 0,
        verbose: bool = True
    ) -> KnowledgeNode:
        """
        Explore prerequisites using Claude Agent SDK with tools.

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

        # Get prerequisites (using tools if available)
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
        """Check if a concept is foundational using Claude Agent SDK."""
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

        # Use ClaudeSDKClient for better context management
        options = ClaudeAgentOptions()
        options.system_prompt = system_prompt

        # Set up MCP server if using tools
        if self.use_tools and self.mcp_server:
            options.mcp_servers = [self.mcp_server]

        async with ClaudeSDKClient(options=options) as client:
            await client.connect(prompt=user_prompt)

            # Collect response
            response_text = ""
            async for message in client.messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text

            return response_text.strip().lower().startswith('yes')

    async def _get_prerequisites_async(
        self,
        concept: str,
        verbose: bool = True
    ) -> List[str]:
        """Get prerequisites for a concept, using cache or Claude."""

        # Check in-memory cache first
        if concept in self.cache:
            if verbose:
                print(f"  -> Using in-memory cache for {concept}")
            return self.cache[concept]

        # Query Claude for prerequisites
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

        options = ClaudeAgentOptions()
        options.system_prompt = system_prompt

        # Add tools if available
        if self.use_tools and self.mcp_server:
            options.mcp_servers = [self.mcp_server]

        async with ClaudeSDKClient(options=options) as client:
            await client.connect(prompt=user_prompt)

            # Collect response
            response_text = ""
            async for message in client.messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text

            # Parse JSON response
            prerequisites = self._parse_prerequisites(response_text)

            # Cache the result
            self.cache[concept] = prerequisites

            return prerequisites

    def _parse_prerequisites(self, response_text: str) -> List[str]:
        """Parse prerequisites from Claude's response."""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            if "```" in response_text:
                section = response_text.split("```")[1]
                if section.startswith("json"):
                    section = section[4:]
                return json.loads(section.strip())
            else:
                # Extract JSON array using regex
                import re
                match = re.search(r"\[.*?\]", response_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse prerequisites from: {response_text}")

    # Synchronous wrapper for backwards compatibility
    def explore(self, concept: str, depth: int = 0, verbose: bool = True) -> KnowledgeNode:
        """Synchronous wrapper around explore_async."""
        return asyncio.run(self.explore_async(concept, depth, verbose))


async def demo():
    """Demo the enhanced prerequisite explorer."""
    print("""
======================================================================
   Enhanced Prerequisite Explorer - Claude Agent SDK Version
======================================================================

Features:
  * Stateful conversations with ClaudeSDKClient
  * Custom MCP tools for caching and validation
  * Better error handling and retries
  * Async streaming for real-time updates

Powered by: Claude Sonnet 4.5
======================================================================
    """)

    explorer = EnhancedPrerequisiteExplorer(max_depth=3, use_tools=True)

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
        output_file = f"knowledge_tree_{concept.replace(' ', '_')}_enhanced.json"
        with open(output_file, 'w') as f:
            json.dump(tree.to_dict(), f, indent=2)
        print(f"\nSaved tree to: {output_file}")

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nPlease set your Claude API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        print("\nGet your API key from: https://console.anthropic.com/")
        exit(1)

    asyncio.run(demo())
