#!/usr/bin/env python3
"""
Simple script to render a single Manim animation as GIF.

Usage:
    python scripts/render_gif.py <file.py> <SceneName> [quality]

Example:
    python scripts/render_gif.py examples/physics/quantum/QED.py QEDJourney l
"""

import sys
import subprocess
from pathlib import Path


def render_gif(file_path, scene_name, quality='l'):
    """Render a Manim scene as GIF."""
    quality_flag = f"-q{quality}"

    cmd = [
        "manim",
        quality_flag,
        "--format", "gif",
        file_path,
        scene_name
    ]

    print(f"Rendering: {file_path} -> {scene_name}.gif")
    print(f"Quality: {quality} ({'480p' if quality == 'l' else '720p' if quality == 'm' else '1080p'})")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ Successfully rendered {scene_name}.gif")
        print(f"→ Check media/videos/{Path(file_path).stem}/ for output")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed to render: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/render_gif.py <file.py> <SceneName> [quality]")
        print()
        print("Quality options:")
        print("  l = low quality (480p, fast)")
        print("  m = medium quality (720p)")
        print("  h = high quality (1080p)")
        print()
        print("Example:")
        print("  python scripts/render_gif.py examples/physics/quantum/QED.py QEDJourney l")
        sys.exit(1)

    file_path = sys.argv[1]
    scene_name = sys.argv[2]
    quality = sys.argv[3] if len(sys.argv) > 3 else 'l'

    if quality not in ['l', 'm', 'h']:
        print(f"Invalid quality: {quality}. Use l, m, or h")
        sys.exit(1)

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    success = render_gif(file_path, scene_name, quality)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
