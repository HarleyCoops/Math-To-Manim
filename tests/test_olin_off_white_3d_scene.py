"""Static production-contract checks for the hand-finished Olin Mythos film.

These tests intentionally do not import Manim or render the scene.  The render
extra is not part of the repository's offline test suite, and importing a
``ThreeDScene`` just to inspect it would make these inexpensive checks depend
on Cairo/FFmpeg.  Numeric coordinate helpers are instead compiled directly
from the scene's AST in a small numpy-only namespace.
"""

from __future__ import annotations

import ast
import copy
import inspect
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np


SCENE = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "mythos"
    / "olin_off_white_3d_space.py"
)
SHOWCASE_ASSETS = Path(__file__).resolve().parents[1] / "docs" / "showcase" / "assets"
SHOWCASE_MP4 = SHOWCASE_ASSETS / "olin-off-white-3d-space.mp4"
SHOWCASE_GIF = SHOWCASE_ASSETS / "olin-off-white-3d-space.gif"

OFF_WHITE = "#f3ecd8"
SEPIA = "#241a12"
STATIC_SAMPLE_COUNT = 10_000
MAX_ANIMATED_SAMPLE_COUNT = 6_000


def _source_and_tree() -> tuple[str, ast.Module]:
    assert SCENE.is_file(), f"missing production scene: {SCENE}"
    source = SCENE.read_text(encoding="utf-8")
    return source, ast.parse(source, filename=str(SCENE))


def _leaf_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [node.attr]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [name for item in node.elts for name in _target_names(item)]
    return []


def _assignments(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    found: list[tuple[str, ast.AST]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                found.extend((name, node.value) for name in _target_names(target))
        elif isinstance(node, ast.AnnAssign):
            found.extend(
                (name, node.value)
                for name in _target_names(node.target)
                if node.value is not None
            )
    return found


def _literal_constants(tree: ast.Module) -> dict[str, Any]:
    constants: dict[str, Any] = {}
    for name, value_node in _assignments(tree):
        try:
            constants[name] = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            pass
    return constants


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    if isinstance(base, ast.Subscript):
        return _base_name(base.value)
    return ""


def _is_self_camera(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "camera"
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    )


def _call_name(call: ast.Call) -> str:
    return _leaf_name(call.func)


def _integer_assignment_candidates(
    tree: ast.Module, required_name_fragments: tuple[str, ...]
) -> list[int]:
    values: list[int] = []
    for name, value_node in _assignments(tree):
        lowered = name.lower()
        if not any(fragment in lowered for fragment in required_name_fragments):
            continue
        try:
            value = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            continue
        if isinstance(value, int) and not isinstance(value, bool):
            values.append(value)
    return values


def _is_even_subset_expression(node: ast.AST) -> bool:
    """Accept deterministic linspace or explicit stepped slicing/arange."""

    for child in ast.walk(node):
        if isinstance(child, ast.Call) and _call_name(child) == "linspace":
            return True
        if isinstance(child, ast.Call) and _call_name(child) == "arange":
            # ``arange`` without a step is the full set, not a subset.
            if len(child.args) >= 3 or any(k.arg == "step" for k in child.keywords):
                return True
        if isinstance(child, ast.Slice) and child.step is not None:
            return True
    return False


def _contains_call(node: ast.AST, names: set[str]) -> bool:
    return any(
        isinstance(child, ast.Call) and _call_name(child) in names
        for child in ast.walk(node)
    )


def test_scene_is_one_archival_three_d_scene_with_real_camera_choreography():
    source, tree = _source_and_tree()

    scene_classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(_base_name(base) == "ThreeDScene" for base in node.bases)
    ]
    assert len(scene_classes) == 1, (
        "the deliverable must contain exactly one ThreeDScene subclass; "
        f"found {[node.name for node in scene_classes]}"
    )

    string_literals = {
        node.value.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert OFF_WHITE in string_literals, "use the literal archival paper #f3ecd8"
    assert SEPIA in string_literals, "use the literal dark-sepia ink #241a12"

    constants = _literal_constants(tree)
    background_assignments = [
        value
        for name, value in _assignments(tree)
        if "background" in name.lower()
    ]
    assert background_assignments, "set the scene/camera background explicitly"
    for value in background_assignments:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            resolved = value.value.lower()
        elif isinstance(value, ast.Name):
            resolved = str(constants.get(value.id, "")).lower()
        else:
            resolved = ast.unparse(value).lower()
        assert OFF_WHITE in resolved, (
            "every explicit background assignment must resolve to #f3ecd8; "
            f"got {ast.unparse(value)!r}"
        )

    forbidden_camera_animation = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and node.attr == "animate"
        and _is_self_camera(node.value)
    ]
    assert not forbidden_camera_animation, (
        "ThreeDScene cameras use move_camera/set_camera_orientation, "
        "never self.camera.animate"
    )

    perspective_calls = [
        call
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and _call_name(call) in {"move_camera", "set_camera_orientation"}
        and any(keyword.arg in {"phi", "theta"} for keyword in call.keywords)
    ]
    assert len(perspective_calls) >= 4, (
        "the lift needs at least four explicit phi/theta camera perspectives; "
        f"found {len(perspective_calls)}"
    )

    forbidden_visual_constructors = {
        "Star",
        "StarField",
        "Stars",
        "Nebula",
        "CosmicBackground",
        "DeepSpace",
    }
    used_forbidden_constructors = {
        _call_name(call)
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and _call_name(call) in forbidden_visual_constructors
    }
    assert not used_forbidden_constructors, (
        "the off-white contract forbids cosmic/dark motifs: "
        f"{sorted(used_forbidden_constructors)}"
    )

    # Also catch custom helpers such as ``make_starfield`` while avoiding
    # harmless identifiers such as ``start_time``.
    forbidden_identifier_parts = ("starfield", "nebula", "cosmic", "deep_space")
    motif_identifiers = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and any(part in node.id.lower() for part in forbidden_identifier_parts)
    }
    assert not motif_identifiers, (
        "remove dark/cosmic motif helpers from this archival-paper film: "
        f"{sorted(motif_identifiers)}"
    )

    # A bare BLACK background can bypass a hex-color check.
    black_backgrounds = [
        ast.unparse(value)
        for name, value in _assignments(tree)
        if "background" in name.lower()
        and isinstance(value, ast.Name)
        and value.id.upper() == "BLACK"
    ]
    assert not black_backgrounds

    assert source.strip(), "scene source unexpectedly empty"


