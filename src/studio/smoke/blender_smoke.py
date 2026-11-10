"""Studio smoke scene for Blender. This file runs inside Blender, not in the venv.

    blender --background --factory-startup --gpu-backend opengl \
        --python blender_smoke.py -- <out_dir> <frames> <width> <height> <samples>

It builds a small lit scene (a two-sublattice crystal with opposite spin
arrows), renders it with EEVEE, and writes ``frame_0001.png`` ... plus
``result.json`` with the Blender version, the GPU backend, and the seconds
each frame took. ``studio doctor`` reads ``result.json``.

Only the standard library and ``bpy`` are imported: Blender's Python does not
see the repository's packages.
"""

import json
import math
import sys
import time
from pathlib import Path

import bpy


def linear(hex_color):
    """sRGB hex to the linear RGBA that Blender's colour sockets expect."""
    channels = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return tuple(
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ) + (1.0,)


PAPER = linear("#0c0c0b")
CORAL = linear("#d97757")
BLUE = linear("#6a9bcc")
IVORY = linear("#faf9f5")


def material(name, color, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        for key, value in (("Base Color", color), ("Roughness", 0.35),
                           ("Emission Color", color), ("Emission Strength", emission)):
            socket = bsdf.inputs.get(key)
            if socket is not None:
                socket.default_value = value
    return mat


def linked(name, mesh, location, mat, rotation=(0.0, 0.0, 0.0), parent=None):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    # Objects share one mesh, so the material must be linked to the object.
    # A material linked to the mesh would be the same for every object.
    obj.material_slots[0].link = "OBJECT"
    obj.material_slots[0].material = mat
    obj.parent = parent
    bpy.context.scene.collection.objects.link(obj)
    return obj


def primitive_mesh(op, **kwargs):
    """Make one primitive, keep its mesh, remove the object that came with it."""
    op(**kwargs)
    obj = bpy.context.active_object
    mesh = obj.data
    bpy.ops.object.shade_smooth()
    mesh.materials.append(None)  # one empty slot; each object fills its own
    bpy.data.objects.remove(obj)
    return mesh


def build_scene(samples, width, height):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = samples
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs[0].default_value = PAPER
        background.inputs[1].default_value = 1.0
    scene.world = world

    sphere = primitive_mesh(bpy.ops.mesh.primitive_uv_sphere_add,
                            radius=0.28, segments=48, ring_count=24)
    shaft = primitive_mesh(bpy.ops.mesh.primitive_cylinder_add,
                           radius=0.05, depth=0.4, vertices=24)
    head = primitive_mesh(bpy.ops.mesh.primitive_cone_add,
                          radius1=0.13, depth=0.22, vertices=24)

    atom_a = material("SublatticeA", CORAL)
    atom_b = material("SublatticeB", BLUE)
    spin_up = material("SpinUp", CORAL, emission=1.0)
    spin_down = material("SpinDown", BLUE, emission=1.0)

    pivot = bpy.data.objects.new("LatticePivot", None)
    scene.collection.objects.link(pivot)
    count = 0
    for ix in range(4):
        for iy in range(4):
            for iz in range(2):
                up = (ix + iy + iz) % 2 == 0
                x, y, z = (ix - 1.5) * 1.4, (iy - 1.5) * 1.4, (iz - 0.5) * 2.2
                linked(f"Atom{count}", sphere, (x, y, z), atom_a if up else atom_b,
                       parent=pivot)
                sign = 1.0 if up else -1.0
                flip = (0.0, 0.0, 0.0) if up else (math.pi, 0.0, 0.0)
                mat = spin_up if up else spin_down
                linked(f"Shaft{count}", shaft, (x, y, z + sign * 0.42), mat, flip, pivot)
                linked(f"Head{count}", head, (x, y, z + sign * 0.7), mat, flip, pivot)
                count += 1

    key = bpy.data.lights.new("Key", "AREA")
    key.energy = 600.0
    key.size = 6.0
    key.color = IVORY[:3]
    key_obj = bpy.data.objects.new("Key", key)
    key_obj.location = (5.0, -6.0, 8.0)
    key_obj.rotation_euler = (math.radians(40), 0.0, math.radians(35))
    scene.collection.objects.link(key_obj)

    fill = bpy.data.lights.new("Fill", "SUN")
    fill.energy = 1.2
    fill_obj = bpy.data.objects.new("Fill", fill)
    fill_obj.rotation_euler = (math.radians(65), 0.0, math.radians(-120))
    scene.collection.objects.link(fill_obj)

    target = bpy.data.objects.new("CameraTarget", None)
    scene.collection.objects.link(target)
    camera_data = bpy.data.cameras.new("StudioCamera")
    camera_data.sensor_fit = "VERTICAL"
    camera_data.angle_y = math.radians(35.0)
    camera = bpy.data.objects.new("StudioCamera", camera_data)
    camera.location = (8.5, -8.5, 5.5)
    track = camera.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    scene.collection.objects.link(camera)
    scene.camera = camera
    return scene, pivot


def gpu_facts():
    facts = {}
    try:
        import gpu

        facts["backend"] = gpu.platform.backend_type_get()
        facts["renderer"] = gpu.platform.renderer_get()
        facts["vendor"] = gpu.platform.vendor_get()
        facts["version"] = gpu.platform.version_get()
    except Exception as exc:  # noqa: BLE001 - facts are best effort
        facts["error"] = f"{type(exc).__name__}: {exc}"
    return facts


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    out_dir = Path(args[0])
    frames, width, height, samples = (int(value) for value in args[1:5])
    out_dir.mkdir(parents=True, exist_ok=True)

    scene, pivot = build_scene(samples, width, height)
    seconds = []
    for index in range(frames):
        pivot.rotation_euler = (0.0, 0.0, math.radians(6.0 * index))
        scene.frame_set(index + 1)
        scene.render.filepath = str(out_dir / f"frame_{index + 1:04d}.png")
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        seconds.append(round(time.perf_counter() - started, 3))

    result = {
        "blender": bpy.app.version_string,
        "engine": scene.render.engine,
        "width": width,
        "height": height,
        "samples": samples,
        "frames": frames,
        "seconds_per_frame": seconds,
        "gpu": gpu_facts(),
    }
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("STUDIO_SMOKE_OK", json.dumps(result))


main()
