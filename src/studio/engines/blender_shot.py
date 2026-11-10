"""Draw a compiled shot with Blender EEVEE. This file runs inside Blender.

    blender --background --factory-startup --gpu-backend opengl \
        --python blender_shot.py -- <compiled.json> <out.png> <samples>

It reads the compiled shot (spheres, arrows, camera, background), builds the
scene, renders one still, and writes ``<out>.json`` with the seconds it took.
Only ``bpy``, ``mathutils`` and the standard library are imported.
"""

import json
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector


def linear(hex_color):
    """sRGB hex to the linear RGBA that Blender's colour sockets expect."""
    channels = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return tuple(
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ) + (1.0,)


_materials = {}


def material(hex_color, emission):
    key = (hex_color, emission)
    if key not in _materials:
        mat = bpy.data.materials.new(f"studio_{hex_color}_{emission}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        colour = linear(hex_color)
        for name, value in (("Base Color", colour), ("Roughness", 0.35),
                            ("Emission Color", colour), ("Emission Strength", emission)):
            socket = bsdf.inputs.get(name) if bsdf is not None else None
            if socket is not None:
                socket.default_value = value
        _materials[key] = mat
    return _materials[key]


def unit_mesh(op, **kwargs):
    """One primitive mesh with an empty material slot; objects fill their own."""
    op(**kwargs)
    obj = bpy.context.active_object
    mesh = obj.data
    bpy.ops.object.shade_smooth()
    mesh.materials.append(None)
    bpy.data.objects.remove(obj)
    return mesh


def place(name, mesh, location, scale, mat, direction=None):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.scale = scale
    if direction is not None:
        obj.rotation_euler = Vector((0.0, 0.0, 1.0)).rotation_difference(direction).to_euler()
    obj.material_slots[0].link = "OBJECT"
    obj.material_slots[0].material = mat
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build(compiled, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = samples
    scene.render.resolution_x = compiled["width"]
    scene.render.resolution_y = compiled["height"]
    scene.render.resolution_percentage = 100
    scene.render.fps = compiled["fps"]
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs[0].default_value = linear(compiled["background"])
        background.inputs[1].default_value = 1.0
    scene.world = world

    # Unit meshes, scaled per instance: radius 1 sphere; radius 1, height 1
    # cylinder and cone, both centred on their own origin.
    sphere = unit_mesh(bpy.ops.mesh.primitive_uv_sphere_add, radius=1.0,
                       segments=48, ring_count=24)
    cylinder = unit_mesh(bpy.ops.mesh.primitive_cylinder_add, radius=1.0, depth=1.0,
                         vertices=24)
    cone = unit_mesh(bpy.ops.mesh.primitive_cone_add, radius1=1.0, depth=1.0, vertices=24)

    for index, item in enumerate(compiled["spheres"]):
        r = item["radius"]
        place(f"sphere_{index}", sphere, item["center"], (r, r, r),
              material(item["color"], 0.0))
    for index, item in enumerate(compiled["arrows"]):
        start, end = Vector(item["start"]), Vector(item["end"])
        direction = (end - start).normalized()
        head = min(item["head_length"], (end - start).length)
        shaft_end = end - direction * head
        shaft_length = (shaft_end - start).length
        mat = material(item["color"], 1.0)
        if shaft_length > 0.0:
            place(f"shaft_{index}", cylinder, (start + shaft_end) / 2,
                  (item["shaft_radius"], item["shaft_radius"], shaft_length), mat, direction)
        place(f"head_{index}", cone, (shaft_end + end) / 2,
              (item["head_radius"], item["head_radius"], head), mat, direction)

    cam = compiled["blender_camera"]
    target = bpy.data.objects.new("CameraTarget", None)
    target.location = cam["target"]
    scene.collection.objects.link(target)
    camera_data = bpy.data.cameras.new("StudioCamera")
    camera_data.sensor_fit = cam["sensor_fit"]
    camera_data.angle_y = cam["angle_y"]
    camera = bpy.data.objects.new("StudioCamera", camera_data)
    camera.location = cam["location"]
    track = camera.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    scene.collection.objects.link(camera)
    scene.camera = camera

    # Lights follow the camera so every shot is lit from the viewer's side.
    position, aim = Vector(cam["location"]), Vector(cam["target"])
    forward = (aim - position).normalized()
    right = forward.cross(Vector((0.0, 0.0, 1.0))).normalized()
    key = bpy.data.lights.new("Key", "AREA")
    key.energy = 55.0 * (aim - position).length_squared / 10.0
    key.size = 6.0
    key_obj = bpy.data.objects.new("Key", key)
    key_obj.location = position + right * 4.0 + Vector((0.0, 0.0, 4.0))
    key_track = key_obj.constraints.new("TRACK_TO")
    key_track.target = target
    key_track.track_axis = "TRACK_NEGATIVE_Z"
    key_track.up_axis = "UP_Y"
    scene.collection.objects.link(key_obj)
    fill = bpy.data.lights.new("Fill", "SUN")
    fill.energy = 1.0
    fill_obj = bpy.data.objects.new("Fill", fill)
    fill_obj.location = position - right * 6.0
    fill_track = fill_obj.constraints.new("TRACK_TO")
    fill_track.target = target
    fill_track.track_axis = "TRACK_NEGATIVE_Z"
    fill_track.up_axis = "UP_Y"
    scene.collection.objects.link(fill_obj)
    return scene


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    compiled = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    out = Path(args[1])
    samples = int(args[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    scene = build(compiled, samples)
    scene.render.filepath = str(out)
    started = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    result = {"image": str(out), "seconds": round(time.perf_counter() - started, 3),
              "blender": bpy.app.version_string, "engine": scene.render.engine,
              "objects": len(scene.objects)}
    Path(str(out) + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("STUDIO_SHOT_OK", json.dumps(result))


main()
