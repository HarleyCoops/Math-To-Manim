"""Missing system tools must never spend a scene-repair model call."""

from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from mythos import cli, doctor, render
from mythos.harness import MythosHarness
from mythos.service import MythosService


SCENE = '''from manim import *
class Demo(ThreeDScene):
    def construct(self):
        self.wait(0.1)
'''


@pytest.fixture
def doctor_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor, "load_env_file", lambda: None)
    monkeypatch.setattr(doctor, "resolve_command", lambda command: command)
    monkeypatch.setattr(doctor, "resolve_manim", lambda: ["mock-manim"])
    monkeypatch.setattr(doctor, "default_runs_dir", lambda: tmp_path / "runs")
    monkeypatch.setattr(doctor, "run_model", Mock(side_effect=AssertionError("model call")))
    monkeypatch.setattr(doctor.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=0, stdout="Manim Community v0.19.0", stderr=""))
    tools = {tool: f"/tools/{tool}" for tool in ("backend", "ffmpeg", "latex", "dvisvgm")}
    monkeypatch.setattr(doctor, "_which", tools.get)
    return tools


@pytest.mark.parametrize("missing", [("latex",), ("dvisvgm",), ("latex", "dvisvgm")])
def test_doctor_missing_tex_fails_without_misleading_summary(doctor_tools, capsys, missing):
    for tool in missing:
        del doctor_tools[tool]
    assert cli.main(["doctor", "--command", "backend"]) == 1
    output = capsys.readouterr().out
    for tool in missing:
        assert f"[FAIL]{tool} not found on PATH" in output
    assert "MathTex/Tex cannot render" in output
    assert f"{len(missing)} check(s) failed" in output
    assert "all checks passed" not in output
    assert "README: Render system setup" in output
    assert "MiKTeX" in output
    doctor.run_model.assert_not_called()


def test_doctor_explicit_non_latex_scope_still_reports_missing_capability(doctor_tools, capsys):
    del doctor_tools["latex"]
    del doctor_tools["dvisvgm"]
    assert cli.main(["doctor", "--command", "backend", "--no-latex"]) == 0
    output = capsys.readouterr().out
    assert "MathTex/Tex cannot render" in output
    assert "non-LaTeX checks passed (LaTeX checks excluded)" in output
    assert "all checks passed" not in output


def test_doctor_no_latex_does_not_exclude_ffmpeg(doctor_tools, capsys):
    del doctor_tools["ffmpeg"]
    assert doctor.run_doctor(command="backend", no_latex=True) == 1
    assert "[FAIL]ffmpeg not found" in capsys.readouterr().out


def test_doctor_complete_toolchain_passes(doctor_tools, capsys):
    assert doctor.main(["--command", "backend"]) == 0
    assert "summary: all checks passed" in capsys.readouterr().out


@pytest.fixture
def harness(tmp_path, monkeypatch):
    harness = MythosHarness(runs_dir=tmp_path, offline=False)
    monkeypatch.setattr(harness, "_run_stage", lambda *args: ({"mocked": True}, False))

    def codegen(run_dir, prompt, scene_spec, manifest):
        code_path = run_dir / "mythos_scene.py"
        code_path.write_text(SCENE, encoding="utf-8")
        return code_path, "Demo"

    monkeypatch.setattr(harness, "_codegen", codegen)
    monkeypatch.setattr(harness, "_model", Mock(side_effect=AssertionError("model call")))
    monkeypatch.setattr(render, "resolve_manim", lambda: ["mock-manim"])
    # A local optional chktex installation must not consume our fake render replies.
    monkeypatch.setattr("mythos.scene_checks._run_chktex", lambda text: [])
    monkeypatch.setattr("mythos.scene_checks._run_lualatex", lambda text: [])
    return harness


@pytest.mark.parametrize("tool", ["latex", "dvisvgm", "ffmpeg", "xelatex"])
def test_missing_binary_stops_before_model_repair_and_records_evidence(harness, monkeypatch, tool):
    output = f"FileNotFoundError: [Errno 2] No such file or directory: '{tool}'\n"
    child = Mock(return_value=SimpleNamespace(returncode=1, stdout="", stderr=output))
    monkeypatch.setattr(render.subprocess, "run", child)
    manifest = harness.run("render missing dependency", render=True, max_repairs=3)
    harness._model.assert_not_called()
    assert child.call_count == 1
    assert manifest["status"]["render"] == "failed"
    assert manifest["static_check"]["passed"] is True
    assert manifest["renders"][0]["exit_code"] == 1  # retain the actual child exit code
    error = manifest["render_error"]
    assert error["type"] == "environment"
    assert error["missing_dependencies"] == [tool]
    assert "PATH" in error["detail"]
    run_dir = harness.runs_dir / manifest["run_id"]
    assert json.loads((run_dir / "manifest.json").read_text("utf-8"))["render_error"] == error
    log = (run_dir / manifest["renders"][0]["log"]).read_text("utf-8")
    assert output in log
    assert "Skipping model scene repair" in log
    assert not list(run_dir.glob("repair_*.raw.txt"))


