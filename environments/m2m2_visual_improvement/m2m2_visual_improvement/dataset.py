"""Deterministic grouped dataset for visual-improvement RL."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field, JsonValue

from .micro_scenes import (
    BASE_SCENES,
    BaseScene,
    mutable_scene_spec,
    render_scene_code,
)
from .schemas import (
    EducationalContract,
    FocusBeat,
    NonEmpty,
    Sha256,
    SourceCode,
    StrictFrozenModel,
)

DATASET_SEED = 20260724
GENERATOR_VERSION = "m2m2.visual_dataset.v1"
PACKAGE_DATA_DIR = Path(__file__).resolve().parent / "data"
Split = Literal["train", "validation", "test"]

DEFECT_FAMILIES = frozenset(
    {
        "off_frame_placement",
        "text_formula_crowding",
        "below_readability_threshold",
        "excessive_simultaneous_objects",
        "absent_or_weak_zoom",
        "temporal_stacking",
    }
)

MUTATIONS: tuple[tuple[str, str], ...] = (
    ("off_frame_right", "off_frame_placement"),
    ("off_frame_top", "off_frame_placement"),
    ("text_overlap", "text_formula_crowding"),
    ("tiny_text", "below_readability_threshold"),
    ("density_burst", "excessive_simultaneous_objects"),
    ("weak_zoom", "absent_or_weak_zoom"),
    ("wrong_zoom", "absent_or_weak_zoom"),
    ("temporal_stack", "temporal_stacking"),
)


class VisualTask(StrictFrozenModel):
    schema_version: Literal["m2m2.visual_task.v1"]
    task_id: NonEmpty
    base_scene_id: NonEmpty
    split: Split
    mutation_id: NonEmpty
    defect_family: NonEmpty
    seed: int = Field(ge=0)
    contract: EducationalContract
    baseline_scene_spec: dict[str, JsonValue]
    baseline_code: SourceCode
    scene_name: NonEmpty
    reference_id: NonEmpty
    focus_beats: tuple[FocusBeat, ...] = Field(min_length=1)
    defect_parameters: dict[str, JsonValue]


class ManifestTask(StrictFrozenModel):
    task_id: NonEmpty
    base_scene_id: NonEmpty
    split: Split
    defect_family: NonEmpty
    payload_sha256: Sha256


class DatasetManifest(StrictFrozenModel):
    schema_version: Literal["m2m2.visual_dataset_manifest.v1"]
    generator_version: Literal["m2m2.visual_dataset.v1"]
    seed: int
    task_count: int
    base_scene_count: int
    mutations_per_base: int
    split_counts: dict[Split, int]
    defect_families: tuple[NonEmpty, ...]
    base_scene_sha256: dict[NonEmpty, Sha256]
    tasks: tuple[ManifestTask, ...]


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _hash_json(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _split_for_index(index: int) -> Split:
    if index <= 12:
        return "train"
    if index <= 15:
        return "validation"
    return "test"


def _object(spec: dict[str, JsonValue], object_id: str) -> dict[str, JsonValue]:
    for value in spec["objects"]:  # type: ignore[index]
        if isinstance(value, dict) and value.get("id") == object_id:
            return value
    raise AssertionError(f"missing fixture object: {object_id}")


def _apply_mutation(
    scene: BaseScene,
    mutation_id: str,
) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
    spec = mutable_scene_spec(scene)
    parameters: dict[str, JsonValue]
    if mutation_id == "off_frame_right":
        _object(spec, "title")["x"] = 8.2
        parameters = {"object_id": "title", "x": 8.2}
    elif mutation_id == "off_frame_top":
        _object(spec, "formula")["y"] = 4.3
        parameters = {"object_id": "formula", "y": 4.3}
    elif mutation_id == "text_overlap":
        _object(spec, "title")["y"] = 0.1
        _object(spec, "formula")["y"] = 0.0
        parameters = {"object_ids": ["title", "formula"], "gap": 0.1}
    elif mutation_id == "tiny_text":
        _object(spec, "title")["font_size"] = 13
        _object(spec, "formula")["scale"] = 0.28
        parameters = {"font_size": 13, "formula_scale": 0.28}
    elif mutation_id == "density_burst":
        spec["staging"]["simultaneous_decoys"] = 18  # type: ignore[index]
        parameters = {"simultaneous_decoys": 18}
    elif mutation_id == "weak_zoom":
        spec["camera"]["zoom_scale"] = 1.0  # type: ignore[index]
        parameters = {"zoom_scale": 1.0}
    elif mutation_id == "wrong_zoom":
        spec["camera"]["zoom_scale"] = 0.65  # type: ignore[index]
        spec["camera"]["center_x"] = 3.8  # type: ignore[index]
        spec["camera"]["center_y"] = 2.5  # type: ignore[index]
        parameters = {"zoom_scale": 0.65, "center": [3.8, 2.5]}
    elif mutation_id == "temporal_stack":
        spec["staging"]["clear_title_before_formula"] = False  # type: ignore[index]
        parameters = {"clear_title_before_formula": False}
    else:
        raise ValueError(f"unknown mutation: {mutation_id}")
    return spec, parameters


def _contract(scene: BaseScene) -> EducationalContract:
    code_hash = hashlib.sha256(scene.code.encode("utf-8")).hexdigest()
    spec_hash = _hash_json(scene.scene_spec)
    return EducationalContract(
        task_id=scene.base_scene_id,
        source_id=scene.base_scene_id,
        original_request=scene.prompt,
        audience=scene.audience,
        required_concepts=scene.required_concepts,
        required_formulas=scene.required_formulas,
        required_narrative_beats=scene.required_narrative_beats,
        min_duration_seconds=6.0,
        max_duration_seconds=12.0,
        provider="synthetic",
        source_artifact_hashes={
            "clean_scene.py": code_hash,
            "clean_scene_spec.json": spec_hash,
        },
    )


def task_payload_sha256(task: VisualTask) -> str:
    return _hash_json(task.model_dump(mode="json"))


def build_dataset(
    *,
    seed: int = DATASET_SEED,
) -> tuple[list[VisualTask], DatasetManifest]:
    tasks: list[VisualTask] = []
    base_hashes: dict[str, str] = {}
    ordered_scenes = sorted(BASE_SCENES.values(), key=lambda item: item.base_scene_id)
    for index, scene in enumerate(ordered_scenes, start=1):
        split = _split_for_index(index)
        base_hashes[scene.base_scene_id] = _hash_json(
            scene.model_dump(mode="json")
        )
        for mutation_index, (mutation_id, family) in enumerate(MUTATIONS):
            spec, parameters = _apply_mutation(scene, mutation_id)
            task_id = f"{scene.base_scene_id}.{mutation_id}"
            task_seed = seed + index * 100 + mutation_index
            contract_payload = _contract(scene).model_dump(mode="json")
            contract_payload["task_id"] = task_id
            tasks.append(
                VisualTask(
                    schema_version="m2m2.visual_task.v1",
                    task_id=task_id,
                    base_scene_id=scene.base_scene_id,
                    split=split,
                    mutation_id=mutation_id,
                    defect_family=family,
                    seed=task_seed,
                    contract=EducationalContract.model_validate(contract_payload),
                    baseline_scene_spec=spec,
                    baseline_code=render_scene_code(scene.scene_name, spec),
                    scene_name=scene.scene_name,
                    reference_id=scene.base_scene_id,
                    focus_beats=scene.focus_beats,
                    defect_parameters=parameters,
                )
            )

    manifest_tasks = tuple(
        ManifestTask(
            task_id=task.task_id,
            base_scene_id=task.base_scene_id,
            split=task.split,
            defect_family=task.defect_family,
            payload_sha256=task_payload_sha256(task),
        )
        for task in tasks
    )
    split_counts = {
        split: sum(task.split == split for task in tasks)
        for split in ("train", "validation", "test")
    }
    manifest = DatasetManifest(
        schema_version="m2m2.visual_dataset_manifest.v1",
        generator_version=GENERATOR_VERSION,
        seed=seed,
        task_count=len(tasks),
        base_scene_count=len(ordered_scenes),
        mutations_per_base=len(MUTATIONS),
        split_counts=split_counts,
        defect_families=tuple(sorted(DEFECT_FAMILIES)),
        base_scene_sha256=base_hashes,
        tasks=manifest_tasks,
    )
    return tasks, manifest


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def write_dataset(output_dir: Path, *, seed: int = DATASET_SEED) -> None:
    output_dir = Path(output_dir)
    tasks, manifest = build_dataset(seed=seed)
    task_bytes = b"".join(
        _canonical(task.model_dump(mode="json")) for task in tasks
    )
    base_bytes = b"".join(
        _canonical(scene.model_dump(mode="json"))
        for scene in sorted(
            BASE_SCENES.values(),
            key=lambda item: item.base_scene_id,
        )
    )
    manifest_bytes = (
        json.dumps(
            manifest.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    _atomic_write(output_dir / "tasks.jsonl", task_bytes)
    _atomic_write(output_dir / "base_scenes.jsonl", base_bytes)
    _atomic_write(output_dir / "manifest.json", manifest_bytes)


def load_tasks(path: Path) -> list[VisualTask]:
    tasks: list[VisualTask] = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            tasks.append(VisualTask.model_validate_json(line))
        except ValueError as exc:
            raise ValueError(f"invalid task at line {line_number}: {exc}") from exc
    return tasks


__all__ = [
    "DATASET_SEED",
    "DEFECT_FAMILIES",
    "DatasetManifest",
    "GENERATOR_VERSION",
    "MUTATIONS",
    "PACKAGE_DATA_DIR",
    "VisualTask",
    "build_dataset",
    "load_tasks",
    "task_payload_sha256",
    "write_dataset",
]
