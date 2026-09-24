from copy import deepcopy

from m2m2_visual_improvement.merge_patch import apply_merge_patch


def test_scalar_patch_replaces_target() -> None:
    assert apply_merge_patch({"a": 1}, "replacement") == "replacement"


def test_nested_objects_merge_without_mutating_target() -> None:
    target = {"camera": {"zoom": 1.0, "center": [0, 0]}, "title": "Lesson"}
    original = deepcopy(target)

    result = apply_merge_patch(target, {"camera": {"zoom": 1.5}})

    assert result == {
        "camera": {"zoom": 1.5, "center": [0, 0]},
        "title": "Lesson",
    }
    assert target == original


def test_arrays_are_replaced_not_merged() -> None:
    assert apply_merge_patch(
        {"objects": [{"id": "a"}, {"id": "b"}]},
        {"objects": [{"id": "c"}]},
    ) == {"objects": [{"id": "c"}]}


def test_null_deletes_an_object_member() -> None:
    assert apply_merge_patch(
        {"caption": "keep?", "camera": {"zoom": 1}},
        {"caption": None},
    ) == {"camera": {"zoom": 1}}


def test_object_patch_converts_non_object_target() -> None:
    assert apply_merge_patch("old", {"camera": {"zoom": 2}}) == {
        "camera": {"zoom": 2}
    }
