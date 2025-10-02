#!/usr/bin/env python3
"""
Reorganization script for Math-To-Manim repository.
This script moves files from the old scattered structure to the new organized structure.
"""

import os
import shutil
from pathlib import Path

# Define the reorganization mapping
FILE_MAPPING = {
    # Core application files
    "app.py": "src/app.py",
    "app_claude.py": "src/app_claude.py",
    "prerequisite_explorer.py": "src/agents/prerequisite_explorer.py",
    "prerequisite_explorer_claude.py": "src/agents/prerequisite_explorer_claude.py",
    "smolagent_prototype.py": "scripts/smolagent_prototype.py",

    # Physics - Quantum
    "Scripts/QED.py": "examples/physics/quantum/QED.py",
    "QEDGemini25.py": "examples/physics/quantum/QEDGemini25.py",
    "Hunyuan-T1QED.py": "examples/physics/quantum/Hunyuan-T1QED.py",
    "Scripts/Verbose_QED.py": "examples/physics/quantum/Verbose_QED.py",
    "Scripts/Vebose_QED.py": "examples/physics/quantum/Vebose_QED.py",
    "Scripts/rotated_QED.py": "examples/physics/quantum/rotated_QED.py",
    "Scripts/rotated_QED2.py": "examples/physics/quantum/rotated_QED2.py",
    "Scripts/Gemini2.5ProQED.py": "examples/physics/quantum/Gemini2.5ProQED.py",
    "QwenMaxQED/qwenQED.py": "examples/physics/quantum/qwenQED.py",
    "Scripts/Grok_Quantum.py": "examples/physics/quantum/Grok_Quantum.py",
    "Scripts/grok_quantum2.py": "examples/physics/quantum/grok_quantum2.py",
    "Scripts/quantum_field_theory.py": "examples/physics/quantum/quantum_field_theory.py",
    "SpacetimeQEDScene.py": "examples/physics/quantum/SpacetimeQEDScene.py",

    # Physics - Gravity
    "GravityWavesDiscovery/gravitational_wave.py": "examples/physics/gravity/gravitational_wave.py",
    "GravityWavesDiscovery/Mistral_gravity_wave.py": "examples/physics/gravity/Mistral_gravity_wave.py",

    # Physics - Nuclear
    "Scripts/radium_atom.py": "examples/physics/nuclear/radium_atom.py",

    # Physics - Particle Physics
    "Scripts/ElectroweakSymmetryScene.py": "examples/physics/particle_physics/ElectroweakSymmetryScene.py",
    "Scripts/strassler.py": "examples/physics/particle_physics/strassler.py",
    "Scripts/Strassler2.py": "examples/physics/particle_physics/Strassler2.py",

    # Mathematics - Geometry
    "Scripts/pythagorean.py": "examples/mathematics/geometry/pythagorean.py",
    "3BouncingBalls/bouncing_balls.py": "examples/mathematics/geometry/bouncing_balls.py",
    "Rhombicosidodecahedron/bouncing.py": "examples/mathematics/geometry/rhombicosidodecahedron_bouncing.py",
    "Rhombicosidodecahedron/flythroughbouncing.py": "examples/mathematics/geometry/rhombicosidodecahedron_flythrough.py",

    # Mathematics - Analysis
    "Scripts/diffusion_optimal_transport.py": "examples/mathematics/analysis/diffusion_optimal_transport.py",
    "Scripts/diffusion_ot.py": "examples/mathematics/analysis/diffusion_ot.py",
    "Benamou-Brenier/Google_Thinking_one_shot.py": "examples/mathematics/analysis/benamou_brenier_google.py",
    "RevisedBenamou-Brenier/scene1.py": "examples/mathematics/analysis/benamou_brenier_revised.py",

    # Mathematics - Fractals
    "Scripts/fractal_scene.py": "examples/mathematics/fractals/fractal_scene.py",

    # Mathematics - Statistics
    "Scripts/brown_einstein.py": "examples/mathematics/statistics/brown_einstein.py",
    "Scripts/information_geometry.py": "examples/mathematics/statistics/information_geometry.py",
    "Scripts/information_geometry2.py": "examples/mathematics/statistics/information_geometry2.py",

    # Mathematics - Trigonometry
    "TrigInference.py": "examples/mathematics/trigonometry/TrigInference.py",

    # Computer Science - Machine Learning
    "AlexNet.py": "examples/computer_science/machine_learning/AlexNet.py",
    "Scripts/NativeSparseAttention.py": "examples/computer_science/machine_learning/NativeSparseAttention.py",
    "Scripts/NativeSparseAttention2.py": "examples/computer_science/machine_learning/NativeSparseAttention2.py",
    "Scripts/GRPO.py": "examples/computer_science/machine_learning/GRPO.py",
    "Scripts/GRPO2.py": "examples/computer_science/machine_learning/GRPO2.py",
    "Scripts/Qwen3.235B.A22B.py": "examples/computer_science/machine_learning/Qwen3.235B.A22B.py",
    "Scripts/regularization.py": "examples/computer_science/machine_learning/regularization.py",

    # Computer Science - Algorithms
    "Scripts/gale-shaply.py": "examples/computer_science/algorithms/gale_shaply.py",
    "Scripts/prolip.py": "examples/computer_science/algorithms/prolip.py",

    # Computer Science - Spatial Reasoning
    "SpatialReasoningTest/DeepSeek_LShape3D.py": "examples/computer_science/spatial_reasoning/DeepSeek_LShape3D.py",
    "SpatialReasoningTest/OpenAIPro_LShape3D.py": "examples/computer_science/spatial_reasoning/OpenAIPro_LShape3D.py",

    # Cosmology
    "Scripts/Claude37Cosmic.py": "examples/cosmology/Claude37Cosmic.py",
    "Scripts/CosmicProbabilityScene.py": "examples/cosmology/CosmicProbabilityScene.py",

    # Finance
    "optionskew.py": "examples/finance/optionskew.py",

    # Miscellaneous
    "Scripts/stickman.py": "examples/misc/stickman.py",
    "GrokLogo.py": "examples/misc/GrokLogo.py",
    "Scripts/generated_scene.py": "examples/misc/generated_scene.py",

    # Utility scripts
    "Scripts/smolagent_expander.py": "scripts/smolagent_expander.py",
    "Scripts/text_to_manim.py": "scripts/text_to_manim.py",
    "run_presentation.py": "scripts/run_presentation.py",
}

