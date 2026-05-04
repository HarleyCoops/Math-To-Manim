# GitHub Copilot Instructions for Math-To-Manim

## Project Overview

Math-To-Manim is an AI-powered system that generates mathematical animations using Manim Community Edition. The project uses Claude AI agents to build knowledge trees and create verbose, LaTeX-rich prompts that generate high-quality educational animations.

**Core Innovation**: Reverse Knowledge Tree - recursively discovers prerequisites before generating animations, ensuring conceptual understanding builds from foundation to advanced topics.

## Key Technologies

- **Python**: 3.10+
- **Manim Community**: v0.19.0 (mathematical animation engine)
- **Claude AI**: Anthropic's Claude Sonnet 4.5 via Anthropic SDK and Claude Agent SDK
- **FFmpeg**: Required for video rendering
- **Gradio**: Web interface for the agent pipeline
- **pytest**: Testing framework

## Development Setup

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys in .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
echo "MOONSHOT_API_KEY=your_key_here" >> .env  # Optional, for Kimi K2

# Install FFmpeg (required for Manim)
# Windows: choco install ffmpeg
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Running the Application
```bash
# Launch the Gradio web interface
python src/app_claude.py

# Run a specific animation example
manim -pql examples/physics/quantum/QED.py QEDJourney
```

### Testing
```bash
# Run all tests with pytest
pytest tests/ -v

# Run tests without live API calls (fast, no cost)
pytest tests/ -v -m "not live"

# Run the interactive test runner
python tests/live_test_runner.py

# Test a specific concept
python tests/live_test_runner.py --concept "quantum mechanics"
```

### Building and Linting
```bash
# Run Python linter (if black is configured)
black src/ tests/

# Check code style
flake8 src/ tests/  # If configured

# Run type checking (if mypy is configured)
mypy src/  # If configured
```

## Code Style and Conventions

### Python Code
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Include docstrings for all functions, classes, and modules
- Keep functions focused on a single responsibility
- Add comments for complex logic, especially in agent prompts
- Use type hints where appropriate

### Manim Animation Code
- Organize scenes into logical sections with comments
- Use descriptive names for mobjects (mathematical objects)
- Include docstrings explaining the mathematical concept being visualized
- Use consistent LaTeX formatting: `$$...$$` for display equations, `$...$` for inline
- Optimize animations for educational clarity
- Test animations render correctly before committing

### LaTeX Conventions
- Always use proper LaTeX syntax for mathematical notation
- Use `\text{}` for text within equations
- Use `\mathcal{}` for script letters (e.g., Lagrangian `\mathcal{L}`)
- Use `\vec{}` or `\mathbf{}` for vectors consistently
- Escape special characters properly
- Test LaTeX rendering in Manim before committing

### Agent System
- Each agent has a specific role (ConceptAnalyzer, PrerequisiteExplorer, MathematicalEnricher, etc.)
- Agents use system prompts to define their behavior
- Keep prompts focused and specific to the agent's role
- Cache API responses when possible to reduce costs
- Handle API errors gracefully with retries and fallbacks

## Project Structure

```
Math-To-Manim/
├── src/                        # Core agent system
│   ├── agents/                 # AI agent implementations
│   │   ├── prerequisite_explorer_claude.py  # Builds knowledge trees
│   │   ├── mathematical_enricher.py         # Adds LaTeX to nodes
│   │   ├── visual_designer.py               # Specifies visualizations
│   │   └── narrative_composer.py            # Creates verbose prompts
│   ├── app_claude.py          # Gradio UI (Claude SDK)
│   └── app.py                 # Legacy UI
│
├── examples/                   # 55+ working animations
│   ├── physics/               # Physics animations (quantum, gravity, etc.)
│   ├── mathematics/           # Math animations (geometry, analysis, etc.)
│   ├── computer_science/      # CS animations (ML, algorithms, etc.)
│   └── cosmology/             # Cosmology animations
│
├── tests/                     # Testing infrastructure
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
│
├── KimiK2Thinking/           # Alternative pipeline using Kimi K2
└── docs/                     # Documentation
```

## Common Tasks and Patterns

### Adding a New Agent
1. Create new file in `src/agents/`
2. Inherit from base agent class (if exists) or create standalone
3. Define system prompt and tool usage
4. Add to agent orchestrator
5. Write unit tests in `tests/unit/`
6. Update documentation

### Adding a New Animation Example
1. Choose appropriate category directory in `examples/`
2. Create Python file with descriptive name (e.g., `schrodinger_equation.py`)
3. Add module docstring explaining the concept
4. Implement Manim Scene class
5. Test rendering: `manim -pql your_file.py YourScene`
6. Add entry to `docs/EXAMPLES.md`

