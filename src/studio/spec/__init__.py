"""SceneSpec: the one scene description that every engine is compiled from.

- ``models``: the typed description (world, palette, equations, objects,
  cameras, shots) and its checks
- ``convert``: the mathematics between conventions (colour, axes, cameras)
- ``compile``: expands a shot into plain spheres and arrows that an engine
  can draw without knowing what a lattice is
"""

from studio.spec.models import SceneSpec, load_spec

__all__ = ["SceneSpec", "load_spec"]