def create_directory_structure():
    """Create the new directory structure."""
    directories = [
        "src/agents",
        "examples/physics/quantum",
        "examples/physics/gravity",
        "examples/physics/nuclear",
        "examples/physics/particle_physics",
        "examples/mathematics/geometry",
        "examples/mathematics/analysis",
        "examples/mathematics/fractals",
        "examples/mathematics/statistics",
        "examples/mathematics/trigonometry",
        "examples/computer_science/machine_learning",
        "examples/computer_science/algorithms",
        "examples/computer_science/spatial_reasoning",
        "examples/cosmology",
        "examples/finance",
        "examples/misc",
        "scripts",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "docs",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    # Create __init__.py files for Python packages
    init_files = [
        "src/__init__.py",
        "src/agents/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/e2e/__init__.py",
    ]

    for init_file in init_files:
        Path(init_file).touch()
        print(f"Created: {init_file}")

def copy_files():
    """Copy files to their new locations."""
    copied = 0
    skipped = 0

    for old_path, new_path in FILE_MAPPING.items():
        if os.path.exists(old_path):
            # Create parent directory if it doesn't exist
            Path(new_path).parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            try:
                shutil.copy2(old_path, new_path)
                print(f"Copied: {old_path} -> {new_path}")
                copied += 1
            except (PermissionError, OSError) as e:
                print(f"WARNING: Could not copy {old_path}: {e}")
                skipped += 1
        else:
            print(f"WARNING: File not found: {old_path}")
            skipped += 1

    print(f"\nSummary: {copied} files copied, {skipped} files skipped")

def create_readme_files():
    """Create README.md files in each example category."""
    readme_content = {
        "examples/physics/quantum/README.md": """# Quantum Physics Animations

This directory contains Manim animations related to quantum physics, including:
- Quantum Electrodynamics (QED)
- Quantum Field Theory
- Spacetime representations

Generated by various AI models including DeepSeek, Gemini, Grok, and others.
""",
        "examples/physics/gravity/README.md": """# Gravitational Physics Animations

This directory contains animations related to gravitational waves and general relativity.
""",
        "examples/physics/nuclear/README.md": """# Nuclear Physics Animations

This directory contains animations related to nuclear physics and atomic structure.
""",
        "examples/physics/particle_physics/README.md": """# Particle Physics Animations

This directory contains animations related to particle physics, including electroweak symmetry.
""",
        "examples/mathematics/geometry/README.md": """# Geometry Animations

This directory contains mathematical animations related to geometry, including:
- Pythagorean theorem
- 3D polyhedra
- Bouncing ball physics
""",
        "examples/mathematics/analysis/README.md": """# Mathematical Analysis Animations

This directory contains animations related to mathematical analysis, including:
- Optimal transport theory
- Benamou-Brenier formulation
- Diffusion processes
""",
        "examples/mathematics/fractals/README.md": """# Fractal Animations

This directory contains animations of fractal patterns and structures.
""",
        "examples/mathematics/statistics/README.md": """# Statistics and Probability Animations

This directory contains animations related to statistics, probability, and information geometry.
""",
        "examples/computer_science/machine_learning/README.md": """# Machine Learning Animations

This directory contains animations of machine learning concepts, including:
- Neural network architectures (AlexNet)
- Attention mechanisms
- Optimization algorithms (GRPO)
- Regularization techniques
""",
        "examples/computer_science/algorithms/README.md": """# Algorithm Animations

This directory contains animations of computer science algorithms.
""",
        "examples/cosmology/README.md": """# Cosmology Animations

This directory contains animations related to cosmology and cosmic probability.
""",
    }

    for filepath, content in readme_content.items():
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created: {filepath}")

def main():
    """Main execution function."""
    print("=" * 60)
    print("Math-To-Manim Repository Reorganization")
    print("=" * 60)
    print()

    print("Step 1: Creating directory structure...")
    create_directory_structure()
    print()

    print("Step 2: Copying files to new locations...")
    copy_files()
    print()

    print("Step 3: Creating category README files...")
    create_readme_files()
    print()

    print("=" * 60)
    print("Reorganization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the new structure")
    print("2. Test that core application still works")
    print("3. Update documentation to reference new locations")
    print("4. Consider archiving old directories")
    print()
    print("Note: Original files have been preserved.")
    print("To complete the migration, you may want to remove old directories.")

if __name__ == "__main__":
    main()
