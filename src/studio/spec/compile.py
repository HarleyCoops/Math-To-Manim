"""Compile one shot into plain geometry that every engine draws the same way.

An engine script never sees a ``lattice``. It sees spheres and arrows with
world positions, sizes and sRGB colours, plus the camera in its own
convention. The expansion happens once, here, so the engines cannot differ.
"""

from __future__ import annotations

from typing import Any

from studio.spec import convert
from studio.spec.models import Lattice, SceneSpec

ARROW_SHAFT_RADIUS = 0.05
ARROW_HEAD_RADIUS = 0.13
ARROW_HEAD_LENGTH = 0.22


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
                arrows.append({
                    "start": [center[0], center[1], center[2] + sign * obj.atom_radius],
                    "end": [center[0], center[1],
                            center[2] + sign * (obj.atom_radius + obj.spin_length)],
                    "color": colour,
                    "shaft_radius": ARROW_SHAFT_RADIUS,
                    "head_radius": ARROW_HEAD_RADIUS,
                    "head_length": ARROW_HEAD_LENGTH,
                })
    return spheres, arrows


def compile_shot(spec: SceneSpec, shot_id: str) -> dict[str, Any]:
    """Everything an engine needs to draw ``shot_id``, as JSON-ready values."""
    shot = spec.shot(shot_id)
    camera = spec.camera(shot.camera)
    spheres: list[dict] = []
    arrows: list[dict] = []
    for object_id in shot.objects:
        more_spheres, more_arrows = expand_lattice(spec.object(object_id), spec.palette)
        spheres += more_spheres
        arrows += more_arrows
    view = dict(position=camera.position, target=camera.target, fov_y_deg=camera.fov_y_deg)
    return {
        "shot": shot.id,
        "title": spec.title,
        "fps": spec.world.fps,
        "frames": shot.frames,
        "width": spec.world.width,
        "height": spec.world.height,
        "background": spec.palette["paper"],
        "camera": {"position": list(camera.position), "target": list(camera.target),
                   "up": list(camera.up), "fov_y_deg": camera.fov_y_deg},
        "manim_camera": convert.manim_camera(**view),
        "blender_camera": convert.blender_camera(**view),
        "three_camera": convert.three_camera(up=camera.up, width=spec.world.width,
                                             height=spec.world.height, **view),
        "spheres": spheres,
        "arrows": arrows,
    }
