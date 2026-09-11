"""Blender orthographic views — run: blender --background --python design/render_blender.py"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "views"
STL = ROOT / "output" / "cad" / "solo1_frame_assembly.stl"

try:
    import bpy
    from mathutils import Vector
except ImportError:
    print("Run inside Blender", file=sys.stderr)
    sys.exit(1)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_frame() -> bpy.types.Object:
    if not STL.is_file():
        bpy.ops.mesh.primitive_cube_add(size=2)
        return bpy.context.active_object
    bpy.ops.wm.stl_import(filepath=str(STL))
    obj = bpy.context.selected_objects[0]
    obj.name = "Solo1_Frame"
    return obj


def world_bbox(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mins = Vector((min(v[i] for v in corners) for i in range(3)))
    maxs = Vector((max(v[i] for v in corners) for i in range(3)))
    return mins, maxs


def setup_material(obj: bpy.types.Object) -> None:
    mat = bpy.data.materials.new("Aluminum")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.55, 0.58, 0.62, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.25
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def setup_world() -> None:
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.08, 0.09, 0.10, 1.0)
        bg.inputs[1].default_value = 1.0


def look_at(cam: bpy.types.Object, target: Vector) -> None:
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_ortho_camera(name: str, center: Vector, eye: Vector, ortho_scale: float) -> bpy.types.Object:
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = eye
    look_at(cam, center)
    return cam


def render_view(cam: bpy.types.Object, path: Path, resolution: int = 2400) -> None:
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = int(resolution * 0.75)
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    clear_scene()
    setup_world()

    frame = import_frame()
    setup_material(frame)
    bpy.context.view_layer.update()

    mins, maxs = world_bbox(frame)
    center = (mins + maxs) / 2
    size = maxs - mins
    span = max(size.x, size.y, size.z)
    ortho = span * 1.35
    dist = span * 2.5

    bpy.ops.object.light_add(type="SUN", location=(center.x + dist, center.y - dist, center.z + dist))
    bpy.context.active_object.data.energy = 4.0
    bpy.ops.object.light_add(type="AREA", location=(center.x - dist, center.y + dist, center.z + dist * 0.5))
    bpy.context.active_object.data.energy = 8000
    bpy.context.active_object.data.size = span

    views = {
        "top": center + Vector((0, 0, dist)),
        "front": center + Vector((0, -dist, 0)),
        "side": center + Vector((dist, 0, 0)),
        "iso": center + Vector((dist * 0.7, -dist * 0.7, dist * 0.55)),
    }

    for name, eye in views.items():
        cam = add_ortho_camera(name, center, eye, ortho)
        render_view(cam, OUT / f"solo1_{name}.png")
        print("rendered", OUT / f"solo1_{name}.png", "ortho", round(ortho), "center", tuple(round(c, 1) for c in center))


if __name__ == "__main__":
    main()
