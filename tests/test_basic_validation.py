import sys
import os
from pathlib import Path

import pytest


class TestBasicSetup:
    """Basic validation tests that don't require external dependencies."""
    
    def test_testing_infrastructure_exists(self):
        """Test that basic testing infrastructure is in place."""
        tests_dir = Path(__file__).parent
        assert tests_dir.exists()
        assert tests_dir.name == "tests"
        assert (tests_dir / "__init__.py").exists()
        assert (tests_dir / "unit" / "__init__.py").exists()
        assert (tests_dir / "integration" / "__init__.py").exists()
    
    def test_project_structure(self):
        """Test that the project has expected structure."""
        project_root = Path(__file__).parent.parent
        assert (project_root / "README.md").exists()
        assert (project_root / "pyproject.toml").exists()
        assert (project_root / "Scripts").exists()
    
    def test_python_version(self):
        """Test that Python version meets minimum requirements."""
        assert sys.version_info >= (3, 10), "Python 3.10+ is required"
    
    @pytest.mark.unit
    def test_markers_work(self):
        """Test that pytest markers are configured."""
        assert True
    
    def test_simple_arithmetic(self):
        """Basic test to ensure pytest is working."""
        assert 2 + 2 == 4
        assert 10 * 5 == 50
        assert 100 / 4 == 25
    
    def test_path_operations(self):
        """Test basic path operations."""
        test_path = Path("/tmp/test_path")
        assert test_path.parent == Path("/tmp")
        assert test_path.name == "test_path"