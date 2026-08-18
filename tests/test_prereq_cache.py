"""WAR-1530: prerequisite cache survives a process-style reload."""

from __future__ import annotations

import importlib

from mythos.prereq_cache import PrerequisiteCache
from sol import prereq_cache as sol_prereq_cache


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


def test_knowledge_map_ingest_and_sol_copy(tmp_path):
    mythos = PrerequisiteCache.for_runs_dir(tmp_path / "mythos")
    mythos.ingest_knowledge_map("heat equation", KNOWLEDGE_MAP)
    assert "Fourier series" in mythos.get("heat equation")

    sol = sol_prereq_cache.PrerequisiteCache.for_runs_dir(tmp_path / "sol")
    sol.ingest_knowledge_map("heat equation", KNOWLEDGE_MAP)
    assert sol.get("heat equation") == mythos.get("heat equation")
    assert (tmp_path / "sol" / "_cache" / "prerequisites.json").is_file()
