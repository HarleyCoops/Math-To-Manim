"""Unit tests for smolagent prototype."""

import pytest
from pathlib import Path
import ast


class TestSmolagentPrototype:
    """Test the smolagent prototype implementation."""
    
    @pytest.fixture
    def smolagent_path(self):
        """Get path to smolagent prototype."""
        return Path(__file__).parent.parent.parent / "smolagent_prototype.py"
    
    @pytest.mark.unit
    def test_smolagent_prototype_exists(self, smolagent_path):
        """Test that smolagent_prototype.py exists."""
        assert smolagent_path.exists(), "smolagent_prototype.py not found"
    
    @pytest.mark.unit
    def test_smolagent_imports(self, smolagent_path):
        """Test that smolagent prototype has expected imports."""
        with open(smolagent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Expected imports for a smolagent implementation
        expected_patterns = [
            'import',  # Has imports
            'from',    # Has from imports
        ]
        
        for pattern in expected_patterns:
            assert pattern in content, f"Missing expected pattern: {pattern}"
    
    @pytest.mark.unit
    def test_smolagent_structure(self, smolagent_path):
        """Test the structure of smolagent prototype using AST."""
        with open(smolagent_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        # Collect defined elements
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        # Should have at least some structure
        assert len(classes) > 0 or len(functions) > 0, \
            "smolagent_prototype.py appears to be empty or have no definitions"
    
    @pytest.mark.unit
    def test_prompt_transformation_patterns(self, smolagent_path):
        """Test for prompt transformation patterns."""
        with open(smolagent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for patterns related to prompt transformation
        transformation_patterns = [
            'prompt',
            'transform',
            'latex',
            'LaTeX',
            'enhance',
            'detailed'
        ]
        
        patterns_found = sum(1 for pattern in transformation_patterns 
                           if pattern.lower() in content.lower())
        
        assert patterns_found >= 2, \
            "smolagent_prototype.py should contain prompt transformation logic"
    
    @pytest.mark.unit
    def test_smolagent_configuration(self, smolagent_path):
        """Test for configuration patterns in smolagent."""
        with open(smolagent_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        # Look for configuration-related patterns
        has_config = False
        
        for node in ast.walk(tree):
            # Check for config dictionaries or classes
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if 'config' in target.id.lower() or 'setting' in target.id.lower():
                            has_config = True
                            break
            
            # Check for initialization methods
            elif isinstance(node, ast.FunctionDef):
                if node.name in ['__init__', 'initialize', 'setup', 'configure']:
                    has_config = True
                    break
        
        assert has_config, "smolagent_prototype.py should have configuration setup"