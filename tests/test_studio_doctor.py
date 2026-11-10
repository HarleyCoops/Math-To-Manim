"""Studio doctor: tool checks, smoke-render parsing and the env lock, with no real tools."""

import json
from pathlib import Path

from studio import doctor, settings
from studio.cli import build_parser


def test_find_blender_and_ant_honour_the_environment(tmp_path, monkeypatch):
    blender = tmp_path / "blender.exe"
    ant = tmp_path / "ant.exe"
    monkeypatch.setenv("STUDIO_BLENDER", str(blender))
    monkeypatch.setenv("STUDIO_ANT", str(ant))
    assert settings.find_blender() == blender
    assert settings.find_ant() == ant


def test_runs_dir_follows_the_shared_rule(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    assert settings.default_runs_dir() == tmp_path / "studio"


def test_check_tool_reports_version_or_absence():
    found = doctor.check_tool("ffmpeg", ["ffmpeg", "-version"],
                              lambda cmd, timeout: (0, "\nffmpeg version 7.1\nmore"))
    assert found.ok and found.version == "ffmpeg version 7.1" and found.required
    absent = doctor.check_tool("typst", ["typst", "--version"],
                               lambda cmd, timeout: (127, "not found"))
    assert not absent.ok and absent.version is None and not absent.required


def test_blender_smoke_forces_opengl_and_averages_steady_frames(tmp_path):
    seen = {}

    def runner(command, timeout):
        seen["command"] = command
        out_dir = Path(command[command.index("--") + 1])
        (out_dir / "frame_0001.png").write_bytes(b"png")
        (out_dir / "result.json").write_text(json.dumps({
            "blender": "5.2.3 LTS", "engine": "BLENDER_EEVEE", "width": 1920,
            "height": 1080, "samples": 64, "seconds_per_frame": [6.0, 1.5, 1.7],
            "gpu": {"backend": "OPENGL"}}), encoding="utf-8")
        return 0, "STUDIO_SMOKE_OK"

    result = doctor.blender_smoke(tmp_path / "blender.exe", tmp_path / "out", runner)
    command = seen["command"]
    assert command[command.index("--gpu-backend") + 1] == "opengl"
    assert "--background" in command and "--factory-startup" in command
    assert result["ok"] is True
    assert result["first_frame_seconds"] == 6.0
    assert result["seconds_per_frame"] == 1.6
    assert result["frames"] == ["frame_0001.png"]


def test_blender_smoke_failure_keeps_the_output(tmp_path):
    result = doctor.blender_smoke(tmp_path / "blender.exe", tmp_path / "out",
                                  lambda cmd, timeout: (1, "EEVEE crashed"))
    assert result == {"ok": False, "exit_code": 1, "detail": "EEVEE crashed"}


def test_doctor_writes_the_lock_and_fails_when_a_required_tool_is_missing(
        tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    monkeypatch.setenv("STUDIO_BLENDER", str(tmp_path / "blender.exe"))
    monkeypatch.setenv("STUDIO_ANT", str(tmp_path / "ant.exe"))

    def runner(command, timeout):
        if "latex" in command[0]:
            return 127, "not found"
        if command[1:3] == ["auth", "status"]:
            return 0, "Logged in to Example Org as someone"
        return 0, f"{Path(command[0]).name} 1.0"

    lines = []
    code = doctor.run_doctor(render=False, runner=runner, log=lines.append)
    lock = json.loads((tmp_path / "studio" / "env.lock.json").read_text(encoding="utf-8"))
    assert code == 1
    assert lock["tools"]["latex"]["ok"] is False
    assert lock["tools"]["ffmpeg"]["ok"] is True
    assert lock["engines"] == {}
    assert lock["managed_agents"]["signed_in"] is True
    assert "sk-ant" not in json.dumps(lock)
    assert any("NOT ready" in line and "latex" in line for line in lines)


def test_doctor_is_ready_when_every_required_tool_answers(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    monkeypatch.setenv("STUDIO_BLENDER", str(tmp_path / "blender.exe"))
    monkeypatch.setenv("STUDIO_ANT", str(tmp_path / "ant.exe"))
    code = doctor.run_doctor(render=False, runner=lambda cmd, timeout: (0, "tool 1.0"),
                             log=lambda line: None)
    assert code == 0


def test_cli_help_names_the_doctor():
    help_text = build_parser().format_help()
    assert "math-to-manim-studio" in help_text
    assert "doctor" in help_text
