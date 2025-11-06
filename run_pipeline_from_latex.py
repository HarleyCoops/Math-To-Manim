#!/usr/bin/env python3
"""
Run the Kimi K2 agent pipeline on a LaTeX document.

Extracts concepts from LaTeX and processes them through the Kimi K2 pipeline.
"""

import os
import sys
import asyncio
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Add paths for Kimi K2 imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "KimiK2Thinking"))

load_dotenv()

from agents.enrichment_chain import KimiEnrichmentPipeline
from agents.prerequisite_explorer_kimi import KimiPrerequisiteExplorer
from kimi_client import KimiClient


def extract_text_from_latex(latex_content: str) -> str:
    """
    Extract readable text from LaTeX content, removing LaTeX commands.
    
    Args:
        latex_content: Raw LaTeX document content
        
    Returns:
        Cleaned text content
    """
    # Remove LaTeX commands but keep content
    text = latex_content
    
    # Remove document structure commands
    text = re.sub(r'\\documentclass.*?\n', '', text)
    text = re.sub(r'\\usepackage.*?\n', '', text)
    text = re.sub(r'\\geometry.*?\n', '', text)
    text = re.sub(r'\\hypersetup.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\title\{.*?\}', '', text)
    text = re.sub(r'\\author\{.*?\}', '', text)
    text = re.sub(r'\\date\{.*?\}', '', text)
    text = re.sub(r'\\maketitle', '', text)
    text = re.sub(r'\\tableofcontents', '', text)
    text = re.sub(r'\\newpage', '\n\n', text)
    
    # Remove sectioning commands but keep titles
    text = re.sub(r'\\section\*?\{([^}]+)\}', r'\n\n## \1\n\n', text)
    text = re.sub(r'\\subsection\*?\{([^}]+)\}', r'\n\n### \1\n\n', text)
    text = re.sub(r'\\paragraph\{([^}]+)\}', r'\n\n**\1**\n\n', text)
    
    # Remove math environments but keep content markers
    text = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'[EQUATION]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{align\}(.*?)\\end\{align\}', r'[EQUATION]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\\item\s+', '- ', text)
    
    # Remove inline math but keep markers
    text = re.sub(r'\$([^$]+)\$', r'[MATH: \1]', text)
    text = re.sub(r'\\\(([^\)]+)\\\)', r'[MATH: \1]', text)
    
    # Remove labels and references
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\eqref\{[^}]+\}', '[equation]', text)
    text = re.sub(r'\\ref\{[^}]+\}', '[reference]', text)
    
    # Remove remaining LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)  # Simple commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remaining commands
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def extract_main_concepts_from_text(text: str, kimi_client: KimiClient) -> str:
    """
    Use Kimi K2 to extract the main concept from the text.
    
    Args:
        text: Extracted text content
        kimi_client: Kimi K2 client
        
    Returns:
        Main concept string
    """
    # Create a prompt to extract the main concept
    prompt = f"""From the following document about Quantum Electrodynamics, identify the MAIN mathematical/physical concept that should be explained in an animation.

Document content:
{text[:3000]}

Please identify the single most important concept that encompasses the entire document. Return only the concept name, nothing else."""

    try:
        response = kimi_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        
        main_concept = kimi_client.get_text_content(response).strip()
        return main_concept
    except Exception as e:
        print(f"Warning: Could not extract concept with Kimi K2: {e}")
        # Fallback: use first section title
        lines = text.split('\n')
        for line in lines:
            if line.startswith('##'):
                return line.replace('##', '').strip()
        return "Quantum Electrodynamics"