def test_missing_manim_launcher_stops_before_model_repair(harness, monkeypatch):
    child = Mock(side_effect=FileNotFoundError(2, "No such file or directory", "mock-manim"))
    monkeypatch.setattr(render.subprocess, "run", child)
    manifest = harness.run("missing Manim", render=True)
    assert manifest["render_error"]["missing_dependencies"] == ["manim"]
    harness._model.assert_not_called()
    assert child.call_count == 1


@pytest.mark.parametrize("path", ["latex", "/Library/TeX/texbin/dvisvgm",
                                  r"C:\Program Files\MiKTeX\miktex\bin\x64\latex.exe"])
def test_missing_binary_named_paths_and_ansi(path):
    output = f"\x1b[31mFileNotFoundError: [Errno 2] No such file or directory: '{path}'\x1b[0m"
    expected = "dvisvgm" if "dvisvgm" in path else "latex"
    assert render.missing_render_dependencies(output) == (expected,)


@pytest.mark.parametrize("output", [
    "FileNotFoundError: [Errno 2] No such file or directory: 'latex.svg'",
    "FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'",
    "FileNotFoundError: [WinError 2] The system cannot find the file specified",
    "ValueError: latex error converting to dvi. See log output above.",
    "TypeError: MathTex() got an unexpected keyword argument 'latex'",
    "NameError: name 'dvisvgm' is not defined",
    "ModuleNotFoundError: No module named 'my_scene_helper'",
    "latex not found in the scene's equation dictionary",
    'Traceback (most recent call last):\n  File "mythos_scene.py", line 8, in construct\n'
    '    open("latex")\nFileNotFoundError: [Errno 2] No such file or directory: \'latex\'',
])
def test_arbitrary_scene_errors_are_not_missing_binary_errors(output):
    assert render.missing_render_dependencies(output) == ()


def test_missing_manim_python_module():
    assert render.missing_render_dependencies("/venv/bin/python: No module named manim\n") == ("manim",)


@pytest.mark.parametrize("output", [
    (
        r'File "C:\venv\Lib\site-packages\manim\utils\tex_file_writing.py", line 211, in compile_tex'
        '\n  subprocess.run(command)\n'
        r'File "C:\Python312\Lib\subprocess.py", line 1548, in _execute_child'
        '\nFileNotFoundError: [WinError 2] The system cannot find the file specified\n'
    ),
    # Captured Manim/Rich Windows shape: long filenames wrap mid-word.
    (
        '| C:\\venv\\Lib\\site-packages\\manim\\utils\\tex_file_w |\n'
        '| riting.py:207 in compile_tex                         |\n'
        '|                                                     |\n'
        '|   204 tex_file,                                      |\n'
        '|   205 tex_dir,                                       |\n'
        '| > 207 cp = subprocess.run(command)                   |\n'
        '| C:\\Python312\\Lib\\subprocess.py:1551 in _execute_child |\n'
        'FileNotFoundError: [WinError 2] The system cannot find the file specified\n'
    ),
    (
        r'File "C:\venv\Lib\site-packages\manim\utils\tex_file_writing.py", line 241, in convert_to_svg'
        '\n  subprocess.run(command)\n'
        r'File "C:\Python312\Lib\subprocess.py", line 1548, in _execute_child'
        '\nFileNotFoundError: [WinError 2] The system cannot find the file specified\n'
    ),
])
def test_windows_tex_subprocess_failure_stops_before_repair(harness, monkeypatch, output):
    monkeypatch.setattr(render.subprocess, "run", Mock(return_value=SimpleNamespace(
        returncode=1, stdout="", stderr=output)))
    manifest = harness.run("Windows missing compiler", render=True)
    assert manifest["render_error"]["missing_dependencies"] == ["tex-toolchain"]
    assert "MathTex/Tex cannot render" in manifest["render_error"]["detail"]
    harness._model.assert_not_called()


