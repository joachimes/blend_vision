from itertools import cycle
import bpy

class scene():
    def __init__(self, engine='BLENDER_EEVEE', device=None) -> None:
        # bpy.context.scene.render.engine = 'CYCLES'
        # bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        # bpy.context.scene.cycles.device = 'GPU'
        self.engine = engine
        bpy.context.scene.render.engine = engine
        if self.engine == 'CYCLES':
            bpy.context.scene.cycles.device = self.__device


    def clean_up(self):
        # Delete all textures, materials and meshes
        for img in bpy.data.images:
            bpy.data.images.remove(img)
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)