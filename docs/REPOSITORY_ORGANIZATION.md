# Repository Organization

## Overview

This document describes the current organization of the Math-To-Manim repository after the reorganization completed on October 4, 2025.

## Directory Structure

```
Math-To-Manim/
├── src/                          # Core application code
│   ├── agents/                   # Agent implementations
│   │   ├── prerequisite_explorer.py
│   │   ├── prerequisite_explorer_claude.py
│   │   ├── nomic_atlas_client.py
│   │   └── video_review_agent.py
│   ├── app.py                    # Legacy Gradio interface
│   └── app_claude.py             # Claude-based Gradio interface
│
├── examples/                     # All animation examples (organized by topic)
│   ├── physics/
│   │   ├── quantum/              # Quantum physics animations
│   │   ├── gravity/              # Gravitational physics
│   │   ├── nuclear/              # Nuclear physics
│   │   └── particle_physics/     # Particle physics
│   ├── mathematics/
│   │   ├── geometry/             # Geometric animations
│   │   ├── analysis/             # Mathematical analysis
│   │   ├── fractals/             # Fractal visualizations
│   │   ├── statistics/           # Statistical visualizations
│   │   └── trigonometry/         # Trigonometry examples
│   ├── computer_science/
│   │   ├── machine_learning/     # ML/AI visualizations
│   │   ├── algorithms/           # Algorithm visualizations
│   │   └── spatial_reasoning/    # Spatial reasoning tests
│   ├── cosmology/                # Cosmology visualizations
│   ├── finance/                  # Financial modeling
│   └── misc/                     # Miscellaneous examples
│
├── scripts/                      # Utility and build scripts
│   ├── add_gif_previews.py       # Add GIF previews to examples
│   ├── batch_test_and_render.py  # Batch testing utility
│   ├── render_examples_as_gifs.py # Render examples to GIFs
│   ├── render_gif.py             # GIF rendering utility
│   ├── reorganize.py             # Repository reorganization script
│   ├── run_presentation.py       # Presentation runner
│   ├── smolagent_expander.py     # Smolagent expansion utility
│   ├── smolagent_prototype.py    # Smolagent prototype
│   ├── text_to_manim.py          # Text-to-Manim converter
│   ├── inspect_agents.py         # Agent inspection tool
│   └── render_all.ps1            # PowerShell batch render script
│
├── docs/                         # All documentation (consolidated)
│   ├── README.md                 # Documentation index
│   ├── ARCHITECTURE.md           # System architecture
│   ├── AGENT_ARCHITECTURE.md     # Agent-specific architecture
│   ├── AGENT_INSPECTION_GUIDE.md # Guide to agent inspection
│   ├── CLAUDE.md                 # Claude integration docs
│   ├── COMMUNICATION_STRATEGY.md # Communication guidelines
│   ├── EXAMPLES.md               # Example catalog
│   ├── GIF_WORKFLOW.md           # GIF creation workflow
│   ├── MCP_TROUBLESHOOTING.md    # MCP troubleshooting
│   ├── MCP_TROUBLESHOOTING_GUIDE.md # Extended MCP guide
│   ├── MCPPostMortem.md          # MCP implementation review
│   ├── MIGRATION_TO_CLAUDE.md    # Claude migration guide
│   ├── NOMIC_ATLAS_INTEGRATION.md # Nomic Atlas docs
│   ├── PROJECT_STRUCTURE.md      # Project structure details
│   ├── QUICK_START_GUIDE.md      # Quick start for new users
│   ├── QUICK_VIDEO_REVIEW_GUIDE.md # Video review guide
│   ├── REFACTOR_SUMMARY.md       # Refactoring summary
│   ├── RENDERING_PROGRESS.md     # Rendering status
│   ├── REORGANIZATION_PLAN.md    # Original reorganization plan
│   ├── REORGANIZATION_SUMMARY.md # Reorganization summary
│   ├── REPOSITORY_ORGANIZATION.md # This document
│   ├── REVERSE_KNOWLEDGE_TREE.md # Knowledge tree structure
│   ├── ROADMAP.md                # Project roadmap
│   ├── SMOLAGENTS_IMPLEMENTATION.md # Smolagents guide
│   ├── SUMMARY.md                # Project summary
│   ├── TESTING_ARCHITECTURE.md   # Testing framework docs
│   ├── VIDEO_REVIEW_TOOLKIT.md   # Video review toolkit
│   ├── readme2.md                # Additional readme
│   ├── Strassler.pdf             # Reference material
│   └── [PDFs]                    # Generated example PDFs
│
├── tests/                        # Testing infrastructure
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
│
├── tools/                        # Development tools
│   ├── frame_viewer.py           # Frame viewing utility
│   └── video_review_toolkit.py   # Video review tools
│
├── media/                        # Generated media files
│   ├── images/                   # Generated images
│   ├── videos/                   # Generated videos
│   ├── review_frames/            # Review frame captures
│   ├── Tex/                      # LaTeX outputs
│   └── texts/                    # Text outputs
│
├── 3BouncingBalls/               # Legacy example directory (to be migrated)
├── Benamou-Brenier/              # Legacy example directory (to be migrated)
├── GravityWavesDiscovery/        # Legacy example directory (to be migrated)
├── Misc/                         # Miscellaneous files
├── QwenMaxQED/                   # Legacy example directory (to be migrated)
├── RevisedBenamou-Brenier/       # Legacy example directory (to be migrated)
├── Rhombicosidodecahedron/       # Legacy example directory (to be migrated)
├── SpatialReasoningTest/         # Legacy example directory (to be migrated)
├── final_output/                 # Legacy output directory
│
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore rules
├── CONTRIBUTING.md               # Contribution guidelines
├── README.md                     # Main project readme
├── requirements.txt              # Python dependencies
└── manim                         # Manim symbolic link/executable
```

