"""Draw a compiled shot with Blender EEVEE. This file runs inside Blender.

    blender --background --factory-startup --gpu-backend opengl \
        --python blender_shot.py -- <compiled.json> <frames_dir> <samples>

It reads the compiled shot (spheres, arrows, meshes, tubes, a camera position
for every frame, the background), builds the scene, renders every frame to
``<frames_dir>/frame_0001.png`` ..., and writes ``<frames_dir>/result.json``
with the seconds each frame took.
Only ``bpy``, ``mathutils`` and the standard library are imported.
"""

import json
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector


def linear(hex_color, alpha=1.0):
    """sRGB hex to the linear RGBA that Blender's colour sockets expect."""
    channels = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return tuple(
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ) + (alpha,)


_materials = {}


def material(hex_color, emission=0.0, opacity=1.0):
    key = (hex_color, emission, opacity)
    if key not in _materials:
        mat = bpy.data.materials.new(f"studio_{hex_color}_{emission}_{opacity}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        colour = linear(hex_color)
        for name, value in (("Base Color", colour), ("Roughness", 0.35),
                            ("Emission Color", colour), ("Emission Strength", emission),
                            ("Alpha", opacity)):
            socket = bsdf.inputs.get(name) if bsdf is not None else None
            if socket is not None:
                socket.default_value = value
        if opacity < 1.0:
            for attribute, value in (("surface_render_method", "BLENDED"),
                                     ("blend_method", "BLEND")):
                try:
                    setattr(mat, attribute, value)
                except (AttributeError, TypeError):
                    pass
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


def track(obj, target):
    constraint = obj.constraints.new("TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"


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

    for index, item in enumerate(compiled.get("spheres", [])):
        r = item["radius"]
        place(f"sphere_{index}", sphere, item["center"], (r, r, r),
              material(item["color"]))
    for index, item in enumerate(compiled.get("arrows", [])):
        start, end = Vector(item["start"]), Vector(item["end"])
        if (end - start).length == 0.0:
            continue
        direction = (end - start).normalized()
        head = min(item["head_length"], (end - start).length)
        shaft_end = end - direction * head
        shaft_length = (shaft_end - start).length
        mat = material(item["color"], emission=1.0)
        if shaft_length > 0.0:
            place(f"shaft_{index}", cylinder, (start + shaft_end) / 2,
                  (item["shaft_radius"], item["shaft_radius"], shaft_length), mat, direction)
        place(f"head_{index}", cone, (shaft_end + end) / 2,
              (item["head_radius"], item["head_radius"], head), mat, direction)
    for index, item in enumerate(compiled.get("meshes", [])):
        mesh = bpy.data.meshes.new(f"surface_{index}")
        mesh.from_pydata(item["vertices"], [], item["faces"])
        mesh.update()
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        mesh.materials.append(material(item["color"], opacity=item.get("opacity", 1.0)))
        scene.collection.objects.link(bpy.data.objects.new(f"surface_{index}", mesh))
    for index, item in enumerate(compiled.get("tubes", [])):
        curve = bpy.data.curves.new(f"tube_{index}", "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = item["radius"]
        curve.bevel_resolution = 4
        spline = curve.splines.new("POLY")
        spline.points.add(len(item["points"]) - 1)
        for point, xyz in zip(spline.points, item["points"]):
            point.co = (xyz[0], xyz[1], xyz[2], 1.0)
        curve.materials.append(material(item["color"], emission=0.6))
        scene.collection.objects.link(bpy.data.objects.new(f"tube_{index}", curve))

    cam = compiled["blender_camera"]
    target = bpy.data.objects.new("CameraTarget", None)
    target.location = cam["target"]
    scene.collection.objects.link(target)
    camera_data = bpy.data.cameras.new("StudioCamera")
    camera_data.sensor_fit = cam["sensor_fit"]
    camera_data.angle_y = cam["angle_y"]
    camera = bpy.data.objects.new("StudioCamera", camera_data)
    camera.location = cam["location"]
    track(camera, target)
    scene.collection.objects.link(camera)
    scene.camera = camera

    # The lights are children of the camera, so they follow it and every
    # frame is lit from the viewer's side. A light shines along its own -Z,
    # which is also the direction the camera looks.
    distance = (Vector(cam["target"]) - Vector(cam["location"])).length
    key = bpy.data.lights.new("Key", "AREA")
    key.energy = 5.5 * distance * distance
    key.size = 6.0
    key_obj = bpy.data.objects.new("Key", key)
    key_obj.parent = camera
    key_obj.location = (4.0, 4.0, 0.0)  # camera space: right of and above the lens
    key_obj.rotation_euler = (-0.3, 0.3, 0.0)  # turned back toward the target
    scene.collection.objects.link(key_obj)
    fill = bpy.data.lights.new("Fill", "SUN")
    fill.energy = 1.0
    fill_obj = bpy.data.objects.new("Fill", fill)
    fill_obj.parent = camera
    fill_obj.rotation_euler = (0.0, -0.5, 0.0)
    scene.collection.objects.link(fill_obj)
    return scene, camera


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    compiled = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    frames_dir = Path(args[1])
    samples = int(args[2])
    frames_dir.mkdir(parents=True, exist_ok=True)
    scene, camera = build(compiled, samples)
    seconds = []
    for index, position in enumerate(compiled["camera_path"]):
        camera.location = position
        scene.frame_set(index + 1)
        scene.render.filepath = str(frames_dir / f"frame_{index + 1:04d}.png")
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        seconds.append(round(time.perf_counter() - started, 3))
    result = {"frames": len(seconds), "seconds_per_frame": seconds,
              "blender": bpy.app.version_string, "engine": scene.render.engine,
              "objects": len(scene.objects)}
    (frames_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("STUDIO_SHOT_OK", json.dumps({"frames": len(seconds)}))


main()
