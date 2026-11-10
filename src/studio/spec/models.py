"""SceneSpec v1: typed, engine-neutral, checked before anything is rendered.

Conventions, fixed here so no engine has to decide them:

- right-handed world, Z up, metres
- one frame rate for every engine
- colours are sRGB hex, named in ``palette`` and used by name
- a camera is a position, a target, an up vector and a VERTICAL field of view
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Vec3 = tuple[float, float, float]
Engine = Literal["manim", "blender", "three"]
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class World(_Strict):
    units: Literal["m"] = "m"
    up: Literal["z"] = "z"
    fps: int = Field(default=30, ge=1, le=120)
    width: int = Field(default=1920, ge=16)
    height: int = Field(default=1080, ge=16)


class Equation(_Strict):
    id: str
    latex: str = Field(min_length=1)
    svg: str | None = None


class Lattice(_Strict):
    """Atoms on a box grid in two sublattices, each atom with a spin arrow.

    ``rule`` says which sublattice an atom is in. ``checkerboard`` alternates
    in all three directions, so every nearest neighbour has the opposite spin.
    """

    type: Literal["lattice"] = "lattice"
    id: str
    counts: tuple[int, int, int]
    spacing: Vec3
    center: Vec3 = (0.0, 0.0, 0.0)
    atom_radius: float = Field(default=0.28, gt=0)
    spin_length: float = Field(default=0.55, gt=0)
    colors: tuple[str, str]
    rule: Literal["checkerboard"] = "checkerboard"

    @field_validator("counts")
    @classmethod
    def _counts_positive(cls, value: tuple[int, int, int]) -> tuple[int, int, int]:
        if any(n < 1 for n in value) or value[0] * value[1] * value[2] > 2000:
            raise ValueError("counts must each be >= 1 and at most 2000 atoms in total")
        return value


class Camera(_Strict):
    id: str
    position: Vec3
    target: Vec3 = (0.0, 0.0, 0.0)
    up: Vec3 = (0.0, 0.0, 1.0)
    fov_y_deg: float = Field(gt=1.0, lt=170.0)

    @model_validator(mode="after")
    def _not_degenerate(self) -> "Camera":
        if self.position == self.target:
            raise ValueError(f"camera {self.id!r}: position and target are the same point")
        return self


class Shot(_Strict):
    id: str
    engine: Engine
    fallback: Engine | None = None
    camera: str
    objects: list[str] = Field(min_length=1)
    equations: list[str] = Field(default_factory=list)
    frames: int = Field(default=1, ge=1)
    narration: str = ""


class SceneSpec(_Strict):
    version: Literal[1] = 1
    title: str
    world: World = Field(default_factory=World)
    palette: dict[str, str]
    equations: list[Equation] = Field(default_factory=list)
    objects: list[Lattice]
    cameras: list[Camera]
    shots: list[Shot]

    @field_validator("palette")
    @classmethod
    def _palette_is_hex(cls, value: dict[str, str]) -> dict[str, str]:
        bad = [name for name, colour in value.items() if not _HEX.match(colour)]
        if bad:
            raise ValueError(f"palette colours must be #rrggbb: {', '.join(bad)}")
        if "paper" not in value:
            raise ValueError("palette needs a 'paper' colour for the background")
        return value

    @model_validator(mode="after")
    def _references_resolve(self) -> "SceneSpec":
        problems: list[str] = []
        for kind, items in (("object", self.objects), ("camera", self.cameras),
                            ("equation", self.equations), ("shot", self.shots)):
            ids = [item.id for item in items]
            problems += [f"duplicate {kind} id {i!r}" for i in set(ids) if ids.count(i) > 1]
        objects = {o.id for o in self.objects}
        cameras = {c.id for c in self.cameras}
        equations = {e.id for e in self.equations}
        for obj in self.objects:
            problems += [f"object {obj.id!r}: unknown palette colour {c!r}"
                         for c in obj.colors if c not in self.palette]
        for shot in self.shots:
            if shot.camera not in cameras:
                problems.append(f"shot {shot.id!r}: unknown camera {shot.camera!r}")
            problems += [f"shot {shot.id!r}: unknown object {o!r}"
                         for o in shot.objects if o not in objects]
            problems += [f"shot {shot.id!r}: unknown equation {e!r}"
                         for e in shot.equations if e not in equations]
        if problems:
            raise ValueError("; ".join(sorted(problems)))
        return self

    def shot(self, shot_id: str) -> Shot:
        for shot in self.shots:
            if shot.id == shot_id:
                return shot
        raise KeyError(f"no shot {shot_id!r}; shots are: {', '.join(s.id for s in self.shots)}")

    def camera(self, camera_id: str) -> Camera:
        return next(c for c in self.cameras if c.id == camera_id)

    def object(self, object_id: str) -> Lattice:
        return next(o for o in self.objects if o.id == object_id)


def load_spec(path: Path | str) -> SceneSpec:
    """Read and check a SceneSpec file."""
    return SceneSpec.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
