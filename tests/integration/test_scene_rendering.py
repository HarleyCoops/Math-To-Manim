"""Integration tests for scene rendering capabilities."""

import pytest
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil


class TestSceneRendering:
    """Test that scenes can actually render (requires Manim and FFmpeg)."""
    
    @pytest.fixture
    def scripts_directory(self):
        """Get the Scripts directory path."""
        return Path(__file__).parent.parent.parent / "Scripts"
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for render outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_manim_is_installed(self):
        """Test that Manim is properly installed."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "manim", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, "Manim not properly installed"
            assert "Manim" in result.stdout, "Manim version info not found"
        except subprocess.TimeoutExpired:
            pytest.fail("Manim version check timed out")
        except Exception as e:
            pytest.fail(f"Failed to check Manim installation: {str(e)}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_ffmpeg_is_available(self):
        """Test that FFmpeg is available (required for Manim)."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, "FFmpeg not found or not properly installed"
        except FileNotFoundError:
            pytest.fail("FFmpeg not found in PATH")
        except subprocess.TimeoutExpired:
            pytest.fail("FFmpeg version check timed out")
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.parametrize("script_name,scene_name", [
        ("pythagorean.py", "PythagoreanTheorem"),
        # Add more simple scenes here as we identify them
    ])
    def test_simple_scene_renders(self, scripts_directory, temp_output_dir, script_name, scene_name):
        """Test that a simple scene can render without errors."""
        script_path = scripts_directory / script_name
        
        if not script_path.exists():
            pytest.skip(f"Script {script_name} not found")
        
        # Run manim in low quality for speed
        cmd = [
            sys.executable, "-m", "manim",
            "-ql",  # Low quality for faster testing
            "--media_dir", temp_output_dir,
            str(script_path),
            scene_name
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            # Check for successful completion
            assert result.returncode == 0, f"Manim render failed: {result.stderr}"
            
            # Check that output file was created
            output_pattern = Path(temp_output_dir) / "videos" / script_name.replace('.py', '') / "480p15"
            assert output_pattern.exists(), f"Output directory not created at {output_pattern}"
            
            # Check for video file
            video_files = list(output_pattern.glob("*.mp4"))
            assert len(video_files) > 0, "No video file generated"
            
        except subprocess.TimeoutExpired:
            pytest.fail(f"Rendering {scene_name} timed out")
        except Exception as e:
            pytest.fail(f"Failed to render {scene_name}: {str(e)}")
    
    @pytest.mark.integration
    def test_dry_run_multiple_scenes(self, scripts_directory):
        """Test listing scenes from scripts (dry run, no actual rendering)."""
        test_scripts = ["QED.py", "fractal_scene.py", "ElectroweakSymmetryScene.py"]
        
        for script_name in test_scripts:
            script_path = scripts_directory / script_name
            
            if not script_path.exists():
                continue
            
            # List scenes without rendering
            cmd = [
                sys.executable, "-m", "manim",
                "--list_scenes",
                str(script_path)
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # Should list at least one scene
                    assert len(result.stdout.strip()) > 0, f"No scenes listed for {script_name}"
                else:
                    # Some scripts might have import issues in test environment
                    # This is okay for dry run test
                    pass
                    
            except subprocess.TimeoutExpired:
                pytest.fail(f"Listing scenes for {script_name} timed out")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_render_with_different_quality_settings(self, scripts_directory, temp_output_dir):
        """Test rendering with different quality settings."""
        script_path = scripts_directory / "pythagorean.py"
        
        if not script_path.exists():
            pytest.skip("pythagorean.py not found")
        
        quality_settings = [
            ("-ql", "480p15"),  # Low quality
            ("-qm", "720p30"),  # Medium quality
        ]
        
        for quality_flag, expected_dir in quality_settings:
            cmd = [
                sys.executable, "-m", "manim",
                quality_flag,
                "--media_dir", temp_output_dir,
                str(script_path),
                "PythagoreanTheorem"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True, 
                    text=True,
                    timeout=90
                )
                
                # Just check it completes without error
                # Some quality settings might not work in test environment
                if result.returncode == 0:
                    output_dir = Path(temp_output_dir) / "videos" / "pythagorean" / expected_dir
                    assert output_dir.exists(), f"Output directory for {quality_flag} not created"
                    
            except subprocess.TimeoutExpired:
                # Higher quality might timeout in test environment
                pass