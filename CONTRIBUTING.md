# Contributing to Math-To-Manim

Thank you for your interest in contributing to Math-To-Manim! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Contributing Code](#contributing-code)
  - [Contributing Examples](#contributing-examples)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug in Math-To-Manim, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots or error messages (if applicable)
- Your environment (OS, Python version, Manim version, etc.)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the enhancement
- Why this enhancement would be useful
- Any relevant examples or mockups

### Contributing Code

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Write or update tests as necessary
5. Ensure all tests pass
6. Submit a pull request

### Contributing Examples

One of the most valuable contributions you can make is to add new examples of mathematical animations. To contribute an example:

1. Create a new Python file in the appropriate directory (or create a new directory if needed)
2. Include detailed comments explaining the mathematical concepts
3. Ensure the code runs successfully with Manim
4. Add documentation for the example in `docs/EXAMPLES.md`
5. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/HarleyCoops/Math-To-Manim.git
   cd Math-To-Manim
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg (required for Manim):
   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

5. Set up environment variables:
   ```bash
   # Create .env file with your API key
   echo "DEEPSEEK_API_KEY=your_key_here" > .env
   ```

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation as necessary
3. Include tests for new features
4. Ensure all tests pass
5. Submit the pull request with a clear description of the changes

## Style Guidelines

### Python Code

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Include docstrings for all functions and classes
- Keep functions focused on a single responsibility
- Add comments for complex sections of code

### Manim Code

- Organize scenes into logical sections
- Use descriptive names for mobjects and animations
- Include comments explaining the mathematical concepts
- Use consistent formatting for LaTeX equations
- Optimize animations for clarity and educational value

### Documentation

- Use clear, concise language
- Include examples where appropriate
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting

## Community

- Join our [Discord server](https://discord.gg/example) to connect with other contributors
- Follow the project on [Twitter](https://twitter.com/example) for updates
- Check out the [project website](https://example.com) for more information

Thank you for contributing to Math-To-Manim!

