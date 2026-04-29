# Proposed Project Structure

## Current Issues
- Scripts scattered across root and `/Scripts/`
- No clear separation of concerns
- Examples mixed with core code
- Testing infrastructure incomplete

## Recommended Structure (v1.0)

```
Math-To-Manim/
├── .github/                          # GitHub-specific files
│   ├── workflows/                    # CI/CD pipelines
│   │   ├── tests.yml
│   │   ├── lint.yml
│   │   └── deploy.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── example_submission.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── src/                              # Core source code
│   ├── math_to_manim/
│   │   ├── __init__.py
│   │   ├── agents/                   # Multi-agent system
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py        # Abstract base class
│   │   │   ├── concept_agent.py     # Extract concepts from prompts
│   │   │   ├── research_agent.py    # Gather mathematical content
│   │   │   ├── prompt_agent.py      # Simple -> verbose transformation
│   │   │   ├── code_agent.py        # Verbose -> Manim code
│   │   │   ├── docs_agent.py        # Generate study notes
│   │   │   └── quality_agent.py     # Validation & QA
│   │   │
│   │   ├── orchestrator/             # Agent coordination
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py          # LangGraph workflow definition
│   │   │   ├── state.py             # Shared state management
│   │   │   └── messaging.py         # Inter-agent communication
│   │   │
│   │   ├── models/                   # LLM integrations
│   │   │   ├── __init__.py
│   │   │   ├── deepseek.py          # DeepSeek API client
│   │   │   ├── gemini.py            # Gemini API client
│   │   │   ├── grok.py              # Grok API client
│   │   │   └── model_router.py      # Select best model per task
│   │   │
│   │   ├── validators/               # Code & LaTeX validation
│   │   │   ├── __init__.py
│   │   │   ├── latex_validator.py
│   │   │   ├── manim_validator.py
│   │   │   └── math_validator.py
│   │   │
│   │   ├── prompts/                  # Prompt templates & engineering
│   │   │   ├── __init__.py
│   │   │   ├── templates/
│   │   │   │   ├── concept_extraction.txt
│   │   │   │   ├── prompt_expansion.txt
│   │   │   │   ├── code_generation.txt
│   │   │   │   └── docs_generation.txt
│   │   │   └── prompt_builder.py
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── latex_helpers.py
│   │   │   ├── file_handlers.py
│   │   │   └── logging.py
│   │   │
│   │   └── config/                   # Configuration management
│   │       ├── __init__.py
│   │       ├── settings.py
│   │       └── defaults.yaml
│   │
│   └── web/                          # Web interface
│       ├── __init__.py
│       ├── app.py                    # Main Gradio app
│       ├── components/               # UI components
│       │   ├── prompt_input.py
│       │   ├── agent_dashboard.py
│       │   └── preview_panel.py
│       └── static/                   # CSS, JS, images
│
├── examples/                         # Curated examples (organized!)
│   ├── README.md
│   ├── physics/
│   │   ├── quantum/
│   │   │   ├── qed_journey.py
│   │   │   ├── quantum_field.py
│   │   │   └── README.md
│   │   ├── gravity/
│   │   │   ├── gravitational_waves.py
│   │   │   └── README.md
│   │   └── electromagnetism/
│   │
│   ├── mathematics/
│   │   ├── analysis/
│   │   │   ├── fourier_series.py
│   │   │   └── README.md
│   │   ├── geometry/
│   │   │   ├── pythagorean_theorem.py
│   │   │   └── README.md
│   │   ├── topology/
│   │   └── algebra/
│   │
│   ├── computer_science/
│   │   ├── algorithms/
│   │   │   ├── gale_shapley.py
│   │   │   └── README.md
│   │   ├── neural_networks/
│   │   │   ├── alexnet.py
│   │   │   └── README.md
│   │   └── information_theory/
│   │
│   └── misc/
│       ├── 3d_demos/
│       └── experimental/
│
├── training/                         # ML training & fine-tuning
│   ├── datasets/
│   │   ├── prompt_pairs.jsonl       # Simple -> verbose examples
│   │   ├── successful_generations/   # Working code examples
│   │   └── feedback_logs/           # User feedback data
│   │
│   ├── scripts/
│   │   ├── prepare_data.py
│   │   ├── train_prompt_agent.py
│   │   └── evaluate.py
│   │
│   └── models/                       # Saved model checkpoints
│       └── prompt_expander_v1/
│
├── tests/                            # Comprehensive test suite
│   ├── __init__.py
│   ├── unit/                         # Unit tests
│   │   ├── test_agents.py
│   │   ├── test_validators.py
│   │   └── test_models.py
│   │
│   ├── integration/                  # Integration tests
│   │   ├── test_workflow.py
│   │   └── test_api.py
│   │
│   ├── e2e/                          # End-to-end tests
│   │   └── test_full_pipeline.py
│   │
│   └── fixtures/                     # Test data
│       ├── sample_prompts.json
│       └── expected_outputs/
│
├── docs/                             # Documentation
│   ├── README.md                     # Docs index
│   ├── getting_started/
│   │   ├── installation.md
│   │   ├── quickstart.md
│   │   └── first_animation.md
│   │
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── agents.md
│   │   ├── orchestration.md
│   │   └── data_flow.md
│   │
│   ├── guides/
│   │   ├── writing_prompts.md
│   │   ├── using_agents.md
│   │   ├── advanced_features.md
│   │   └── troubleshooting.md
│   │
│   ├── api/
│   │   ├── agents_api.md
│   │   ├── models_api.md
│   │   └── utils_api.md
│   │
│   ├── examples/
│   │   └── EXAMPLES.md              # Gallery of examples
│   │
│   ├── contributing/
│   │   ├── CONTRIBUTING.md
│   │   ├── code_style.md
│   │   ├── testing.md
│   │   └── documentation.md
│   │
│   └── research/
│       ├── latex_study_notes/        # Generated PDF notes
│       └── papers/                   # Related research papers
│
├── scripts/                          # Utility scripts
│   ├── setup_env.sh                 # Environment setup
│   ├── render_all_examples.py       # Batch rendering
│   ├── benchmark_models.py          # Performance testing
│   └── migrate_structure.py         # Migration helper
│
├── .env.example                      # Example environment variables
├── .gitignore
├── .pre-commit-config.yaml          # Pre-commit hooks
├── pyproject.toml                   # Poetry/PEP 621 config
├── requirements.txt                 # Pip dependencies (generated)
├── requirements-dev.txt             # Dev dependencies
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Multi-service setup
│
├── README.md                        # Main README
├── ROADMAP.md                       # This roadmap!
├── LICENSE                          # MIT License
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # How to contribute
└── CODE_OF_CONDUCT.md              # Community guidelines

```

