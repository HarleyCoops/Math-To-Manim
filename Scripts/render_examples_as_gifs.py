#!/usr/bin/env python3
"""
Batch render Manim examples as GIFs for repository previews.

This script finds all Manim animation files in the examples/ directory,
renders them as GIFs, and saves them alongside the source files.

Usage:
    python scripts/render_examples_as_gifs.py [options]

Options:
    --quality, -q: Quality level (l=low, m=medium, h=high) [default: l]
    --category, -c: Only render specific category (e.g., physics, mathematics)
    --dry-run: Show what would be rendered without actually rendering
    --max-scenes: Maximum number of scenes to render per file [default: 1]
"""

import os
import subprocess
import argparse
from pathlib import Path
import re


def find_manim_files(examples_dir="examples", category=None):
    """
    Find all Manim Python files in the examples directory.

    Args:
        examples_dir: Root examples directory
        category: Optional category filter (e.g., 'physics', 'mathematics')

    Returns:
        List of (file_path, relative_path) tuples
    """
    examples_path = Path(examples_dir)

    if not examples_path.exists():
        print(f"Error: {examples_dir} directory not found")
        return []

    pattern = f"{examples_dir}/**/*.py"
    if category:
        pattern = f"{examples_dir}/{category}/**/*.py"

    files = []
    for py_file in Path().glob(pattern):
        # Skip __init__.py and README files
        if py_file.name == "__init__.py" or "README" in py_file.name:
            continue

        relative = py_file.relative_to(examples_dir)
        files.append((str(py_file), str(relative)))

    return sorted(files)


def extract_scene_classes(file_path):
    """
    Extract Scene class names from a Manim Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of scene class names
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for class definitions that inherit from Scene
        pattern = r'class\s+(\w+)\s*\([^)]*Scene[^)]*\)'
        matches = re.findall(pattern, content)

        return matches
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return []


def render_as_gif(file_path, scene_name, quality='l', output_dir=None):
    """
    Render a Manim scene as a GIF.

    Args:
        file_path: Path to the Python file
        scene_name: Name of the scene class to render
        quality: Quality level (l, m, h)
        output_dir: Optional custom output directory

    Returns:
        True if successful, False otherwise
    """
    quality_flag = f"-q{quality}"

    cmd = [
        "manim",
        quality_flag,
        "--format", "gif",
        file_path,
        scene_name
    ]

    print(f"Rendering: {file_path} -> {scene_name}.gif")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per scene
        )

        if result.returncode == 0:
            print(f"✓ Successfully rendered {scene_name}")
            return True
        else:
            print(f"✗ Failed to render {scene_name}")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout rendering {scene_name} (>5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Error rendering {scene_name}: {e}")
        return False


def move_gif_to_examples(file_path, scene_name, quality='l'):
    """
    Move the rendered GIF from media/ to the examples/ directory alongside the source.

    Args:
        file_path: Original Python file path
        scene_name: Scene class name
        quality: Quality level used for rendering

    Returns:
        True if successful, False otherwise
    """
    # Manim output path structure
    quality_map = {'l': '480p15', 'm': '720p30', 'h': '1080p60'}
    quality_dir = quality_map.get(quality, '480p15')

    source_file = Path(file_path)
    gif_filename = f"{scene_name}.gif"

    # Expected Manim output location
    media_path = Path("media") / "videos" / source_file.stem / quality_dir / gif_filename

    # Destination: same directory as source file
    dest_path = source_file.parent / gif_filename

    if media_path.exists():
        try:
            # Copy instead of move to preserve media/ structure
            import shutil
            shutil.copy2(media_path, dest_path)
            print(f"→ Copied GIF to: {dest_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to copy GIF: {e}")
            return False
    else:
        print(f"✗ GIF not found at expected location: {media_path}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch render Manim examples as GIFs"
    )
    parser.add_argument(
        "--quality", "-q",
        choices=['l', 'm', 'h'],
        default='l',
        help="Quality level (l=low, m=medium, h=high)"
    )
    parser.add_argument(
        "--category", "-c",
        help="Only render specific category (e.g., physics, mathematics)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be rendered without actually rendering"
    )
    parser.add_argument(
        "--max-scenes",
        type=int,
        default=1,
        help="Maximum number of scenes to render per file"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Manim Examples GIF Renderer")
    print("=" * 60)
    print(f"Quality: {args.quality}")
    print(f"Category: {args.category or 'all'}")
    print(f"Max scenes per file: {args.max_scenes}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Find all Manim files
    files = find_manim_files(category=args.category)

    if not files:
        print("No Manim files found!")
        return

    print(f"Found {len(files)} Manim files")
    print()

    total_rendered = 0
    total_failed = 0

    for file_path, relative_path in files:
        print(f"\n{'=' * 60}")
        print(f"Processing: {relative_path}")
        print(f"{'=' * 60}")

        # Extract scene classes
        scenes = extract_scene_classes(file_path)

        if not scenes:
            print(f"No scene classes found in {file_path}")
            continue

        print(f"Found {len(scenes)} scene(s): {', '.join(scenes)}")

        # Limit to max_scenes
        scenes_to_render = scenes[:args.max_scenes]

        if len(scenes) > args.max_scenes:
            print(f"Limiting to first {args.max_scenes} scene(s)")

        for scene in scenes_to_render:
            if args.dry_run:
                print(f"[DRY RUN] Would render: {scene}")
                continue

            # Render the scene
            success = render_as_gif(file_path, scene, quality=args.quality)

            if success:
                # Move GIF to examples directory
                move_gif_to_examples(file_path, scene, quality=args.quality)
                total_rendered += 1
            else:
                total_failed += 1

            print()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(files)}")
    print(f"Scenes rendered: {total_rendered}")
    print(f"Scenes failed: {total_failed}")
    print()

    if args.dry_run:
        print("This was a dry run. No files were actually rendered.")


if __name__ == "__main__":
    main()
