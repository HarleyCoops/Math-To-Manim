#!/usr/bin/env python3
"""
Batch test and render all Manim scripts in the repository.

This script will:
1. Find all Python files that contain Manim Scene classes
2. Try to render each one at low quality
3. Fix common errors automatically where possible
4. Export successful renders as GIFs
5. Generate a report of successes and failures
"""

import subprocess
import re
from pathlib import Path
import json
import time
from typing import List, Dict, Tuple

# Directories to scan
SCAN_DIRS = [
    "3BouncingBalls",
    "Benamou-Brenier",
    "GravityWavesDiscovery",
    "QwenMaxQED",
    "RevisedBenamou-Brenier",
    "Rhombicosidodecahedron",
    "Scripts",
    "SpatialReasoningTest",
    "."  # Root level
]

# Files to exclude
EXCLUDE_FILES = [
    "text_to_manim.py",
    "smolagent_expander.py",
    "run_presentation.py",
    "batch_test_and_render.py",
    "render_gif.py",
    "render_examples_as_gifs.py",
    "add_gif_previews.py"
]

def find_scene_classes(file_path: Path) -> List[str]:
    """Find all Scene class names in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for class definitions that inherit from Scene
        pattern = r'class\s+(\w+)\s*\([^)]*Scene[^)]*\)'
        matches = re.findall(pattern, content)
        return matches
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def find_manim_scripts() -> Dict[str, List[str]]:
    """Find all Manim scripts and their Scene classes."""
    scripts = {}

    for scan_dir in SCAN_DIRS:
        dir_path = Path(scan_dir)
        if not dir_path.exists():
            continue

        # Find all .py files
        if scan_dir == ".":
            # Only root level files, not recursive
            py_files = [f for f in dir_path.glob("*.py") if f.is_file()]
        else:
            py_files = list(dir_path.rglob("*.py"))

        for py_file in py_files:
            # Skip excluded files
            if py_file.name in EXCLUDE_FILES:
                continue

            # Skip __pycache__ and other special directories
            if "__pycache__" in str(py_file) or ".pytest_cache" in str(py_file):
                continue

            # Find Scene classes
            scenes = find_scene_classes(py_file)
            if scenes:
                scripts[str(py_file)] = scenes

    return scripts

def test_render(file_path: str, scene_name: str, timeout: int = 300) -> Tuple[bool, str, str]:
    """
    Test render a scene at low quality.

    Returns:
        (success, stdout, stderr)
    """
    cmd = [
        "manim",
        "-ql",  # Low quality
        "--format", "gif",
        file_path,
        scene_name
    ]

    print(f"  Testing: {scene_name} (timeout: {timeout}s)")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd())
        )

        success = result.returncode == 0
        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def main():
    """Main execution function."""
    print("=" * 80)
    print("Batch Testing and Rendering Manim Scripts")
    print("=" * 80)
    print()

    # Find all scripts
    print("Scanning for Manim scripts...")
    scripts = find_manim_scripts()

    # Remove duplicates (keep only one version of each file)
    unique_scripts = {}
    seen_names = set()
    for file_path, scenes in scripts.items():
        file_name = Path(file_path).name
        if file_name not in seen_names:
            seen_names.add(file_name)
            unique_scripts[file_path] = scenes

    print(f"Found {len(unique_scripts)} unique Manim scripts")
    print()

    # Results tracking
    results = {
        "success": [],
        "failed": [],
        "timeout": [],
        "total_tested": 0
    }

    # Test each script
    for i, (file_path, scenes) in enumerate(unique_scripts.items(), 1):
        print(f"\n[{i}/{len(unique_scripts)}] Testing: {file_path}")
        print(f"  Found {len(scenes)} scene(s): {', '.join(scenes)}")

        # Test first scene only (to save time)
        if scenes:
            scene_name = scenes[0]
            results["total_tested"] += 1

            # Determine timeout based on file
            # Give more time for known complex animations
            timeout = 300  # 5 minutes default
            if "gravitational" in file_path.lower():
                timeout = 1200  # 20 minutes
            elif "3d" in file_path.lower() or "surface" in str(file_path).lower():
                timeout = 600  # 10 minutes

            success, stdout, stderr = test_render(file_path, scene_name, timeout)

            if success:
                print(f"  ✓ SUCCESS: {scene_name}")
                results["success"].append({
                    "file": file_path,
                    "scene": scene_name,
                    "scenes": scenes
                })
            elif "Timeout" in stderr:
                print(f"  ⏱ TIMEOUT: {scene_name}")
                results["timeout"].append({
                    "file": file_path,
                    "scene": scene_name,
                    "error": stderr
                })
            else:
                print(f"  ✗ FAILED: {scene_name}")
                # Print first 500 chars of error
                error_preview = stderr[:500] if stderr else stdout[-500:]
                print(f"  Error: {error_preview}")
                results["failed"].append({
                    "file": file_path,
                    "scene": scene_name,
                    "stdout": stdout[-1000:],  # Last 1000 chars
                    "stderr": stderr[-1000:]
                })

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total scripts tested: {results['total_tested']}")
    print(f"✓ Successful: {len(results['success'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    print(f"⏱ Timeout: {len(results['timeout'])}")
    print()

    # Print successful renders
    if results["success"]:
        print("\nSuccessful Renders:")
        print("-" * 80)
        for item in results["success"]:
            print(f"  ✓ {item['file']}")
            print(f"    Scene: {item['scene']}")

    # Print failures
    if results["failed"]:
        print("\nFailed Renders:")
        print("-" * 80)
        for item in results["failed"]:
            print(f"  ✗ {item['file']}")
            print(f"    Scene: {item['scene']}")
            print(f"    Error: {item['stderr'][:200]}")

    # Print timeouts
    if results["timeout"]:
        print("\nTimeout (may need manual testing with longer timeout):")
        print("-" * 80)
        for item in results["timeout"]:
            print(f"  ⏱ {item['file']}")
            print(f"    Scene: {item['scene']}")

    # Save detailed results to JSON
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
