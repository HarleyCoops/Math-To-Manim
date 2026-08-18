"""Versioned Sol run-manifest contract."""

from __future__ import annotations

from typing import Any, Callable

CURRENT_SCHEMA_VERSION = 2
Migrator = Callable[[dict[str, Any]], dict[str, Any]]


class ManifestSchemaError(ValueError):
    """The on-disk manifest cannot be migrated to the current schema."""


def validation_template() -> dict[str, Any]:
    return {
        "latex": None,
        "manim_code": None,
        "complexity": None,
        "ran_at": None,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _migrate_unversioned_to_v1(manifest: dict[str, Any]) -> dict[str, Any]:
    upgraded = dict(manifest)
    upgraded["schema_version"] = 1
    artifacts = dict(_as_dict(upgraded.get("artifacts")))
    artifacts.setdefault("scene", upgraded.get("scene_file") or "sol_scene.py")
    artifacts.setdefault("manifest", "manifest.json")
    upgraded["artifacts"] = artifacts
    return upgraded


def _migrate_v1_to_v2(manifest: dict[str, Any]) -> dict[str, Any]:
    upgraded = dict(manifest)
    artifacts = dict(_as_dict(upgraded.get("artifacts")))
    artifacts.setdefault("validation", "validation.json")
    upgraded["artifacts"] = artifacts
    # Sol already uses ``status`` for the run lifecycle string. Validation
    # gate state lives in ``status_detail`` so the two do not collide.
    detail = dict(_as_dict(upgraded.get("status_detail")))
    if isinstance(upgraded.get("status"), dict):
        detail.update(upgraded["status"])
        upgraded.pop("status", None)
    detail.setdefault("validation", "pending")
    upgraded["status_detail"] = detail
    upgraded["schema_version"] = 2
    return upgraded


MIGRATIONS: dict[int, Migrator] = {
    0: _migrate_unversioned_to_v1,
    1: _migrate_v1_to_v2,
}


def migrate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict) or not manifest:
        raise ManifestSchemaError("manifest is not a JSON object")
    current = dict(manifest)
    version = current.get("schema_version", 0)
    if version is None:
        version = 0
    if not isinstance(version, int):
        raise ManifestSchemaError(f"invalid schema_version: {version!r}")
    if version > CURRENT_SCHEMA_VERSION:
        raise ManifestSchemaError(
            f"manifest schema_version {version} is newer than supported "
            f"{CURRENT_SCHEMA_VERSION}"
        )
    while version < CURRENT_SCHEMA_VERSION:
        migrator = MIGRATIONS.get(version)
        if migrator is None:
            raise ManifestSchemaError(
                f"no migrator registered for schema_version {version}"
            )
        current = migrator(current)
        version = int(current.get("schema_version", version + 1))
    return current
