#!/usr/bin/env python3
"""
10-minute live demo runner for Math-To-Manim.

Flow:
1. Take a simple natural-language prompt.
2. Run the Claude reverse-knowledge-tree multi-agent pipeline.
3. Save the generated knowledge tree, verbose prompt, and Manim Python file.
4. Optionally render the generated scene to an MP4 with Manim.

Example:
    python3 scripts/demo_10_minute_pipeline.py \
      --prompt "Explain the Pythagorean theorem with a visual proof" \
      --depth 2
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure repo root is importable when the script is run from any directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_PROMPT = "Explain the Pythagorean theorem with a visual proof"

STYLE_BRIEFS = {
    "basic": "",
    "cinematic": """
Make this feel like a polished 3Blue1Brown-style conference demo rather than a plain slide deck.
Use one cohesive dark-background palette, large readable labels, opacity layering, camera-like staging,
and one memorable visual aha moment. Show geometry before algebra. Include short pauses after reveals.
Use robust Manim CE primitives that are likely to render on the first try.
""".strip(),
    "experimental": """
Use a creative visual metaphor or SCAMPER-style twist while staying mathematically correct.
Start with an intuitive spatial image, transform it into the formal equation, and end with a satisfying
visual payoff. Prefer dynamic transformations, tracing, braces, highlighted regions, and staged reveals
over static text. Keep it renderable with standard Manim CE v0.19+.
""".strip(),
}


class _SceneClassFinder(ast.NodeVisitor):
    """Find the first Manim Scene/ThreeDScene class in generated code."""

    def __init__(self) -> None:
        self.scene_name: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802 - ast API name
        if self.scene_name:
            return
        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        if any(name.endswith("Scene") for name in base_names):
            self.scene_name = node.name
            return
        self.generic_visit(node)


def find_scene_name(code_file: Path) -> Optional[str]:
    """Return the first class inheriting from Scene/ThreeDScene in a Python file."""
    try:
        tree = ast.parse(code_file.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        print(f"[WARN] Generated code has a syntax error, cannot infer scene name: {exc}")
        return None
    finder = _SceneClassFinder()
    finder.visit(tree)
    return finder.scene_name


def find_rendered_mp4(scene_name: str, quality: str) -> Optional[Path]:
    """Find the newest MP4 produced by Manim for the given scene."""
    quality_dir = {
        "l": "480p15",
        "m": "720p30",
        "h": "1080p60",
        "p": "1440p60",
        "k": "2160p60",
    }.get(quality, "480p15")

    candidates = list((REPO_ROOT / "media" / "videos").glob(f"**/{quality_dir}/{scene_name}.mp4"))
    if not candidates:
        candidates = list((REPO_ROOT / "media" / "videos").glob(f"**/{scene_name}.mp4"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Run a quick Math-To-Manim multi-agent demo and render an MP4.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Simple natural-language animation prompt.")
    parser.add_argument("--output-dir", default="output/demo_10_minute", help="Directory for generated artifacts.")
    parser.add_argument("--depth", type=int, default=2, help="Knowledge-tree depth. Use 2 for live demos, 3-4 for richer output.")
    parser.add_argument("--model", default=os.getenv("CLAUDE_MODEL", "claude-opus-4-7"), help="Claude model ID to use for all Anthropic agent calls.")
    parser.add_argument("--style", choices=sorted(STYLE_BRIEFS), default="cinematic", help="Visual ambition for the generated Manim code.")
    parser.add_argument("--scene", default=None, help="Override generated Manim scene class name.")
    parser.add_argument("--quality", choices=["l", "m", "h", "p", "k"], default="l", help="Manim quality flag suffix. l = quick preview.")
    parser.add_argument("--threejs", action="store_true", help="Also generate an interactive Three.js artifact for the concept.")
    parser.add_argument("--no-render", action="store_true", help="Only generate code; skip Manim rendering.")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv
        from src.agents.orchestrator import ReverseKnowledgeTreeOrchestrator
    except ModuleNotFoundError as exc:
        print(f"[FAIL] Missing Python dependency: {exc.name}")
        print("Install the project first, for example:")
        print('  python3 -m venv .venv && source .venv/bin/activate')
        print('  pip install -e ".[dev,claude,web]"')
        return 1

    load_dotenv(REPO_ROOT / ".env")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] ANTHROPIC_API_KEY is not set. Add it to .env or export it before the demo.")
        return 1

    output_dir = (REPO_ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("MATH-TO-MANIM 10-MINUTE MULTI-AGENT DEMO")
    print("=" * 78)
    print(f"Prompt:     {args.prompt}")
    print(f"Model:      {args.model}")
    print(f"Style:      {args.style}")
    print(f"Tree depth: {args.depth}")
    print(f"Artifacts:  {output_dir}")
    print("\nWatch the live log below: each STEP banner is one agent stage.\n")

    orchestrator = ReverseKnowledgeTreeOrchestrator(
        model=args.model,
        max_tree_depth=args.depth,
        enable_code_generation=True,
        enable_threejs_generation=args.threejs,
        enable_atlas=False,
        creative_brief=STYLE_BRIEFS[args.style] or None,
    )
    result = orchestrator.process(user_input=args.prompt, output_dir=str(output_dir))

    safe_concept = "".join(c if c.isalnum() else "_" for c in result.target_concept)
    code_file = output_dir / f"{safe_concept}_animation.py"
    tree_file = output_dir / f"{safe_concept}_tree.json"
    prompt_file = output_dir / f"{safe_concept}_prompt.txt"

    print("\n" + "=" * 78)
    print("GENERATED ARTIFACTS")
    print("=" * 78)
    print(f"Knowledge tree: {tree_file}")
    print(f"Verbose prompt: {prompt_file}")
    print(f"Manim code:     {code_file}")

    if args.no_render:
        print("\nSkipping render because --no-render was supplied.")
        return 0

    scene_name = args.scene or find_scene_name(code_file)
    if not scene_name:
        print("\n[WARN] Could not infer the scene class. Open the Manim code and render manually, e.g.:")
        print(f"  manim -pq{args.quality} {code_file} SceneName")
        return 2

    print("\n" + "=" * 78)
    print("RENDERING MP4 WITH MANIM")
    print("=" * 78)

    # Prefer the current Python interpreter so Windows installs where `python -m manim`
    # works but the `manim.exe` console script is not on PATH still render correctly.
    cmd = [sys.executable, "-m", "manim", f"-q{args.quality}", str(code_file), scene_name]
    display_cmd = f'"{sys.executable}" -m manim -q{args.quality} "{code_file}" {scene_name}'
    print("$ " + display_cmd)
    completed = subprocess.run(cmd, cwd=REPO_ROOT)
    if completed.returncode != 0:
        print("\n[FAIL] Manim render failed. Inspect the generated code above and rerun:")
        print(f'  "{sys.executable}" -m manim -pq{args.quality} "{code_file}" {scene_name}')
        return completed.returncode

    mp4_path = find_rendered_mp4(scene_name, args.quality)
    print("\n" + "=" * 78)
    print("DEMO COMPLETE")
    print("=" * 78)
    if mp4_path:
        print(f"Final MP4: {mp4_path}")
    else:
        print("Render succeeded, but the MP4 path could not be auto-detected. Check media/videos/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
