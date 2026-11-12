"""The mathematics between conventions. Agents never do this; this module does.

World: right-handed, Z up, metres. Camera: position, target, up, vertical FOV.
Every function here is pure and has a test.
"""

from __future__ import annotations

import math

Vec3 = tuple[float, float, float]

#: Manim's frame is 8 units high at zoom 1.
MANIM_FRAME_HEIGHT = 8.0


def srgb_hex_to_linear(hex_color: str) -> Vec3:
    """``#rrggbb`` (sRGB) to linear RGB, which Blender's colour sockets expect."""
    channels = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
               for c in channels)
    return (r, g, b)


def to_three(v: Vec3) -> Vec3:
    """A Z-up world point as a three.js (Y-up) point. Both are right-handed."""
    x, y, z = v
    return (x, z, -y)


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a: Vec3) -> Vec3:
    length = math.sqrt(_dot(a, a))
    if length == 0.0:
        raise ValueError("zero-length vector")
    return (a[0] / length, a[1] / length, a[2] / length)


def distance(a: Vec3, b: Vec3) -> float:
    d = _sub(a, b)
    return math.sqrt(_dot(d, d))


def project(point: Vec3, *, position: Vec3, target: Vec3, up: Vec3, fov_y_deg: float,
            width: int, height: int) -> tuple[float, float, float]:
    """The reference pinhole camera: a world point to (pixel x, pixel y, depth).

    Pixel (0, 0) is the top-left corner. Every engine must agree with this.
    """
    forward = _unit(_sub(target, position))
    right = _unit(_cross(forward, up))
    true_up = _cross(right, forward)
    rel = _sub(point, position)
    depth = _dot(rel, forward)
    if depth <= 0.0:
        raise ValueError("point is behind the camera")
    scale = (height / 2.0) / math.tan(math.radians(fov_y_deg) / 2.0)
    return (width / 2.0 + _dot(rel, right) / depth * scale,
            height / 2.0 - _dot(rel, true_up) / depth * scale,
            depth)


def manim_camera(*, position: Vec3, target: Vec3, fov_y_deg: float) -> dict[str, object]:
    """Arguments for ``ThreeDScene.set_camera_orientation`` that match the pinhole.

    Manim places its camera at ``focal_distance`` from ``frame_center`` and
    scales a point at depth D by focal_distance / D, then by ``zoom``, in a
    frame 8 units high. Equal to the pinhole when
    zoom = 4 / (focal_distance * tan(fov / 2)).
    """
    d = distance(position, target)
    rel = _sub(position, target)
    return {
        "phi_deg": math.degrees(math.acos(max(-1.0, min(1.0, rel[2] / d)))),
        "theta_deg": math.degrees(math.atan2(rel[1], rel[0])),
        "focal_distance": d,
        "zoom": (MANIM_FRAME_HEIGHT / 2.0) / (d * math.tan(math.radians(fov_y_deg) / 2.0)),
        "frame_center": list(target),
    }


def blender_camera(*, position: Vec3, target: Vec3, fov_y_deg: float) -> dict[str, object]:
    """Blender camera values: same axes as the world; sensor fit is VERTICAL."""
    return {"location": list(position), "target": list(target),
            "sensor_fit": "VERTICAL", "angle_y": math.radians(fov_y_deg)}


def three_camera(*, position: Vec3, target: Vec3, up: Vec3, fov_y_deg: float,
                 width: int, height: int) -> dict[str, object]:
    """three.js PerspectiveCamera values. Its ``fov`` is vertical, in degrees."""
    return {"position": list(to_three(position)), "target": list(to_three(target)),
            "up": list(to_three(up)), "fov": fov_y_deg, "aspect": width / height}
