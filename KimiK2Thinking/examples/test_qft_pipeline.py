#!/usr/bin/env python3
"""
Test the Kimi K2 pipeline with a QFT animation prompt.

This script extracts concepts from the prompt, builds prerequisite trees,
runs enrichment, and reports any failures.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "KimiK2Thinking"))

load_dotenv()

from KimiK2Thinking.agents.enrichment_chain import KimiEnrichmentPipeline
from KimiK2Thinking.agents.prerequisite_explorer_kimi import (
    KimiPrerequisiteExplorer,
    KnowledgeNode,
)


QFT_PROMPT = r"""Begin by slowly fading in a panoramic star field backdrop to set a cosmic stage. As the camera orients itself to reveal a three-dimensional axis frame, introduce a large title reading 'Quantum Field Theory: 

A Journey into the Electromagnetic Interaction,' written in bold, glowing text at the center of the screen. The title shrinks and moves into the upper-left corner, making room for a rotating wireframe representation of 4D Minkowski spacetime—though rendered in 3D for clarity—complete with a light cone that stretches outward. While this wireframe slowly rotates, bring in color-coded equations of the relativistic metric, such as 

ds2=−c2dt2+dx2+dy2+dz2ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2, with each component highlighted in a different hue to emphasize the negative time component and positive spatial components.



Next, zoom the camera into the wireframe's origin to introduce the basic concept of a quantum field. Show a ghostly overlay of undulating plane waves in red and blue, symbolizing an electric field and a magnetic field respectively, oscillating perpendicularly in sync. Label these fields as E⃗\vec{E} and B⃗\vec{B}, placing them on perpendicular axes with small rotating arrows that illustrate their directions over time. Simultaneously, use a dynamic 3D arrow to demonstrate that the wave propagates along the z-axis. 



As the wave advances, display a short excerpt of Maxwell's equations, morphing from their classical form in vector calculus notation to their elegant, relativistic compact form: ∂μFμν=μ0Jν\partial_\mu F^{\mu \nu} = \mu_0 J^\nu. Animate each transformation by dissolving and reassembling the symbols, underscoring the transition from standard form to four-vector notation.



Then, shift the focus to the Lagrangian density for quantum electrodynamics (QED):

LQED=ψˉ(iγμDμ−m)ψ−14FμνFμν.\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}.



Project this equation onto a semi-transparent plane hovering in front of the wireframe spacetime, with each symbol color-coded: the Dirac spinor ψ\psi in orange, the covariant derivative DμD_\mu in green, the gamma matrices γμ\gamma^\mu in bright teal, and the field strength tensor FμνF_{\mu\nu} in gold. Let these terms gently pulse to indicate they are dynamic fields in spacetime, not just static quantities. 



While the Lagrangian is on screen, illustrate the gauge invariance by showing a quick animation where ψ\psi acquires a phase factor eiα(x)e^{i \alpha(x)}, while the gauge field transforms accordingly. Arrows and short textual callouts appear around the equation to explain how gauge invariance enforces charge conservation.

Next, pan the camera over to a large black background to present a simplified Feynman diagram. Show two electron lines approaching from the left and right, exchanging a wavy photon line in the center. 



The electron lines are labeled e−e^- in bright blue, and the photon line is labeled γ\gamma in yellow. Subtitles and small pop-up text boxes narrate how this basic vertex encapsulates the electromagnetic interaction between charged fermions, highlighting that the photon is the force carrier. Then, animate the coupling constant α≈1137\alpha \approx \frac{1}{137} flashing above the diagram, gradually evolving from a numeric approximation to the symbolic form α=e24πϵ0ℏc\alpha = \frac{e^2}{4 \pi \epsilon_0 \hbar c}.



Afterward, transition to a 2D graph that plots the running of the coupling constant α\alpha with respect to energy scale, using the renormalization group flow. As the graph materializes, a vertical axis labeled 'Coupling Strength' and a horizontal axis labeled 'Energy Scale' come into view, each sporting major tick marks and numerical values. The curve gently slopes upward, illustrating how α\alpha grows at higher energies, with dynamic markers along the curve to indicate different experimental data points. Meanwhile, short textual captions in the corners clarify that this phenomenon arises from virtual particle-antiparticle pairs contributing to vacuum polarization.



In the final sequence, zoom back out to reveal a cohesive collage of all elements: the rotating spacetime grid, the undulating electromagnetic fields, the QED Lagrangian, and the Feynman diagram floating in the foreground. Fade in an overarching summary text reading 'QED: Unifying Light and Matter Through Gauge Theory,' emphasized by a halo effect. The camera then slowly pulls away, letting the cosmic background re-emerge until each component gracefully dissolves, ending on a single star field reminiscent of the opening shot. A concluding subtitle, 'Finis,' appears, marking the animation's closure and prompting reflection on how fundamental quantum field theory is in describing our universe."""


def extract_key_concepts(prompt: str) -> List[str]:
    """Extract key physics/math concepts from the prompt."""
    concepts = [
        "quantum field theory",
        "Minkowski spacetime",
        "relativistic metric",
        "quantum field",
        "Maxwell's equations",
        "quantum electrodynamics",
        "QED Lagrangian",
        "Dirac spinor",
        "gauge invariance",
        "Feynman diagram",
        "renormalization group",
        "vacuum polarization",
    ]
    return concepts


