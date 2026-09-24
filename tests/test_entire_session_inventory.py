"""Tests for privacy-preserving ENTIRE historical-session discovery."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.entire.session_inventory import discover_claude, discover_codex


def test_codex_inventory_matches_repo_cwd_and_remote(tmp_path: Path) -> None:
    root = tmp_path / "codex"
    root.mkdir()
    matching = root / "rollout-2026-07-01T00-00-00-session-a.jsonl"
    matching.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-01T00:00:00Z",
                "type": "session_meta",
                "payload": {
                    "session_id": "session-a",
                    "cwd": "C:/work/Math-To-Manim",
                    "git": {
                        "repository_url": (
                            "https://github.com/HarleyCoops/Math-To-Manim.git"
                        )
                    },
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    candidates = discover_codex(
        root,
        Path("C:/work/Math-To-Manim"),
        {"https://github.com/HarleyCoops/Math-To-Manim.git"},
    )

    assert [item.session_id for item in candidates] == ["session-a"]
    assert len(candidates[0].sha256) == 64


def test_codex_inventory_treats_repo_descendants_as_cwd_matches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codex"
    root.mkdir()
    transcript = root / "rollout-session-child.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-01T00:00:00Z",
                "type": "session_meta",
                "payload": {
                    "id": "session-child",
                    "cwd": "C:/work/Math-To-Manim/.worktrees/experiment",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    candidates = discover_codex(
        root,
        Path("C:/work/Math-To-Manim"),
        set(),
    )

    assert [item.session_id for item in candidates] == ["session-child"]
    assert candidates[0].repo_match == "cwd"


def test_codex_inventory_supports_legacy_top_level_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codex"
    root.mkdir()
    transcript = root / "legacy.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "id": "legacy-session",
                "cwd": "C:/elsewhere/checkout",
                "git": {
                    "repository_url": (
                        "https://github.com/unitseeker/math-to-manim"
                    )
                },
                "timestamp": "2025-12-01T00:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    candidates = discover_codex(
        root,
        Path("C:/work/Math-To-Manim"),
        {"https://github.com/unitseeker/math-to-manim.git"},
    )

    assert [item.session_id for item in candidates] == ["legacy-session"]
    assert candidates[0].repo_match == "remote"


def test_codex_inventory_bounds_metadata_scan_to_128_records(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codex"
    root.mkdir()
    transcript = root / "late-metadata.jsonl"
    records = [json.dumps({"type": "event"}) for _ in range(128)]
    records.append(
        json.dumps(
            {
                "type": "session_meta",
                "payload": {
                    "id": "too-late",
                    "cwd": "C:/work/Math-To-Manim",
                },
            }
        )
    )
    transcript.write_text("\n".join(records) + "\n", encoding="utf-8")

    candidates = discover_codex(
        root,
        Path("C:/work/Math-To-Manim"),
        set(),
    )

    assert candidates == []


def test_claude_inventory_uses_repo_scoped_project_dirs(tmp_path: Path) -> None:
    project = tmp_path / "C--work-Math-To-Manim"
    project.mkdir()
    transcript = project / "session-b.jsonl"
    transcript.write_text(
        json.dumps({"type": "ai-title", "sessionId": "session-b"}) + "\n",
        encoding="utf-8",
    )

    candidates = discover_claude([project])

    assert [item.session_id for item in candidates] == ["session-b"]
    assert candidates[0].agent == "claude-code"


def test_claude_inventory_does_not_treat_subagents_as_sessions(
    tmp_path: Path,
) -> None:
    project = tmp_path / "C--work-Math-To-Manim"
    subagents = project / "session-b" / "subagents"
    subagents.mkdir(parents=True)
    (project / "session-b.jsonl").write_text("{}\n", encoding="utf-8")
    (subagents / "agent-c.jsonl").write_text("{}\n", encoding="utf-8")

    candidates = discover_claude([project])

    assert [item.session_id for item in candidates] == ["session-b"]