## Migration Plan

### Phase 1: Create New Structure (Non-Breaking)
1. Create new directories under `src/`
2. Keep old files in place
3. Add new code to proper locations

### Phase 2: Move Examples (Low Risk)
1. Organize examples by topic
2. Add README files to each category
3. Update documentation links

### Phase 3: Refactor Core Code (Breaking Changes)
1. Move `app.py` -> `src/web/app.py`
2. Create agent modules
3. Update imports throughout
4. Update CI/CD

### Phase 4: Deprecation
1. Mark old locations as deprecated
2. Add migration warnings
3. Update all documentation
4. Archive old examples

## Benefits of New Structure

1. **Clarity**: Clear separation between core, examples, docs, tests
2. **Scalability**: Easy to add new agents/features
3. **Professionalism**: Industry-standard Python project layout
4. **Discoverability**: New contributors can navigate easily
5. **Automation**: CI/CD knows where to find tests, code, etc.

## Implementation Notes

- Use **Poetry** for dependency management (better than pip)
- Add **pre-commit hooks** for code quality (black, flake8, mypy)
- Set up **GitHub Actions** for automated testing
- Create **Docker containers** for reproducible environments
- Use **Sphinx** or **MkDocs** for documentation site

## Questions?

- Should we keep backward compatibility with old structure?
- How to handle existing user scripts that import old paths?
- Timeline for full migration?
