# Folder Structure Reorganization Plan

## Current Issues
- 57+ Python files scattered across root directory and subdirectories
- No clear categorization by topic
- Difficult for first-time users to navigate
- Mix of core application code and example animations
- Inconsistent naming conventions

## Proposed New Structure

```
Math-To-Manim/
├── src/                          # Core application code
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── prerequisite_explorer.py
│   │   └── prerequisite_explorer_claude.py
│   ├── app.py                    # Legacy Gradio interface
│   └── app_claude.py             # Claude-based Gradio interface
│
├── examples/                     # All animation examples
│   ├── physics/
│   │   ├── quantum/
│   │   │   ├── QED.py
│   │   │   ├── QEDGemini25.py
│   │   │   ├── Hunyuan-T1QED.py
│   │   │   ├── Verbose_QED.py
│   │   │   ├── Vebose_QED.py
│   │   │   ├── rotated_QED.py
│   │   │   ├── rotated_QED2.py
│   │   │   ├── Gemini2.5ProQED.py
│   │   │   ├── qwenQED.py
│   │   │   ├── Grok_Quantum.py
│   │   │   ├── grok_quantum2.py
│   │   │   ├── quantum_field_theory.py
│   │   │   └── SpacetimeQEDScene.py
│   │   ├── gravity/
│   │   │   ├── gravitational_wave.py
│   │   │   └── Mistral_gravity_wave.py
│   │   ├── nuclear/
│   │   │   └── radium_atom.py
│   │   └── particle_physics/
│   │       ├── ElectroweakSymmetryScene.py
│   │       ├── strassler.py
│   │       └── Strassler2.py
│   │
│   ├── mathematics/
│   │   ├── geometry/
│   │   │   ├── pythagorean.py
│   │   │   ├── bouncing_balls.py
│   │   │   ├── rhombicosidodecahedron_bouncing.py
│   │   │   └── rhombicosidodecahedron_flythrough.py
│   │   ├── analysis/
│   │   │   ├── diffusion_optimal_transport.py
│   │   │   ├── diffusion_ot.py
│   │   │   ├── benamou_brenier_google.py
│   │   │   └── benamou_brenier_revised.py
│   │   ├── fractals/
│   │   │   └── fractal_scene.py
│   │   ├── statistics/
│   │   │   ├── brown_einstein.py
│   │   │   └── information_geometry.py
│   │   └── trigonometry/
│   │       └── TrigInference.py
│   │
│   ├── computer_science/
│   │   ├── machine_learning/
│   │   │   ├── AlexNet.py
│   │   │   ├── NativeSparseAttention.py
│   │   │   ├── NativeSparseAttention2.py
│   │   │   ├── GRPO.py
│   │   │   ├── GRPO2.py
│   │   │   ├── Qwen3.235B.A22B.py
│   │   │   └── regularization.py
│   │   ├── algorithms/
│   │   │   ├── gale_shaply.py
│   │   │   └── prolip.py
│   │   └── spatial_reasoning/
│   │       ├── DeepSeek_LShape3D.py
│   │       └── OpenAIPro_LShape3D.py
│   │
│   ├── cosmology/
│   │   ├── Claude37Cosmic.py
│   │   └── CosmicProbabilityScene.py
│   │
│   ├── finance/
│   │   └── optionskew.py
│   │
│   └── misc/
│       ├── stickman.py
│       ├── GrokLogo.py
│       └── generated_scene.py
│
├── tests/                        # Testing infrastructure
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md
│   ├── SMOLAGENTS_IMPLEMENTATION.md
│   ├── REVERSE_KNOWLEDGE_TREE.md
│   ├── ROADMAP.md
│   ├── MIGRATION_TO_CLAUDE.md
│   ├── TESTING_ARCHITECTURE.md
│   ├── EXAMPLES.md
│   └── CLAUDE.md
│
├── scripts/                      # Utility scripts
│   ├── smolagent_expander.py
│   ├── text_to_manim.py
│   └── run_presentation.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## File Mapping

### Core Application (root -> src/)
- app.py -> src/app.py
- app_claude.py -> src/app_claude.py
- prerequisite_explorer.py -> src/agents/prerequisite_explorer.py
- prerequisite_explorer_claude.py -> src/agents/prerequisite_explorer_claude.py
- smolagent_prototype.py -> scripts/smolagent_prototype.py

### Physics Examples (various -> examples/physics/)

**Quantum:**
- Scripts/QED.py -> examples/physics/quantum/QED.py
- QEDGemini25.py -> examples/physics/quantum/QEDGemini25.py
- Hunyuan-T1QED.py -> examples/physics/quantum/Hunyuan-T1QED.py
- Scripts/Verbose_QED.py -> examples/physics/quantum/Verbose_QED.py
- Scripts/Vebose_QED.py -> examples/physics/quantum/Vebose_QED.py
- Scripts/rotated_QED.py -> examples/physics/quantum/rotated_QED.py
- Scripts/rotated_QED2.py -> examples/physics/quantum/rotated_QED2.py
- Scripts/Gemini2.5ProQED.py -> examples/physics/quantum/Gemini2.5ProQED.py
- QwenMaxQED/qwenQED.py -> examples/physics/quantum/qwenQED.py
- Scripts/Grok_Quantum.py -> examples/physics/quantum/Grok_Quantum.py
- Scripts/grok_quantum2.py -> examples/physics/quantum/grok_quantum2.py
- Scripts/quantum_field_theory.py -> examples/physics/quantum/quantum_field_theory.py
- SpacetimeQEDScene.py -> examples/physics/quantum/SpacetimeQEDScene.py

**Gravity:**
- GravityWavesDiscovery/gravitational_wave.py -> examples/physics/gravity/gravitational_wave.py
- GravityWavesDiscovery/Mistral_gravity_wave.py -> examples/physics/gravity/Mistral_gravity_wave.py

**Nuclear:**
- Scripts/radium_atom.py -> examples/physics/nuclear/radium_atom.py

**Particle Physics:**
- Scripts/ElectroweakSymmetryScene.py -> examples/physics/particle_physics/ElectroweakSymmetryScene.py
- Scripts/strassler.py -> examples/physics/particle_physics/strassler.py
- Scripts/Strassler2.py -> examples/physics/particle_physics/Strassler2.py

### Mathematics Examples (various -> examples/mathematics/)

**Geometry:**
- Scripts/pythagorean.py -> examples/mathematics/geometry/pythagorean.py
- 3BouncingBalls/bouncing_balls.py -> examples/mathematics/geometry/bouncing_balls.py
- Rhombicosidodecahedron/bouncing.py -> examples/mathematics/geometry/rhombicosidodecahedron_bouncing.py
- Rhombicosidodecahedron/flythroughbouncing.py -> examples/mathematics/geometry/rhombicosidodecahedron_flythrough.py

**Analysis:**
- Scripts/diffusion_optimal_transport.py -> examples/mathematics/analysis/diffusion_optimal_transport.py
- Scripts/diffusion_ot.py -> examples/mathematics/analysis/diffusion_ot.py
- Benamou-Brenier/Google_Thinking_one_shot.py -> examples/mathematics/analysis/benamou_brenier_google.py
- RevisedBenamou-Brenier/scene1.py -> examples/mathematics/analysis/benamou_brenier_revised.py

**Fractals:**
- Scripts/fractal_scene.py -> examples/mathematics/fractals/fractal_scene.py

**Statistics:**
- Scripts/brown_einstein.py -> examples/mathematics/statistics/brown_einstein.py
- Scripts/information_geometry.py -> examples/mathematics/statistics/information_geometry.py
- Scripts/information_geometry2.py -> examples/mathematics/statistics/information_geometry2.py

**Trigonometry:**
- TrigInference.py -> examples/mathematics/trigonometry/TrigInference.py

### Computer Science Examples (various -> examples/computer_science/)

**Machine Learning:**
- AlexNet.py -> examples/computer_science/machine_learning/AlexNet.py
- Scripts/NativeSparseAttention.py -> examples/computer_science/machine_learning/NativeSparseAttention.py
- Scripts/NativeSparseAttention2.py -> examples/computer_science/machine_learning/NativeSparseAttention2.py
- Scripts/GRPO.py -> examples/computer_science/machine_learning/GRPO.py
- Scripts/GRPO2.py -> examples/computer_science/machine_learning/GRPO2.py
- Scripts/Qwen3.235B.A22B.py -> examples/computer_science/machine_learning/Qwen3.235B.A22B.py
- Scripts/regularization.py -> examples/computer_science/machine_learning/regularization.py

**Algorithms:**
- Scripts/gale-shaply.py -> examples/computer_science/algorithms/gale_shaply.py
- Scripts/prolip.py -> examples/computer_science/algorithms/prolip.py

**Spatial Reasoning:**
- SpatialReasoningTest/DeepSeek_LShape3D.py -> examples/computer_science/spatial_reasoning/DeepSeek_LShape3D.py
- SpatialReasoningTest/OpenAIPro_LShape3D.py -> examples/computer_science/spatial_reasoning/OpenAIPro_LShape3D.py

### Cosmology Examples (Scripts -> examples/cosmology/)
- Scripts/Claude37Cosmic.py -> examples/cosmology/Claude37Cosmic.py
- Scripts/CosmicProbabilityScene.py -> examples/cosmology/CosmicProbabilityScene.py

### Finance Examples (root -> examples/finance/)
- optionskew.py -> examples/finance/optionskew.py

### Miscellaneous (various -> examples/misc/)
- Scripts/stickman.py -> examples/misc/stickman.py
- GrokLogo.py -> examples/misc/GrokLogo.py
- Scripts/generated_scene.py -> examples/misc/generated_scene.py

### Utility Scripts (Scripts -> scripts/)
- Scripts/smolagent_expander.py -> scripts/smolagent_expander.py
- Scripts/text_to_manim.py -> scripts/text_to_manim.py
- run_presentation.py -> scripts/run_presentation.py

## Benefits of New Structure

1. **Clear Navigation**: First-time users can easily find examples by topic
2. **Separation of Concerns**: Core code separated from examples
3. **Professional Layout**: Matches standard Python project structure
4. **Scalability**: Easy to add new categories or examples
5. **Testing Ready**: Clear location for test infrastructure
6. **Documentation Organized**: All docs in one place

## Implementation Steps

1. Create new directory structure
2. Copy files to new locations (preserve originals initially)
3. Create __init__.py files for Python packages
4. Update import statements where necessary
5. Update README.md with new structure
6. Create EXAMPLES.md catalog
7. Test core application still works
8. Archive old directories
9. Update .gitignore if needed

## Backward Compatibility

To maintain backward compatibility during transition:
- Keep original files for 1-2 releases
- Add deprecation warnings in old file locations
- Update all documentation to reference new locations
- Provide migration script for users

## Next Steps

1. Review and approve this plan
2. Execute reorganization
3. Update documentation
4. Test all imports work correctly
5. Create catalog of examples by difficulty level