def test_point_clouds_are_vectorized_and_density_is_bounded():
    source, tree = _source_and_tree()

    numpy_aliases = {
        alias.asname or alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "numpy"
    }
    numpy_from_import = any(
        isinstance(node, ast.ImportFrom) and node.module == "numpy"
        for node in tree.body
    )
    assert numpy_aliases or numpy_from_import, "point coordinates must use numpy arrays"

    used_names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert {"PMobject", "PGroup"} & used_names, (
        "render point clouds with PMobject/PGroup rather than thousands of Dots"
    )

    full_density_values = _integer_assignment_candidates(
        tree, ("static", "full", "density")
    )
    assert STATIC_SAMPLE_COUNT in full_density_values, (
        "declare a clearly named static/full-density count of exactly 10,000; "
        f"found {full_density_values}"
    )

    animated_values = _integer_assignment_candidates(tree, ("anim", "subset"))
    bounded_values = [
        value for value in animated_values if 0 < value <= MAX_ANIMATED_SAMPLE_COUNT
    ]
    assert bounded_values, (
        "declare a clearly named animated/subset count in 1..6000; "
        f"found {animated_values}"
    )

    even_subset_assignments = [
        (name, value)
        for name, value in _assignments(tree)
        if any(fragment in name.lower() for fragment in ("anim", "subset", "indices"))
        and _is_even_subset_expression(value)
    ]
    assert even_subset_assignments, (
        "build one deterministic evenly spaced animated index set "
        "(for example numpy.linspace(..., dtype=int))"
    )

    random_calls = [
        ast.unparse(call)
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and (
            _call_name(call) in {"random", "choice", "shuffle", "permutation"}
            or "random." in ast.unparse(call.func).lower()
        )
    ]
    assert not random_calls, (
        "the animated subset must be deterministic, not random: "
        f"{random_calls}"
    )

    iterative_nodes = (
        ast.For,
        ast.AsyncFor,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )
    dot_loops = [
        (getattr(node, "lineno", "?"), type(node).__name__)
        for node in ast.walk(tree)
        if isinstance(node, iterative_nodes)
        and _contains_call(node, {"Dot", "Dot3D"})
    ]
    assert not dot_loops, (
        "do not construct Dot/Dot3D objects inside loops/comprehensions; "
        f"found iterative construction at {dot_loops}"
    )

    # Literal density values should remain visible in production source and
    # not be hidden behind a tiny test-only default.
    assert "10_000" in source or "10000" in source


