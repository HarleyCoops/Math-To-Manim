"""Persist reverse-prerequisite trees across Sol process restarts.

The retired Hermes MCP kept ``PREREQUISITE_CACHE`` as a process-local dict, so
every server restart re-derived the same trees. The live Sol equivalent is
the knowledge-map artifact. This sidecar stores extracted prerequisite names
under ``<runs_dir>/_cache/prerequisites.json`` with a configurable TTL.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_TTL_DAYS = 30
CACHE_SCHEMA_VERSION = 1


def _ttl_days() -> int:
    raw = os.getenv("M2M_PREREQ_CACHE_TTL_DAYS", str(DEFAULT_TTL_DAYS))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_TTL_DAYS


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def extract_prerequisites(knowledge_map: dict[str, Any], source_concept: str) -> list[str]:
    """Pull a flat prerequisite list out of a cartographer knowledge map."""
    found: list[str] = []
    seen: set[str] = set()

    def add(name: str | None) -> None:
        if not name:
            return
        cleaned = str(name).strip()
        if not cleaned or cleaned == source_concept or cleaned in seen:
            return
        seen.add(cleaned)
        found.append(cleaned)

    nodes = knowledge_map.get("nodes")
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            add(node.get("name") or node.get("id") or node.get("label"))
            nested = node.get("prerequisites")
            if isinstance(nested, list):
                for item in nested:
                    if isinstance(item, dict):
                        add(item.get("name") or item.get("id") or item.get("label"))
                    else:
                        add(str(item))
    explicit = knowledge_map.get("prerequisites")
    if isinstance(explicit, list):
        for item in explicit:
            if isinstance(item, dict):
                add(item.get("name") or item.get("id") or item.get("label"))
            else:
                add(str(item))
    return found


class PrerequisiteCache:
    """JSON sidecar cache with write-then-rename persistence."""

    def __init__(self, path: Path, *, ttl_days: int | None = None):
        self.path = Path(path)
        self.ttl_days = DEFAULT_TTL_DAYS if ttl_days is None else max(1, ttl_days)
        self._entries: dict[str, dict[str, Any]] = {}
        self.load()

    @classmethod
    def for_runs_dir(cls, runs_dir: Path, *, ttl_days: int | None = None) -> "PrerequisiteCache":
        path = Path(runs_dir) / "_cache" / "prerequisites.json"
        return cls(path, ttl_days=ttl_days if ttl_days is not None else _ttl_days())

    def load(self) -> None:
        if not self.path.is_file():
            self._entries = {}
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._entries = {}
            return
        entries = payload.get("entries") if isinstance(payload, dict) else None
        if not isinstance(entries, dict):
            self._entries = {}
            return
        cleaned: dict[str, dict[str, Any]] = {}
        for key, value in entries.items():
            if isinstance(key, str) and isinstance(value, dict):
                cleaned[key] = value
        self._entries = cleaned

    def _is_fresh(self, entry: dict[str, Any], *, now: datetime | None = None) -> bool:
        cached_at = _parse_iso(str(entry.get("cached_at", "")))
        if cached_at is None:
            return False
        moment = now or _now()
        return cached_at + timedelta(days=self.ttl_days) >= moment

    def get(self, concept: str) -> list[str] | None:
        entry = self._entries.get(concept)
        if entry is None or not self._is_fresh(entry):
            return None
        prerequisites = entry.get("prerequisites")
        if not isinstance(prerequisites, list):
            return None
        return [str(item) for item in prerequisites]

    def put(self, concept: str, prerequisites: list[str], *, persist: bool = True) -> None:
        self._prune_stale()
        self._entries[concept] = {
            "prerequisites": list(prerequisites),
            "cached_at": _now().isoformat(),
            "source_concept": concept,
        }
        if persist:
            self.save()

    def ingest_knowledge_map(
        self,
        concept: str,
        knowledge_map: dict[str, Any],
        *,
        persist: bool = True,
    ) -> list[str]:
        prerequisites = extract_prerequisites(knowledge_map, concept)
        if prerequisites:
            self.put(concept, prerequisites, persist=persist)
        return prerequisites

    def _prune_stale(self) -> None:
        now = _now()
        self._entries = {
            key: value
            for key, value in self._entries.items()
            if self._is_fresh(value, now=now)
        }

    def save(self) -> None:
        self._prune_stale()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "entries": self._entries,
        }
        encoded = json.dumps(payload, indent=2)
        fd, tmp_name = tempfile.mkstemp(
            prefix=".prerequisites.",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(encoded)
            os.replace(tmp_name, self.path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
