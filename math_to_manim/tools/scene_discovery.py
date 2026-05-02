"""AST-based Manim scene class discovery."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SCENE_BASES = (
    "Scene",
    "ThreeDScene",
    "MovingCameraScene",
    "ZoomedScene",
    "GraphScene",
    "VectorScene",
    "LinearTransformationScene",
    "SpecialThreeDScene",
    "SampleSpaceScene",
)


@dataclass(frozen=True)
class SceneClass:
    """A discovered scene class definition."""

    name: str
    bases: tuple[str, ...]
    lineno: int
    has_construct: bool
    methods: tuple[str, ...]
    docstring: str | None = None


def discover_scene_classes(
    source: str,
    *,
    filename: str = "<generated>",
    base_class_names: tuple[str, ...] = DEFAULT_SCENE_BASES,
    require_construct: bool = False,
    match_scene_suffix: bool = True,
) -> tuple[SceneClass, ...]:
    """Discover likely Manim scene classes from Python source without imports."""

    tree = ast.parse(source, filename=filename)
    scenes: list[SceneClass] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = tuple(filter(None, (_base_name(base) for base in node.bases)))
        if not _is_scene_class(bases, base_class_names, match_scene_suffix):
            continue
        methods = tuple(child.name for child in node.body if isinstance(child, ast.FunctionDef))
        has_construct = "construct" in methods
        if require_construct and not has_construct:
            continue
        scenes.append(
            SceneClass(
                name=node.name,
                bases=bases,
                lineno=node.lineno,
                has_construct=has_construct,
                methods=methods,
                docstring=ast.get_docstring(node),
            )
        )
    return tuple(sorted(scenes, key=lambda scene: (scene.lineno, scene.name)))


def discover_scene_classes_in_file(
    path: str | Path,
    *,
    base_class_names: tuple[str, ...] = DEFAULT_SCENE_BASES,
    require_construct: bool = False,
    match_scene_suffix: bool = True,
    encoding: str = "utf-8",
) -> tuple[SceneClass, ...]:
    """Read a Python file and discover likely Manim scene classes."""

    source_path = Path(path)
    return discover_scene_classes(
        source_path.read_text(encoding=encoding),
        filename=str(source_path),
        base_class_names=base_class_names,
        require_construct=require_construct,
        match_scene_suffix=match_scene_suffix,
    )


def find_primary_scene_class(source: str, *, filename: str = "<generated>") -> SceneClass | None:
    """Return the first construct-bearing scene class, falling back to the first scene."""

    with_construct = discover_scene_classes(source, filename=filename, require_construct=True)
    if with_construct:
        return with_construct[0]
    scenes = discover_scene_classes(source, filename=filename)
    return scenes[0] if scenes else None


def _is_scene_class(
    bases: tuple[str, ...],
    base_class_names: tuple[str, ...],
    match_scene_suffix: bool,
) -> bool:
    for base in bases:
        short_name = base.rsplit(".", 1)[-1]
        if short_name in base_class_names:
            return True
        if match_scene_suffix and short_name.endswith("Scene"):
            return True
    return False


def _base_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _base_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    if isinstance(node, ast.Subscript):
        return _base_name(node.value)
    return None
