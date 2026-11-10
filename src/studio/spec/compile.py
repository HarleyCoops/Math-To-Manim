"""Compile one shot into plain values that an engine draws without thinking.

An engine script never sees a ``lattice`` or an expression. It sees spheres,
arrows, meshes and tubes with world positions and sRGB colours, a camera
position for every frame, and the camera in its own convention. The
expansion happens once, here, so the engines cannot differ.
"""

from __future__ import annotations

import math
from typing import Any

from studio.spec import convert
from studio.spec.expr import compile_expression
from studio.spec.models import (
    Arrows,
    Curve,
    Lattice,
    Points,
    SceneSpec,
    Shot,
    Surface,
)

ARROW_SHAFT_RADIUS = 0.05
ARROW_HEAD_RADIUS = 0.13
ARROW_HEAD_LENGTH = 0.22


def _arrow(start, end, colour: str, shaft_radius: float = ARROW_SHAFT_RADIUS) -> dict:
    scale = shaft_radius / ARROW_SHAFT_RADIUS
    return {"start": list(start), "end": list(end), "color": colour,
            "shaft_radius": shaft_radius, "head_radius": ARROW_HEAD_RADIUS * scale,
            "head_length": ARROW_HEAD_LENGTH * scale}


def expand_lattice(obj: Lattice, palette: dict[str, str]) -> tuple[list[dict], list[dict]]:
    """Atoms as spheres and spins as arrows along +Z or -Z."""
    spheres: list[dict] = []
    arrows: list[dict] = []
    nx, ny, nz = obj.counts
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                first = (ix + iy + iz) % 2 == 0
                colour = palette[obj.colors[0] if first else obj.colors[1]]
                center = (
                    obj.center[0] + (ix - (nx - 1) / 2) * obj.spacing[0],
                    obj.center[1] + (iy - (ny - 1) / 2) * obj.spacing[1],
                    obj.center[2] + (iz - (nz - 1) / 2) * obj.spacing[2],
                )
                sign = 1.0 if first else -1.0
                spheres.append({"center": list(center), "radius": obj.atom_radius,
                                "color": colour})
                arrows.append(_arrow(
                    (center[0], center[1], center[2] + sign * obj.atom_radius),
                    (center[0], center[1],
                     center[2] + sign * (obj.atom_radius + obj.spin_length)),
                    colour))
    return spheres, arrows


def expand_surface(obj: Surface, palette: dict[str, str]) -> dict:
    """A grid mesh of z = f(x, y): vertices row by row, one quad per cell."""
    f = compile_expression(obj.z, ("x", "y"))
    n = obj.resolution
    vertices: list[list[float]] = []
    for j in range(n + 1):
        y = obj.y_range[0] + (obj.y_range[1] - obj.y_range[0]) * j / n
        for i in range(n + 1):
            x = obj.x_range[0] + (obj.x_range[1] - obj.x_range[0]) * i / n
            vertices.append([x, y, f(x=x, y=y)])
    faces = [[j * (n + 1) + i, j * (n + 1) + i + 1,
              (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i]
             for j in range(n) for i in range(n)]
    return {"vertices": vertices, "faces": faces, "color": palette[obj.color],
            "opacity": obj.opacity}


def expand_curve(obj: Curve, palette: dict[str, str]) -> dict:
    fx, fy, fz = (compile_expression(s, ("t",)) for s in (obj.x, obj.y, obj.z))
    t0, t1 = obj.t_range
    points = []
    for k in range(obj.samples + 1):
        t = t0 + (t1 - t0) * k / obj.samples
        points.append([fx(t=t), fy(t=t), fz(t=t)])
    return {"points": points, "radius": obj.radius, "color": palette[obj.color]}


def camera_path(position, target, orbit_deg: float, frames: int) -> list[list[float]]:
    """The camera position for each frame: an orbit about the vertical through the target."""
    rel = [position[i] - target[i] for i in range(3)]
    path = []
    for index in range(frames):
        share = index / (frames - 1) if frames > 1 else 0.0
        angle = math.radians(orbit_deg) * share
        c, s = math.cos(angle), math.sin(angle)
        path.append([target[0] + rel[0] * c - rel[1] * s,
                     target[1] + rel[0] * s + rel[1] * c,
                     target[2] + rel[2]])
    return path


def _common(spec: SceneSpec, shot: Shot, frames: int) -> dict[str, Any]:
    return {
        "shot": shot.id,
        "kind": shot.kind,
        "title": spec.title,
        "fps": spec.world.fps,
        "frames": frames,
        "duration_s": frames / spec.world.fps,
        "width": spec.world.width,
        "height": spec.world.height,
        "background": spec.palette["paper"],
        "ink": spec.colour("ink"),
        "muted": spec.colour("muted"),
        "accent": spec.colour("accent"),
        "equations": [spec.equation(e).latex for e in shot.equations],
    }


def compile_shot(spec: SceneSpec, shot_id: str, *, still: bool = False) -> dict[str, Any]:
    """Everything an engine needs to draw ``shot_id``, as JSON-ready values.

    ``still=True`` compiles one frame, for a single picture of the shot.
    """
    shot = spec.shot(shot_id)
    frames = 1 if still else spec.frame_count(shot)
    compiled = _common(spec, shot, frames)
    if shot.kind == "card":
        compiled.update(headline=shot.headline, body=shot.body)
        return compiled

    camera = spec.camera(shot.camera)
    spheres: list[dict] = []
    arrows: list[dict] = []
    meshes: list[dict] = []
    tubes: list[dict] = []
    for object_id in shot.objects:
        obj = spec.object(object_id)
        if isinstance(obj, Lattice):
            more_spheres, more_arrows = expand_lattice(obj, spec.palette)
            spheres += more_spheres
            arrows += more_arrows
        elif isinstance(obj, Surface):
            meshes.append(expand_surface(obj, spec.palette))
        elif isinstance(obj, Curve):
            tubes.append(expand_curve(obj, spec.palette))
        elif isinstance(obj, Points):
            spheres += [{"center": list(p), "radius": obj.radius,
                         "color": spec.palette[obj.color]} for p in obj.points]
        elif isinstance(obj, Arrows):
            arrows += [_arrow(a.start, a.end, spec.palette[obj.color], obj.shaft_radius)
                       for a in obj.arrows]
    view = dict(position=camera.position, target=camera.target, fov_y_deg=camera.fov_y_deg)
    compiled.update({
        "caption": shot.caption,
        "camera": {"position": list(camera.position), "target": list(camera.target),
                   "up": list(camera.up), "fov_y_deg": camera.fov_y_deg},
        "camera_path": camera_path(camera.position, camera.target, shot.orbit_deg, frames),
        "manim_camera": convert.manim_camera(**view),
        "blender_camera": convert.blender_camera(**view),
        "three_camera": convert.three_camera(up=camera.up, width=spec.world.width,
                                             height=spec.world.height, **view),
        "spheres": spheres,
        "arrows": arrows,
        "meshes": meshes,
        "tubes": tubes,
    })
    return compiled