### Working with Knowledge Trees
- Trees are built recursively by PrerequisiteExplorer
- Each node has: concept, depth, prerequisites (children)
- Foundation concepts (depth 0) are high school level basics
- Trees are enriched by adding LaTeX, visuals, and narrative
- Serialized as JSON for caching and reuse

### Debugging Animation Rendering Issues
1. Check FFmpeg is installed: `ffmpeg -version`
2. Verify LaTeX syntax is correct
3. Run Manim with verbose output: `manim -pql --verbose DEBUG file.py Scene`
4. Check Manim logs in `media/` directory
5. Test LaTeX rendering separately if needed

## Important Considerations

### API Costs
- Claude API calls cost money - use caching when possible
- Test with simple concepts before running on complex topics
- Use `pytest -m "not live"` to skip tests requiring API calls
- Consider using the legacy DeepSeek implementation for experimentation

### LaTeX Rendering
- LaTeX errors are the most common cause of failed animations
- Always escape special characters: `\_`, `\{`, `\}`
- Test complex LaTeX equations in isolation first
- Use raw strings in Python: `r"$\frac{1}{2}$"` to avoid escape issues

### Performance
- Knowledge tree generation: ~30-60 seconds for complex topics
- Animation rendering varies by complexity and quality settings
- Use `-ql` (low quality) for fast testing
- Use `-qh` (high quality) or `-qk` (4K) for final output

### File Organization
- Keep animations in topic-specific directories
- Use descriptive filenames, not generic names like `scene1.py`
- Add comprehensive docstrings to explain mathematical concepts
- Include comments for complex mathematical transformations

## Testing Guidelines

### Unit Tests
- Test individual agent methods
- Mock API calls where possible
- Use fixtures for common test data
- Test edge cases and error handling

### Integration Tests
- Test agent interactions
- Test full pipeline with simple concepts
- Verify output format and structure
- Test caching behavior

### End-to-End Tests
- Test complete workflows
- Verify animations render correctly
- Test error recovery
- Check output quality

### Live Tests
- Mark with `@pytest.mark.live` decorator
- Only run when explicitly requested
- Use for validating against real API
- Cache results to reduce costs

## Documentation Standards

- Keep README.md up-to-date with major changes
- Update EXAMPLES.md when adding animations
- Document breaking changes in commit messages
- Add inline comments for complex logic
- Update type hints when changing function signatures

## Best Practices for Copilot Agent

### Good Issue Descriptions Should Include
- Clear description of the problem or enhancement
- Specific files or directories to modify
- Acceptance criteria (e.g., "should include passing tests")
- Examples of desired behavior
- Any relevant context about mathematical concepts

### Types of Tasks Well-Suited for Copilot
- Adding new animation examples
- Fixing LaTeX rendering bugs
- Improving test coverage
- Updating documentation
- Refactoring agent prompts
- Adding new test cases
- Fixing accessibility issues in Gradio UI

### Types of Tasks to Avoid Delegating
- Major architecture changes to the agent system
- Changes requiring deep mathematical domain knowledge
- Security-critical API key handling
- Large-scale refactoring across multiple agents
- Design decisions about visual style

### Iterating on Copilot's Work
- Review pull requests carefully
- Test animations actually render correctly
- Verify LaTeX equations are mathematically accurate
- Check that code follows existing patterns
- Provide specific feedback in PR comments mentioning @copilot

## Getting Help

- **Full Documentation**: See [docs/](docs/) directory
- **Examples**: See [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Testing**: See [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)
- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Environment Variables

Required in `.env` file:
- `ANTHROPIC_API_KEY`: For Claude API access (required)
- `MOONSHOT_API_KEY`: For Kimi K2 API access (optional)

## Common Pitfalls to Avoid

1. **LaTeX Errors**: Always test LaTeX syntax before committing
2. **Missing FFmpeg**: Animations won't render without FFmpeg installed
3. **API Costs**: Don't run live tests repeatedly without caching
4. **Inconsistent Notation**: Keep mathematical notation consistent within an animation
5. **Vague Prompts**: Specify exact camera movements, colors, and timing for animations
6. **Missing Prerequisites**: Ensure knowledge trees build from foundations up
7. **Breaking Changes**: Don't modify core agent interfaces without updating all callers

## Additional Resources

- [Manim Community Documentation](https://docs.manim.community/)
- [LaTeX Mathematical Symbols](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)
- [Claude API Documentation](https://docs.anthropic.com/)
- [pytest Documentation](https://docs.pytest.org/)
