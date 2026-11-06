"""`math-to-manim gif`: source resolution logic (no ffmpeg required)."""

from __future__ import annotations

import json

import pytest

from mythos.cli import build_parser
from mythos.gifs import resolve_source


def _run(tmp_path, run_id="20260710-000000-test", scene_name="TestScene"):
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps({"scene_name": scene_name}), encoding="utf-8")
    return run_dir


def test_resolve_source_finds_the_fresh_render_inside_the_run(tmp_path):
    # render.py pins Manim's media dir inside the run directory.
    run_dir = _run(tmp_path)
    old = run_dir / "media" / "videos" / "mythos_scene" / "480p15"
    new = run_dir / "media" / "videos" / "mythos_scene" / "720p15"
    partial = old / "partial_movie_files" / "TestScene"
    for d in (old, new, partial):
        d.mkdir(parents=True)
    (old / "TestScene.mp4").write_bytes(b"old")
    (partial / "TestScene.mp4").write_bytes(b"partial")
    newest = new / "TestScene.mp4"
    newest.write_bytes(b"new")

    src, out = resolve_source("20260710-000000-test", runs_dir=tmp_path / "runs")
    assert src == newest
    assert out == run_dir / "TestScene.gif"


def test_resolve_source_unrendered_run_says_how_to_render(tmp_path):
    _run(tmp_path)
    with pytest.raises(FileNotFoundError, match="Render first"):
        resolve_source("20260710-000000-test", runs_dir=tmp_path / "runs")


def test_resolve_source_accepts_mp4_path(tmp_path):
    mp4 = tmp_path / "film.mp4"
    mp4.write_bytes(b"x")
    src, out = resolve_source(str(mp4))
    assert src == mp4
    assert out == tmp_path / "film.gif"


def test_resolve_source_rejects_unknown_target():
    with pytest.raises(FileNotFoundError):
        resolve_source("definitely-not-a-run-id")


def test_resolve_source_uses_run_manifest(tmp_path):
    run_dir = _run(tmp_path)
    (run_dir / "TestScene.mp4").write_bytes(b"x")
    src, out = resolve_source("20260710-000000-test", runs_dir=tmp_path / "runs")
    assert src == run_dir / "TestScene.mp4"
    assert out == run_dir / "TestScene.gif"


def test_cli_wires_gif_subcommand():
    args = build_parser().parse_args(
        ["gif", "somerun", "-o", "out.gif", "--fps", "10", "--width", "480"])
    assert args.target == "somerun"
    assert args.output == "out.gif"
    assert args.fps == 10 and args.width == 480
