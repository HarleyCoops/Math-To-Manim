"""Small content-addressed artifact store for local generated outputs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any


class ArtifactStoreError(RuntimeError):
    """Raised when the artifact store cannot read or write its manifest."""


@dataclass(frozen=True)
class Artifact:
    """Metadata for one stored artifact."""

    id: str
    path: Path
    kind: str
    sha256: str
    size_bytes: int
    metadata: Mapping[str, Any]


class ArtifactStore:
    """A deterministic local store keyed by file content and sanitized names."""

    manifest_name = "manifest.json"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.artifacts_dir = self.root / "artifacts"
        self.manifest_path = self.root / self.manifest_name
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._manifest = self._load_manifest()

    def put_bytes(
        self,
        data: bytes,
        name: str = "artifact.bin",
        *,
        kind: str = "artifact",
        metadata: Mapping[str, Any] | None = None,
    ) -> Artifact:
        digest = sha256(data).hexdigest()
        safe_name = _safe_name(name)
        artifact_id = f"{digest[:16]}-{safe_name}"
        target = (self.artifacts_dir / artifact_id).resolve()
        _ensure_child_path(self.artifacts_dir, target)

        if not target.exists() or target.read_bytes() != data:
            tmp_path = target.with_name(f".{target.name}.tmp")
            tmp_path.write_bytes(data)
            os.replace(tmp_path, target)

        artifact_record = {
            "id": artifact_id,
            "relative_path": str(Path("artifacts") / artifact_id),
            "kind": kind,
            "sha256": digest,
            "size_bytes": len(data),
            "metadata": dict(metadata or {}),
        }
        self._manifest[artifact_id] = artifact_record
        self._write_manifest()
        return self._artifact_from_record(artifact_record)

    def put_text(
        self,
        text: str,
        name: str,
        *,
        kind: str = "text",
        metadata: Mapping[str, Any] | None = None,
        encoding: str = "utf-8",
    ) -> Artifact:
        return self.put_bytes(text.encode(encoding), name, kind=kind, metadata=metadata)

    def put_json(
        self,
        value: Any,
        name: str,
        *,
        kind: str = "json",
        metadata: Mapping[str, Any] | None = None,
    ) -> Artifact:
        data = json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
        return self.put_bytes(data, name, kind=kind, metadata=metadata)

    def put_file(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        kind: str = "file",
        metadata: Mapping[str, Any] | None = None,
    ) -> Artifact:
        source = Path(path)
        return self.put_bytes(source.read_bytes(), name or source.name, kind=kind, metadata=metadata)

    def get(self, artifact_id: str) -> Artifact | None:
        record = self._manifest.get(artifact_id)
        if record is None:
            return None
        return self._artifact_from_record(record)

    def list(self, *, kind: str | None = None) -> tuple[Artifact, ...]:
        records = sorted(self._manifest.values(), key=lambda record: record["id"])
        artifacts = (self._artifact_from_record(record) for record in records)
        if kind is None:
            return tuple(artifacts)
        return tuple(artifact for artifact in artifacts if artifact.kind == kind)

    def _load_manifest(self) -> dict[str, dict[str, Any]]:
        if not self.manifest_path.exists():
            return {}
        try:
            raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ArtifactStoreError(f"Invalid artifact manifest: {self.manifest_path}") from exc
        if not isinstance(raw, dict):
            raise ArtifactStoreError("Artifact manifest must be a JSON object")
        return raw

    def _write_manifest(self) -> None:
        payload = json.dumps(self._manifest, indent=2, sort_keys=True)
        tmp_path = self.manifest_path.with_suffix(".json.tmp")
        tmp_path.write_text(payload + "\n", encoding="utf-8")
        os.replace(tmp_path, self.manifest_path)

    def _artifact_from_record(self, record: Mapping[str, Any]) -> Artifact:
        path = (self.root / str(record["relative_path"])).resolve()
        _ensure_child_path(self.root, path)
        return Artifact(
            id=str(record["id"]),
            path=path,
            kind=str(record["kind"]),
            sha256=str(record["sha256"]),
            size_bytes=int(record["size_bytes"]),
            metadata=dict(record.get("metadata") or {}),
        )


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name).strip("._-")
    return (cleaned or "artifact.bin")[:96]


def _ensure_child_path(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    if child_resolved != parent_resolved and parent_resolved not in child_resolved.parents:
        raise ArtifactStoreError(f"Path escapes artifact store: {child}")
