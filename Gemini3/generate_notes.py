import sys
import os
from dotenv import load_dotenv

# Path setup
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from Gemini3.src.pipeline import run_agent_sync, create_mathematical_enricher, logger

def main():
    load_dotenv()
    
    # Prompt
    prompt = r"""
    ACT AS: An expert mathematics professor and LaTeX typesetter.
    
    TASK: Create a comprehensive, verbose set of Study Notes in LaTeX format (.tex).
    
    TITLE: From Formulas to Topology: The Hidden Geometry of Taylor Series
    
    NARRATIVE ARC TO DOCUMENT:
    1.  **The Standard View**: We often see Taylor Series as just a list of formulas (referencing the 'wall of text' image style with expansions for e^x, sin(x), etc).
    2.  **The Counter-Example**: Introduce the Runge function $f(x) = \frac{1}{1+x^2}$.
    3.  **The Mystery**: It is effectively smooth and perfect on the Real line, yet its Taylor series explodes for $|x| \ge 1$. Why?
    4.  **The Topological Unveiling (The Animation)**:
        *   Describe the 3D rotation into the Complex Plane.
        *   Reveal the "invisible villains": The singularities at $z = \pm i$.
        *   Explain the Convergence Disk: It expands until it hits the singularity.
    5.  **The Geometric Proof**: Show that the radius $R$ is simply the Euclidean distance from the center $z_0$ to the singularity. $R = \sqrt{1^2 + 0^2} = 1$ at the origin.
    
    OUTPUT FORMAT:
    -   Full LaTeX document class (article).
    -   Use `amsmath`, `amssymb`, `geometry`, `hyperref`.
    -   Include a `\maketitle`.
    -   Use `\section`, `\subsection`.
    -   Use `\begin{equation}` for math.
    -   Make it educational, rigorous, yet intuitive.
    -   Do not output markdown code blocks around it if possible, just the LaTeX.
    """
    
    # We use the Mathematical Enricher as it is tuned for Math/LaTeX
    enricher = create_mathematical_enricher()
    
    logger.console.print("[bold blue]Generating LaTeX Study Notes via Gemini...[/bold blue]")
    result = run_agent_sync(enricher, prompt)
    
    # Clean up potential markdown blocks if the model adds them
    clean_result = str(result)
    if clean_result.startswith("```latex"):
        clean_result = clean_result.replace("```latex", "", 1)
    if clean_result.startswith("```tex"):
        clean_result = clean_result.replace("```tex", "", 1)
    if clean_result.endswith("```"):
        clean_result = clean_result[:-3]
    
    output_path = os.path.join(root_dir, "Gemini3", "Taylor_Topology_Notes.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(clean_result.strip())
        
    logger.console.print(f"[bold green]Notes saved to {output_path}[/bold green]")

if __name__ == "__main__":
    main()
