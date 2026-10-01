"""Render a Blender preview PNG of the PCBA GLB. Run from pcb/ (paths are relative):
   LC_ALL=C blender -b -noaudio --python scripts/render_glb.py
"""
import math
import bpy
from mathutils import Vector

GLB = "renders/einhander-pcba.glb"
OUT = "renders/einhander-pcba-preview.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

objs = [o for o in bpy.data.objects if o.type == "MESH"]
mn = Vector((1e18,) * 3)
mx = Vector((-1e18,) * 3)
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i])
            mx[i] = max(mx[i], w[i])
center = (mn + mx) / 2
size = (mx - mn).length

cam_d = bpy.data.cameras.new("c")
cam = bpy.data.objects.new("c", cam_d)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam
d = size * 0.95
cam.location = center + Vector((d * 0.8, -d * 0.9, d * 0.75))
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.clip_end = size * 20

su = bpy.data.lights.new("s", "SUN")
so = bpy.data.objects.new("s", su)
bpy.context.scene.collection.objects.link(so)
so.rotation_euler = (math.radians(55), math.radians(15), math.radians(40))
su.energy = 4

w = bpy.data.worlds.new("w")
bpy.context.scene.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 1.2

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.color_type = "MATERIAL"
sc.display.shading.light = "STUDIO"
sc.render.resolution_x = 1500
sc.render.resolution_y = 1000
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("rendered", OUT)
