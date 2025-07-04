"""Simple validation tests that don't require external dependencies."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_project_structure():
    """Test basic project structure exists."""
    assert project_root.exists(), "Project root not found"
    
    # Check key directories
    scripts_dir = project_root / "Scripts"
    assert scripts_dir.exists(), "Scripts directory not found"
    assert scripts_dir.is_dir(), "Scripts is not a directory"
    
    tests_dir = project_root / "tests"
    assert tests_dir.exists(), "tests directory not found"
    assert tests_dir.is_dir(), "tests is not a directory"
    
    # Check key files
    app_file = project_root / "app.py"
    assert app_file.exists(), "app.py not found"
    
    readme = project_root / "README.md"
    assert readme.exists(), "README.md not found"
    
    print("✓ Project structure is valid")


def test_scripts_directory_contents():
    """Test that Scripts directory contains Python files."""
    scripts_dir = project_root / "Scripts"
    py_files = list(scripts_dir.glob("*.py"))
    
    assert len(py_files) > 0, "No Python files found in Scripts directory"
    assert len(py_files) > 10, f"Expected more animation scripts, found only {len(py_files)}"
    
    # Check some expected files
    expected_scripts = ["QED.py", "pythagorean.py", "fractal_scene.py"]
    for script in expected_scripts:
        script_path = scripts_dir / script
        assert script_path.exists(), f"Expected script {script} not found"
    
    print(f"✓ Found {len(py_files)} Python scripts in Scripts directory")


def test_script_basic_structure():
    """Test basic structure of a few scripts."""
    scripts_dir = project_root / "Scripts"
    test_scripts = ["pythagorean.py", "fractal_scene.py"]
    
    for script_name in test_scripts:
        script_path = scripts_dir / script_name
        if not script_path.exists():
            continue
            
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic checks
        assert len(content) > 100, f"{script_name} appears to be empty"
        assert "from manim import" in content or "import manim" in content, \
            f"{script_name} doesn't import manim"
        assert "class" in content, f"{script_name} doesn't define any classes"
        assert "def construct" in content, f"{script_name} missing construct method"
        
    print("✓ Script structure validation passed")


def test_no_hardcoded_secrets():
    """Test that scripts don't contain obvious hardcoded secrets."""
    scripts_dir = project_root / "Scripts"
    suspicious_patterns = [
        "sk-",  # OpenAI keys
        "AIza",  # Google API keys
        "api_key=",
        "API_KEY=",
        "password=",
        "PASSWORD=",
    ]
    
    issues = []
    for script_path in scripts_dir.glob("*.py"):
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for line_num, line in enumerate(content.split('\n'), 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
                
            for pattern in suspicious_patterns:
                if pattern in line and '"""' not in line and "'''" not in line:
                    issues.append(f"{script_path.name}:{line_num} - Found '{pattern}'")
    
    assert len(issues) == 0, f"Potential secrets found:\n" + "\n".join(issues)
    print("✓ No hardcoded secrets detected")


def test_environment_setup():
    """Test environment configuration."""
    # Check for .env.example or documentation about env vars
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    
    # At least one should exist or be documented
    assert env_example.exists() or env_file.exists() or \
        "DEEPSEEK_API_KEY" in open(project_root / "README.md").read(), \
        "No environment configuration found or documented"
    
    print("✓ Environment configuration validated")


def test_testing_infrastructure():
    """Test that testing infrastructure is properly set up."""
    # Check test directories
    assert (project_root / "tests" / "unit").exists(), "unit test directory missing"
    assert (project_root / "tests" / "integration").exists(), "integration test directory missing"
    assert (project_root / "tests" / "conftest.py").exists(), "conftest.py missing"
    
    # Check test files were created
    test_files = list((project_root / "tests").rglob("test_*.py"))
    assert len(test_files) > 5, f"Expected more test files, found only {len(test_files)}"
    
    # Check pyproject.toml exists and has test configuration
    pyproject = project_root / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml not found"
    
    with open(pyproject, 'r') as f:
        content = f.read()
        assert "[tool.pytest.ini_options]" in content, "pytest configuration missing"
        assert "test = " in content or "tests = " in content, "test command not configured"
    
    print(f"✓ Testing infrastructure validated with {len(test_files)} test files")


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_project_structure,
        test_scripts_directory_contents,
        test_script_basic_structure,
        test_no_hardcoded_secrets,
        test_environment_setup,
        test_testing_infrastructure,
    ]
    
    failed = 0
    for test_func in test_functions:
        try:
            print(f"\nRunning {test_func.__name__}...")
            test_func()
        except AssertionError as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests completed: {len(test_functions) - failed}/{len(test_functions)} passed")
    
    if failed > 0:
        sys.exit(1)