@pytest.mark.parametrize("output", [
    "AttributeError: 'ThreeDCamera' object has no attribute 'animate'",
    "FileNotFoundError: [Errno 2] No such file or directory: 'diagram.svg'",
    "ValueError: latex error converting to dvi. See log output above.",
    'Traceback (most recent call last):\n  File "mythos_scene.py", line 8, in construct\n'
    '    open("latex")\nFileNotFoundError: [Errno 2] No such file or directory: \'latex\'',
])
def test_scene_error_still_invokes_model_repair_and_renders(harness, monkeypatch, output):
    replies = [SimpleNamespace(returncode=1, stdout="", stderr=output),
               SimpleNamespace(returncode=0, stdout="rendered", stderr="")]
    child = Mock(side_effect=replies)
    monkeypatch.setattr(render.subprocess, "run", child)
    harness._model.side_effect = None
    harness._model.return_value = f"```python\n{SCENE}```"
    manifest = harness.run("repair scene code", render=True)
    assert manifest["status"]["render"] == "complete"
    assert "render_error" not in manifest
    assert [item["exit_code"] for item in manifest["renders"]] == [1, 0]
    harness._model.assert_called_once()
    assert "Repair it surgically" in harness._model.call_args.args[0]
    assert output in harness._model.call_args.args[0]
    assert child.call_count == 2


def test_static_scene_failure_still_invokes_model_repair(harness, monkeypatch):
    verify = Mock(side_effect=[(False, "invalid scene syntax"), (True, None)])
    monkeypatch.setattr(harness, "_verify", verify)
    monkeypatch.setattr(render.subprocess, "run", Mock(return_value=SimpleNamespace(
        returncode=0, stdout="rendered", stderr="")))
    harness._model.side_effect = None
    harness._model.return_value = f"```python\n{SCENE}```"
    manifest = harness.run("static repair", render=True)
    assert manifest["status"]["render"] == "complete"
    harness._model.assert_called_once()


def test_non_latex_render_does_not_require_tex_tools(harness, monkeypatch):
    monkeypatch.setattr(render.shutil, "which", lambda tool: None)
    monkeypatch.setattr(render.subprocess, "run", Mock(return_value=SimpleNamespace(
        returncode=0, stdout="rendered geometry", stderr="")))
    manifest = harness.run("geometry only", render=True)
    assert manifest["status"]["render"] == "complete"
    assert "render_error" not in manifest
    harness._model.assert_not_called()


def test_timeout_remains_non_repairable(harness, monkeypatch):
    monkeypatch.setattr(render.subprocess, "run", Mock(side_effect=subprocess.TimeoutExpired(
        "mock-manim", 5, stderr=b"partial render")))
    manifest = harness.run("slow scene", render=True)
    assert manifest["render_timed_out"] is True
    assert "render_error" not in manifest
    harness._model.assert_not_called()


def test_cli_environment_failure_returns_nonzero(harness, monkeypatch):
    monkeypatch.setattr("mythos.harness.MythosHarness", lambda **kwargs: harness)
    monkeypatch.setattr(render.subprocess, "run", Mock(return_value=SimpleNamespace(
        returncode=1, stdout="", stderr="FileNotFoundError: [Errno 2] No such file or directory: 'latex'")))
    assert cli.main(["run", "missing latex", "--render"]) == 1
    harness._model.assert_not_called()


def test_service_environment_failure_is_failed_job(harness, monkeypatch):
    service = MythosService(runs_dir=harness.runs_dir, harness_factory=lambda **kwargs: harness)
    monkeypatch.setattr(render.subprocess, "run", Mock(return_value=SimpleNamespace(
        returncode=1, stdout="", stderr="FileNotFoundError: [Errno 2] No such file or directory: 'dvisvgm'")))
    job = service.run_sync("missing converter", render=True)
    assert job.status == "failed"
    assert job.manifest["render_error"]["type"] == "environment"
    assert "dvisvgm" in job.error
    harness._model.assert_not_called()


def test_render_workspace_records_environment_error_and_can_retry_after_install(harness, monkeypatch):
    manifest = harness.run("existing scene")
    run_dir = harness.runs_dir / manifest["run_id"]
    child = Mock(side_effect=[
        SimpleNamespace(returncode=1, stdout="", stderr="FileNotFoundError: [Errno 2] No such file or directory: 'latex'"),
        SimpleNamespace(returncode=0, stdout="rendered", stderr=""),
    ])
    monkeypatch.setattr(render.subprocess, "run", child)
    blocked = harness.render_workspace(run_dir, "Demo")
    assert blocked["exit_code"] != 0
    assert blocked["manifest"]["render_error"]["type"] == "environment"
    assert "PATH" in blocked["output"]
    repaired_environment = harness.render_workspace(run_dir, "Demo")
    assert repaired_environment["exit_code"] == 0
    assert repaired_environment["manifest"]["status"]["render"] == "complete"
    assert "render_error" not in repaired_environment["manifest"]
    old_attempt, new_attempt = repaired_environment["manifest"]["renders"]
    assert old_attempt["error"]["type"] == "environment"
    assert old_attempt["log"] != new_attempt["log"]
    assert "Skipping model scene repair" in (run_dir / old_attempt["log"]).read_text("utf-8")
    harness._model.assert_not_called()
