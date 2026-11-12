"""One builder per engine. Each draws a compiled shot (see ``studio.spec.compile``).

``blender_shot`` runs inside Blender and imports only ``bpy`` and the standard
library. ``manim_shot`` runs in the Studio Python environment.
"""