async def test_pipeline():
    """Test the full pipeline with QFT concepts."""
    print("=" * 70)
    print("TESTING KIMI K2 PIPELINE WITH QFT PROMPT")
    print("=" * 70)
    
    # Extract concepts
    concepts = extract_key_concepts(QFT_PROMPT)
    print(f"\nExtracted {len(concepts)} key concepts:")
    for i, concept in enumerate(concepts, 1):
        print(f"  {i}. {concept}")
    
    # Build prerequisite trees for main concepts
    print("\n" + "=" * 70)
    print("STAGE 1: Building Prerequisite Trees")
    print("=" * 70)
    
    explorer = KimiPrerequisiteExplorer(max_depth=3, use_tools=True)
    trees = {}
    failures = []
    
    # Focus on the main concept: quantum field theory
    main_concept = "quantum field theory"
    print(f"\nBuilding tree for: {main_concept}")
    
    try:
        tree = await explorer.explore_async(main_concept, verbose=True)
        trees[main_concept] = tree
        print(f"\n[OK] Successfully built tree for {main_concept}")
        print(f"  Tree depth: {tree.depth}")
        print(f"  Total nodes: {count_nodes(tree)}")
    except Exception as e:
        print(f"\n[FAIL] Failed to build tree for {main_concept}: {e}")
        failures.append(("prerequisite_exploration", main_concept, str(e)))
        import traceback
        traceback.print_exc()
        return
    
    # Save tree
    tree_file = Path("output") / "qft_test_tree.json"
    tree_file.parent.mkdir(exist_ok=True)
    with tree_file.open("w") as f:
        json.dump(tree.to_dict(), f, indent=2)
    print(f"\n[OK] Saved tree to {tree_file}")
    
    # Run enrichment pipeline
    print("\n" + "=" * 70)
    print("STAGE 2: Running Enrichment Pipeline")
    print("=" * 70)
    
    try:
        pipeline = KimiEnrichmentPipeline()
        print("\nRunning mathematical enrichment...")
        result = await pipeline.run_async(tree)
        
        print(f"\n[OK] Enrichment completed successfully")
        print(f"  Narrative length: {len(result.narrative.verbose_prompt)} characters")
        print(f"  Total duration: {result.narrative.total_duration}s")
        print(f"  Scene count: {result.narrative.scene_count}")
        
        # Save enriched tree
        enriched_file = Path("output") / "qft_enriched_tree.json"
        with enriched_file.open("w") as f:
            json.dump(result.enriched_tree.to_dict(), f, indent=2)
        print(f"\n[OK] Saved enriched tree to {enriched_file}")
        
        # Save narrative
        narrative_file = Path("output") / "qft_narrative.txt"
        narrative_file.write_text(result.narrative.verbose_prompt, encoding="utf-8")
        print(f"[OK] Saved narrative to {narrative_file}")
        
        # Check for missing data
        print("\n" + "=" * 70)
        print("STAGE 3: Checking Data Completeness")
        print("=" * 70)
        
        check_node_data(result.enriched_tree, failures)
        
    except Exception as e:
        print(f"\n[FAIL] Failed during enrichment: {e}")
        failures.append(("enrichment", "pipeline", str(e)))
        import traceback
        traceback.print_exc()
    
    # Report failures
    print("\n" + "=" * 70)
    print("FAILURE REPORT")
    print("=" * 70)
    
    if failures:
        print(f"\nFound {len(failures)} failure(s):")
        for stage, concept, error in failures:
            print(f"\n  Stage: {stage}")
            print(f"  Concept: {concept}")
            print(f"  Error: {error}")
    else:
        print("\n[OK] No failures detected!")
    
    print("\n" + "=" * 70)


def count_nodes(node: KnowledgeNode) -> int:
    """Count total nodes in tree."""
    count = 1
    for prereq in node.prerequisites:
        count += count_nodes(prereq)
    return count


def check_node_data(node: KnowledgeNode, failures: List) -> None:
    """Check if node has required data and report issues."""
    issues = []
    
    if not node.equations:
        issues.append("missing equations")
    if not node.definitions:
        issues.append("missing definitions")
    if not node.visual_spec:
        issues.append("missing visual_spec")
    elif isinstance(node.visual_spec, dict):
        if not node.visual_spec.get("visual_description"):
            issues.append("visual_spec missing visual_description")
        if not node.visual_spec.get("animation_description"):
            issues.append("visual_spec missing animation_description")
    
    if issues:
        print(f"\n  [WARN] {node.concept} (depth {node.depth}): {', '.join(issues)}")
        failures.append(("data_check", node.concept, ", ".join(issues)))
    else:
        print(f"  [OK] {node.concept} (depth {node.depth}): complete")
    
    for prereq in node.prerequisites:
        check_node_data(prereq, failures)


if __name__ == "__main__":
    try:
        asyncio.run(test_pipeline())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