async def main():
    """Main async function"""
    
    # Check for LaTeX file path argument or use provided content
    if len(sys.argv) > 1:
        latex_path = Path(sys.argv[1])
        if latex_path.exists():
            print(f"Reading LaTeX file: {latex_path}")
            with open(latex_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
        else:
            print(f"ERROR: File not found: {latex_path}")
            sys.exit(1)
    else:
        # Use the provided LaTeX content directly
        print("Using provided LaTeX content from command")
        latex_content = """\\documentclass[12pt]{article}
\\usepackage{amsmath, amssymb, amsfonts}
\\title{A Deeper Dive into the Mathematics of Quantum Electrodynamics}
\\begin{document}
\\maketitle
\\section*{Introduction}
Quantum Electrodynamics (QED) is the relativistic quantum field theory of the electromagnetic interaction.
\\section{Minkowski Spacetime and the Relativistic Metric}
The stage for relativistic physics, including QED, is Minkowski spacetime.
\\section{Classical Electromagnetism: Maxwell's Equations}
QED builds upon classical electrodynamics, described by Maxwell's equations.
\\section{The Lagrangian Density for Quantum Electrodynamics}
The dynamics of a quantum field theory are encoded in its Lagrangian density.
\\section{Gauge Invariance}
QED is a U(1) gauge theory.
\\section{Feynman Diagrams and Perturbative QED}
Feynman diagrams are a pictorial representation of terms in the perturbative expansion.
\\section{Running of the Coupling Constant and Renormalization}
The change in the coupling strength with energy scale is described by the Renormalization Group Equations.
\\end{document}"""
    
    # Check API key
    if not os.getenv("MOONSHOT_API_KEY"):
        print("[ERROR] MOONSHOT_API_KEY not set!")
        print("\nPlease set it in your .env file:")
        print("  MOONSHOT_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 70)
    print("LATEX TO MANIM PIPELINE - KIMI K2")
    print("=" * 70)
    
    # Step 1: Extract text from LaTeX
    print("\n" + "=" * 70)
    print("STEP 1: EXTRACTING TEXT FROM LATEX")
    print("=" * 70)
    try:
        extracted_text = extract_text_from_latex(latex_content)
        print(f"\nExtracted {len(extracted_text)} characters")
        print(f"Preview:\n{extracted_text[:500]}...")
    except Exception as e:
        print(f"\nERROR: Failed to extract text from LaTeX: {e}")
        sys.exit(1)
    
    # Step 2: Extract main concept using Kimi K2
    print("\n" + "=" * 70)
    print("STEP 2: EXTRACTING MAIN CONCEPT (KIMI K2)")
    print("=" * 70)
    try:
        kimi_client = KimiClient()
        main_concept = extract_main_concepts_from_text(extracted_text, kimi_client)
        print(f"\nMain concept: {main_concept}")
    except Exception as e:
        print(f"\nWarning: Could not extract concept: {e}")
        main_concept = "Quantum Electrodynamics"
        print(f"Using fallback: {main_concept}")
    
    # Step 3: Build knowledge tree with Kimi K2
    print("\n" + "=" * 70)
    print("STEP 3: BUILDING KNOWLEDGE TREE (KIMI K2)")
    print("=" * 70)
    
    try:
        explorer = KimiPrerequisiteExplorer(max_depth=4, use_tools=False)
        tree = await explorer.explore_async(main_concept, verbose=True)
        
        # Print tree
        print("\n" + "=" * 70)
        print("KNOWLEDGE TREE:")
        print("=" * 70)
        tree.print_tree()

    except Exception as e:
        print(f"\nERROR: Pipeline failed during prerequisite discovery: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Enrich tree (math, visuals, narrative)
    print("\n" + "=" * 70)
    print("STEP 4: ENRICHING KNOWLEDGE TREE (KIMI K2)")
    print("=" * 70)

    try:
        enrichment_pipeline = KimiEnrichmentPipeline()
        enrichment_result = await enrichment_pipeline.run_async(tree)
        tree = enrichment_result.enriched_tree
        narrative_result = enrichment_result.narrative

        print(f"\n✓ Enrichment complete: {len(tree.equations or [])} equations at root")
        print(f"  Narrative length: {len(narrative_result.verbose_prompt)} characters")
        print(f"  Scene count: {narrative_result.scene_count}")

    except Exception as e:
        print(f"\nERROR: Enrichment stage failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Save results
    try:
        # Save results
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        safe_name = "".join(c if c.isalnum() else "_" for c in main_concept[:50])
        
        # Save tree as JSON
        tree_file = output_dir / f"{safe_name}_kimi_tree.json"
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree.to_dict(), f, indent=2)
        print(f"\nSaved knowledge tree to: {tree_file}")
        
        # Save extracted text
        text_file = output_dir / f"{safe_name}_extracted_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"Saved extracted text to: {text_file}")

        # Save narrative
        narrative_file = output_dir / f"{safe_name}_narrative.txt"
        with open(narrative_file, 'w', encoding='utf-8') as f:
            f.write(narrative_result.verbose_prompt)
        print(f"Saved narrative prompt to: {narrative_file}")
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        print(f"\nMain Concept: {main_concept}")
        print(f"Tree Depth: {tree.depth}")
        print(f"\nOutput saved to:")
        print(f"  - {tree_file}")
        print(f"  - {text_file}")
        print(f"  - {narrative_file}")

    except Exception as e:
        print(f"\nERROR: Failed to persist pipeline outputs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

