#!/usr/bin/env python3
"""
Run the Kimi K2 enrichment pipeline on an existing knowledge tree JSON file.

This mirrors the Claude orchestrator stages but routes every call through the
Kimi tool-calling implementation added in `agents.enrichment_chain`.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from agents.enrichment_chain import KimiEnrichmentPipeline  # noqa: E402
from agents.prerequisite_explorer_kimi import KnowledgeNode  # noqa: E402


def load_tree(path: Path) -> KnowledgeNode:
    """Load a knowledge tree JSON into KnowledgeNode objects."""

    def _dict_to_node(data: dict) -> KnowledgeNode:
        return KnowledgeNode(
            concept=data["concept"],
            depth=data["depth"],
            is_foundation=data["is_foundation"],
            prerequisites=[_dict_to_node(p) for p in data.get("prerequisites", [])],
            equations=data.get("equations"),
            definitions=data.get("definitions"),
            visual_spec=data.get("visual_spec"),
            narrative=data.get("narrative"),
        )

    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return _dict_to_node(payload)


def save_tree(path: Path, root: KnowledgeNode) -> None:
    """Persist the enriched knowledge tree back to disk."""
    with path.open("w", encoding="utf-8") as fh:
        json.dump(root.to_dict(), fh, indent=2)


async def main_async(tree_path: Path) -> None:
    if not tree_path.exists():
        raise FileNotFoundError(f"Knowledge tree not found: {tree_path}")

    print("=" * 70)
    print("KIMI K2 ENRICHMENT PIPELINE")
    print("=" * 70)
    print(f"\nLoading tree: {tree_path}")

    root = load_tree(tree_path)
    pipeline = KimiEnrichmentPipeline()

    print("\nRunning enrichment chain (math ➜ visuals ➜ narrative)...")
    result = await pipeline.run_async(root)

    save_tree(tree_path, result.enriched_tree)
    print(f"\n✓ Enriched tree written to {tree_path}")

    narrative_file = tree_path.with_name(f"{tree_path.stem}_narrative.txt")
    narrative_file.write_text(result.narrative.verbose_prompt, encoding="utf-8")
    print(f"✓ Narrative prompt written to {narrative_file}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_enrichment_pipeline.py <path_to_tree.json>")
        sys.exit(1)

    tree_path = Path(sys.argv[1])
    try:
        asyncio.run(main_async(tree_path))
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"\n[ERROR] {exc}")
        raise


if __name__ == "__main__":
    main()
