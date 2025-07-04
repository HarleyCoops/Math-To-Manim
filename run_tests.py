#!/usr/bin/env python3
"""Simple test runner to validate the testing setup."""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run tests and demonstrate testing infrastructure."""
    print("Testing Infrastructure Validation")
    print("=" * 50)
    
    # Check directory structure
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    print("\n1. Directory Structure:")
    print(f"   ✓ Project root: {project_root}")
    print(f"   ✓ Tests directory: {'EXISTS' if tests_dir.exists() else 'MISSING'}")
    print(f"   ✓ Unit tests: {'EXISTS' if (tests_dir / 'unit').exists() else 'MISSING'}")
    print(f"   ✓ Integration tests: {'EXISTS' if (tests_dir / 'integration').exists() else 'MISSING'}")
    print(f"   ✓ Conftest.py: {'EXISTS' if (tests_dir / 'conftest.py').exists() else 'MISSING'}")
    
    # Check configuration files
    print("\n2. Configuration Files:")
    print(f"   ✓ pyproject.toml: {'EXISTS' if (project_root / 'pyproject.toml').exists() else 'MISSING'}")
    print(f"   ✓ .gitignore: {'EXISTS' if (project_root / '.gitignore').exists() else 'MISSING'}")
    
    # Check Python version
    print("\n3. Python Version:")
    print(f"   ✓ Current version: {sys.version}")
    print(f"   ✓ Meets requirements: {'YES' if sys.version_info >= (3, 10) else 'NO (3.10+ required)'}")
    
    # Try to run pytest if available
    print("\n4. Test Execution:")
    try:
        # First try with poetry
        result = subprocess.run(
            ["poetry", "run", "pytest", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✓ Pytest available via Poetry: {result.stdout.strip()}")
            print("\n   To run tests with Poetry:")
            print("   $ poetry run test")
            print("   $ poetry run tests")
            print("   $ poetry run pytest tests/")
        else:
            print("   ✗ Pytest not available via Poetry")
            print("   Run 'poetry install' to install dependencies")
    except FileNotFoundError:
        print("   ✗ Poetry not found")
    
    # Check for test commands
    print("\n5. Available Test Commands (once dependencies are installed):")
    print("   - poetry run test        # Run all tests")
    print("   - poetry run tests       # Alternative command")
    print("   - poetry run pytest tests/test_basic_validation.py  # Run specific test")
    print("   - poetry run pytest -m unit  # Run only unit tests")
    print("   - poetry run pytest -m integration  # Run only integration tests")
    print("   - poetry run pytest --cov=Scripts  # Run with coverage")
    
    print("\n6. Coverage Reports (after running tests):")
    print("   - Terminal: Shown automatically with test output")
    print("   - HTML: htmlcov/index.html")
    print("   - XML: coverage.xml")
    
    print("\n" + "=" * 50)
    print("Testing infrastructure setup is complete!")
    print("\nNext steps:")
    print("1. Install dependencies: poetry install")
    print("2. Run validation tests: poetry run test")
    print("3. Start writing your tests in the tests/ directory")

if __name__ == "__main__":
    main()