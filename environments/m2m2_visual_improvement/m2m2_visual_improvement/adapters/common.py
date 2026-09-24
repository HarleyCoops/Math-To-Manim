"""Filesystem-only normalization shared by provider adapters."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

from pydantic import JsonValue

from ..schemas import (
    EducationalContract,
    NonEmpty,
    Sha256,
    StrictFrozenModel,
)

Provider = Literal["mythos", "sol"]
MAX_ARTIFACT_BYTES = 2_000_000
REASONING_ARTIFACTS = (
    "01_intent.json",
    "02_knowledge_map.json",
    "03_curriculum.json",
    "04_math_dossier.json",
    "05_shot_list.json",
    "06_scene_spec.json",
)


class AdapterError(ValueError):
    """A run directory cannot be normalized without guessing."""


class TaskBundle(StrictFrozenModel):
    provider: Provider
    run_id: NonEmpty
    contract: EducationalContract
    scene_spec: dict[str, JsonValue]
    code: str
    manifest: dict[str, JsonValue]
    review: dict[str, JsonValue] | None
    source_artifact_hashes: dict[NonEmpty, Sha256]


def normalize_relative_path(value: str) -> str:
    """Normalize a manifest path without resolving it on the host."""

    return PurePosixPath(value.replace("\\", "/")).as_posix()


def _safe_path(run_dir: Path, relative: str) -> Path:
    normalized = normalize_relative_path(relative)
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(relative)
    if (
        not normalized
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or ".." in posix.parts
    ):
        raise AdapterError(
            f"artifact path must stay inside the run directory: {relative!r}"
        )
    root = run_dir.resolve()
    candidate = (root / Path(*posix.parts)).resolve()
    if not candidate.is_relative_to(root):
        raise AdapterError(
            f"artifact path must stay inside the run directory: {relative!r}"
        )
    return candidate


def _read_text(run_dir: Path, relative: str) -> str:
    path = _safe_path(run_dir, relative)
    if not path.is_file():
        raise AdapterError(f"required artifact is missing: {relative}")
    size = path.stat().st_size
    if size > MAX_ARTIFACT_BYTES:
        raise AdapterError(
            f"artifact exceeds {MAX_ARTIFACT_BYTES} bytes: {relative}"
        )
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise AdapterError(f"artifact is not UTF-8: {relative}") from exc


def _read_json(run_dir: Path, relative: str) -> dict[str, JsonValue]:
    try:
        value = json.loads(_read_text(run_dir, relative))
    except json.JSONDecodeError as exc:
        raise AdapterError(
            f"artifact is not valid JSON: {relative} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from None
    if not isinstance(value, dict):
        raise AdapterError(f"artifact must contain a JSON object: {relative}")
    return value


def _sha256(run_dir: Path, relative: str) -> str:
    return hashlib.sha256(_safe_path(run_dir, relative).read_bytes()).hexdigest()


def _strings(value: JsonValue) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        result: list[str] = []
        for nested in value.values():
            result.extend(_strings(nested))
        return result
    if isinstance(value, list):
        result = []
        for nested in value:
            result.extend(_strings(nested))
        return result
    return []


def _unique(values: list[str], *, limit: int = 24) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = " ".join(value.split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
        if len(result) >= limit:
            break
    return tuple(result)


def _audience(intent: dict[str, JsonValue], provider: Provider) -> str:
    key = "audience" if provider == "mythos" else "learner_altitude"
    values = _strings(intent.get(key))
    return values[0] if values else "unspecified learner"


def _duration(
    intent: dict[str, JsonValue],
    scene_spec: dict[str, JsonValue],
    provider: Provider,
) -> float:
    keys = (
        ("duration_seconds", "target_duration_seconds")
        if provider == "mythos"
        else ("duration_target_seconds", "target_duration_seconds")
    )
    for source, key in ((intent, keys[0]), (scene_spec, keys[1])):
        value = source.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value > 0:
                return float(value)
        if isinstance(value, dict):
            for candidate in value.values():
                if (
                    isinstance(candidate, (int, float))
                    and not isinstance(candidate, bool)
                    and candidate > 0
                ):
                    return float(candidate)
    return 8.0


def build_bundle(
    run_dir: Path,
    *,
    provider: Provider,
    default_scene_file: str,
    require_review: bool,
) -> TaskBundle:
    """Read one completed provider bundle into the experiment contract."""

    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        raise AdapterError(f"run directory does not exist: {run_dir}")

    artifacts = {
        name: _read_json(run_dir, name) for name in REASONING_ARTIFACTS
    }
    manifest = _read_json(run_dir, "manifest.json")
    status = manifest.get("status")
    completed = manifest.get("completed_utc")
    if provider == "sol":
        if status != "completed" or not completed:
            raise AdapterError("Sol manifest is not completed")
    elif status not in (None, "completed") or not completed:
        raise AdapterError("Mythos manifest is not completed")

    scene_reference = manifest.get("scene_file", default_scene_file)
    if not isinstance(scene_reference, str) or not scene_reference.strip():
        raise AdapterError("manifest scene_file must be a non-empty path")
    normalized_scene = normalize_relative_path(scene_reference)
    code = _read_text(run_dir, normalized_scene)
    if not code.strip():
        raise AdapterError("scene source is empty")

    review = _read_json(run_dir, "review.json") if require_review else None
    source_names = [
        *REASONING_ARTIFACTS,
        "manifest.json",
        normalized_scene,
    ]
    if require_review:
        source_names.append("review.json")
    hashes = {name: _sha256(run_dir, name) for name in source_names}

    intent = artifacts["01_intent.json"]
    knowledge = artifacts["02_knowledge_map.json"]
    curriculum = artifacts["03_curriculum.json"]
    dossier = artifacts["04_math_dossier.json"]
    scene_spec = artifacts["06_scene_spec.json"]
    run_id = manifest.get("run_id")
    prompt = manifest.get("prompt")
    if not isinstance(run_id, str) or not run_id.strip():
        raise AdapterError("manifest run_id is missing")
    if not isinstance(prompt, str) or not prompt.lstrip("\ufeff").strip():
        raise AdapterError("manifest prompt is missing")

    concepts = _unique(_strings(knowledge))
    formulas = _unique(_strings(dossier))
    beats = _unique(_strings(curriculum))
    if not concepts:
        raise AdapterError("knowledge map contains no concepts")
    if not formulas:
        raise AdapterError("math dossier contains no formulas")
    if not beats:
        raise AdapterError("curriculum contains no narrative beats")

    target_duration = _duration(intent, scene_spec, provider)
    contract = EducationalContract(
        task_id=f"{provider}.{run_id}",
        source_id=run_id,
        original_request=prompt.lstrip("\ufeff").strip(),
        audience=_audience(intent, provider),
        required_concepts=concepts,
        required_formulas=formulas,
        required_narrative_beats=beats,
        min_duration_seconds=max(1.0, target_duration * 0.8),
        max_duration_seconds=target_duration * 1.2,
        provider=provider,
        source_artifact_hashes=hashes,
    )
    return TaskBundle(
        provider=provider,
        run_id=run_id,
        contract=contract,
        scene_spec=scene_spec,
        code=code,
        manifest=manifest,
        review=review,
        source_artifact_hashes=hashes,
    )


__all__ = [
    "AdapterError",
    "REASONING_ARTIFACTS",
    "TaskBundle",
    "build_bundle",
    "normalize_relative_path",
]
