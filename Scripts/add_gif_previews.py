#!/usr/bin/env python3
"""
Add GIF previews to category README files.

This script scans for GIF files in example directories and adds them to the
category README.md files with proper formatting.

Usage:
    python scripts/add_gif_previews.py [--category <name>]
"""

import os
import argparse
from pathlib import Path


def find_gifs_in_directory(directory):
    """
    Find all GIF files in a directory.

    Args:
        directory: Path to search

    Returns:
        List of (gif_file, python_file) tuples
    """
    gifs = []
    for gif_path in Path(directory).glob("*.gif"):
        # Try to find corresponding Python file
        py_file = gif_path.with_suffix('.py')
        if py_file.exists():
            gifs.append((gif_path.name, py_file.name))
        else:
            gifs.append((gif_path.name, None))
    return sorted(gifs)


def generate_readme_content(category_path, gifs):
    """
    Generate README content with GIF previews.

    Args:
        category_path: Path to the category directory
        gifs: List of (gif_file, python_file) tuples

    Returns:
        README content string
    """
    category_name = category_path.name.replace('_', ' ').title()

    content = f"# {category_name} Examples\n\n"
    content += f"This directory contains {len(gifs)} animation{'s' if len(gifs) != 1 else ''} "
    content += f"related to {category_name.lower()}.\n\n"

    if gifs:
        content += "## Animations\n\n"

        for gif_file, py_file in gifs:
            scene_name = gif_file.replace('.gif', '')
            content += f"### {scene_name}\n\n"

            if py_file:
                content += f"**Source**: [`{py_file}`]({py_file})\n\n"

            content += f"![{scene_name}]({gif_file})\n\n"

    content += "---\n\n"
    content += "## Running These Examples\n\n"
    content += "```bash\n"
    content += f"# Render as video\n"
    content += f"manim -pql <filename>.py <SceneName>\n\n"
    content += f"# Render as GIF\n"
    content += f"manim -pql --format gif <filename>.py <SceneName>\n"
    content += "```\n\n"
    content += "**Quality options**: `-ql` (low/fast), `-qm` (medium), `-qh` (high), `-qk` (4K)\n\n"

    return content


def update_category_readme(category_path, dry_run=False):
    """
    Update README.md in a category directory with GIF previews.

    Args:
        category_path: Path to the category directory
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    gifs = find_gifs_in_directory(category_path)

    if not gifs:
        print(f"  No GIFs found in {category_path}")
        return False

    readme_path = category_path / "README.md"
    content = generate_readme_content(category_path, gifs)

    if dry_run:
        print(f"  [DRY RUN] Would update {readme_path}")
        print(f"  Found {len(gifs)} GIF(s)")
        return True

    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {readme_path} with {len(gifs)} GIF(s)")
        return True
    except Exception as e:
        print(f"  ✗ Failed to update {readme_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Add GIF previews to category README files"
    )
    parser.add_argument(
        "--category", "-c",
        help="Only update specific category (e.g., physics/quantum)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Add GIF Previews to README Files")
    print("=" * 60)
    print()

    examples_path = Path("examples")

    if not examples_path.exists():
        print("Error: examples/ directory not found")
        return

    # Find all directories with README.md files
    if args.category:
        # Specific category
        category_path = examples_path / args.category
        if not category_path.exists():
            print(f"Error: Category not found: {args.category}")
            return

        categories = [category_path]
    else:
        # All categories
        categories = []
        for item in examples_path.rglob("README.md"):
            if item.parent != examples_path:  # Skip root examples README
                categories.append(item.parent)

    print(f"Found {len(categories)} categor{'ies' if len(categories) != 1 else 'y'}\n")

    updated = 0
    skipped = 0

    for category_path in sorted(categories):
        relative = category_path.relative_to(examples_path)
        print(f"Processing: {relative}")

        if update_category_readme(category_path, dry_run=args.dry_run):
            updated += 1
        else:
            skipped += 1

        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Categories processed: {len(categories)}")
    print(f"READMEs updated: {updated}")
    print(f"Skipped (no GIFs): {skipped}")

    if args.dry_run:
        print("\nThis was a dry run. No files were modified.")


if __name__ == "__main__":
    main()
