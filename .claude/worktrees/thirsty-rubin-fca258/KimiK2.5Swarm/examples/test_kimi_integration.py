"""Test script for Kimi K2 integration.

This script demonstrates how to use the Kimi K2 refactored agents.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directories to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import modules directly
from agents.prerequisite_explorer_kimi import (
    KimiPrerequisiteExplorer,
    KnowledgeNode
)
from kimi_client import KimiClient
from tool_adapter import ToolAdapter


async def test_basic_api_call():
    """Test basic Kimi K2 API call."""
    print("\n" + "="*70)
    print("Test 1: Basic API Call")
    print("="*70)

    client = KimiClient()

    response = client.chat_completion(
        messages=[
            {"role": "user", "content": "What is 2+2? Answer in one sentence."}
        ],
        max_tokens=50,
    )

    print(f"Response: {client.get_text_content(response)}")
    print(f"Usage: {response.get('usage', {})}")


async def test_prerequisite_explorer():
    """Test the prerequisite explorer."""
    print("\n" + "="*70)
    print("Test 2: Prerequisite Explorer")
    print("="*70)

    explorer = KimiPrerequisiteExplorer(max_depth=2, use_tools=False)

    concept = "special relativity"
    print(f"\nExploring prerequisites for: {concept}")
    print("-" * 70)

    try:
        tree = await explorer.explore_async(concept, verbose=True)

        print("\n" + "-" * 70)
        print("Knowledge Tree:")
        print("-" * 70)
        tree.print_tree()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


async def test_tool_adapter():
    """Test tool adapter functionality."""
    print("\n" + "="*70)
    print("Test 3: Tool Adapter")
    print("="*70)

    adapter = ToolAdapter()

    # Example tool definition
    example_tool = {
        "type": "function",
        "function": {
            "name": "get_cached_prerequisites",
            "description": "Retrieve previously discovered prerequisites for a concept",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                        "description": "The concept to look up"
                    }
                },
                "required": ["concept"]
            }
        }
    }

    instruction = adapter.tool_to_instruction(example_tool)
    print("\nTool converted to instruction:")
    print("-" * 70)
    print(instruction)

    # Test verbose prompt creation
    base_prompt = "What are the prerequisites for quantum mechanics?"
    verbose_prompt = adapter.create_verbose_prompt(
        base_prompt,
        tools=[example_tool],
        tool_call_context="We want to check cache first, then provide prerequisites."
    )
    print("\n\nVerbose prompt:")
    print("-" * 70)
    print(verbose_prompt[:500] + "..." if len(verbose_prompt) > 500 else verbose_prompt)


async def main():
    """Run all tests."""
    print("""
======================================================================
          Kimi K2 Integration Test Suite
======================================================================
    """)

    # Check API key
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        print("[ERROR] MOONSHOT_API_KEY not set!")
        print("\nPlease set it in your .env file:")
        print("  MOONSHOT_API_KEY=your_key_here")
        return
    
    # Debug: Show API key status (masked)
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"[DEBUG] API Key loaded: {masked_key}")
    print(f"[DEBUG] API Key length: {len(api_key)}")

    # Run tests
    try:
        await test_basic_api_call()
        await test_tool_adapter()
        await test_prerequisite_explorer()

        print("\n" + "="*70)
        print("All tests completed!")
        print("="*70)

    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