## Key Changes from Previous Organization

### 1. Markdown Files Consolidated to docs/
All markdown documentation files have been moved from the root directory to `docs/`:
- AGENT_ARCHITECTURE.md -> docs/
- CLAUDE.md -> docs/
- COMMUNICATION_STRATEGY.md -> docs/
- GIF_WORKFLOW.md -> docs/
- MCP_Troubleshooting_Guide.md -> docs/
- MCPPostMortem.md -> docs/
- PROJECT_STRUCTURE.md -> docs/
- QUICK_START_GUIDE.md -> docs/
- QUICK_VIDEO_REVIEW_GUIDE.md -> docs/
- REFACTOR_SUMMARY.md -> docs/
- RENDERING_PROGRESS.md -> docs/
- REORGANIZATION_PLAN.md -> docs/
- REORGANIZATION_SUMMARY.md -> docs/
- REVERSE_KNOWLEDGE_TREE.md -> docs/
- ROADMAP.md -> docs/
- SUMMARY.md -> docs/
- readme2.md -> docs/

### 2. Duplicate Python Files Removed
Removed duplicate files that existed in both root/Scripts/ and examples/:
- AlexNet.py (kept in examples/computer_science/machine_learning/)
- GrokLogo.py (kept in examples/misc/)
- Hunyuan-T1QED.py (kept in examples/physics/quantum/)
- optionskew.py (kept in examples/finance/)
- QEDGemini25.py (kept in examples/physics/quantum/)
- SpacetimeQEDScene.py (kept in examples/physics/quantum/)
- TrigInference.py (kept in examples/mathematics/trigonometry/)
- And ~30 other duplicate files from Scripts/

### 3. Scripts Organized
All utility scripts moved to new lowercase `scripts/` directory:
- Scripts/ -> scripts/ (directory renamed for Python conventions)
- Utility scripts moved: add_gif_previews.py, batch_test_and_render.py, etc.
- PowerShell scripts: render_all.ps1

### 4. Core Application Files in src/
Application core files remain in src/:
- app.py
- app_claude.py
- src/agents/ (agent implementations)

### 5. Miscellaneous Files Relocated
- ULTRAQED.py -> examples/misc/
- ultraqed_player.html -> media/
- Strassler.pdf -> docs/
- radiumatom.jpg -> media/images/

### 6. Temporary Files Removed
- filelist.txt (removed)
- mylist.txt (removed)

## Root Directory Cleanup

The root directory now contains only essential files:
- `.env.example` - Environment configuration template
- `.gitattributes` - Git attributes
- `.gitignore` - Git ignore rules
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Main project readme
- `requirements.txt` - Python dependencies
- `manim` - Manim executable/symlink
- `python` - Python executable/symlink

## Finding Examples

### By Topic
1. **Physics Examples**: `examples/physics/`
   - Quantum mechanics: `examples/physics/quantum/`
   - Gravity: `examples/physics/gravity/`
   - Nuclear physics: `examples/physics/nuclear/`
   - Particle physics: `examples/physics/particle_physics/`

2. **Mathematics Examples**: `examples/mathematics/`
   - Geometry: `examples/mathematics/geometry/`
   - Analysis: `examples/mathematics/analysis/`
   - Statistics: `examples/mathematics/statistics/`
   - Trigonometry: `examples/mathematics/trigonometry/`

3. **Computer Science**: `examples/computer_science/`
   - Machine Learning: `examples/computer_science/machine_learning/`
   - Algorithms: `examples/computer_science/algorithms/`

4. **Other Topics**: `examples/cosmology/`, `examples/finance/`, `examples/misc/`

### By Name
Use the catalog in `docs/EXAMPLES.md` for a complete list of all examples with descriptions.

## Running Scripts

All utility scripts are now in the `scripts/` directory:

```bash
# Render examples as GIFs
python scripts/render_examples_as_gifs.py

# Batch test and render
python scripts/batch_test_and_render.py

# Run presentations
python scripts/run_presentation.py

# Add GIF previews
python scripts/add_gif_previews.py
```

## Development Workflow

1. **Core Application**: Work in `src/` for application code
2. **Examples**: Create new examples in appropriate `examples/` subdirectories
3. **Documentation**: Add documentation to `docs/`
4. **Utilities**: Place utility scripts in `scripts/`
5. **Tests**: Write tests in `tests/`

## Next Steps

The following legacy directories should be migrated in future updates:
- `3BouncingBalls/` -> Move content to appropriate examples/ subdirectory
- `Benamou-Brenier/` -> Consolidate with examples/mathematics/analysis/
- `GravityWavesDiscovery/` -> Already migrated to examples/physics/gravity/
- `QwenMaxQED/` -> Already migrated to examples/physics/quantum/
- `RevisedBenamou-Brenier/` -> Consolidate with examples/mathematics/analysis/
- `Rhombicosidodecahedron/` -> Already migrated to examples/mathematics/geometry/
- `SpatialReasoningTest/` -> Already migrated to examples/computer_science/spatial_reasoning/
- `Misc/` -> Review and categorize contents

## Benefits of New Organization

1. **Clean Root Directory**: Only essential configuration and documentation files
2. **Consolidated Documentation**: All docs in one place (`docs/`)
3. **No Duplicates**: Removed ~40 duplicate files
4. **Topic-Based Navigation**: Easy to find examples by subject area
5. **Standard Python Structure**: Follows Python project conventions
6. **Clear Separation**: Core app, examples, scripts, and docs are distinct

## See Also

- [REORGANIZATION_PLAN.md](REORGANIZATION_PLAN.md) - Original reorganization plan
- [EXAMPLES.md](EXAMPLES.md) - Catalog of all examples
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Getting started guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture documentation
