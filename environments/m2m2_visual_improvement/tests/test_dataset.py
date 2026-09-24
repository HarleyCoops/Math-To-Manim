from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from m2m2_visual_improvement.dataset import (
    DATASET_SEED,
    DEFECT_FAMILIES,
    PACKAGE_DATA_DIR,
    build_dataset,
    load_tasks,
    task_payload_sha256,
    write_dataset,
)
from m2m2_visual_improvement.micro_scenes import BASE_SCENES


def test_manifest_has_144_tasks() -> None:
    tasks, manifest = build_dataset()
    assert len(tasks) == 144
    assert manifest.task_count == 144
    assert manifest.split_counts == {
        "train": 96,
        "validation": 24,
        "test": 24,
    }


def test_grouped_splits_are_96_24_24() -> None:
    tasks, _ = build_dataset()
    counts = Counter(task.split for task in tasks)
    assert counts == Counter(train=96, validation=24, test=24)


def test_base_scene_never_crosses_splits() -> None:
    tasks, _ = build_dataset()
    splits_by_base: dict[str, set[str]] = defaultdict(set)
    for task in tasks:
        splits_by_base[task.base_scene_id].add(task.split)
    assert len(splits_by_base) == 18
    assert all(len(splits) == 1 for splits in splits_by_base.values())


def test_all_six_defect_families_are_represented() -> None:
    tasks, _ = build_dataset()
    assert {task.defect_family for task in tasks} == DEFECT_FAMILIES
    assert len(DEFECT_FAMILIES) == 6


def test_each_base_scene_has_eight_real_mutations() -> None:
    tasks, _ = build_dataset()
    counts = Counter(task.base_scene_id for task in tasks)
    assert set(counts.values()) == {8}

    for task in tasks:
        clean = BASE_SCENES[task.base_scene_id]
        assert (
            task.baseline_code != clean.code
            or task.baseline_scene_spec != clean.scene_spec
        )


def test_base_scenes_are_short_and_instructionally_typed() -> None:
    assert len(BASE_SCENES) == 18
    for scene in BASE_SCENES.values():
        assert 6.0 <= scene.duration_seconds <= 12.0
        assert scene.required_concepts
        assert scene.required_formulas
        assert scene.focus_beats
        assert "class " + scene.scene_name in scene.code


def test_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_dataset(first, seed=DATASET_SEED)
    write_dataset(second, seed=DATASET_SEED)

    for name in ("tasks.jsonl", "manifest.json", "base_scenes.jsonl"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_task_ids_and_hashes_match_payloads() -> None:
    tasks, manifest = build_dataset()
    assert len({task.task_id for task in tasks}) == 144
    hashes = {entry.task_id: entry.payload_sha256 for entry in manifest.tasks}
    assert set(hashes) == {task.task_id for task in tasks}
    for task in tasks:
        assert hashes[task.task_id] == task_payload_sha256(task)


def test_committed_dataset_matches_generator(tmp_path: Path) -> None:
    write_dataset(tmp_path, seed=DATASET_SEED)
    for name in ("tasks.jsonl", "manifest.json", "base_scenes.jsonl"):
        assert (PACKAGE_DATA_DIR / name).read_bytes() == (tmp_path / name).read_bytes()

    committed = load_tasks(PACKAGE_DATA_DIR / "tasks.jsonl")
    assert len(committed) == 144
