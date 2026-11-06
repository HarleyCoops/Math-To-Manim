"""WAR-1530: Sol prerequisite cache ingests the cartographer knowledge map."""

from __future__ import annotations

from sol.prereq_cache import PrerequisiteCache


KNOWLEDGE_MAP = {
    "target": "heat equation",
    "nodes": [
        {"id": "heat", "name": "heat equation", "depth": 0},
        {"id": "fourier", "name": "Fourier series", "depth": 1},
        {"id": "deriv", "name": "partial derivatives", "depth": 2},
    ],
    "edges": [["deriv", "fourier"], ["fourier", "heat"]],
}


def test_knowledge_map_ingest(tmp_path):
    cache = PrerequisiteCache.for_runs_dir(tmp_path / "sol")
    cache.ingest_knowledge_map("heat equation", KNOWLEDGE_MAP)
    assert cache.get("heat equation") == ["Fourier series", "partial derivatives"]
    assert (tmp_path / "sol" / "_cache" / "prerequisites.json").is_file()
