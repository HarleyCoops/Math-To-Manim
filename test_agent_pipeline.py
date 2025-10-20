#!/usr/bin/env python3
"""
Test script for the complete agent pipeline

This script tests the full Reverse Knowledge Tree approach:
1. ConceptAnalyzer
2. PrerequisiteExplorer
3. MathematicalEnricher
4. VisualDesigner
5. NarrativeComposer
6. Complete orchestrator

Run with: python test_agent_pipeline.py
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents import (
    ConceptAnalyzer,
    PrerequisiteExplorer,
    MathematicalEnricher,
    VisualDesigner,
    NarrativeComposer,
    ReverseKnowledgeTreeOrchestrator
)

load_dotenv()


def test_individual_agents():
    """Test each agent individually"""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                  TESTING INDIVIDUAL AGENTS                       ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    user_input = "Explain the Pythagorean theorem"

    # Test 1: ConceptAnalyzer
    print("\n" + "="*70)
    print("TEST 1: ConceptAnalyzer")
    print("="*70)
    analyzer = ConceptAnalyzer()
    analysis = analyzer.analyze(user_input)
    print(f"✓ Core concept: {analysis['core_concept']}")
    print(f"  Domain: {analysis['domain']}")
    print(f"  Level: {analysis['level']}")
    assert 'core_concept' in analysis
    assert 'domain' in analysis
    print("✅ ConceptAnalyzer PASSED")

    # Test 2: PrerequisiteExplorer
    print("\n" + "="*70)
    print("TEST 2: PrerequisiteExplorer")
    print("="*70)
    explorer = PrerequisiteExplorer(max_depth=2)
    tree = explorer.explore(analysis['core_concept'])
    print(f"✓ Built tree for: {tree.concept}")
    tree.print_tree()
    assert tree.concept == analysis['core_concept']
    print("✅ PrerequisiteExplorer PASSED")

    # Test 3: MathematicalEnricher
    print("\n" + "="*70)
    print("TEST 3: MathematicalEnricher")
    print("="*70)
    enricher = MathematicalEnricher()
    enriched = enricher.enrich_tree(tree)
    print(f"✓ Enriched tree with math content")
    assert enriched.equations is not None or len(enriched.prerequisites) > 0
    print(f"  Equations for {enriched.concept}: {len(enriched.equations or [])} found")
    print("✅ MathematicalEnricher PASSED")

    # Test 4: VisualDesigner
    print("\n" + "="*70)
    print("TEST 4: VisualDesigner")
    print("="*70)
    designer = VisualDesigner()
    designed = designer.design_tree(enriched)
    print(f"✓ Designed visual specs")
    assert designed.visual_spec is not None
    print(f"  Visual elements: {designed.visual_spec.get('elements', [])[:3]}")
    print("✅ VisualDesigner PASSED")

    # Test 5: NarrativeComposer
    print("\n" + "="*70)
    print("TEST 5: NarrativeComposer")
    print("="*70)
    composer = NarrativeComposer()
    narrative = composer.compose(designed)
    print(f"✓ Composed narrative")
    print(f"  Prompt length: {len(narrative.verbose_prompt)} chars")
    print(f"  Scene count: {narrative.scene_count}")
    assert len(narrative.verbose_prompt) > 500  # Should be verbose!
    print("✅ NarrativeComposer PASSED")

    print("\n" + "="*70)
    print("✅ ALL INDIVIDUAL AGENT TESTS PASSED!")
    print("="*70)


def test_orchestrator():
    """Test the complete orchestrator pipeline"""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                  TESTING COMPLETE ORCHESTRATOR                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    orchestrator = ReverseKnowledgeTreeOrchestrator(
        max_tree_depth=2,  # Keep it small for testing
        enable_code_generation=True
    )

    user_input = "Visualize Newton's second law"

    print(f"\n📝 Testing with input: \"{user_input}\"")

    result = orchestrator.process(
        user_input=user_input,
        output_dir="test_output"
    )

    # Validate result
    print("\n" + "="*70)
    print("VALIDATING RESULTS")
    print("="*70)

    assert result.target_concept is not None, "Missing target concept"
    print(f"✓ Target concept: {result.target_concept}")

    assert result.knowledge_tree is not None, "Missing knowledge tree"
    print(f"✓ Knowledge tree: {len(str(result.knowledge_tree))} chars")

    assert len(result.verbose_prompt) > 500, "Prompt too short"
    print(f"✓ Verbose prompt: {len(result.verbose_prompt)} chars")

    if result.manim_code:
        assert "from manim import" in result.manim_code, "Invalid Manim code"
        print(f"✓ Manim code: {len(result.manim_code)} chars")

    assert len(result.concept_order) > 0, "Empty concept order"
    print(f"✓ Concept order: {' → '.join(result.concept_order)}")

    print("\n✅ ORCHESTRATOR TEST PASSED!")


def test_quick_run():
    """Quick test with minimal depth"""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                      QUICK INTEGRATION TEST                      ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    orchestrator = ReverseKnowledgeTreeOrchestrator(
        max_tree_depth=1,  # Very shallow for quick test
        enable_code_generation=False  # Skip code gen for speed
    )

    test_prompts = [
        "Explain velocity",
        "Show the quadratic formula"
    ]

    for prompt in test_prompts:
        print(f"\n📝 Testing: \"{prompt}\"")
        result = orchestrator.process(prompt, output_dir="test_output")
        print(f"   ✓ Generated {len(result.verbose_prompt)} char prompt")
        print(f"   ✓ {result.scene_count} scenes")

    print("\n✅ QUICK INTEGRATION TEST PASSED!")


def main():
    """Run all tests"""

    # Verify API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set!")
        print("\nPlease create a .env file with:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return 1

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          MATH-TO-MANIM AGENT PIPELINE TEST SUITE                 ║
║                                                                   ║
║  Testing the complete Reverse Knowledge Tree implementation      ║
║  Powered by Claude Sonnet 4.5 + Claude Agent SDK                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run test suites
        print("\n🧪 Starting tests...\n")

        # Test 1: Individual agents
        test_individual_agents()

        # Test 2: Complete orchestrator
        test_orchestrator()

        # Test 3: Quick integration
        test_quick_run()

        # Final summary
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        print("\nThe Reverse Knowledge Tree agent pipeline is working correctly!")
        print("\nWhat was tested:")
        print("  ✓ ConceptAnalyzer - parsing user intent")
        print("  ✓ PrerequisiteExplorer - building knowledge trees")
        print("  ✓ MathematicalEnricher - adding equations")
        print("  ✓ VisualDesigner - designing animations")
        print("  ✓ NarrativeComposer - generating verbose prompts")
        print("  ✓ ReverseKnowledgeTreeOrchestrator - full pipeline")
        print("\nYou can now use the agents to generate Manim animations!")
        print("\nNext steps:")
        print("  1. Try: python src/agents/orchestrator.py")
        print("  2. Or import and use in your own code")
        print("  3. Check test_output/ for generated files")

        return 0

    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED!")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
