"""`math-to-manim gif`: source resolution logic (no ffmpeg required)."""

from __future__ import annotations

import json

import pytest

from mythos.cli import build_parser
from mythos.gifs import find_scene_mp4, resolve_source


def test_find_scene_mp4_prefers_newest_and_skips_partials(tmp_path):
    old = tmp_path / "scene_a" / "480p15"
    new = tmp_path / "scene_a" / "720p15"
    partial = tmp_path / "scene_a" / "480p15" / "partial_movie_files" / "MyScene"
    for d in (old, new, partial):
        d.mkdir(parents=True)
    (old / "MyScene.mp4").write_bytes(b"old")
    (partial / "MyScene.mp4").write_bytes(b"partial")
    newest = new / "MyScene.mp4"
    newest.write_bytes(b"new")

    found = find_scene_mp4("MyScene", media_root=tmp_path)
    assert found == newest


def test_find_scene_mp4_missing_returns_none(tmp_path):
    assert find_scene_mp4("NoSuchScene", media_root=tmp_path) is None


def test_resolve_source_accepts_mp4_path(tmp_path):
    mp4 = tmp_path / "film.mp4"
    mp4.write_bytes(b"x")
    src, out = resolve_source(str(mp4))
    assert src == mp4
    assert out == tmp_path / "film.gif"


def test_resolve_source_rejects_unknown_target():
    with pytest.raises(FileNotFoundError):
        resolve_source("definitely-not-a-run-id")


def test_resolve_source_uses_run_manifest(tmp_path, monkeypatch):
    import mythos.gifs as gifs_mod

    run_dir = tmp_path / "runs" / "20260710-000000-test"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps({"scene_name": "TestScene"}), encoding="utf-8")
    (run_dir / "TestScene.mp4").write_bytes(b"x")
    monkeypatch.setattr(gifs_mod, "default_runs_dir",
                        lambda: tmp_path / "runs")
    src, out = resolve_source("20260710-000000-test")
    assert src == run_dir / "TestScene.mp4"
    assert out == run_dir / "TestScene.gif"


def test_cli_wires_gif_subcommand():
    args = build_parser().parse_args(
        ["gif", "somerun", "-o", "out.gif", "--fps", "10", "--width", "480"])
    assert args.target == "somerun"
    assert args.output == "out.gif"
    assert args.fps == 10 and args.width == 480