def _without_runtime_annotations(function: ast.FunctionDef) -> ast.FunctionDef:
    """Make a top-level helper definable without importing Manim names."""

    function = copy.deepcopy(function)
    function.decorator_list = []
    function.returns = None
    all_args = (
        function.args.posonlyargs
        + function.args.args
        + function.args.kwonlyargs
    )
    if function.args.vararg is not None:
        all_args.append(function.args.vararg)
    if function.args.kwarg is not None:
        all_args.append(function.args.kwarg)
    for arg in all_args:
        arg.annotation = None

    # Defaults such as ``color=SEPIA`` are irrelevant to coordinate helpers
    # but are evaluated when unrelated helper definitions execute.
    for defaults in (function.args.defaults, function.args.kw_defaults):
        for index, default in enumerate(defaults):
            if default is None:
                continue
            try:
                ast.literal_eval(default)
            except (ValueError, TypeError):
                defaults[index] = ast.Constant(None)
    return function


def _numeric_namespace(tree: ast.Module) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "np": np,
        "numpy": np,
        "math": math,
        "sin": np.sin,
        "cos": np.cos,
        "sqrt": np.sqrt,
        "pi": np.pi,
        "PI": np.pi,
    }
    namespace.update(_literal_constants(tree))

    helper_definitions = [
        _without_runtime_annotations(node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]
    helper_module = ast.Module(body=helper_definitions, type_ignores=[])
    ast.fix_missing_locations(helper_module)
    exec(compile(helper_module, str(SCENE), "exec"), namespace)
    return namespace


def _coordinate_helper(
    namespace: dict[str, Any], name_fragments: tuple[str, ...]
) -> tuple[str, Callable[..., Any]]:
    candidates: list[tuple[str, Callable[..., Any]]] = []
    for name, value in namespace.items():
        lowered = name.lower()
        if callable(value) and any(fragment in lowered for fragment in name_fragments):
            candidates.append((name, value))
    assert candidates, (
        "expose a module-level numeric coordinate helper whose name contains "
        f"one of {name_fragments}"
    )

    # Prefer the most explicit names while remaining tolerant of concise
    # ``exact_embedding`` / ``cylindrical_points`` spellings.
    candidates.sort(
        key=lambda item: (
            "coordinate" not in item[0].lower(),
            "point" not in item[0].lower(),
            item[0],
        )
    )
    return candidates[0]


def _as_points(value: Any, dimensions: int) -> np.ndarray:
    if isinstance(value, dict):
        lower_keys = {str(key).lower(): key for key in value}
        if dimensions == 3 and {"x", "y", "z"} <= lower_keys.keys():
            value = tuple(
                value[lower_keys[axis]] for axis in ("x", "y", "z")
            )
        elif dimensions == 2 and {"x", "z"} <= lower_keys.keys():
            value = tuple(value[lower_keys[axis]] for axis in ("x", "z"))

    array = np.asarray(value, dtype=float)
    if array.ndim == 1 and array.size == dimensions:
        return array.reshape(1, dimensions)
    if array.ndim != 2:
        raise AssertionError(
            f"coordinate helper returned shape {array.shape}, expected N×{dimensions}"
        )
    if array.shape[1] == dimensions:
        return array
    if array.shape[0] == dimensions:
        return array.T
    raise AssertionError(
        f"coordinate helper returned shape {array.shape}, expected N×{dimensions}"
    )


def _call_coordinates(
    function: Callable[..., Any], indices: np.ndarray, time: float, dimensions: int
) -> np.ndarray:
    """Call a vectorized helper, with a scalar fallback for readable helpers."""

    signature = inspect.signature(function)
    positional = [
        parameter
        for parameter in signature.parameters.values()
        if parameter.kind
        in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
    ]
    assert len(positional) >= 2, (
        f"{function.__name__} must accept sample indices and time"
    )

    try:
        points = _as_points(function(indices, time), dimensions)
        if len(points) == len(indices):
            return points
    except (TypeError, ValueError, AssertionError):
        pass

    scalar_points = [
        _as_points(function(float(index), time), dimensions)[0]
        for index in indices
    ]
    return np.asarray(scalar_points)


def _reference_coordinates(
    indices: np.ndarray, time: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    i = np.asarray(indices, dtype=float)
    y = i / 235.0
    k = (4.0 + np.cos(i / 9.0 - 2.0 * time)) * np.cos(i / 35.0)
    e = y / 7.0 - 13.0
    d = np.sqrt(k * k + e * e) + np.sin(e / 9.0 + time / 2.0) - 4.0
    c = d - time
    q = (
        2.0 * np.sin(3.0 * k)
        - y
        / 35.0
        * k
        * (9.0 + k * np.sin(9.0 * np.cos(e) - 2.0 * d + time))
    )

    shadow = np.column_stack(
        (q + 40.0 * np.cos(c), q * np.sin(c) + 35.0 * d)
    )
    exact_lift = np.column_stack(
        (shadow[:, 0], 40.0 * np.sin(c), shadow[:, 1])
    )
    cylindrical = np.column_stack(
        (
            (40.0 + q) * np.cos(c),
            (40.0 + q) * np.sin(c),
            35.0 * d,
        )
    )
    return shadow, exact_lift, cylindrical


def test_exact_lift_preserves_tweet_xz_and_c_is_separate():
    _, tree = _source_and_tree()
    namespace = _numeric_namespace(tree)
    lift_name, lift_function = _coordinate_helper(
        namespace, ("exact_lift", "lift_coordinates", "exact_embedding")
    )
    cylinder_name, cylinder_function = _coordinate_helper(
        namespace, ("cylindrical", "cylinder_coordinates", "c_coordinates")
    )
    assert lift_function is not cylinder_function
    assert lift_name != cylinder_name

    representative_indices = np.array(
        [0, 1, 17, 234, 999, 3_456, 7_777, 9_999], dtype=float
    )
    representative_times = (0.0, np.pi / 80.0, 0.73, 2.1, 4.0 * np.pi - 0.2)

    for time in representative_times:
        shadow, expected_lift, expected_cylinder = _reference_coordinates(
            representative_indices, time
        )
        actual_lift = _call_coordinates(
            lift_function, representative_indices, time, dimensions=3
        )
        actual_cylinder = _call_coordinates(
            cylinder_function, representative_indices, time, dimensions=3
        )

        # This is the central mathematical promise: no normalization, scaling,
        # or reinterpretation may alter E's visible x and z coordinates.
        np.testing.assert_allclose(
            actual_lift[:, (0, 2)],
            shadow,
            rtol=2e-12,
            atol=2e-12,
            err_msg=f"{lift_name} does not preserve the tweet's exact x,z shadow",
        )
        np.testing.assert_allclose(
            actual_lift,
            expected_lift,
            rtol=2e-12,
            atol=2e-12,
            err_msg=f"{lift_name} is not the exact E(i,t) lift",
        )
        np.testing.assert_allclose(
            actual_cylinder,
            expected_cylinder,
            rtol=2e-12,
            atol=2e-12,
            err_msg=f"{cylinder_name} is not the separate C(i,t) interpretation",
        )

    labels = " ".join(
        node.value.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    assert "cylindrical" in labels, "label C as cylindrical on screen"
    assert any(
        qualifier in labels
        for qualifier in ("interpretation", "reinterpretation", "alternate")
    ), "label C honestly as an interpretation/alternate, not the literal lift"


def test_reviewed_showcase_assets_are_committed_and_bounded():
    assert SHOWCASE_MP4.is_file(), f"missing full showcase film: {SHOWCASE_MP4}"
    assert SHOWCASE_GIF.is_file(), f"missing showcase loop: {SHOWCASE_GIF}"

    mp4_size = SHOWCASE_MP4.stat().st_size
    gif_size = SHOWCASE_GIF.stat().st_size
    assert 1_000_000 < mp4_size < 50 * 1024 * 1024
    assert 500_000 < gif_size < 15 * 1024 * 1024

    with SHOWCASE_MP4.open("rb") as movie:
        assert movie.read(12)[4:8] == b"ftyp", "full film is not an MP4 container"
    with SHOWCASE_GIF.open("rb") as loop:
        assert loop.read(6) in {b"GIF87a", b"GIF89a"}, "loop is not a GIF"
