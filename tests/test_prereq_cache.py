"""WAR-1530: prerequisite cache survives a process-style reload."""

from __future__ import annotations

import importlib

from mythos.prereq_cache import PrerequisiteCache
from mythos.settings import PipelineSettings


KNOWLEDGE_MAP = {
    "target": "heat equation",
    "nodes": [
        {"id": "heat", "name": "heat equation", "depth": 0},
        {"id": "fourier", "name": "Fourier series", "depth": 1},
        {"id": "deriv", "name": "partial derivatives", "depth": 2},
    ],
    "edges": [["deriv", "fourier"], ["fourier", "heat"]],
}


def test_cache_write_reload_read(tmp_path):
    first = PrerequisiteCache(tmp_path / "prerequisites.json", ttl_days=30)
    first.put("heat equation", ["Fourier series", "partial derivatives"])
    assert first.path.is_file()

    reloaded = importlib.reload(importlib.import_module("mythos.prereq_cache"))
    second = reloaded.PrerequisiteCache(tmp_path / "prerequisites.json", ttl_days=30)
    assert second.get("heat equation") == ["Fourier series", "partial derivatives"]


def test_stale_entries_are_skipped_and_pruned(tmp_path, monkeypatch):
    cache = PrerequisiteCache(tmp_path / "prerequisites.json", ttl_days=1)
    cache.put("old", ["a"])
    cache._entries["old"]["cached_at"] = "2000-01-01T00:00:00+00:00"
    cache.save()
    assert cache.get("old") is None
    cache.put("fresh", ["b"])
    assert "old" not in cache._entries
    assert cache.get("fresh") == ["b"]


def test_knowledge_map_ingest(tmp_path):
    cache = PrerequisiteCache.for_runs_dir(tmp_path / "mythos")
    cache.ingest_knowledge_map("heat equation", KNOWLEDGE_MAP)
    assert cache.get("heat equation") == ["Fourier series", "partial derivatives"]


def test_pipeline_settings_ttl_from_env(monkeypatch):
    monkeypatch.setenv("M2M_PREREQ_CACHE_TTL_DAYS", "14")
    assert PipelineSettings.from_env().prereq_cache_ttl_days == 14


def test_cache_ttl_for_runs_dir_comes_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_PREREQ_CACHE_TTL_DAYS", "7")
    cache = PrerequisiteCache.for_runs_dir(tmp_path / "runs")
    assert cache.ttl_days == 7
    assert cache.path == tmp_path / "runs" / "_cache" / "prerequisites.json"
