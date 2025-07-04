import sys
import os
from pathlib import Path

import pytest


class TestSetupValidation:
    """Validation tests to ensure the testing infrastructure is properly configured."""
    
    def test_python_path_configured(self):
        """Test that the Python path includes the project root."""
        project_root = Path(__file__).parent.parent
        assert str(project_root) in sys.path or str(project_root.absolute()) in sys.path
    
    def test_fixtures_available(self, temp_dir, mock_openai_client, sample_math_expression):
        """Test that custom fixtures are available and working."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        assert mock_openai_client is not None
        assert sample_math_expression == "f(x) = x^2 + 2x + 1"
    
    def test_temp_dir_cleanup(self, temp_dir):
        """Test that temporary directories are created and will be cleaned up."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that the unit test marker is properly configured."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that the integration test marker is properly configured."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that the slow test marker is properly configured."""
        assert True
    
    def test_mock_env_vars(self, mock_env_vars):
        """Test that environment variables can be mocked."""
        assert os.environ.get("OPENAI_API_KEY") == "test-api-key"
        assert os.environ.get("DEEPSEEK_API_KEY") == "test-deepseek-key"
        assert os.environ.get("GEMINI_API_KEY") == "test-gemini-key"
    
    def test_capture_logs(self, capture_logs):
        """Test that log capturing is working."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        
        assert "Test log message" in capture_logs.text
    
    def test_mock_file_system(self, mock_file_system):
        """Test that the mock file system fixture creates expected structure."""
        scripts_dir = mock_file_system / "Scripts"
        assert scripts_dir.exists()
        assert (scripts_dir / "__init__.py").exists()
        assert (scripts_dir / "example.py").exists()
        assert (scripts_dir / "examples" / "basic.py").exists()
    
    def test_pytest_configuration(self):
        """Test that pytest is properly configured."""
        import pytest
        assert hasattr(pytest, "main")
        assert hasattr(pytest, "fixture")
        assert hasattr(pytest, "mark")


@pytest.mark.unit 
class TestCoverageValidation:
    """Tests to validate coverage configuration."""
    
    def test_coverage_installed(self):
        """Test that pytest-cov is installed and importable."""
        try:
            import pytest_cov
            assert pytest_cov is not None
        except ImportError:
            pytest.fail("pytest-cov is not installed")
    
    def test_sample_coverage_target(self):
        """Test a simple function to ensure coverage tracking works."""
        def add(a: int, b: int) -> int:
            return a + b
        
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0