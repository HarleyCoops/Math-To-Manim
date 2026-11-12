"""SceneSpec v1: typed, engine-neutral, checked before anything is rendered.

Conventions, fixed here so no engine has to decide them:

- right-handed world, Z up, metres
- one frame rate and one frame size for every engine
- colours are sRGB hex, named in ``palette`` and used by name
- a camera is a position, a target, an up vector and a VERTICAL field of view

A film is a list of shots. A shot is one of two kinds:

- ``scene3d``: objects seen from a camera, drawn by Blender. The camera can
  orbit its target. A caption and one equation can lie over the picture.
- ``card``: a headline, equations and a few lines of text, drawn by Manim.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from studio.spec.expr import ExpressionError, compile_expression

Vec3 = tuple[float, float, float]
Range = tuple[float, float]
Engine = Literal["manim", "blender", "three"]
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

#: Colours a spec may leave out; the compiler fills them in.
DEFAULT_PALETTE = {"ink": "#faf9f5", "muted": "#a8a69d", "accent": "#d97757"}


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
    latex: str = Field(min_length=1, max_length=400)
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
        if any(n < 1 for n in value) or value[0] * value[1] * value[2] > 400:
            raise ValueError("counts must each be >= 1 and at most 400 atoms in total")
        return value


class Surface(_Strict):
    """The graph z = f(x, y) over a rectangle."""

    type: Literal["surface"]
    id: str
    z: str
    x_range: Range
    y_range: Range
    resolution: int = Field(default=40, ge=4, le=100)
    color: str
    opacity: float = Field(default=1.0, gt=0.0, le=1.0)

    @model_validator(mode="after")
    def _expression_is_safe(self) -> "Surface":
        _try_expression(self.id, self.z, ("x", "y"),
                        {"x": self.x_range[0], "y": self.y_range[0]})
        return self


class Curve(_Strict):
    """A space curve (x(t), y(t), z(t)), drawn as a tube."""

    type: Literal["curve"]
    id: str
    x: str
    y: str
    z: str
    t_range: Range
    samples: int = Field(default=120, ge=2, le=600)
    radius: float = Field(default=0.04, gt=0, le=1.0)
    color: str

    @model_validator(mode="after")
    def _expressions_are_safe(self) -> "Curve":
        for source in (self.x, self.y, self.z):
            _try_expression(self.id, source, ("t",), {"t": self.t_range[0]})
        return self


class Points(_Strict):
    """Spheres at given points."""

    type: Literal["points"]
    id: str
    points: list[Vec3] = Field(min_length=1, max_length=400)
    radius: float = Field(default=0.12, gt=0, le=3.0)
    color: str


class ArrowSpan(_Strict):
    start: Vec3
    end: Vec3


class Arrows(_Strict):
    """Arrows from start to end."""

    type: Literal["arrows"]
    id: str
    arrows: list[ArrowSpan] = Field(min_length=1, max_length=300)
    shaft_radius: float = Field(default=0.04, gt=0, le=0.5)
    color: str


SceneObject = Annotated[Union[Lattice, Surface, Curve, Points, Arrows],
                        Field(discriminator="type")]


def _try_expression(owner: str, source: str, variables: tuple[str, ...],
                    sample: dict[str, float]) -> None:
    try:
        compile_expression(source, variables)(**sample)
    except ExpressionError as exc:
        raise ValueError(f"object {owner!r}: {exc}") from exc


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
    kind: Literal["scene3d", "card"] = "scene3d"
    engine: Engine | None = None
    fallback: Engine | None = None
    # scene3d
    camera: str | None = None
    objects: list[str] = Field(default_factory=list)
    orbit_deg: float = Field(default=0.0, ge=-360.0, le=360.0)
    caption: str = Field(default="", max_length=120)
    # card
    headline: str = Field(default="", max_length=80)
    body: str = Field(default="", max_length=320)
    # both
    equations: list[str] = Field(default_factory=list)
    duration_s: float = Field(default=4.0, ge=0.5, le=20.0)
    frames: int | None = Field(default=None, ge=1)
    narration: str = ""

    @model_validator(mode="after")
    def _kind_has_what_it_needs(self) -> "Shot":
        if self.kind == "scene3d":
            if not self.camera or not self.objects:
                raise ValueError(f"shot {self.id!r}: a scene3d shot needs a camera and objects")
            self.engine = self.engine or "blender"
        else:
            if not self.headline:
                raise ValueError(f"shot {self.id!r}: a card shot needs a headline")
            self.engine = self.engine or "manim"
        return self


class SceneSpec(_Strict):
    version: Literal[1] = 1
    title: str
    world: World = Field(default_factory=World)
    palette: dict[str, str]
    equations: list[Equation] = Field(default_factory=list)
    objects: list[SceneObject] = Field(default_factory=list)
    cameras: list[Camera] = Field(default_factory=list)
    shots: list[Shot] = Field(min_length=1, max_length=24)

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
            names = obj.colors if isinstance(obj, Lattice) else (obj.color,)
            problems += [f"object {obj.id!r}: unknown palette colour {c!r}"
                         for c in names if c not in self.palette]
        for shot in self.shots:
            if shot.camera is not None and shot.camera not in cameras:
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

    def object(self, object_id: str):
        return next(o for o in self.objects if o.id == object_id)

    def equation(self, equation_id: str) -> Equation:
        return next(e for e in self.equations if e.id == equation_id)

    def colour(self, name: str) -> str:
        return self.palette.get(name) or DEFAULT_PALETTE[name]

    def frame_count(self, shot: Shot) -> int:
        return shot.frames or max(1, round(shot.duration_s * self.world.fps))

    def duration_s(self) -> float:
        return sum(self.frame_count(shot) for shot in self.shots) / self.world.fps


def load_spec(path: Path | str) -> SceneSpec:
    """Read and check a SceneSpec file."""
    return SceneSpec.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
