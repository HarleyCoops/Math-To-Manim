"""Build a metadata-only inventory of historical Math-To-Manim sessions.

The inventory deliberately excludes transcript bodies.  It records only the
information needed to reconcile a source transcript with an ENTIRE import.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


MAX_METADATA_RECORDS = 128
HASH_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class SessionCandidate:
    """Metadata needed to reconcile one local agent transcript."""

    agent: str
    session_id: str
    source_path: str
    started_at: str | None
    repo_match: str
    sha256: str
    import_status: str = "pending"
    checkpoint_id: str | None = None


def _jsonl_records(path: Path, limit: int) -> Iterator[dict[str, Any]]:
    """Yield at most ``limit`` decoded object records without loading a file."""
    with path.open("r", encoding="utf-8", errors="replace") as transcript:
        for index, line in enumerate(transcript):
            if index >= limit:
                break
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def _streaming_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as transcript:
        for chunk in iter(lambda: transcript.read(HASH_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalized_path(path: Path | str) -> str:
    """Return a separator- and case-insensitive path key on Windows."""
    resolved = os.path.abspath(os.path.normpath(os.fspath(path)))
    return os.path.normcase(resolved).replace("\\", "/").casefold()


def _path_belongs_to_repo(cwd: Path | str, repo_root: Path | str) -> bool:
    normalized_cwd = _normalized_path(cwd)
    normalized_root = _normalized_path(repo_root).rstrip("/")
    return normalized_cwd == normalized_root or normalized_cwd.startswith(
        normalized_root + "/"
    )


def _normalized_repo_url(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if normalized.casefold().endswith(".git"):
        normalized = normalized[:-4]
    return normalized.casefold()


def _git_repository_url(git: object) -> str | None:
    if not isinstance(git, dict):
        return None
    for key in ("repository_url", "repositoryUrl", "repo_url", "remote"):
        value = git.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _candidate_sort_key(candidate: SessionCandidate) -> tuple[str, str, str]:
    return (
        candidate.agent,
        candidate.started_at or "",
        candidate.session_id,
    )


def discover_codex(
    root: Path,
    repo_root: Path,
    repo_urls: set[str],
) -> list[SessionCandidate]:
    """Discover Codex transcripts whose metadata belongs to this repository."""
    expected_urls = {_normalized_repo_url(url) for url in repo_urls}
    candidates: list[SessionCandidate] = []

    if not root.is_dir():
        return candidates

    for transcript in sorted(root.rglob("*.jsonl")):
        session_id: str | None = None
        started_at: str | None = None
        matched_cwd = False
        matched_remote = False

        for record in _jsonl_records(transcript, MAX_METADATA_RECORDS):
            payload = record.get("payload")
            metadata = payload if isinstance(payload, dict) else record

            possible_id = metadata.get("session_id") or metadata.get("id")
            if isinstance(possible_id, str) and possible_id:
                session_id = session_id or possible_id

            timestamp = record.get("timestamp") or metadata.get("timestamp")
            if isinstance(timestamp, str) and timestamp:
                started_at = started_at or timestamp

            cwd = metadata.get("cwd")
            if isinstance(cwd, str) and cwd:
                matched_cwd = matched_cwd or _path_belongs_to_repo(cwd, repo_root)

            repository_url = _git_repository_url(metadata.get("git"))
            if repository_url:
                matched_remote = matched_remote or (
                    _normalized_repo_url(repository_url) in expected_urls
                )

            if session_id and (matched_cwd or matched_remote):
                break

        if not session_id or not (matched_cwd or matched_remote):
            continue

        match_parts = []
        if matched_cwd:
            match_parts.append("cwd")
        if matched_remote:
            match_parts.append("remote")
        candidates.append(
            SessionCandidate(
                agent="codex",
                session_id=session_id,
                source_path=str(transcript.resolve()),
                started_at=started_at,
                repo_match="+".join(match_parts),
                sha256=_streaming_sha256(transcript),
            )
        )

    return sorted(candidates, key=_candidate_sort_key)


def discover_claude(project_dirs: list[Path]) -> list[SessionCandidate]:
    """Discover transcripts below explicitly repository-scoped Claude roots."""
    candidates: list[SessionCandidate] = []

    for project_dir in sorted(project_dirs):
        if not project_dir.is_dir():
            continue
        # Claude stores subagent logs below <session>/subagents.  Those belong
        # to the parent session and are consumed by ENTIRE's parent importer;
        # only top-level project transcripts are standalone sessions.
        for transcript in sorted(project_dir.glob("*.jsonl")):
            session_id: str | None = None
            started_at: str | None = None

            for record in _jsonl_records(transcript, MAX_METADATA_RECORDS):
                possible_id = record.get("sessionId") or record.get("session_id")
                if isinstance(possible_id, str) and possible_id:
                    session_id = session_id or possible_id
                timestamp = record.get("timestamp")
                if isinstance(timestamp, str) and timestamp:
                    started_at = started_at or timestamp
                if session_id and started_at:
                    break

            candidates.append(
                SessionCandidate(
                    agent="claude-code",
                    session_id=session_id or transcript.stem,
                    source_path=str(transcript.resolve()),
                    started_at=started_at,
                    repo_match="project-dir",
                    sha256=_streaming_sha256(transcript),
                )
            )

    return sorted(candidates, key=_candidate_sort_key)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory local agent sessions without transcript bodies."
    )
    parser.add_argument("--codex-root", required=True, type=Path)
    parser.add_argument("--claude-project-dir", action="append", default=[], type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--repo-url", action="append", default=[])
    parser.add_argument("--output", required=True, type=Path)
    return parser


def _deduplicate(candidates: Iterable[SessionCandidate]) -> list[SessionCandidate]:
    """Keep one deterministic record per agent, session ID, and file hash."""
    unique: dict[tuple[str, str, str], SessionCandidate] = {}
    for candidate in candidates:
        key = (candidate.agent, candidate.session_id, candidate.sha256)
        unique.setdefault(key, candidate)
    return sorted(unique.values(), key=_candidate_sort_key)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    sessions = _deduplicate(
        [
            *discover_codex(args.codex_root, args.repo_root, set(args.repo_url)),
            *discover_claude(args.claude_project_dir),
        ]
    )
    payload = {
        "schema_version": 1,
        "sessions": [asdict(candidate) for candidate in sessions],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
